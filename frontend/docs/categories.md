# Categories

## List Categories

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

## Create Category

```
POST /api/categories/
Content-Type: application/json

{ "name": "Bookstores", "slug": "bookstores", "icon_name": "book", "parent": 4 }
```

## Update Category

```
PATCH /api/categories/{id}/
Content-Type: application/json

{ "icon_name": "new-icon" }
```

## Delete Category

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
