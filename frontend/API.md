# FBLC API Reference

Complete reference for all backend API endpoints. Base URL: `/api`

All responses are JSON. Paginated endpoints return `{ count, next, previous, results }`.

---

## Tags

### List Tags

```
GET /api/tags/
```

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Filter by name (case-insensitive substring) |
| `min_usage` | int | Only tags used by ≥ N businesses |

**Response:** Paginated list of tags.

```json
{
  "count": 264,
  "next": "http://localhost/api/tags/?page=2",
  "previous": null,
  "results": [
    { "id": 148, "name": "cozy", "usage_count": 385 },
    { "id": 233, "name": "desserts", "usage_count": 80 },
    { "id": 98, "name": "outdoor-seating", "usage_count": 70 }
  ]
}
```

**Client function:**

```javascript
import { getTags } from '@/api/client'

const { data } = await getTags({ q: 'coffee', min_usage: 5 })
console.log(data.results) // [{ id, name, usage_count }, ...]
```

### Get Tag

```
GET /api/tags/{id}/
```

### Vector Search Tags

```
GET /api/tags/search/?q=outdoor+dining
```

Embeds the query with OpenAI and finds tags by **cosine similarity** — matches by meaning, not text.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | Yes | Natural language query |
| `limit` | int | No | Max results (default 20, max 50) |
| `min_usage` | int | No | Min business count filter |

**Response:** Array (not paginated) with `similarity` score.

```json
[
  { "id": 98, "name": "outdoor-seating", "usage_count": 70, "similarity": 0.7924 },
  { "id": 236, "name": "outdoor-living", "usage_count": 9, "similarity": 0.6701 },
  { "id": 248, "name": "dine-in", "usage_count": 9, "similarity": 0.5975 }
]
```

Falls back to text search if embedding fails.

**Client function:**

```javascript
import { searchTags } from '@/api/client'

const { data } = await searchTags({ q: 'romantic evening', limit: 10 })
console.log(data) // [{ id, name, usage_count, similarity }, ...]
```

---

## Categories

### List Categories

```
GET /api/categories/
```

**Response:**

```json
{
  "count": 22,
  "results": [
    {
      "id": 1,
      "name": "Restaurants",
      "slug": "restaurants",
      "icon_name": "restaurant",
      "parent": null,
      "parent_name": null,
      "updated_at": "2026-02-15T20:00:00Z"
    },
    {
      "id": 6,
      "name": "Cafés & Coffee",
      "slug": "cafes-coffee",
      "icon_name": "coffee",
      "parent": 1,
      "parent_name": "Restaurants",
      "updated_at": "2026-02-15T20:00:00Z"
    }
  ]
}
```

### Create Category

```
POST /api/categories/
Content-Type: application/json

{ "name": "Bookstores", "slug": "bookstores", "icon_name": "book", "parent": 4 }
```

### Update Category

```
PATCH /api/categories/{id}/
Content-Type: application/json

{ "icon_name": "new-icon" }
```

### Delete Category

```
DELETE /api/categories/{id}/
```

**Client functions:**

```javascript
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/client'

const { data } = await getCategories()
await createCategory({ name: 'Bookstores', slug: 'bookstores' })
await updateCategory(1, { icon_name: 'new-icon' })
await deleteCategory(1)
```

---

## Businesses

### List Businesses

```
GET /api/businesses/
```

| Param | Type | Description |
|-------|------|-------------|
| `category` | int | Filter by category ID |
| `onboarding_status` | string | `discovered`, `contacted`, `active` |
| `search` | string | Search name, email, Google Place ID |
| `ordering` | string | Sort: `avg_rating`, `-avg_rating`, `name`, `created_at`, `review_count` |
| `page` | int | Page number (default 1) |
| `page_size` | int | Items per page (default 50, max 100) |

**Response:**

