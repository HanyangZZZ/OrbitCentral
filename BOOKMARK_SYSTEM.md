# Orbit — Bookmark System: Technical Deep-Dive

> **Scope:** This document covers the backend systems for **saving, unsaving, toggling, checking, and listing user bookmarks** (saved businesses). Business discovery, reviews, and authentication are out of scope.

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

> *"A user discovers a local bakery through search, taps the bookmark icon to save it, navigates away, and later returns to their saved list. Another time they tap the same icon — it unsaves. How does the backend handle all of this?"*

The answer involves **1 model**, **1 database constraint**, and **5 API actions** — making the bookmark system the simplest and most self-contained module in Orbit.

### Master Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                                    │
│                                                                         │
│  1. Save:   POST /api/bookmarks/         {business: 42}               │
│  2. Toggle: POST /api/bookmarks/toggle/  {business: 42}               │
│  3. Check:  GET  /api/bookmarks/check/?business=42                    │
│  4. List:   GET  /api/bookmarks/                                       │
│  5. IDs:    GET  /api/bookmarks/ids/                                   │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │
                               ▼
              ┌───────────────────────────────────┐
              │       BookmarkViewSet              │
              │       (DRF ModelViewSet)           │
              │                                    │
              │  All actions require:              │
              │    ✓ IsAuthenticated               │
              │    ✓ IsEmailVerified               │
              │                                    │
              │  Queryset scoped to:               │
              │    user = request.user              │
              │    (users ONLY see their own)       │
              └──────────┬────────────────────────┘
                         │
           ┌─────────────┼──────────────┬──────────────┐
           ▼             ▼              ▼              ▼
    ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐
    │  Standard  │ │  Toggle  │ │   Check   │ │    IDs     │
    │  CRUD      │ │  Action  │ │   Action  │ │   Action   │
    │            │ │          │ │           │ │            │
    │ list()     │ │ Exists?  │ │ Exists?   │ │ SELECT     │
    │ create()   │ │  YES →   │ │  → true/  │ │ business_id│
    │ retrieve() │ │  DELETE  │ │    false   │ │ FROM       │
    │ update()   │ │  NO →    │ │           │ │ bookmarks  │
    │ destroy()  │ │  CREATE  │ │ Lightweight│ │ WHERE user │
    │            │ │          │ │ bool check│ │            │
    └────────────┘ └──────────┘ └───────────┘ └────────────┘
```

### Toggle: The Primary Interaction Pattern

The **toggle** action is the most important endpoint — it's what the bookmark icon on every business card calls. One endpoint handles both save and unsave:

```
POST /api/bookmarks/toggle/  {"business": 42}

┌──────────────────────────────────────────────────────────────────┐
│                       Toggle Flow                                 │
│                                                                   │
│  Step 1: Validate business ID exists                             │
│            │                                                      │
│            ├── Missing → 400 "business field is required"        │
│            └── Not found → 404 "Business not found."             │
│                                                                   │
│  Step 2: get_or_create(user=request.user, business=business)     │
│            │                                                      │
│            ├── CREATED (new bookmark)                             │
│            │     → 201 {"status": "added",                       │
│            │            "bookmark": {id, business, user, ...}}   │
│            │                                                      │
│            └── ALREADY EXISTS (was bookmarked)                   │
│                  → DELETE the existing bookmark                   │
│                  → 200 {"status": "removed", "business": 42}    │
│                                                                   │
│  Result: Frontend flips the bookmark icon ON or OFF              │
└──────────────────────────────────────────────────────────────────┘
```

**Key insight:** `get_or_create` is atomic in PostgreSQL — even if two simultaneous requests arrive for the same user+business, only one bookmark is created. The second request will find the existing one and delete it.

### Check: Lightweight Boolean Probe

The **check** endpoint answers one question: "has this user bookmarked this business?" It returns only a boolean — no joins, no serialization, minimal overhead:

```
GET /api/bookmarks/check/?business=42

