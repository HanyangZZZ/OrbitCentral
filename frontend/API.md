# Orbit API Reference

Complete reference for all backend API endpoints. Base URL: `/api`

All responses are JSON. Paginated endpoints return `{ count, next, previous, results }`.

## Table of Contents

- [Tags](#tags) — list, get, vector search
- [Categories](#categories) — CRUD
- [Businesses](#businesses) — CRUD, photo proxy
- [Weighted Vibe Search](#weighted-vibe-search) — AI-powered semantic search
- [Stats](#stats) — database overview
- [Error Responses](#error-responses)
- [Pagination](#pagination)
- [Authentication](#authentication) — register, login, verify email, password reset
- [Bookmarks](#bookmarks) — save businesses, toggle, check
- [Reviews](#reviews) — CRUD, helpfulness voting, Bayesian ratings
- [AI Reviews](#ai-reviews) — GPT-powered conversational review writing
- [AI Personalization](#ai-personalization) — GPT-powered business recommendations

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

## Business Photo Proxy

```
GET /api/businesses/{id}/photo/?idx=0&maxHeight=400
```

Returns a **302 redirect** to the Google Places photo for the business. Use this as an `<img src>` — the browser follows the redirect automatically.

Most businesses have `image_url: null` because GCS image storage isn't configured yet. This proxy endpoint resolves photos on the fly from the `photo_references` stored on each business.

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `idx` | int | `0` | Index into the business's `photo_references` array |
| `maxHeight` | int | `400` | Maximum height in pixels for the returned image |

### Response

- **302** — Redirect to the resolved Google Places photo URL
- **404** — Business not found, or no photo at the given index
- **503** — `GOOGLE_PLACES_API_KEY` not configured on the server

### Usage

```html
<!-- Direct in HTML/Vue template -->
<img :src="`${apiBase}/businesses/${business.id}/photo/`" @error="handleNoPhoto" />

<!-- Higher resolution -->
<img :src="`${apiBase}/businesses/${business.id}/photo/?maxHeight=800`" />

<!-- Second photo -->
<img :src="`${apiBase}/businesses/${business.id}/photo/?idx=1`" />
```

**Client function:**

```javascript
import { getBusinessPhotoUrl } from '@/api/client'

const url = getBusinessPhotoUrl(42)                          // first photo, 400px
const url = getBusinessPhotoUrl(42, { idx: 1, maxHeight: 800 }) // second photo, 800px

// Check if business has photos before rendering
const hasPhotos = business.photo_references?.length > 0
```

> **Tip:** Always add an `@error` handler on `<img>` tags — some businesses have stale photo references that may 404.

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
| `GET/POST /api/ai-reviews/*` | Yes | **Yes** |
| `DELETE /api/ai-reviews/{id}/` | Yes (owner) | **Yes** |
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

---

## AI Reviews

AI-powered conversational review writing using GPT-4.1. The user chats naturally about their experience, the AI detects relevant tags (add/remove), and generates a polished review description.

**Flow:**
1. **Start** → AI sends a friendly opening question
2. **Message** → User chats back and forth (AI calls `add_tag`/`remove_tag` tools behind the scenes)
3. **Generate** → AI writes the final review description from the conversation
4. **Confirm** → Creates a real `Review` object and applies tag changes to the business

All endpoints require **authentication** and **verified email**.

### List AI Review Sessions

```
GET /api/ai-reviews/
```

Returns all of the current user's AI review chat sessions.

**Response:**

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "business": 42,
    "business_name": "Café Luna",
    "user": 1,
    "username": "hanyang",
    "rating": 4,
    "status": "active",
    "conversation": [
      { "role": "assistant", "content": "Hey! You gave Café Luna 4 stars..." },
      { "role": "user", "content": "The oat milk lattes are amazing" }
    ],
    "tags_to_add": ["oat-milk", "cozy"],
    "tags_to_remove": [],
    "generated_description": "",
    "review": null,
    "created_at": "2025-02-20T01:23:45Z",
    "updated_at": "2025-02-20T01:24:12Z"
  }
]
```

### Retrieve AI Review Session

```
GET /api/ai-reviews/{id}/
```

Returns a single chat session by UUID.

### Start AI Review Chat

```
POST /api/ai-reviews/start/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `business` | int | Yes | Business ID to review |
| `rating` | int (1-5) | Yes | Star rating |

**Request:**

```json
{ "business": 42, "rating": 4 }
```

**Response (201 Created):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business": 42,
  "business_name": "Café Luna",
  "user": 1,
  "username": "hanyang",
  "rating": 4,
  "status": "active",
  "conversation": [
    {
      "role": "assistant",
      "content": "Hey! You gave Café Luna 4 stars — sounds like a solid spot! What stood out most about your visit?"
    }
  ],
  "tags_to_add": [],
  "tags_to_remove": [],
  "generated_description": "",
  "review": null,
  "created_at": "2025-02-20T01:23:45Z",
  "updated_at": "2025-02-20T01:23:45Z"
}
```

**Notes:**
- If the user already has an active session for the same business, returns the existing session (200) instead of creating a new one.
- If the user has already reviewed the business, returns a validation error.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Already reviewed this business |
| 503 | AI service temporarily unavailable |

### Send Message

```
POST /api/ai-reviews/{id}/message/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's reply (max 2000 chars) |

**Request:**

```json
{ "message": "The oat milk lattes are incredible, and the atmosphere is super cozy" }
```

**Response (200):**

```json
{
  "reply": "Oat milk lattes AND a cozy vibe — that's a winning combo! Was it more of a quick grab-and-go, or did you settle in for a while?",
  "tags_added": ["oat-milk", "cozy"],
  "tags_removed": [],
  "session": { /* full ReviewChat session object (same shape as List response) */ }
}
```

**How tags work:** The AI uses OpenAI function-calling tools (`add_tag`, `remove_tag`) during the conversation. Tags are accumulated in `tags_to_add` / `tags_to_remove` on the session and applied to the business only when the review is confirmed.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active |
| 503 | AI service temporarily unavailable |

### Generate Review

```
POST /api/ai-reviews/{id}/generate/
```

No request body required. Uses the conversation history to generate a natural review description.

**Response (200):**

```json
{
  "generated_description": "Café Luna is my go-to for a chill morning pick-me-up. Their oat milk lattes are velvety smooth — easily some of the best in the area. The interior has a warm, cozy feel that makes you want to linger, even on a quick coffee run. Service is friendly and fast. A solid 4-star spot I'll keep coming back to.",
  "session": { /* full ReviewChat session object */ }
}
```

**Notes:**
- Requires at least one user message in the conversation.
- Can be called multiple times to regenerate.

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active / no user messages yet |
| 503 | AI service temporarily unavailable |

### Confirm Review

```
POST /api/ai-reviews/{id}/confirm/
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | No | Override the generated text |
| `photo` | string | No | Base64-encoded photo (same as normal reviews) |

Creates a real `Review` object (same model as manual reviews) and applies all accumulated tag changes to the business.

**Request:**

```json
{}
```

Or with overrides:

```json
{
  "description": "My custom review text...",
  "photo": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response (201 Created):**

```json
{
  "review": {
    "id": 6,
    "user": 1,
    "username": "hanyang",
    "business": 42,
    "business_name": "Café Luna",
    "rating": 4,
    "description": "Café Luna is my go-to for a chill morning pick-me-up...",
    "image_url": null,
    "helpfulness_score": 0,
    "created_at": "2025-02-20T01:30:00Z"
  },
  "tags_added": ["oat-milk", "cozy"],
  "tags_removed": []
}
```

**Errors:**

| Status | Reason |
|--------|--------|
| 400 | Session is no longer active / no description available / already reviewed |

### Abandon Session

```
DELETE /api/ai-reviews/{id}/
```

Marks the session as `abandoned`. No review is created, no tags are applied.

**Response:** `204 No Content`

### Session Status Values

| Status | Description |
|--------|-------------|
| `active` | Chat in progress |
| `completed` | Review created successfully |
| `abandoned` | User cancelled the session |

### Client Functions

```javascript
import {
  getAIReviewSessions, startAIReview, sendAIReviewMessage,
  generateAIReview, confirmAIReview, abandonAIReview
} from '@/api/client'

// List sessions
const { data } = await getAIReviewSessions()

// Start a new chat
const { data: session } = await startAIReview(42, 4)  // business=42, rating=4

// Chat with the AI
const { data: msgRes } = await sendAIReviewMessage(session.id, 'Great oat milk lattes!')
console.log(msgRes.reply)         // AI's response
console.log(msgRes.tags_added)    // ['oat-milk']

// Generate the review text
const { data: genRes } = await generateAIReview(session.id)
console.log(genRes.generated_description)

// Confirm and publish
const { data: confirmRes } = await confirmAIReview(session.id)
console.log(confirmRes.review)     // the created Review object
console.log(confirmRes.tags_added) // tags applied to the business

// Or abandon
await abandonAIReview(session.id)
```

---

## AI Personalization

GPT-4.1 analyzes a user's recent reviews and bookmarked businesses to understand their taste profile, generates a natural-language search query, then runs the full weighted vibe search (embedding similarity + proximity + rating) to surface new businesses the user will love.

**Requirements:** Authentication + verified email.

### Get Personalized Recommendations

```
GET /api/businesses/personalized/
Authorization: Token <token>
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `lat` | float | — | User latitude (enables proximity scoring) |
| `lng` | float | — | User longitude |
| `limit` | int | 5 | Max results (1–50) |

**How it works:**

1. Fetches user's 20 most recent reviews + 20 most recent bookmarks (de-duplicated)
2. Extracts business name, category, tags, rating, price level, and user's review text
3. Sends profile to GPT-4.1 which generates a 3–8 word search query capturing taste patterns
4. Generates an embedding for the query via `text-embedding-3-small`
5. Runs weighted vibe search: 70% vibe similarity + 15% proximity + 15% rating
6. Excludes businesses the user has already reviewed or bookmarked
7. Returns top results

**Response:**

```json
{
  "query": "cozy affordable brunch cafes outdoor seating",
  "profile_size": 15,
  "results": [
    {
      "id": 42,
      "name": "The Morning Owl",
      "category": "cafe",
      "category_name": "Cafe",
      "description": "A cozy brunch spot with fresh pastries...",
      "address": "123 Queen St E, Toronto",
      "avg_rating": 4.3,
      "review_count": 12,
      "price_level": 2,
      "photo_url": "https://storage.googleapis.com/.../photo.jpg",
      "tags": [
        { "id": 148, "name": "cozy" },
        { "id": 55, "name": "brunch" }
      ],
      "distance_km": 1.2,
      "similarity": 0.891,
      "score": 0.847
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `query` | The search query GPT generated from the user's profile |
| `profile_size` | Number of businesses analyzed (reviews + bookmarks) |
| `results` | Array of `BusinessSearchSerializer` objects (same shape as weighted vibe search) |

**Error responses:**

| Status | Reason |
|--------|--------|
| 401 | Not authenticated |
| 403 | Email not verified |
| 400 | No reviews or bookmarks found — need activity to personalize |
| 502 | OpenAI API error |

### Client usage

```js
import { getPersonalized } from './api/client'

// Basic — no location
const { data } = await getPersonalized()
console.log(data.query)   // "cozy affordable brunch cafes"
console.log(data.results)  // top 5 businesses

// With location for proximity scoring
const { data: nearby } = await getPersonalized({
  lat: 43.651,
  lng: -79.347,
  limit: 10
})
```

### Permissions

| Endpoint | Auth | Verified Email |
|----------|------|----------------|
| `GET /api/businesses/personalized/` | ✅ Required | ✅ Required |

---