```json
{
  "count": 1312,
  "next": "http://localhost/api/businesses/?page=2",
  "results": [
    {
      "id": 42,
      "name": "The Blue Bird Café",
      "description": "A cozy café with artisan coffee and pastries",
      "category": 6,
      "category_detail": {
        "id": 6,
        "name": "Cafés & Coffee",
        "slug": "cafes-coffee",
        "parent_name": "Restaurants"
      },
      "tags": [
        { "id": 148, "name": "cozy", "usage_count": 0 },
        { "id": 52, "name": "artisan-coffee", "usage_count": 0 }
      ],
      "address": "123 Queen St W, Toronto, ON",
      "phone": "+1 416-555-0123",
      "website_url": "https://bluebirdcafe.ca",
      "google_place_id": "ChIJ...",
      "google_types": ["cafe", "food", "point_of_interest"],
      "price_level": 2,
      "photo_references": ["places/ChIJ.../photos/..."],
      "business_status": "OPERATIONAL",
      "opening_hours": {
        "weekdayDescriptions": ["Monday: 7:00 AM – 6:00 PM", "Tuesday: 7:00 AM – 6:00 PM"]
      },
      "google_maps_uri": "https://maps.google.com/?cid=12345",
      "reviews_data": [
        {
          "author": "Jane D.",
          "rating": 5,
          "text": "Amazing coffee!",
          "relativePublishTimeDescription": "2 months ago"
        }
      ],
      "accessibility": { "wheelchairAccessibleParking": true, "wheelchairAccessibleEntrance": true },
      "payment_options": { "acceptsCreditCards": true, "acceptsDebitCards": true, "acceptsCashOnly": false },
      "parking": { "paidParkingLot": true, "freeStreetParking": false },
      "dine_in": true,
      "takeout": true,
      "delivery": false,
      "reservable": false,
      "serves_beer": true,
      "serves_wine": true,
      "serves_breakfast": true,
      "serves_lunch": true,
      "serves_dinner": false,
      "serves_brunch": true,
      "outdoor_seating": true,
      "live_music": false,
      "good_for_children": true,
      "good_for_groups": true,
      "allows_dogs": false,
      "restroom": true,
      "onboarding_status": "discovered",
      "lat": 43.6512,
      "lng": -79.3950,
      "avg_rating": 4.50,
      "review_count": 0,
      "user_rating_count": 287,
      "metadata": null,
      "image_url": "https://storage.googleapis.com/orbit-media-prod/businesses/42/0.jpg",
      "contact_email": null,
      "created_at": "2026-02-15T20:05:00Z",
      "updated_at": "2026-02-15T20:05:00Z"
    }
  ]
}
```

### Get Business

```
GET /api/businesses/{id}/
```

### Create Business

```
POST /api/businesses/
Content-Type: application/json

{
  "name": "Joe's Coffee",
  "description": "Cozy neighborhood café",
  "category": 6,
  "address": "123 Main St",
  "contact_email": "joe@coffee.com",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "onboarding_status": "active"
}
```

> Send `latitude` and `longitude` as write-only fields. They're converted to a PostGIS point. Read responses return `lat` and `lng` as computed fields.

### Update Business

```
PATCH /api/businesses/{id}/
Content-Type: application/json

{ "description": "Updated description" }
```

### Delete Business

```
DELETE /api/businesses/{id}/
```

**Client functions:**

```javascript
import { getBusinesses, getBusiness, createBusiness, updateBusiness, deleteBusiness } from '@/api/client'

const { data } = await getBusinesses({ category: 6, ordering: '-avg_rating' })
const { data: biz } = await getBusiness(42)
await createBusiness({ name: 'New Place', latitude: 43.65, longitude: -79.38 })
await updateBusiness(42, { description: 'Updated' })
await deleteBusiness(42)
```

---

## Weighted Vibe Search

```
GET /api/businesses/search/?q=cozy+coffee&lat=43.6532&lng=-79.3832
```

