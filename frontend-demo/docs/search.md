# Weighted Vibe Search

```
GET /api/businesses/search/?q=cozy+coffee&lat=43.6532&lng=-79.3832
```

AI-powered semantic search with weighted scoring.

## Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | **Yes** | Natural language query |
| `lat` | float | No | User latitude (enables proximity scoring + auto-import) |
| `lng` | float | No | User longitude |
| `category` | int | No | Category ID filter |
| `tag` | int/int[] | No | Tag ID(s) — AND logic. `?tag=1&tag=2` or `?tag=1,2` |
| `sort` | string | No | Override: `distance` or `rating` (default: weighted) |
| `limit` | int | No | Max results 1–50 (default 10) |

## Scoring Formula

Default weighted mode:

```
score = 0.70 × vibe_similarity              (cosine similarity of embeddings)
      + 0.15 × proximity_score              (1 / (1 + distance_km / 5.0))
      + 0.15 × rating_score                 (avg_rating / 5.0)
```

- At 0 km → proximity = 1.0, at 5 km → 0.5, at 15 km → 0.25
- Without lat/lng → proximity = 0 (vibe + rating only)

## Response

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

## Auto-Import Behavior

When `lat`/`lng` is provided and the area hasn't been searched before:
1. A **background thread** imports businesses from Google Places (~20 search types)
2. Import is **capped at 100 businesses** per area (`MAX_BUSINESSES_PER_IMPORT`)
3. GPT-4o-mini classifies and generates tags
4. **Images are downloaded** from Google Places Photos API and uploaded to GCS (`gs://orbit-media-prod/businesses/{id}/0.jpg`)
5. `image_url` is set to the **public GCS URL** — the Google API is never called again for that business
6. Embeddings are created
7. The search returns immediately with existing data; new businesses appear on subsequent searches

## Image Pipeline

Businesses images are served from a **public GCS bucket** (`orbit-media-prod`):
- During import, the first photo reference is downloaded from Google Places Photos API
- The image is uploaded to `businesses/{id}/0.jpg` in the GCS bucket
- `image_url` is set to `https://storage.googleapis.com/orbit-media-prod/businesses/{id}/0.jpg`
- Google Places API is called **exactly once** per business — subsequent reads use the stored GCS URL
- If a business has no photos or download fails, `image_url` remains `null`

## Examples

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