┌──────────────────────────────────────────────────────────────────┐
│  SELECT EXISTS(                                                   │
│    SELECT 1 FROM bookmarks                                        │
│    WHERE user_id = $user AND business_id = 42                    │
│  )                                                                │
│                                                                   │
│  → {"bookmarked": true, "business": 42}                          │
│  or                                                               │
│  → {"bookmarked": false, "business": 42}                         │
└──────────────────────────────────────────────────────────────────┘
```

Uses `.exists()` which generates a `SELECT EXISTS(...)` query — the fastest possible boolean check in PostgreSQL (stops at first match, no row fetching).

### IDs: Bulk Status for List Views

When the frontend renders a list of businesses (search results, homepage), it needs to know which ones are bookmarked to show filled vs. outline bookmark icons. The **ids** endpoint returns all bookmarked business IDs in a single lightweight call:

```
GET /api/bookmarks/ids/

┌──────────────────────────────────────────────────────────────────┐
│  SELECT business_id FROM bookmarks WHERE user_id = $user         │
│                                                                   │
│  → {"business_ids": [42, 17, 89, 103, 5]}                       │
│                                                                   │
│  Frontend usage:                                                  │
│    const bookmarkedSet = new Set(response.business_ids)          │
│    businesses.forEach(b => {                                      │
│      b.isBookmarked = bookmarkedSet.has(b.id)                    │
│    })                                                             │
└──────────────────────────────────────────────────────────────────┘
```

Uses `values_list('business_id', flat=True)` — returns just integers, no joins, no serialization. Designed for the common case where the frontend needs to decorate 10–50 business cards with bookmark state.

### Three API Patterns for Three Use Cases

| Use Case | Endpoint | Query Cost | Data Returned |
|----------|----------|------------|---------------|
| **Tap bookmark icon** (single business) | `POST /toggle/` | 1 read + 1 write | Status + bookmark data |
| **Load business detail page** (single check) | `GET /check/?business=N` | 1 EXISTS query | Boolean |
| **Load business list** (bulk check) | `GET /ids/` | 1 query, N results | Array of IDs |
| **View saved list** (full details) | `GET /` | 1 query + select_related | Full bookmark + business data |

---

## 1.2 Modularity & Modular Design

### Layer Separation

The bookmark system spans **3 layers**:

```
┌──────────────────────────────────────────────────────────────────┐
│  URL Layer                                                        │
│  urls.py: router.register('bookmarks', BookmarkViewSet)          │
│                                                                   │
│  Routes generated by DRF DefaultRouter:                          │
│    /api/bookmarks/           → list, create                      │
│    /api/bookmarks/<id>/      → retrieve, update, destroy         │
│    /api/bookmarks/toggle/    → toggle() custom action            │
│    /api/bookmarks/check/     → check() custom action             │
│    /api/bookmarks/ids/       → ids() custom action               │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│  ViewSet Layer (viewsets/bookmarks.py)                            │
│                                                                   │
│  BookmarkViewSet (ModelViewSet)                                   │
│    ├── get_queryset()  → scoped to request.user + select_related │
│    ├── perform_create() → auto-set user from request             │
│    ├── toggle()   → @action(POST) — bookmark on/off              │
│    ├── check()    → @action(GET)  — boolean probe                │
│    └── ids()      → @action(GET)  — lightweight ID list          │
│                                                                   │
│  Responsibilities:                                                │
│    • User scoping (every query filtered to current user)         │
│    • Business existence validation (toggle)                      │
│    • Input validation (check: business must be integer)          │
│    • HTTP status codes and response shaping                      │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│  Serializer Layer (serializers/bookmark.py)                      │
│                                                                   │
│  BookmarkSerializer (ModelSerializer)                             │
│    ├── Fields: id, business, user, username, business_name,      │
│    │           note, created_at                                  │
│    ├── username      → read-only from user.username              │
│    ├── business_name → read-only from business.name              │
│    └── validate()    → duplicate bookmark prevention             │
│                                                                   │
│  Responsibilities:                                                │
│    • Denormalized convenience fields (username, business_name)   │
│    • Duplicate detection for direct POST /api/bookmarks/         │
│    • Read-only enforcement (id, user, created_at)                │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│  Model Layer (models/business.py)                                │
│                                                                   │
│  Bookmark                                                        │
│    ├── FK → User (CASCADE)                                       │
│    ├── FK → Business (CASCADE)                                   │
│    ├── note: VARCHAR(500) — optional private note                │
│    ├── created_at: auto                                          │
│    └── UniqueConstraint(user, business)                          │
│                                                                   │
│  Responsibilities:                                                │
│    • Schema definition + unique constraint                       │
│    • Cascading deletes (user or business deleted → bookmark gone)│
│    • Ordering: newest first (-created_at)                        │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **No service layer** | Bookmarks have zero business logic beyond CRUD. No AI, no external APIs, no signals. A service module would be empty ceremony. |
| **Three custom actions (toggle, check, ids)** | Each serves a distinct frontend UX need: single toggle, single check, bulk check. A single generic endpoint would require the frontend to do more work. |
| **`get_or_create` in toggle** | Atomic PostgreSQL operation. No race condition between "check if exists" and "create/delete". Eliminates need for explicit locking. |
| **`select_related('business')` on queryset** | The list endpoint serializes `business_name`. Without select_related, each bookmark would trigger a separate query to fetch the business — N+1 problem. |
| **`note` field** | Future-proofing: users might want to annotate their bookmarks ("Try the latte here", "Go on weekends"). The field exists but is optional (default empty string). |
| **CASCADE on both FKs** | Unlike Review (which uses SET_NULL for user), bookmarks are personal. If the user or business is deleted, the bookmark has no meaning and should be cleaned up. |
| **No pagination on ids endpoint** | The `/ids/` endpoint returns all bookmarked business IDs as a flat array. Even power users with 1000 bookmarks produce a response under 10KB. Pagination overhead would exceed the data saved. |

