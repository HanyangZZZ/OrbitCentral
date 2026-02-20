# Reviews

User-submitted reviews for businesses. Each user can leave one review per business.
**Creating, updating, and deleting reviews requires a verified email.**

## List Reviews

```
GET /api/reviews/?business=<id>
```

**Public** — no authentication required.

| Param | Type | Description |
|-------|------|-------------|
| `business` | int | Filter by business ID (required for meaningful results) |
| `user` | int | Filter by user ID |
| `rating` | int | Filter by exact rating (1–5) |
| `ordering` | string | `rating`, `-rating`, `created_at`, `-created_at` |

**Response:** Paginated list of reviews. Each review now includes `vote_counts` and `user_votes`.

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "business": 42,
      "user": 1,
      "username": "johndoe",
      "rating": 5,
      "description": "Amazing coffee and friendly staff!",
      "image_url": "https://storage.googleapis.com/orbit-media-prod/reviews/42/abc123.jpg",
      "vote_counts": { "useful": 12, "funny": 3, "cool": 5 },
      "user_votes": ["useful"],
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

- `vote_counts` — aggregate count of each vote type on this review
- `user_votes` — list of vote types the current authenticated user has cast (empty array if not logged in)

## Create Review

```
POST /api/reviews/
```

**Requires authentication** (Token auth) **and a verified email address.**

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `business` | int | Yes | Business ID |
| `rating` | int | Yes | 1–5 star rating |
| `description` | string | No | Review text |
| `photo` | string | No | Base64-encoded image (with or without `data:image/...;base64,` prefix) |

```json
{
  "business": 42,
  "rating": 5,
  "description": "Amazing coffee and friendly staff!",
  "photo": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response:** `201 Created` with the review object. The `photo` field is processed server-side:
the image is uploaded to GCS and the public URL is returned in `image_url`.

**Constraints:**
- One review per user per business (`unique_review_per_user_per_business`).
- Submitting a second review for the same business returns `400`.

## Retrieve Review

```
GET /api/reviews/<id>/
```

**Public.** Returns a single review object.

## Update Review

```
PATCH /api/reviews/<id>/
```

**Owner only.** Only the review author can update their review. Accepts the same fields as create.
A new `photo` field replaces the existing image.

## Delete Review

```
DELETE /api/reviews/<id>/
```

**Owner only.** Returns `204 No Content`.

## Vote on Review (Helpfulness)

```
POST /api/reviews/<id>/vote/
```

**Requires authentication + verified email.** Toggle a helpfulness vote on a review. Calling the same endpoint again with the same vote type removes the vote (toggle behavior).

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vote_type` | string | Yes | One of: `useful`, `funny`, `cool` |

```json
{ "vote_type": "useful" }
```

**Response (added):** `201`

```json
{ "status": "added", "vote_type": "useful" }
```

**Response (removed):** `200`

```json
{ "status": "removed", "vote_type": "useful" }
```

A user can vote on a review with _multiple different_ types (e.g. both "useful" and "cool"), but only one vote of each type per review.

## Bayesian Rating System

Business `avg_rating` is computed using a **Bayesian estimate** that blends Google's established rating with user reviews:

$$W = \frac{vR + mC}{v + m}$$

| Variable | Description |
|----------|-------------|
| $v$ | Number of user reviews on Orbit |
| $R$ | Average of Orbit user review ratings |
| $m$ | Confidence threshold (set to **10**) |
| $C$ | `google_rating` — the Google Places API rating (the prior) |

**Behavior:**
- **0 user reviews:** `avg_rating = google_rating` (falls back to Google's rating)
- **Few user reviews (v < m):** Strongly weighted toward Google's rating
- **Many user reviews (v >> m):** Converges toward user review average

The `google_rating` field is set once during import from Google Places and never auto-modified. The `avg_rating` field is recomputed automatically via a Django signal whenever a review is created, updated, or deleted.

**Business response now includes:**

```json
{
  "id": 42,
  "google_rating": "4.50",
  "avg_rating": "4.35",
  "review_count": 3,
  ...
}
```

## Client Functions

```javascript
import {
  getReviews, getReview, createReview, updateReview, deleteReview, voteReview
} from '@/api/client'

// List reviews for a business
const { data } = await getReviews({ business: 42 })

// Create a review
await createReview({ business: 42, rating: 5, description: 'Great!' })

// Vote on a review (toggle)
const { data: vote } = await voteReview(1, 'useful')
// vote.status === 'added' || 'removed'

// Delete
await deleteReview(1)
```
