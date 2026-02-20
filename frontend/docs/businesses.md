# Businesses

## List Businesses

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

## Get Business

```
GET /api/businesses/{id}/
```

## Create Business

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

## Update Business

```
PATCH /api/businesses/{id}/
Content-Type: application/json

{ "description": "Updated description" }
```

## Delete Business

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