---

## 1.3 Clean Logic & Data Types

### Model Field Types — Why Each Was Chosen

| Field | Type | Why |
|-------|------|-----|
| `user` | `ForeignKey(CASCADE)` | CASCADE (not SET_NULL) — bookmark is meaningless without a user. No "anonymous bookmarks" concept. |
| `business` | `ForeignKey(CASCADE)` | CASCADE — if a business is deleted, its bookmarks should vanish. No orphan references. |
| `note` | `CharField(max_length=500, blank=True, default='')` | CharField (not TextField) — bounded at 500 chars, suitable for a quick note. Default empty string (not null) simplifies frontend: always a string, never null. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Tracks when the bookmark was created. Used for default ordering (newest first) and display in "saved" list. |

### Serializer Convenience Fields

The serializer adds two **denormalized read-only fields** so the frontend doesn't need separate API calls:

```python
username = CharField(source='user.username', read_only=True)
business_name = CharField(source='business.name', read_only=True)
```

Without these, the "saved businesses" list page would need to:
1. `GET /api/bookmarks/` → get business IDs
2. `GET /api/businesses/:id/` × N → fetch each business name

With denormalization:
1. `GET /api/bookmarks/` → get everything in one response

The `select_related('business')` in the queryset ensures these fields are fetched with a single SQL JOIN, not N+1 separate queries.

### Duplicate Detection — Two Layers

```
Layer 1: Serializer (user-friendly)
──────────────────────────────────
  def validate(self, attrs):
      if Bookmark.objects.filter(user=user, business=business).exists():
          raise ValidationError('You have already bookmarked this business.')

  • Only runs on POST (create) requests
  • Returns a descriptive 400 error
  • Triggered by direct POST /api/bookmarks/

Layer 2: Database Constraint (hard guarantee)
─────────────────────────────────────────────
  UniqueConstraint(
      fields=['user', 'business'],
      name='unique_bookmark_per_user_per_business',
  )

  • Catches any race conditions the serializer misses
  • Enforced at the PostgreSQL level
  • IntegrityError → DRF auto-converts to 400

Note: The toggle endpoint bypasses the serializer entirely
(uses get_or_create), so it relies solely on Layer 2.
```

---

# 2. The Toolbox (Tech Stack)

## 2.1 Data Storage Method & Structure

### Database Table

