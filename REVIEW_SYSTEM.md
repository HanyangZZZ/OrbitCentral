# Orbit — Review System: Technical Deep-Dive

> **Scope:** This document covers the backend systems for **creating, reading, updating, deleting user reviews**, the **helpfulness voting mechanism**, **photo uploads to Google Cloud Storage**, and the **Bayesian rating aggregation** that feeds back into business search ranking. Business discovery, bookmarks, and authentication are out of scope.

---

## Table of Contents

1. [The Blueprint (Design & Logic)](#1-the-blueprint-design--logic)
2. [The Toolbox (Tech Stack)](#2-the-toolbox-tech-stack)
3. [The Safeguards (Quality & Growth)](#3-the-safeguards-quality--growth)
4. [The Process (Workflow & Launch)](#4-the-process-workflow--launch)

---

# 1. The Blueprint (Design & Logic)

## 1.1 Logic Overview & Data Flow

### The Core Question

> *"A user writes a 4-star review for their favourite local bakery, attaches a photo, and later another user marks it as 'useful'. What happens in the backend?"*

The answer involves **3 models**, **2 external services** (GCS for photo storage, PostgreSQL for data), and a **Django signal** that automatically recalculates the business's Bayesian rating.

### Master Data Flow Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                          USER ACTION                                   │
│  POST /api/reviews/  {business: 42, rating: 4, description: "...",    │
│                        photo: "data:image/jpeg;base64,/9j/4AAQ..."}   │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
              ┌────────────────────────────────────┐
              │        ReviewViewSet.create()       │
              │        (DRF ModelViewSet)           │
              └──────────┬─────────────────────────┘
                         │
           ┌─────────────┼─────────────────────┐
           ▼             ▼                     ▼
  ┌─────────────┐ ┌──────────────┐   ┌────────────────────┐
  │ Serializer  │ │ perform_     │   │ Django Signal       │
  │ Validation  │ │ create()     │   │ (post_save)         │
  │             │ │              │   │                     │
  │ • rating    │ │ 1. Pop photo │   │ Triggered AFTER     │
  │   1–5 check│ │    from data │   │ Review is saved     │
  │ • duplicate │ │              │   │                     │
  │   detection │ │ 2. Upload to │   │ Recalculates:       │
  │   (user +   │ │    GCS if    │   │ • Business.avg_     │
  │    business)│ │    present   │   │   rating (Bayesian) │
  │             │ │              │   │ • Business.review_  │
  │ Returns     │ │ 3. Save      │   │   count             │
  │ existing_   │ │    Review    │   │                     │
  │ review_id   │ │    with      │   │ W = (vR + mC)/(v+m)│
  │ on conflict │ │    image_url │   │                     │
  └─────────────┘ └──────────────┘   └────────────────────┘
                         │
                         ▼
              ┌────────────────────────────────────┐
              │         JSON Response               │
              │  {id, business, user, username,     │
              │   rating, description, image_url,   │
              │   vote_counts, user_votes,           │
              │   created_at, updated_at}            │
              └────────────────────────────────────┘
```

### Review Photo Upload Pipeline

When a user includes a base64-encoded photo in their review, the backend processes it through a self-contained upload pipeline:

```
Step 1: Extract Base64 Data ────────────────────────────────────────────
   │  Strip optional data-URI prefix ("data:image/jpeg;base64,")
   │  Split on comma, take the payload portion
   │  Decode from base64 → raw bytes
   ▼
Step 2: Size Validation ────────────────────────────────────────────────
   │  Check decoded bytes ≤ 5 MB
   │  If exceeded → log warning, return None (review saves without photo)
   ▼
Step 3: Format Detection (Magic Bytes) ────────────────────────────────
   │  Inspect first bytes of image data:
   │    • 0xFF 0xD8 0xFF           → JPEG  (image/jpeg)
   │    • 0x89 PNG \r\n \x1a \n   → PNG   (image/png)
   │    • RIFF....WEBP             → WebP  (image/webp)
   │    • Anything else            → fallback to JPEG
   ▼
Step 4: Generate Unique Path ──────────────────────────────────────────
   │  Path: reviews/{business_id}/{uuid_hex}.{ext}
   │  Example: reviews/42/a1b2c3d4e5f6...hex.jpg
   │  UUID ensures no filename collisions
   ▼
Step 5: Upload to Google Cloud Storage ────────────────────────────────
   │  Bucket: orbit-media-prod
   │  Set cache-control BEFORE upload: "public, max-age=31536000" (1 year)
   │  Upload with correct content_type
   │  (No blob.patch() call — avoids needing devstorage.full_control scope)
   ▼
Step 6: Return Public URL ─────────────────────────────────────────────
      https://storage.googleapis.com/orbit-media-prod/reviews/42/a1b2c3d4...hex.jpg
      Stored in Review.image_url field
```

### Helpfulness Voting System

Users can vote on other users' reviews with three vote types — acting as a **toggle** mechanism:

```
POST /api/reviews/7/vote/  {"vote_type": "useful"}

┌─────────────────────────────────────────────────────────────────┐
│                    Vote Toggle Flow                              │
│                                                                  │
│  Request: vote_type = "useful" on Review #7                     │
│                                                                  │
│  Step 1: Validate vote_type ∈ {useful, funny, cool}            │
│            │                                                     │
│  Step 2: Check self-vote → reject if review.user == request.user│
│            │                                                     │
│  Step 3: Query existing vote                                    │
│            │                                                     │
│            ├── EXISTS → DELETE → Response: {"status": "removed"} │
│            │                                                     │
│            └── NOT EXISTS → CREATE → Response: {"status":"added"}│
│                              HTTP 201                            │
└─────────────────────────────────────────────────────────────────┘
```

### Bayesian Rating Aggregation (Signal-Driven)

Every time a Review is created, updated, or deleted, a Django signal fires to recalculate the associated business's rating:

$$W = \frac{v \cdot R + m \cdot C}{v + m}$$

| Variable | Meaning | Source |
|----------|---------|--------|
| $v$ | # of user reviews on our platform | `Review.objects.filter(business=biz).count()` |
| $R$ | Average of user review ratings | `Review.objects.filter(business=biz).aggregate(Avg('rating'))` |
| $m$ | Confidence threshold (constant) | `10` — hardcoded in `BAYESIAN_CONFIDENCE_THRESHOLD` |
| $C$ | Google rating (the prior) | `Business.google_rating` — immutable after import |

**How the prior fades as user reviews accumulate:**

| $v$ (user reviews) | Weight on user scores ($\frac{v}{v+m}$) | Weight on Google ($\frac{m}{v+m}$) | Effect |
|--------------------:|------------------------------------------:|------------------------------------:|--------|
| 0 | 0% | 100% | Pure Google rating |
| 5 | 33% | 67% | Google still dominates |
| 10 | 50% | 50% | Equal blend |
| 50 | 83% | 17% | User reviews dominate |
| 100 | 91% | 9% | Nearly pure user rating |

**Signal implementation:**

```python
@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_business_review_aggregates(sender, instance, **kwargs):
    biz = instance.business
    agg = Review.objects.filter(business=biz).aggregate(
        avg=Avg('rating'), count=Count('id'),
    )
    v, R = agg['count'], float(agg['avg'] or 0)
    m, C = BAYESIAN_CONFIDENCE_THRESHOLD, float(biz.google_rating or 0)
    
    biz.avg_rating = round((v * R + m * C) / (v + m), 2) if v else C
    biz.review_count = v
    biz.save(update_fields=['avg_rating', 'review_count'])
```

This means:
- **Create** a review → business rating is immediately recalculated
- **Update** a review (change rating) → business rating is immediately recalculated
- **Delete** a review → business rating is immediately recalculated
- The rating feeds into the **weighted search score** (15% weight) in the business discovery system

### Duplicate Review Prevention

Each user can only review a business once. The system enforces this at **two levels**:

```
Level 1: Database Constraint (hard guarantee)
──────────────────────────────────────────────
  UniqueConstraint(
      fields=['business', 'user'],
      condition=Q(user__isnull=False),
      name='unique_review_per_user_per_business',
  )
  
  • Allows multiple reviews with user=NULL (deleted accounts)
  • Prevents the same authenticated user from having two reviews
  • Enforced at the database level — impossible to bypass

Level 2: Serializer Validation (user-friendly error)
──────────────────────────────────────────────────────
  On POST, the serializer checks:
    existing = Review.objects.filter(user=user, business=business).first()
    if existing:
        raise ValidationError({
            'detail': 'You have already reviewed this business.',
            'existing_review_id': existing.id,
        })

  • Returns the existing review's ID so the frontend can:
    → Navigate to that review for editing
    → Offer a "delete and re-review" flow
    → Show the user's existing review inline
```

---

## 1.2 Modularity & Modular Design

### Layer Separation

The review system spans **4 layers** with clear boundaries:

```
┌──────────────────────────────────────────────────────────────────┐
│  URL Layer                                                        │
│  urls.py: router.register('reviews', ReviewViewSet)              │
│  Route: /api/reviews/ → ReviewViewSet                            │
│  Route: /api/reviews/<id>/vote/ → ReviewViewSet.vote()           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│  ViewSet Layer (viewsets/reviews.py)                              │
│                                                                   │
│  ReviewViewSet (ModelViewSet)                                     │
│    ├── list()      → public, cursor-paginated                    │
│    ├── create()    → auth+verified, calls perform_create()       │
│    ├── retrieve()  → public                                      │
│    ├── update()    → owner only, calls perform_update()          │
│    ├── destroy()   → owner only                                  │
│    ├── vote()      → auth+verified, toggle helpfulness           │
│    └── _upload_photo()  → static helper, GCS upload              │
│                                                                   │
│  Responsibilities:                                               │
│    • Permission checking (per-action)                            │
│    • Photo extraction + upload orchestration                     │
│    • Vote toggle logic                                           │
│    • HTTP status codes                                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│  Serializer Layer (serializers/review.py)                        │
│                                                                   │
│  ReviewSerializer (ModelSerializer)                               │
│    ├── Fields: id, business, user, username, rating, description │
│    │           image_url, photo (write-only), vote_counts,       │
│    │           user_votes, created_at, updated_at                │
│    ├── get_username()    → "Deleted User" if user is NULL        │
│    ├── get_vote_counts() → {useful: N, funny: N, cool: N}       │
│    ├── get_user_votes()  → ["useful"] (current user's votes)    │
│    ├── validate_rating() → 1 ≤ rating ≤ 5                       │
│    └── validate()        → duplicate detection, returns          │
│                            existing_review_id on conflict        │
│                                                                   │
│  Responsibilities:                                               │
│    • Data validation (rating range, duplicate check)             │
│    • JSON output shaping (vote aggregation, username resolution) │
│    • Context-aware fields (user_votes depends on request.user)   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│  Model Layer (models/business.py)                                │
│                                                                   │
│  Review                                                          │
│    ├── FK → Business (CASCADE)                                   │
│    ├── FK → User (SET_NULL, nullable)                            │
│    ├── rating (1–5), description, image_url                      │
│    ├── UniqueConstraint(business, user) where user IS NOT NULL   │
│    └── Signal: post_save/post_delete → recalculate avg_rating   │
│                                                                   │
│  ReviewVote                                                      │
│    ├── FK → User (CASCADE)                                       │
│    ├── FK → Review (CASCADE)                                     │
│    ├── vote_type: useful | funny | cool                          │
│    └── UniqueConstraint(user, review, vote_type)                 │
│                                                                   │
│  Responsibilities:                                               │
│    • Schema definition + constraints                             │
│    • Cascading deletes (user deleted → reviews anonymized,       │
│      review deleted → votes cascade)                             │
│    • Bayesian rating signal                                      │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Photo handling in ViewSet, not Serializer** | Upload is side-effectful (GCS network call). Serializers should only validate/transform data. The ViewSet's `perform_create()` pops the `photo` field and calls `_upload_photo()` before saving. |
| **Vote as `@action`, not separate ViewSet** | Votes are semantically attached to a review (`/reviews/7/vote/`). A nested action keeps the URL structure RESTful and avoids a separate router registration. |
| **Cursor pagination for reviews** | Reviews are append-heavy. Page-number pagination suffers from item shifting when new reviews are inserted mid-scroll. Cursor pagination uses opaque tokens → no COUNT query, stable ordering. |
| **`SET_NULL` on user FK** | When a user deletes their account, their reviews remain visible (anonymized as "Deleted User") rather than disappearing. Preserves business rating integrity. |
| **Vote uniqueness constraint per type** | A user can cast one `useful` AND one `funny` on the same review, but NOT two `useful` votes. This mirrors Yelp-style multi-dimension feedback. |
| **Signal for rating updates** | Decouples the rating calculation from the viewset. Any code path that saves/deletes a Review (admin panel, management commands, bulk operations) automatically triggers recalculation. |

---

## 1.3 Clean Logic & Data Types

### Model Field Types — Why Each Was Chosen

| Field | Type | Why |
|-------|------|-----|
| `Review.rating` | `IntegerField` + validators `[1,5]` | Integer (not decimal) — star ratings are always whole numbers. DB validators prevent invalid data even if serializer is bypassed. |
| `Review.description` | `TextField(blank=True)` | Unlimited length, optional. Text not required — some users just want to leave a star rating. |
| `Review.image_url` | `TextField(blank=True, null=True)` | URL can be long (GCS paths). `null` distinguishes "no photo" from "empty string". |
| `Review.user` | `ForeignKey(SET_NULL, null=True)` | Nullable so reviews survive user account deletion. `SET_NULL` → anonymization, not data loss. |
| `ReviewVote.vote_type` | `CharField(max_length=10, choices=VOTE_TYPES)` | Enum-like with `choices` for validation. 3 current types: `useful`, `funny`, `cool`. Extensible by adding to `VOTE_TYPES`. |
| `ReviewVote.created_at` | `DateTimeField(auto_now_add=True)` | Tracks when the vote was cast. Useful for analytics (vote trends over time). |

### Vote Count Optimization

The serializer computes vote counts in **two modes** depending on whether `prefetch_related` was used:

```python
# Mode 1: Prefetched (used in list views — N+1 safe)
if 'votes' in obj._prefetched_objects_cache:
    for v in obj.votes.all():      # iterates in-memory, no DB hit
        counts[v.vote_type] += 1

# Mode 2: Fresh query (used in detail views or when not prefetched)
else:
    qs = obj.votes.values('vote_type').annotate(c=Count('id'))
    # Single aggregate query: SELECT vote_type, COUNT(*) GROUP BY vote_type
```

The ViewSet's `get_queryset()` uses `prefetch_related('votes')`, so **list views** use Mode 1 (zero extra queries), while **ad-hoc access** falls back to Mode 2 (one efficient aggregate query per review).

### Context-Aware Serialization

The `user_votes` field demonstrates context-dependent serialization:

```
Anonymous user → []                    (no votes to show)
Logged-in user → ["useful", "cool"]   (their specific votes on this review)
```

This enables the frontend to render pre-selected vote buttons without a separate API call. The serializer reads `self.context['request'].user` to determine the current user.

---

# 2. The Toolbox (Tech Stack)

## 2.1 Data Storage Method & Structure

### Database Tables (Review Domain)

```
┌──────────────────────────────────────────────────────────────────┐
│                          reviews                                  │
├──────────────────────────────────────────────────────────────────┤
│ id              SERIAL PRIMARY KEY                                │
│ business_id     FK → businesses (CASCADE)                         │
│ user_id         FK → auth_user (SET_NULL, nullable)               │
│ rating          INTEGER CHECK(1 ≤ rating ≤ 5)                    │
│ description     TEXT (default '')                                 │
│ image_url       TEXT (nullable)                                   │
│ created_at      TIMESTAMPTZ (auto)                                │
│ updated_at      TIMESTAMPTZ (auto)                                │
├──────────────────────────────────────────────────────────────────┤
│ CONSTRAINTS:                                                      │
│   unique_review_per_user_per_business                             │
│     UNIQUE(business_id, user_id) WHERE user_id IS NOT NULL        │
│                                                                   │
│ ORDERING: -created_at (newest first)                              │
└──────────────────────────────┬───────────────────────────────────┘
                               │ FK (review_id)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                       review_votes                                │
├──────────────────────────────────────────────────────────────────┤
│ id              SERIAL PRIMARY KEY                                │
│ user_id         FK → auth_user (CASCADE)                          │
│ review_id       FK → reviews (CASCADE)                            │
│ vote_type       VARCHAR(10) ∈ {useful, funny, cool}               │
│ created_at      TIMESTAMPTZ (auto)                                │
├──────────────────────────────────────────────────────────────────┤
│ CONSTRAINTS:                                                      │
│   unique_vote_per_user_per_review_per_type                        │
│     UNIQUE(user_id, review_id, vote_type)                         │
└──────────────────────────────────────────────────────────────────┘
```

### Relationship Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────────┐
│ auth_user│       │businesses │       │ GCS Bucket   │
│          │       │           │       │ orbit-media- │
│ id ──────┼──┐    │ id ───────┼──┐   │ prod         │
│ username │  │    │ name      │  │   │              │
│ email    │  │    │ avg_rating│  │   │ /reviews/    │
└──────────┘  │    │ review_   │  │   │  /{biz_id}/  │
              │    │  count    │  │   │  /{uuid}.jpg │
              │    └───────────┘  │   └──────────────┘
              │                   │          ▲
              │    ┌──────────────┘          │ image_url points here
              │    │                         │
              ▼    ▼                         │
         ┌──────────────┐                   │
         │   reviews     │──────────────────┘
         │               │
         │ id            │
         │ business_id ──┤ FK → businesses (CASCADE)
         │ user_id ──────┤ FK → auth_user (SET_NULL)
         │ rating        │
         │ description   │
         │ image_url ────┤ → GCS public URL
         │ created_at    │
         │ updated_at    │
         └───────┬───────┘
                 │ FK (review_id)
                 ▼
         ┌──────────────┐
         │ review_votes  │
         │               │
         │ id            │
         │ user_id ──────┤ FK → auth_user (CASCADE)
         │ review_id ────┤ FK → reviews (CASCADE)
         │ vote_type     │ ∈ {useful, funny, cool}
         │ created_at    │
         └──────────────┘
```

### Cascade Behaviour Matrix

| Event | reviews table | review_votes table | Business.avg_rating |
|-------|--------------|-------------------|---------------------|
| **User deletes account** | `user_id` → `NULL`, review remains ("Deleted User") | Vote rows **deleted** (CASCADE from auth_user) | Recalculated (review still counts) |
| **Business deleted** | Review rows **deleted** (CASCADE) | Vote rows **deleted** (CASCADE from review) | N/A (business gone) |
| **Review deleted** | Row removed | Vote rows **deleted** (CASCADE from review) | Recalculated (review no longer counts) |

### External Storage: Google Cloud Storage

| Property | Value |
|----------|-------|
| Bucket name | `orbit-media-prod` |
| Path pattern | `reviews/{business_id}/{uuid_hex}.{ext}` |
| Access | Public read (uniform bucket-level ACL) |
| Cache-Control | `public, max-age=31536000` (1 year) |
| Supported formats | JPEG, PNG, WebP (detected via magic bytes) |
| Max upload size | 5 MB |
| URL format | `https://storage.googleapis.com/orbit-media-prod/reviews/...` |

---

## 2.2 API & Libraries Used

### REST API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/reviews/` | Public | Cursor-paginated list, filterable |
| `GET` | `/api/reviews/:id/` | Public | Single review detail |
| `POST` | `/api/reviews/` | Auth + Verified | Create review (with optional photo) |
| `PATCH` | `/api/reviews/:id/` | Owner | Update review (can replace photo) |
| `DELETE` | `/api/reviews/:id/` | Owner | Delete review |
| `POST` | `/api/reviews/:id/vote/` | Auth + Verified | Toggle helpfulness vote |

### Query Parameters (List Endpoint)

| Param | Type | Description |
|-------|------|-------------|
| `business` | int | Filter reviews for a specific business |
| `user` | int | Filter reviews by a specific user |
| `rating` | int | Filter by exact star rating (1–5) |
| `cursor` | string | Opaque pagination cursor from `next`/`previous` links |
| `page_size` | int | Results per page (default: 10, max: 50) |

### Create/Update Request Body

```json
{
    "business": 42,
    "rating": 4,
    "description": "Amazing croissants and great atmosphere!",
    "photo": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `business` | int | Yes (create) | Business ID (read-only on update) |
| `rating` | int | Yes | 1–5, validated in serializer |
| `description` | string | No | Free-text review body |
| `photo` | string | No | Base64-encoded image (with or without data-URI prefix), max 5 MB decoded |

### Response Body (Single Review)

```json
{
    "id": 15,
    "business": 42,
    "user": 3,
    "username": "jane_doe",
    "rating": 4,
    "description": "Amazing croissants and great atmosphere!",
    "image_url": "https://storage.googleapis.com/orbit-media-prod/reviews/42/a1b2c3d4.jpg",
    "vote_counts": {
        "useful": 7,
        "funny": 2,
        "cool": 3
    },
    "user_votes": ["useful"],
    "created_at": "2026-02-15T14:30:00Z",
    "updated_at": "2026-02-15T14:30:00Z"
}
```

### Vote Request/Response

**Request:**
```json
POST /api/reviews/15/vote/
{"vote_type": "useful"}
```

**Response (vote added):**
```json
{"status": "added", "vote_type": "useful"}   // HTTP 201
```

**Response (vote removed — toggle off):**
```json
{"status": "removed", "vote_type": "useful"} // HTTP 200
```

### Error Responses

| Scenario | HTTP Status | Response Body |
|----------|-------------|---------------|
| Duplicate review | 400 | `{"detail": "You have already reviewed this business.", "existing_review_id": 15}` |
| Rating out of range | 400 | `{"rating": ["Rating must be between 1 and 5."]}` |
| Self-vote | 400 | `{"detail": "You cannot vote on your own review."}` |
| Invalid vote type | 400 | `{"detail": "vote_type must be one of: cool, funny, useful"}` |
| Not authenticated | 401 | `{"detail": "Authentication credentials were not provided."}` |
| Email not verified | 403 | `{"detail": "You must verify your email address before performing this action."}` |
| Not owner (edit/delete) | 403 | `{"detail": "You do not have permission to perform this action."}` |
| Review not found | 404 | `{"detail": "Not found."}` |

### Key Libraries

| Library | Purpose in Review System |
|---------|------------------------|
| Django REST Framework | ModelViewSet, serializers, permissions, pagination |
| google-cloud-storage | GCS bucket access for photo uploads |
| psycopg2 | PostgreSQL adapter (constraints, aggregations) |
| uuid (stdlib) | Unique filenames for GCS objects |
| base64 (stdlib) | Decode photo data from frontend |

---

## 2.3 Tools Used

| Tool | Purpose |
|------|---------|
| **PostgreSQL** | Primary data store — reviews, votes, constraints, aggregations |
| **Google Cloud Storage** | Review photo storage (public bucket) |
| **Django Signals** | Automatic Bayesian rating recalculation on review changes |
| **DRF Cursor Pagination** | Infinite-scroll-friendly pagination for review feeds |
| **Docker Compose** | Containerized deployment (django container handles all review logic) |

---

# 3. The Safeguards (Quality & Growth)

## 3.1 Security & Privacy

### Permission Matrix

| Action | Anonymous | Authenticated | Email Verified | Owner |
|--------|:---------:|:-------------:|:--------------:|:-----:|
| List reviews | ✅ | ✅ | ✅ | ✅ |
| View single review | ✅ | ✅ | ✅ | ✅ |
| Create review | ❌ | ❌ | ✅ | ✅ |
| Edit review | ❌ | ❌ | ❌ | ✅ |
| Delete review | ❌ | ❌ | ❌ | ✅ |
| Vote on review | ❌ | ❌ | ✅ | N/A (self-vote blocked) |

### Three-Layer Permission System

```
Layer 1: IsAuthenticated
  └── Rejects anonymous users with 401

Layer 2: IsEmailVerified
  └── Checks user.profile.email_verified == True
  └── Rejects unverified users with 403 + descriptive message

Layer 3: IsOwnerOrReadOnly
  └── Safe methods (GET, HEAD, OPTIONS) → always allowed
  └── Unsafe methods (PATCH, DELETE) → only if obj.user == request.user
  └── Rejects non-owners with 403
```

### Security Measures

| Threat | Mitigation |
|--------|------------|
| **Review spam** | Email verification required before creating reviews |
| **Duplicate reviews** | DB unique constraint + serializer pre-check with friendly error |
| **Photo abuse (oversized)** | 5 MB hard limit checked after base64 decode |
| **Photo abuse (format)** | Magic-byte detection — only JPEG, PNG, WebP accepted |
| **Vote manipulation** | One vote per type per user per review (DB constraint) |
| **Self-voting** | Explicit check: `review.user == request.user` → 400 |
| **Data tampering** | `user` and `image_url` are read-only fields in serializer |
| **Unauthorized edits** | `IsOwnerOrReadOnly` permission on object-level |
| **User deletion privacy** | Reviews anonymized (`user_id → NULL`, shown as "Deleted User") |
| **SQL injection** | Django ORM parameterized queries throughout |
| **API key exposure** | GCS client uses Application Default Credentials, no keys in code |

### Data Integrity Guarantees

```
┌─────────────────────────────────────────────────────────────────┐
│                    Constraint Stack                               │
│                                                                  │
│  DB Level:                                                       │
│    • CHECK(rating >= 1 AND rating <= 5)                         │
│    • UNIQUE(business_id, user_id) WHERE user_id IS NOT NULL     │
│    • UNIQUE(user_id, review_id, vote_type)                      │
│    • FK CASCADE/SET_NULL enforced by PostgreSQL                  │
│                                                                  │
│  Serializer Level:                                               │
│    • validate_rating(): 1 ≤ value ≤ 5                           │
│    • validate(): duplicate check with existing_review_id        │
│    • read_only_fields: [id, user, image_url, timestamps]        │
│                                                                  │
│  ViewSet Level:                                                  │
│    • perform_create(): auto-sets user from request               │
│    • vote(): self-vote check, valid vote_type check             │
│    • _upload_photo(): 5MB limit, magic-byte format check        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3.2 Scalability

### Current Performance Profile

| Operation | Query Strategy | Estimated Time |
|-----------|---------------|----------------|
| List reviews for a business | Index scan on `business_id`, cursor pagination (no COUNT) | ~5ms |
| Create review | INSERT + signal (2 queries: aggregate + update) | ~10ms |
| Vote toggle | SELECT + DELETE/INSERT (1–2 queries) | ~5ms |
| Photo upload | GCS upload over network | ~200–500ms |
| Aggregate vote counts | In-memory iteration (prefetched) or single GROUP BY | ~1ms |

### Pagination: Why Cursor, Not Page-Number

```
Page-Number Pagination:
  Problem: INSERT a new review while user is on page 2
  → Items shift, user sees duplicates or misses items
  → Requires COUNT(*) query on every page (expensive at scale)

Cursor Pagination (what we use):
  ?cursor=cD0yMDI2LTAyLTE1VDE0... (opaque token)
  → Encodes "created_at < this timestamp"
  → No COUNT query needed
  → New inserts don't shift existing pages
  → Perfect for infinite-scroll UIs
  
  Settings:
    page_size = 10 (default)
    max_page_size = 50
    ordering = -created_at (newest first)
```

### Scaling Paths

| Component | Current | Bottleneck At | Scaling Path |
|-----------|---------|---------------|--------------|
| **Review queries** | Single PostgreSQL | ~1M reviews | Add index on `(business_id, created_at)`, read replicas |
| **Vote counts** | Computed per-request (prefetched) | ~10k votes per review | Denormalize: add `useful_count`, `funny_count`, `cool_count` columns to Review model |
| **Photo uploads** | Synchronous in request | ~100 concurrent uploads | Move to async (Celery task), return review immediately, update image_url when done |
| **GCS bandwidth** | Direct public URL | High traffic | Put Cloud CDN in front of GCS bucket |
| **Rating recalculation** | Signal on every save/delete | Bulk import/delete scenarios | Batch recalculation via management command for bulk operations |

---

## 3.3 User Engagement

### How Reviews Drive Engagement

| Feature | Backend Logic | User Benefit |
|---------|--------------|--------------|
| **One-click rating** | Only `rating` is required, `description` is optional | Low barrier to contribute — even a star rating helps |
| **Photo reviews** | Base64 upload, auto-stored on GCS with 1-year cache | Visual reviews are more engaging and trustworthy |
| **Vote feedback** | `user_votes` array in every review response | Users see their own votes pre-highlighted — instant feedback |
| **Multi-dimension voting** | Three independent vote types (useful, funny, cool) | Richer feedback than simple upvote/downvote |
| **Toggle voting** | Same endpoint to add/remove — idempotent | No "undo" complexity — just tap again |
| **Deleted user handling** | Reviews preserved as "Deleted User" | Community content survives individual account changes |
| **Duplicate prevention with guidance** | Returns `existing_review_id` on conflict | Frontend can direct user to edit instead of hitting a dead end |
| **Bayesian rating** | New businesses inherit Google's credibility | Users trust ratings from day one, even with few reviews |

### Review Feed Lifecycle

```
User opens business page
    │
    ▼  GET /api/reviews/?business=42
    │  (cursor-paginated, 10 per page)
    │
    ▼  Frontend renders reviews with:
    │    • Star rating (1–5)
    │    • Description text
    │    • Photo (if image_url present)
    │    • Vote buttons with counts
    │    • User's own votes highlighted (from user_votes)
    │
    ▼  User scrolls → GET /api/reviews/?business=42&cursor=<next>
    │  (next page loads seamlessly)
    │
    ▼  User taps "useful" on a review
    │    POST /api/reviews/15/vote/ {"vote_type": "useful"}
    │    → {"status": "added"} → button highlights
    │
    ▼  User taps "useful" again (toggle off)
    │    POST /api/reviews/15/vote/ {"vote_type": "useful"}
    │    → {"status": "removed"} → button de-highlights
    │
    ▼  User writes their own review
    │    POST /api/reviews/ {business: 42, rating: 4, ...}
    │    → 201 Created
    │    → Business.avg_rating auto-recalculated (signal)
    │
    ▼  User tries to review again
         POST /api/reviews/ {business: 42, ...}
         → 400 {"detail": "...", "existing_review_id": 15}
         → Frontend navigates to existing review for editing
```

---

# 4. The Process (Workflow & Launch)

## 4.1 Development Workflow

### Code Organization

```
backend/api/
├── models/business.py
│   ├── Review              ← Model definition + DB constraints
│   ├── ReviewVote           ← Vote model + type choices
│   ├── BAYESIAN_CONFIDENCE_THRESHOLD = 10
│   └── update_business_review_aggregates()  ← Signal handler
│
├── serializers/review.py
│   └── ReviewSerializer     ← Validation, vote aggregation, duplicate check
│
├── viewsets/reviews.py
│   └── ReviewViewSet        ← CRUD + vote action + photo upload
│
├── pagination.py
│   └── ReviewCursorPagination  ← Cursor-based, 10/page, max 50
│
├── permissions.py
│   ├── IsEmailVerified      ← Profile-based email check
│   └── IsOwnerOrReadOnly    ← Object-level ownership check
│
├── services/gcs.py
│   └── _get_gcs_client()    ← Lazy-initialized GCS client (shared)
│
└── urls.py
    └── router.register('reviews', ReviewViewSet)
```

### Adding a New Feature (Example: "Review Reactions — 😍 emoji votes")

1. **Model**: Add new choices to `ReviewVote.VOTE_TYPES`: `('love', 'Love'), ('wow', 'Wow')`
2. **Migration**: `python manage.py makemigrations` — no schema change (just `choices` metadata)
3. **Serializer**: Update `get_vote_counts()` default dict to include new types
4. **ViewSet**: No change needed — `valid_types` dynamically reads from `VOTE_TYPES`
5. **Frontend**: Add new emoji buttons, same toggle API
6. **Deploy**: Rebuild django container, restart

---

## 4.2 Deployment Method

### Review System Components in Docker

```
┌──────────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  django (gunicorn, 3 workers)                              │   │
│  │                                                            │   │
│  │  Handles:                                                  │   │
│  │    • All review CRUD endpoints                            │   │
│  │    • Vote toggle endpoint                                 │   │
│  │    • Photo upload to GCS                                  │   │
│  │    • Bayesian rating signals (in-process)                 │   │
│  │                                                            │   │
│  │  Connects to:                                              │   │
│  │    • PostgreSQL (reviews, votes tables)                    │   │
│  │    • GCS (photo upload via Application Default Creds)     │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐   │
│  │  postgres        │  │  nginx                               │   │
│  │                  │  │                                      │   │
│  │  Tables:         │  │  Proxies:                            │   │
│  │  • reviews       │  │  business.orbitcentral.ca            │   │
│  │  • review_votes  │  │    → django:8000                    │   │
│  │  • businesses    │  │                                      │   │
│  │    (avg_rating)  │  │  Rate limit: 20r/s, burst=40        │   │
│  └─────────────────┘  └──────────────────────────────────────┘   │
│                                                                   │
│  Note: Review system does NOT use Celery.                        │
│  All operations are synchronous within the Django request.       │
└──────────────────────────────────────────────────────────────────┘
```

### Deployment Steps

```bash
# After code changes:
rsync -avz -e ssh \
  backend/api/viewsets/reviews.py \
  backend/api/serializers/review.py \
  backend/api/models/business.py \
  gcp-vm:~/FBLC/backend/api/

# Rebuild + restart django (includes signal changes)
ssh gcp-vm "cd ~/FBLC && docker compose build django --quiet && docker compose up -d django"
```

---

## 4.3 Production Method

### Typical Review Creation Lifecycle

```
Mobile App (orbitcentral.ca)
    │
    │  POST /api/reviews/
    │  Headers: Authorization: Token abc123...
    │  Body: {business: 42, rating: 4, description: "...", photo: "base64..."}
    │
    ▼
Nginx (business.orbitcentral.ca)
    │  proxy_pass → django:8000
    │  Rate limit check (20r/s)
    ▼
Gunicorn Worker
    │
    ├── [AUTH] ExpiringTokenAuthentication
    │     └── Token valid? Not expired (72h TTL)? → 200 or 401
    │
    ├── [PERM] IsAuthenticated + IsEmailVerified
    │     └── User has verified email? → proceed or 403
    │
    ├── [VALIDATE] ReviewSerializer
    │     ├── rating: 4 ∈ [1,5] → ✅
    │     ├── business: 42 exists → ✅
    │     └── duplicate check: no existing review → ✅
    │
    ├── [UPLOAD] _upload_photo()
    │     ├── Strip data-URI prefix
    │     ├── Decode base64 → 2.1 MB JPEG
    │     ├── Size check: 2.1 MB ≤ 5 MB → ✅
    │     ├── Magic bytes: 0xFF 0xD8 0xFF → JPEG
    │     ├── GCS upload: reviews/42/a1b2c3d4.jpg
    │     └── Return URL: https://storage.googleapis.com/...
    │         Duration: ~300ms
    │
    ├── [SAVE] Review.objects.create(
    │     user=request.user, business=42, rating=4,
    │     description="...", image_url="https://...")
    │
    ├── [SIGNAL] post_save → update_business_review_aggregates
    │     ├── SELECT AVG(rating), COUNT(*) FROM reviews WHERE business_id=42
    │     ├── Bayesian: W = (v*R + 10*C) / (v+10) = (1*4.0 + 10*4.3) / 11 = 4.27
    │     └── UPDATE businesses SET avg_rating=4.27, review_count=1 WHERE id=42
    │
    └── [RESPONSE] 201 Created
          {id: 15, business: 42, user: 3, username: "jane_doe",
           rating: 4, image_url: "https://...", vote_counts: {useful:0, funny:0, cool:0},
           user_votes: [], created_at: "2026-02-15T14:30:00Z"}

Total: ~350ms (dominated by GCS upload)
```

### Monitoring

| What to Watch | How | Source |
|---------------|-----|--------|
| Review creation rate | `docker compose logs django \| grep "POST /api/reviews"` | Django access logs |
| Photo upload failures | `docker compose logs django \| grep "photo upload failed"` | Logger warning in `_upload_photo()` |
| Rating recalculation | `SELECT avg_rating, review_count FROM businesses WHERE id=N` | Adminer / psql |
| Vote activity | `SELECT vote_type, COUNT(*) FROM review_votes GROUP BY vote_type` | Adminer / psql |
| GCS storage usage | GCP Console → Cloud Storage → orbit-media-prod | Google Cloud Console |

### Key Production Numbers (Current)

| Metric | Value |
|--------|-------|
| Pagination | Cursor-based, 10/page default, 50 max |
| Max photo size | 5 MB (decoded) |
| Photo formats | JPEG, PNG, WebP |
| Vote types | 3 (useful, funny, cool) |
| Rating range | 1–5 (integer) |
| Bayesian threshold (m) | 10 reviews |
| Auth token TTL | 72 hours |
| GCS cache TTL | 1 year |
