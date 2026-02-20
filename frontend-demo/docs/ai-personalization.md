# AI Personalization

GPT-4.1 analyzes a user's recent reviews and bookmarked businesses to understand their taste profile, generates a natural-language search query, then runs the full weighted vibe search (embedding similarity + proximity + rating) to surface new businesses the user will love.

**Requirements:** Authentication + verified email.

## Get Personalized Recommendations

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

## Client Usage

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

## Permissions

| Endpoint | Auth | Verified Email |
|----------|------|----------------|
| `GET /api/businesses/personalized/` | Required | Required |