```
┌──────────────────────────────────────────────────────────────────┐
│                          bookmarks                                │
├──────────────────────────────────────────────────────────────────┤
│ id              SERIAL PRIMARY KEY                                │
│ user_id         FK → auth_user (CASCADE)                          │
│ business_id     FK → businesses (CASCADE)                         │
│ note            VARCHAR(500) (default '')                         │
│ created_at      TIMESTAMPTZ (auto_now_add)                        │
├──────────────────────────────────────────────────────────────────┤
│ CONSTRAINTS:                                                      │
│   unique_bookmark_per_user_per_business                           │
│     UNIQUE(user_id, business_id)                                  │
│                                                                   │
│ ORDERING: -created_at (newest first)                              │
│                                                                   │
│ AUTO-INDEXES (from FKs + constraint):                             │
│   • idx_bookmarks_user_id         (user queries: list, ids, check)│
│   • idx_bookmarks_business_id     (business cascade deletes)      │
│   • unique_bookmark_per_user_...  (composite unique index)        │
└──────────────────────────────────────────────────────────────────┘
```

### Relationship Diagram

```
┌──────────┐              ┌──────────────┐
│ auth_user│              │  businesses   │
│          │              │               │
│ id ──────┼──┐      ┌───┤ id            │
│ username │  │      │   │ name          │
│ email    │  │      │   │ ...           │
└──────────┘  │      │   └───────────────┘
              │      │
              ▼      ▼
         ┌──────────────────┐
         │    bookmarks      │
         │                   │
         │ id                │
         │ user_id ──────────┤ FK → auth_user (CASCADE)
         │ business_id ──────┤ FK → businesses (CASCADE)
         │ note              │ VARCHAR(500), optional
         │ created_at        │ auto, used for ordering
         │                   │
         │ UNIQUE(user_id,   │
         │        business_id)│
         └──────────────────┘
```

### Cascade Behaviour

| Event | Effect on Bookmarks |
|-------|-------------------|
| **User deletes account** | All user's bookmarks **deleted** (CASCADE) |
| **Business deleted** | All bookmarks for that business **deleted** (CASCADE) |
| **Admin removes bookmark** | Single row deleted, no side effects |

Unlike the review system (which anonymizes reviews on user deletion via SET_NULL), bookmarks use CASCADE because:
- Bookmarks are **personal** — they have no community value after the user leaves
- There's no rating impact — bookmarks don't affect business rankings
- Cleanup is the expected behaviour — no reason to keep orphan bookmarks

---

## 2.2 API & Libraries Used

### REST API Endpoints

| Method | Endpoint | Auth | Response | Description |
|--------|----------|------|----------|-------------|
| `GET` | `/api/bookmarks/` | Auth + Verified | Paginated bookmark list | All user's bookmarks with business details |
| `POST` | `/api/bookmarks/` | Auth + Verified | Created bookmark | Direct create (fails if duplicate) |
| `GET` | `/api/bookmarks/:id/` | Auth + Verified | Single bookmark | Retrieve by bookmark ID |
| `PATCH` | `/api/bookmarks/:id/` | Auth + Verified | Updated bookmark | Update note field |
| `DELETE` | `/api/bookmarks/:id/` | Auth + Verified | 204 No Content | Remove bookmark |
| `POST` | `/api/bookmarks/toggle/` | Auth + Verified | Added/removed status | Toggle bookmark on/off |
| `GET` | `/api/bookmarks/check/?business=N` | Auth + Verified | Boolean | Check if bookmarked |
| `GET` | `/api/bookmarks/ids/` | Auth + Verified | ID array | All bookmarked business IDs |

### Request/Response Examples

**Toggle (add):**
```http
POST /api/bookmarks/toggle/
Authorization: Token abc123...
Content-Type: application/json

{"business": 42}
```
```json
// 201 Created
{
    "status": "added",
    "bookmark": {
        "id": 8,
        "business": 42,
        "user": 3,
        "username": "jane_doe",
        "business_name": "La Petite Boulangerie",
        "note": "",
        "created_at": "2026-02-19T10:15:00Z"
    }
}
```

**Toggle (remove):**
```http
POST /api/bookmarks/toggle/
Authorization: Token abc123...
Content-Type: application/json

{"business": 42}
```
```json
// 200 OK
{"status": "removed", "business": 42}
```

**Check:**
```http
GET /api/bookmarks/check/?business=42
Authorization: Token abc123...
```
```json
{"bookmarked": true, "business": 42}
```

**IDs:**
```http
GET /api/bookmarks/ids/
Authorization: Token abc123...
```
```json
{"business_ids": [42, 17, 89, 103, 5]}
```