AI-powered semantic search with weighted scoring.

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | **Yes** | Natural language query |
| `lat` | float | No | User latitude (enables proximity scoring + auto-import) |
| `lng` | float | No | User longitude |
| `category` | int | No | Category ID filter |
| `tag` | int/int[] | No | Tag ID(s) — AND logic. `?tag=1&tag=2` or `?tag=1,2` |
| `sort` | string | No | Override: `distance` or `rating` (default: weighted) |
| `limit` | int | No | Max results 1–50 (default 10) |

### Scoring Formula

Default weighted mode:

```
score = 0.70 × vibe_similarity              (cosine similarity of embeddings)
      + 0.15 × proximity_score              (1 / (1 + distance_km / 5.0))
      + 0.15 × rating_score                 (avg_rating / 5.0)
```

- At 0 km → proximity = 1.0, at 5 km → 0.5, at 15 km → 0.25
- Without lat/lng → proximity = 0 (vibe + rating only)

### Response

Array (not paginated) — each result includes all business fields plus:

| Extra Field | Description |
|-------------|-------------|
| `similarity` | Cosine similarity to query (0–1) |
| `distance_km` | Distance from user in km (null if no lat/lng) |
| `score` | Final weighted score (null when using sort override) |

```json
[
  {
    "id": 42,
    "name": "The Blue Bird Café",
    "similarity": 0.8234,
    "distance_km": 1.23,
    "score": 0.724,
    "tags": [{ "id": 148, "name": "cozy" }],
    "avg_rating": 4.50,
    ...
  }
]
```

### Auto-Import Behavior

When `lat`/`lng` is provided and the area hasn't been searched before:
1. A **background thread** imports businesses from Google Places (~20 search types)
2. Import is **capped at 100 businesses** per area (`MAX_BUSINESSES_PER_IMPORT`)
3. GPT-4o-mini classifies and generates tags
4. **Images are downloaded** from Google Places Photos API and uploaded to GCS (`gs://orbit-media-prod/businesses/{id}/0.jpg`)
5. `image_url` is set to the **public GCS URL** — the Google API is never called again for that business
6. Embeddings are created
7. The search returns immediately with existing data; new businesses appear on subsequent searches

### Image Pipeline

Businesses images are served from a **public GCS bucket** (`orbit-media-prod`):
- During import, the first photo reference is downloaded from Google Places Photos API
- The image is uploaded to `businesses/{id}/0.jpg` in the GCS bucket
- `image_url` is set to `https://storage.googleapis.com/orbit-media-prod/businesses/{id}/0.jpg`
- Google Places API is called **exactly once** per business — subsequent reads use the stored GCS URL
- If a business has no photos or download fails, `image_url` remains `null`

### Examples

```bash
# Basic vibe search
curl "http://localhost/api/businesses/search/?q=romantic+dinner&limit=5"

# With location (enables proximity scoring + auto-import)
curl "http://localhost/api/businesses/search/?q=cozy+coffee&lat=43.6532&lng=-79.3832"

# Filter by category and tags
curl "http://localhost/api/businesses/search/?q=brunch&category=6&tag=148&tag=98"

# Sort by distance
curl "http://localhost/api/businesses/search/?q=pizza&lat=43.6532&lng=-79.3832&sort=distance"
```

**Client function:**

```javascript
import { searchBusinesses } from '@/api/client'

const { data } = await searchBusinesses({
  q: 'cozy coffee shop',
  lat: 43.6532,
  lng: -79.3832,
  tag: [148, 98],    // AND filter: must have both tags
  category: 6,
  limit: 10
})

data.forEach(biz => {
  console.log(`${biz.name} — score: ${biz.score}, distance: ${biz.distance_km}km`)
})
```

---

## Stats

```
GET /api/businesses/stats/
```

No parameters. Returns database overview.

**Response:**

```json
{
  "total_businesses": 1312,
  "with_embeddings": 1312,
  "with_tags": 1280,
  "tag_count": 264,
  "searched_areas": 3,
  "avg_rating": 4.12,
  "top_tags": [
    { "id": 148, "name": "cozy", "c": 385 },
    { "id": 233, "name": "desserts", "c": 80 },
    { "id": 98, "name": "outdoor-seating", "c": 70 }
  ]
}
```

