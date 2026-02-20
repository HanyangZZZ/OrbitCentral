# Stats

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