**List (paginated):**
```http
GET /api/bookmarks/?page_size=10
Authorization: Token abc123...
```
```json
{
    "count": 23,
    "next": "http://business.orbitcentral.ca/api/bookmarks/?page=2&page_size=10",
    "previous": null,
    "results": [
        {
            "id": 8,
            "business": 42,
            "user": 3,
            "username": "jane_doe",
            "business_name": "La Petite Boulangerie",
            "note": "Try the croissants!",
            "created_at": "2026-02-19T10:15:00Z"
        }
    ]
}
```

### Error Responses

| Scenario | HTTP Status | Response Body |
|----------|-------------|---------------|
| Missing business field (toggle) | 400 | `{"detail": "business field is required."}` |
| Business not found (toggle) | 404 | `{"detail": "Business not found."}` |
| Missing business param (check) | 400 | `{"detail": "business query parameter is required."}` |
| Non-integer business (check) | 400 | `{"detail": "business must be an integer."}` |
| Duplicate bookmark (direct create) | 400 | `{"non_field_errors": ["You have already bookmarked this business."]}` |
| Not authenticated | 401 | `{"detail": "Authentication credentials were not provided."}` |
| Email not verified | 403 | `{"detail": "You must verify your email address before performing this action."}` |
| Bookmark not found | 404 | `{"detail": "Not found."}` |

### Key Libraries

| Library | Purpose in Bookmark System |
|---------|--------------------------|
| Django REST Framework | ModelViewSet, serializers, permissions, `@action` decorator |
| psycopg2 | PostgreSQL adapter (unique constraints, get_or_create atomic ops) |

No external services (no GCS, no OpenAI, no Celery). The bookmark system is **entirely self-contained** within Django + PostgreSQL.

---

## 2.3 Tools Used

| Tool | Purpose |
|------|---------|
| **PostgreSQL** | Primary data store — bookmarks table, unique constraint, auto-indexes |
| **DRF DefaultRouter** | Auto-generates RESTful URL patterns from ViewSet |
| **DRF @action decorator** | Custom endpoints (toggle, check, ids) nested under `/bookmarks/` |
| **Docker Compose** | Containerized deployment (django container handles all bookmark logic) |

---

# 3. The Safeguards (Quality & Growth)

## 3.1 Security & Privacy

### Permission Matrix

| Action | Anonymous | Authenticated | Email Verified |
|--------|:---------:|:-------------:|:--------------:|
| List bookmarks | ❌ | ❌ | ✅ (own only) |
| Create bookmark | ❌ | ❌ | ✅ |
| Toggle bookmark | ❌ | ❌ | ✅ |
| Check bookmark | ❌ | ❌ | ✅ |
| Get bookmark IDs | ❌ | ❌ | ✅ |
| Edit bookmark (note) | ❌ | ❌ | ✅ (own only) |
| Delete bookmark | ❌ | ❌ | ✅ (own only) |

**Key difference from the review system:** There is **no public access** to bookmarks. Every endpoint requires authentication + email verification. Users can only see their own bookmarks.

### User Isolation

```python
def get_queryset(self):
    return Bookmark.objects.filter(user=self.request.user).select_related('business')
```

This single line ensures:
- **User A** never sees **User B**'s bookmarks
- Even if User A guesses a bookmark ID belonging to User B → **404 Not Found** (not 403)
- The queryset filter runs **before** any permission check or serialization
- SQL: `WHERE user_id = $current_user` is always present

### Security Measures