**Client function:**

```javascript
import { getStats } from '@/api/client'

const { data } = await getStats()
console.log(`${data.total_businesses} businesses, ${data.tag_count} tags`)
```

---

## Error Responses

All errors return JSON with a `detail` field:

```json
{ "detail": "Query parameter \"q\" is required." }
```

| Status | Meaning |
|--------|---------|
| `400` | Bad request (missing/invalid parameters) |
| `404` | Resource not found |
| `503` | Embedding service unavailable (OpenAI down) |

---

## Pagination

Paginated endpoints (`/tags/`, `/categories/`, `/businesses/`) return:

```json
{
  "count": 1312,
  "next": "http://localhost/api/businesses/?page=2",
  "previous": null,
  "results": [...]
}
```

| Param | Default | Max | Description |
|-------|---------|-----|-------------|
| `page` | 1 | — | Page number |
| `page_size` | 50 | 100 | Items per page |

Action endpoints (`/search/`, `/stats/`, `/tags/search/`) return raw arrays or objects (not paginated).

---

## Authentication

User system with email verification via Brevo (Sendinblue). All auth endpoints are under `/api/auth/`.

### Register

```
POST /api/auth/register/
```

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Unique email address |
| `username` | string | Yes | Unique username |
| `password` | string | Yes | Min 8 characters, Django validators applied |
| `display_name` | string | No | Profile display name |

```json
{
  "email": "jane@example.com",
  "username": "janedoe",
  "password": "secret123!",
  "display_name": "Jane"
}
```

**Response:** `201 Created`

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "username": "janedoe",
    "email": "jane@example.com",
    "display_name": "Jane",
    "avatar_url": null,
    "bio": "",
    "email_verified": false,
    "metadata": {}
  }
}
```

A verification email is sent asynchronously via Celery + Brevo.

### Login

```
POST /api/auth/login/
```

**Request body:**

```json
{
  "username": "janedoe",
  "password": "secret123!"
}
```

The `username` field accepts either a username or an email address.

**Response:** `200 OK`

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "username": "janedoe",
    "email": "jane@example.com",
    "display_name": "Jane",
    "avatar_url": null,
    "bio": "",
    "email_verified": true,
    "metadata": {}
  }
}
```

### Verify Email

```
POST /api/auth/verify-email/
```

**Request body:**

```json
{ "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890" }
```

**Response:** `200 OK`

```json
{ "detail": "Email verified successfully." }
```

Tokens expire after 24 hours and are single-use.

### Get / Update Profile

```
GET  /api/auth/me/
PATCH /api/auth/me/
```

**Requires authentication.**

GET returns the current user's profile. PATCH accepts:

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | string | Display name |
| `avatar_url` | string | Avatar URL |
| `bio` | string | Bio text |
| `metadata` | object | Arbitrary JSON (extensible) |

### Resend Verification Email

```
POST /api/auth/resend-verify/
```

**Requires authentication.** Invalidates previous unused tokens and sends a new verification email.

**Response:** `200 OK`

```json
{ "detail": "Verification email sent." }
```

### Legacy Token Endpoint

```
POST /api/auth/token/
```

Still available for backward compatibility. Accepts `{ username, password }` and returns `{ token }`.

### Forgot Password

```
POST /api/auth/forgot-password/
```

**No authentication required.** Initiates a password-reset flow by sending an email with a reset link.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | The registered email address |

```json
{ "email": "jane@example.com" }
```

**Response:** Always `200 OK` — prevents email enumeration.

```json
{ "detail": "If an account with that email exists, a reset link has been sent." }
```

The email contains a link to `{FRONTEND_BASE_URL}/reset-password?token=<uuid>`. Tokens expire in **1 hour**.

### Reset Password

```
POST /api/auth/reset-password/
```

**No authentication required.** Resets the user's password using a token from the reset email.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `token` | string | Yes | UUID from the reset email |
| `new_password` | string | Yes | New password (Django validators applied) |

