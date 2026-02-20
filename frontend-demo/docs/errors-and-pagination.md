# Error Responses & Pagination

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
