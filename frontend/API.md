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
      "onboarding_status": "discovered",
      "lat": 43.6512,
      "lng": -79.3950,
      "avg_rating": 4.50,
      "review_count": 0,
      "user_rating_count": 287,
      "metadata": null,
      "image_url": null,
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
2. GPT-4o-mini classifies and generates tags
3. Embeddings are created
4. The search returns immediately with existing data; new businesses appear on subsequent searches

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
