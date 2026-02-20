# Bookmarks

Authenticated, verified users can save (bookmark) businesses for later. Each user's bookmarks are private — other users cannot see or modify them.

**All bookmark endpoints require authentication + verified email.**

## List Bookmarks

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

## Create Bookmark

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

## Update Bookmark

```
PATCH /api/bookmarks/<id>/
```

Only the `note` field can be updated. Users can only update their own bookmarks.

## Delete Bookmark

```
DELETE /api/bookmarks/<id>/
```

Returns `204`. Users can only delete their own bookmarks.

## Toggle Bookmark

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

## Check Bookmark

```
GET /api/bookmarks/check/?business=42
```

Returns whether the current user has bookmarked a specific business.

```json
{ "bookmarked": true, "business": 42 }
```

## Get Bookmark IDs

```
GET /api/bookmarks/ids/
```

**Lightweight endpoint** — returns just the business IDs the user has bookmarked. Ideal for rendering bookmark icons across a list of businesses without fetching full bookmark objects.

```json
{ "business_ids": [3, 2, 1] }
```

## Client Functions

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

## Frontend Implementation Guide

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

## Security Notes

- **Queryset-level isolation**: `get_queryset()` filters by `user=request.user`. Other users' bookmarks return 404, not 403 — this prevents enumeration.
- **Email verification required**: Unverified users get `403` on all bookmark endpoints.
- **No public bookmark counts**: Bookmark counts are not exposed on the Business model to protect user privacy.