```json
{
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "new_password": "newSecure123!"
}
```

**Response:** `200 OK`

```json
{ "detail": "Password reset successfully. Please log in." }
```

**Side effects:**
- The reset token is marked as used (single-use)
- **All existing auth tokens are deleted** — the user is logged out on all devices and must log in again with the new password

**Error responses:**

| Status | Detail |
|--------|--------|
| `400` | `"token is required."` / `"new_password is required."` |
| `400` | `"Invalid or expired reset token."` |
| `400` | `["This password is too short. It must contain at least 8 characters."]` (Django password validators) |

### Client Functions

```javascript
import {
  register, login, verifyEmail, getMe, updateMe, resendVerify,
  forgotPassword, resetPassword, setAuthToken
} from '@/api/client'

// Register
const { data } = await register({ email: 'j@ex.com', username: 'jane', password: 'secret123!' })
setAuthToken(data.token)

// Login (username or email)
const { data } = await login('jane', 'secret123!')
setAuthToken(data.token)

// Verify email
await verifyEmail('a1b2c3d4-e5f6-7890-abcd-ef1234567890')

// Get profile
const { data: profile } = await getMe()

// Update profile
await updateMe({ display_name: 'Jane D.', bio: 'Coffee lover' })

// Resend verification
await resendVerify()

// Forgot password — always returns 200
await forgotPassword('jane@example.com')

// Reset password with token from email
await resetPassword('a1b2c3d4-e5f6-...', 'newSecure123!')
// User must log in again after this
```

### Permissions

| Endpoint | Auth Required | Email Verified |
|----------|:------------:|:--------------:|
| `GET /api/reviews/` | No | No |
| `POST /api/reviews/` | Yes | **Yes** |
| `PATCH/DELETE /api/reviews/{id}/` | Yes (owner) | **Yes** |
| `POST /api/reviews/{id}/vote/` | Yes | **Yes** |
| `GET/POST /api/bookmarks/*` | Yes | **Yes** |
| `PATCH/DELETE /api/bookmarks/{id}/` | Yes (owner) | **Yes** |
| `GET /api/auth/me/` | Yes | No |
| `POST /api/auth/forgot-password/` | No | No |
| `POST /api/auth/reset-password/` | No | No |
| All other read endpoints | No | No |

---

## Bookmarks

Authenticated, verified users can save (bookmark) businesses for later. Each user's bookmarks are private — other users cannot see or modify them.

**All bookmark endpoints require authentication + verified email.**

### List Bookmarks

```
GET /api/bookmarks/
```

Returns the current user's bookmarks (paginated). Only the authenticated user's bookmarks are returned — no cross-user access.

**Response:**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 4,
      "business": 3,
      "user": 2,
      "username": "janedoe",
      "business_name": "1/2 COFFEE",
      "note": "Amazing tacos",
      "created_at": "2026-02-18T20:29:28Z"
    }
  ]
}
```

### Create Bookmark

```
POST /api/bookmarks/
Content-Type: application/json

