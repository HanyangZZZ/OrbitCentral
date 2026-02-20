# Tags

## List Tags

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

## Get Tag

```
GET /api/tags/{id}/
```

## Vector Search Tags

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