| Threat | Mitigation |
|--------|------------|
| **Bookmark snooping** | Queryset scoped to `request.user` — other users' bookmarks invisible |
| **IDOR (Insecure Direct Object Reference)** | ID-based lookups filtered by user → 404, not 403 (no information leak) |
| **Spam bookmarking** | Email verification required + unique constraint (can't bookmark same business twice) |
| **Business enumeration via bookmarks** | No public bookmark endpoint — can't enumerate which businesses are popular |
| **Data tampering** | `user` and `created_at` are read-only in serializer; user auto-set in `perform_create()` |
| **Race condition on toggle** | `get_or_create` is atomic in PostgreSQL — no double-create possible |
| **SQL injection** | Django ORM parameterized queries throughout |

### Privacy by Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Privacy Guarantees                             │
│                                                                  │
│  ✓ Bookmarks are NEVER exposed to other users                   │
│  ✓ No "most bookmarked businesses" public endpoint              │
│  ✓ No bookmark count on business detail response                │
│  ✓ Deleting account CASCADE-deletes all bookmarks               │
│  ✓ No analytics tracking on bookmark events                     │
│                                                                  │
│  Bookmarks are treated as private user data,                    │
│  equivalent to a browser bookmark — personal and invisible.     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3.2 Scalability

### Current Performance Profile

| Operation | Query Strategy | Estimated Time |
|-----------|---------------|----------------|
| Toggle | `get_or_create` + conditional DELETE (1–2 queries) | ~3ms |
| Check | `EXISTS` subquery (1 query) | ~1ms |
| IDs | `values_list` flat query (1 query) | ~2ms |
| List | `SELECT * ... JOIN businesses` with pagination (1 query) | ~5ms |

### Scaling Paths

| Component | Current | Bottleneck At | Scaling Path |
|-----------|---------|---------------|--------------|
| **IDs query** | Flat array, no pagination | ~10k bookmarks per user | Pagination with cursor (unlikely scenario — 10k array is ~80KB) |
| **List query** | Page-number pagination, `select_related` | ~100k total bookmarks | Add composite index `(user_id, created_at)` for sorted lookups |
| **Toggle throughput** | Synchronous `get_or_create` | ~10k toggles/second | Already near-optimal; connection pooling if needed |
| **Storage** | ~100 bytes per bookmark row | ~10M bookmarks | Standard PostgreSQL scaling (vacuuming, connection pooling) |

### Why the Bookmark System Doesn't Need Optimization

The bookmark system is **read-heavy** and **small per-user**:
- Average user might bookmark 10–50 businesses
- The most expensive query (`/ids/`) returns a flat integer array — no joins, no serialization
- PostgreSQL's FK indexes handle all lookup patterns efficiently
- No full-text search, no embeddings, no AI — pure relational CRUD

---

## 3.3 User Engagement

### How Bookmarks Drive Engagement

| Feature | Backend Logic | User Benefit |
|---------|--------------|--------------|
| **Toggle UX** | Single endpoint for save/unsave, returns status | One-tap bookmark — no confirmation dialogs needed |
| **Instant check** | `EXISTS` query, pure boolean | Bookmark icon renders correctly on every business card |
| **Bulk ID check** | Single query returns all bookmarked IDs | Business list page shows bookmark state without N queries |
| **Saved list** | Paginated with business name denormalized | "My Saved Places" page loads instantly with all needed data |
| **Private notes** | `note` field (up to 500 chars) | Users annotate their bookmarks — "go here for lunch" |
| **Privacy** | No public bookmark data, no social pressure | Users bookmark freely — it's their private list |
| **Consistent state** | DB unique constraint, atomic toggle | No ghost bookmarks, no duplicate saves — always consistent |

### Frontend Integration Pattern

```
App Startup:
    GET /api/bookmarks/ids/
    → Store in memory: bookmarkedSet = new Set([42, 17, 89])

Business Card Render:
    isBookmarked = bookmarkedSet.has(business.id)
    → Show filled ★ or outline ☆

User taps bookmark icon:
    POST /api/bookmarks/toggle/  {"business": 42}
    → Optimistic UI: immediately toggle icon
    → On success: update local Set
    → On error: revert icon, show toast

Business Detail Page (optional double-check):
    GET /api/bookmarks/check/?business=42
    → Confirm bookmark state (handles stale local state)

My Saved Places tab:
    GET /api/bookmarks/?page_size=20
    → Render full bookmark list with business names + notes
```

---

# 4. The Process (Workflow & Launch)

## 4.1 Development Workflow

### Code Organization

```
backend/api/
├── models/business.py
│   └── Bookmark              ← Model + unique constraint
│
├── serializers/bookmark.py
│   └── BookmarkSerializer    ← Validation + convenience fields
│
├── viewsets/bookmarks.py
│   └── BookmarkViewSet       ← CRUD + toggle + check + ids
│
├── permissions.py
│   └── IsEmailVerified       ← Shared with review system
│
└── urls.py
    └── router.register('bookmarks', BookmarkViewSet)
```

**Total code:** ~130 lines across 3 files. The simplest subsystem in Orbit.

### Adding a New Feature (Example: "Bookmark Folders/Collections")

1. **Model**: Create `BookmarkFolder` model with `name`, `user` FK, and add `folder` FK to `Bookmark`
2. **Migration**: `python manage.py makemigrations`
3. **Serializer**: Add `BookmarkFolderSerializer`, add `folder` field to `BookmarkSerializer`
4. **ViewSet**: Create `BookmarkFolderViewSet` or add nested actions to `BookmarkViewSet`
5. **URL**: Register new viewset: `router.register('bookmark-folders', BookmarkFolderViewSet)`
6. **Deploy**: Rebuild django container, run migrations

---

## 4.2 Deployment Method

### Bookmark System in Docker

```
┌──────────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                          │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  django (gunicorn, 3 workers)                              │   │
│  │                                                            │   │
│  │  Handles:                                                  │   │
│  │    • All bookmark CRUD + toggle/check/ids endpoints       │   │
│  │    • User-scoped querysets                                │   │
│  │    • No external service calls                            │   │
│  └────────────────────────┬──────────────────────────────────┘   │
│                           │                                       │
│  ┌────────────────────────▼──────────────────────────────────┐   │
│  │  postgres                                                  │   │
│  │                                                            │   │
│  │  Table: bookmarks                                          │   │
│  │    • unique_bookmark_per_user_per_business constraint      │   │
│  │    • FK indexes auto-created                              │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Note: Bookmark system uses NO external services.                │
│  No GCS, no OpenAI, no Celery, no Redis.                        │
│  Pure Django + PostgreSQL.                                       │
└──────────────────────────────────────────────────────────────────┘
```

### Deployment Steps

```bash
# After code changes:
rsync -avz -e ssh \
  backend/api/viewsets/bookmarks.py \
  backend/api/serializers/bookmark.py \
  backend/api/models/business.py \
  gcp-vm:~/FBLC/backend/api/

# Rebuild + restart
ssh gcp-vm "cd ~/FBLC && docker compose build django --quiet && docker compose up -d django"
```

---

## 4.3 Production Method

### Typical Bookmark Toggle Lifecycle

```
Mobile App (orbitcentral.ca)
    │
    │  POST /api/bookmarks/toggle/
    │  Headers: Authorization: Token abc123...
    │  Body: {"business": 42}
    │
    ▼
Nginx (business.orbitcentral.ca)
    │  proxy_pass → django:8000
    │  Rate limit: 20r/s, burst=40
    ▼
Gunicorn Worker
    │
    ├── [AUTH] ExpiringTokenAuthentication
    │     └── Token valid? Not expired (72h TTL)? → proceed or 401
    │
    ├── [PERM] IsAuthenticated + IsEmailVerified
    │     └── Email verified? → proceed or 403
    │
    ├── [VALIDATE] Business.objects.get(pk=42)
    │     └── Exists? → proceed or 404
    │
    ├── [TOGGLE] Bookmark.objects.get_or_create(user=user, business=business)
    │     ├── Created=True → bookmark saved
    │     │     └── Serialize → 201 {"status": "added", "bookmark": {...}}
    │     └── Created=False → already bookmarked
    │           └── Delete → 200 {"status": "removed", "business": 42}
    │
    └── [DONE] Total: ~5ms (no external calls)

Response time breakdown:
    Nginx routing:     ~1ms
    Auth + permissions: ~2ms
    Toggle query:       ~2ms
    Total:             ~5ms
```

### Monitoring

| What to Watch | How |
|---------------|-----|
| Bookmark activity | `docker compose logs django \| grep "bookmarks"` |
| Bookmark count per user | `SELECT user_id, COUNT(*) FROM bookmarks GROUP BY user_id` |
| Most bookmarked businesses | `SELECT business_id, COUNT(*) FROM bookmarks GROUP BY business_id ORDER BY count DESC` |
| Constraint violations | `docker compose logs django \| grep "IntegrityError"` |

### Key Production Numbers (Current)

| Metric | Value |
|--------|-------|
| Pagination | Page-number, 50/page default, 100 max |
| Note max length | 500 characters |
| Toggle response time | ~5ms |
| Check response time | ~1ms |
| IDs response time | ~2ms |
| Auth token TTL | 72 hours |
| External dependencies | None (pure Django + PostgreSQL) |