{
  "business": 42,
  "note": "Try the latte next time"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `business` | int | Yes | Business ID |
| `note` | string | No | Private note (max 500 chars) |

Returns `201`. Duplicate bookmarks return `400`.

### Update Bookmark

```
PATCH /api/bookmarks/<id>/
```

Only the `note` field can be updated. Users can only update their own bookmarks.

### Delete Bookmark

```
DELETE /api/bookmarks/<id>/
```

Returns `204`. Users can only delete their own bookmarks.

### Toggle Bookmark

```
POST /api/bookmarks/toggle/
Content-Type: application/json

{ "business": 42 }
```

**Convenience endpoint** — adds the bookmark if it doesn't exist, removes it if it does.

**Response (added):** `201`

```json
{
  "status": "added",
  "bookmark": { "id": 5, "business": 42, "user": 2, "username": "janedoe", "business_name": "Blue Bird Café", "note": "", "created_at": "..." }
}
```

**Response (removed):** `200`

```json
{ "status": "removed", "business": 42 }
```

### Check Bookmark

```
GET /api/bookmarks/check/?business=42
```

Returns whether the current user has bookmarked a specific business.

```json
{ "bookmarked": true, "business": 42 }
```

### Get Bookmark IDs

```
GET /api/bookmarks/ids/
```

**Lightweight endpoint** — returns just the business IDs the user has bookmarked. Ideal for rendering bookmark icons across a list of businesses without fetching full bookmark objects.

```json
{ "business_ids": [3, 2, 1] }
```

### Client Functions

```javascript
import { getBookmarks, createBookmark, updateBookmark, deleteBookmark, toggleBookmark, checkBookmark, getBookmarkIds } from '@/api/client'

// List my bookmarks
const { data } = await getBookmarks()

// Toggle bookmark (add or remove)
const { data: result } = await toggleBookmark(42)
// result.status === 'added' || 'removed'

// Check if bookmarked
const { data: check } = await checkBookmark(42)
// check.bookmarked === true/false

// Get all bookmarked IDs (for rendering icons)
const { data: ids } = await getBookmarkIds()
// ids.business_ids === [3, 2, 1]

// Create with note
await createBookmark({ business: 42, note: 'Try the latte' })

// Update note
await updateBookmark(5, { note: 'Updated note' })

// Delete
await deleteBookmark(5)
```

### Frontend Implementation Guide

To integrate bookmarks into the actual frontend:

1. **On app load** (after auth), call `getBookmarkIds()` and store `business_ids` in a reactive Set for O(1) lookups.

2. **Bookmark icon on business cards**: Check `bookmarkSet.has(business.id)` to render filled/unfilled heart/bookmark icon.

3. **Toggle on click**: Call `toggleBookmark(businessId)`. On success, add/remove from the local Set — no need to refetch.

4. **Bookmarks page**: Call `getBookmarks()` for the full list with business names, notes, and dates. Support PATCH for editing notes.

5. **Optimistic UI**: Update the icon immediately, revert on error. The toggle endpoint is idempotent and safe.

```vue
<!-- Example: Bookmark button component -->
<template>
  <button @click="toggle" :class="{ active: isBookmarked }">
    {{ isBookmarked ? '★' : '☆' }} Save
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { toggleBookmark } from '@/api/client'

const props = defineProps({ businessId: Number, bookmarkSet: Set })
const emit = defineEmits(['toggled'])

const isBookmarked = computed(() => props.bookmarkSet.has(props.businessId))

const toggle = async () => {
  // Optimistic update
  const was = isBookmarked.value
  if (was) props.bookmarkSet.delete(props.businessId)
  else props.bookmarkSet.add(props.businessId)

  try {
    await toggleBookmark(props.businessId)
    emit('toggled', props.businessId, !was)
  } catch {
    // Revert on error
    if (was) props.bookmarkSet.add(props.businessId)
    else props.bookmarkSet.delete(props.businessId)
  }
}
</script>
```

### Security Notes

- **Queryset-level isolation**: `get_queryset()` filters by `user=request.user`. Other users' bookmarks return 404, not 403 — this prevents enumeration.
- **Email verification required**: Unverified users get `403` on all bookmark endpoints.
- **No public bookmark counts**: Bookmark counts are not exposed on the Business model to protect user privacy.

---

## Reviews

User-submitted reviews for businesses. Each user can leave one review per business.
**Creating, updating, and deleting reviews requires a verified email.**

### List Reviews

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

### Create Review

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

### Retrieve Review

```
GET /api/reviews/<id>/
```

**Public.** Returns a single review object.

### Update Review

```
PATCH /api/reviews/<id>/
```

**Owner only.** Only the review author can update their review. Accepts the same fields as create.
A new `photo` field replaces the existing image.

### Delete Review

```
DELETE /api/reviews/<id>/
```

**Owner only.** Returns `204 No Content`.

### Vote on Review (Helpfulness)

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

### Bayesian Rating System

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

### Client Functions

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
