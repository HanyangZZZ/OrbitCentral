# Frontend ↔ Backend API Reference

> This document describes every API endpoint the frontend can call, with request/response
> examples and the matching `client.js` function.

## Base Configuration

The Axios client is configured in `src/api/client.js`:

```js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})
```

In development, Vite proxies `/api` → `http://localhost:8001` (configured in `vite.config.js`).

---

## Response Format

### List (paginated)

Every list endpoint returns a **paginated envelope**:

```json
{
  "count": 42,
  "next": "http://localhost:8001/api/users/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

To extract the array: `response.data.results`

### Detail / Create / Update

Returns the single object directly:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "role": "customer",
  ...
}
```

### Errors

```json
{
  "email": ["This field must be unique."],
  "status_code": 400
}
```

Access the error detail: `err.response.data`

---

## Pagination & Query Parameters

All list endpoints accept:

| Param        | Example                     | Description                          |
| ------------ | --------------------------- | ------------------------------------ |
| `page`       | `?page=2`                   | Page number (1-indexed)              |
| `page_size`  | `?page_size=10`             | Items per page (max 100, default 50) |
| `search`     | `?search=cafe`              | Full-text search across configured fields |
| `ordering`   | `?ordering=-created_at`     | Sort by field (prefix `-` for descending) |

Filter params are endpoint-specific (see each section below).

```js
// Example: page 2, 10 per page, filtered
const res = await getBusinesses({ page: 2, page_size: 10, category: 1 })
const items = res.data.results
const total = res.data.count
```

---

## Endpoints

### Users

| Method   | URL              | `client.js` function | Description          |
| -------- | ---------------- | -------------------- | -------------------- |
| `GET`    | `/users/`        | `getUsers(params)`   | List all users       |
| `POST`   | `/users/`        | `createUser(data)`   | Create a user        |
| `GET`    | `/users/:id/`    | —                    | Get one user         |
| `PATCH`  | `/users/:id/`    | `updateUser(id, data)` | Partial update     |
| `DELETE` | `/users/:id/`    | `deleteUser(id)`     | Delete a user        |

**Filters:** `?role=customer`, `?is_verified_human=true`
**Search:** `?search=alice` (searches `email`)
**Ordering:** `?ordering=-created_at`, `?ordering=email`

**POST body:**
```json
{
  "email": "alice@example.com",
  "password_hash": "raw-password-will-be-hashed",
  "role": "customer",
  "is_verified_human": false
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "alice@example.com",
  "role": "customer",
  "is_verified_human": false,
  "created_at": "2026-02-11T12:00:00Z",
  "updated_at": "2026-02-11T12:00:00Z"
}
```

> Note: `password_hash` is write-only — never returned in responses.

---

### Profiles

| Method   | URL                | `client.js` function        | Description      |
| -------- | ------------------ | --------------------------- | ---------------- |
| `GET`    | `/profiles/`       | `getProfiles(params)`       | List all profiles |
| `POST`   | `/profiles/`       | `upsertProfile(data)`       | Create or update  |
| `GET`    | `/profiles/:userId/` | —                         | Get one profile   |
| `PATCH`  | `/profiles/:userId/` | `updateProfile(userId, data)` | Partial update |
| `DELETE` | `/profiles/:userId/` | `deleteProfile(userId)`   | Delete a profile  |

**Filters:** `?high_contrast=true`, `?keyboard_only_nav=true`
**Search:** `?search=alice` (searches `display_name`, `user__email`)

**POST body (upsert — creates if missing, updates if exists):**
```json
{
  "user": 1,
  "display_name": "Alice",
  "avatar_url": "https://...",
  "high_contrast": false,
  "keyboard_only_nav": false,
  "loyalty_points": 100
}
```

---

### Categories

| Method   | URL                 | `client.js` function          | Description       |
| -------- | ------------------- | ----------------------------- | ----------------- |
| `GET`    | `/categories/`      | `getCategories(params)`       | List categories   |
| `POST`   | `/categories/`      | `createCategory(data)`        | Create a category |
| `GET`    | `/categories/:id/`  | —                             | Get one           |
| `PATCH`  | `/categories/:id/`  | `updateCategory(id, data)`    | Partial update    |
| `DELETE` | `/categories/:id/`  | `deleteCategory(id)`          | Delete            |

**Search:** `?search=food` (searches `name`, `slug`)

**POST body:**
```json
{
  "name": "Food & Drink",
  "slug": "food-drink",
  "icon_name": "utensils"
}
```

---

### Businesses

| Method   | URL                  | `client.js` function          | Description        |
| -------- | -------------------- | ----------------------------- | ------------------ |
| `GET`    | `/businesses/`       | `getBusinesses(params)`       | List businesses    |
| `POST`   | `/businesses/`       | `createBusiness(data)`        | Create a business  |
| `GET`    | `/businesses/:id/`   | —                             | Get one            |
| `PATCH`  | `/businesses/:id/`   | `updateBusiness(id, data)`    | Partial update     |
| `DELETE` | `/businesses/:id/`   | `deleteBusiness(id)`          | Delete             |

**Filters:** `?category=1`, `?owner=2`, `?onboarding_status=active`
**Search:** `?search=nova` (searches `name`, `contact_email`, `google_place_id`)
**Ordering:** `?ordering=-avg_rating`, `?ordering=name`, `?ordering=review_count`

**POST body:**
```json
{
  "name": "Cafe Nova",
  "lat": 37.7749,
  "lng": -122.4194,
  "category": 1,
  "owner": null,
  "description": "Great coffee spot",
  "address": "123 Main St",
  "contact_email": "info@cafenova.com",
  "onboarding_status": "discovered"
}
```

**Response includes computed fields (read-only):**
- `avg_rating` — auto-calculated
- `review_count` — auto-calculated
- `created_at`, `updated_at` — auto-set

---

### Reviews

| Method   | URL               | `client.js` function        | Description      |
| -------- | ----------------- | --------------------------- | ---------------- |
| `GET`    | `/reviews/`       | `getReviews(params)`        | List reviews     |
| `POST`   | `/reviews/`       | `createReview(data)`        | Create a review  |
| `GET`    | `/reviews/:id/`   | —                           | Get one          |
| `PATCH`  | `/reviews/:id/`   | `updateReview(id, data)`    | Partial update   |
| `DELETE` | `/reviews/:id/`   | `deleteReview(id)`          | Delete           |

**Filters:** `?business=1`, `?user=3`, `?rating=5`, `?is_visible=true`
**Search:** `?search=amazing` (searches `content`)
**Ordering:** `?ordering=-created_at`, `?ordering=rating`

**POST body:**
```json
{
  "business": 1,
  "user": 3,
  "rating": 5,
  "content": "Amazing food and service!"
}
```

> `rating` must be 1–5 (enforced by database constraint).

---

### Bookmarks

| Method   | URL                | `client.js` function      | Description        |
| -------- | ------------------ | ------------------------- | ------------------ |
| `GET`    | `/bookmarks/`      | `getBookmarks(params)`    | List bookmarks     |
| `POST`   | `/bookmarks/`      | `createBookmark(data)`    | Create a bookmark  |
| `DELETE` | `/bookmarks/:id/`  | `deleteBookmark(id)`      | Delete             |

**Filters:** `?user=1`, `?business=2`

**POST body:**
```json
{
  "user": 1,
  "business": 2
}
```

> Duplicate (user, business) pairs return a `400` error.

---

### Rewards

| Method   | URL              | `client.js` function        | Description      |
| -------- | ---------------- | --------------------------- | ---------------- |
| `GET`    | `/rewards/`      | `getRewards(params)`        | List rewards     |
| `POST`   | `/rewards/`      | `createReward(data)`        | Create a reward  |
| `GET`    | `/rewards/:id/`  | —                           | Get one          |
| `PATCH`  | `/rewards/:id/`  | `updateReward(id, data)`    | Partial update   |
| `DELETE` | `/rewards/:id/`  | `deleteReward(id)`          | Delete           |

**Filters:** `?provider_business=1`, `?trigger_business=2`, `?reward_type=dividend`
**Search:** `?search=discount` (searches `title`)
**Ordering:** `?ordering=expiry_date`, `?ordering=-discount_val`

**POST body:**
```json
{
  "provider_business": 1,
  "trigger_business": null,
  "title": "10% Off Next Visit",
  "description": "Valid for dine-in only",
  "discount_val": 10.00,
  "reward_type": "standard_coupon",
  "expiry_date": "2026-12-31T23:59:59Z"
}
```

**Reward types:** `dividend`, `standard_coupon`, `quest_reward`

---

### Coupons

| Method   | URL              | `client.js` function        | Description      |
| -------- | ---------------- | --------------------------- | ---------------- |
| `GET`    | `/coupons/`      | `getCoupons(params)`        | List coupons     |
| `POST`   | `/coupons/`      | `createCoupon(data)`        | Create a coupon  |
| `GET`    | `/coupons/:id/`  | —                           | Get one          |
| `PATCH`  | `/coupons/:id/`  | `updateCoupon(id, data)`    | Partial update   |
| `DELETE` | `/coupons/:id/`  | `deleteCoupon(id)`          | Delete           |

**Filters:** `?user=1`, `?reward=2`, `?status=locked`

**POST body:**
```json
{
  "user": 1,
  "reward": 2,
  "status": "locked"
}
```

**Statuses:** `locked`, `unlocked`, `redeemed`

---

### Automation Logs

| Method   | URL                    | `client.js` function          | Description    |
| -------- | ---------------------- | ----------------------------- | -------------- |
| `GET`    | `/automation-logs/`    | `getAutomationLogs(params)`   | List logs      |
| `POST`   | `/automation-logs/`    | `createAutomationLog(data)`   | Create a log   |

**Filters:** `?business=1`, `?action_type=email_sent`, `?status=success`
**Ordering:** `?ordering=-logged_at`

**POST body:**
```json
{
  "business": 1,
  "action_type": "email_sent",
  "status": "success"
}
```

---

## Common Patterns

### Loading a list with extract helper

```js
import { getBusinesses } from '@/api/client'

const response = await getBusinesses({ page: 1, page_size: 20 })
const businesses = response.data.results   // array of objects
const totalCount = response.data.count     // total in database
const nextPage   = response.data.next      // URL or null
```

### Creating a resource

```js
import { createBusiness } from '@/api/client'

try {
  const response = await createBusiness({
    name: 'Cafe Nova',
    lat: 37.7749,
    lng: -122.4194,
  })
  const newBusiness = response.data  // the created object
} catch (err) {
  // err.response.data contains field-level errors
  // e.g. { "name": ["This field is required."], "status_code": 400 }
  console.error(err.response.data)
}
```

### Updating a resource (PATCH)

```js
import { updateBusiness } from '@/api/client'

// Only send the fields you want to change
const response = await updateBusiness(1, { name: 'Cafe Nova 2.0' })
```

### Deleting a resource

```js
import { deleteBusiness } from '@/api/client'

await deleteBusiness(1)  // returns 204 No Content
```

### Filtering + searching

```js
// Get active businesses in category 1 matching "nova"
const res = await getBusinesses({
  category: 1,
  onboarding_status: 'active',
  search: 'nova',
  ordering: '-avg_rating',
})
```

### Error handling

```js
try {
  await createUser({ email: 'duplicate@test.com', password_hash: '...' })
} catch (err) {
  if (err.response) {
    // Server responded with an error
    const status = err.response.status       // 400, 404, 500, etc.
    const errors = err.response.data         // { "email": ["already exists"] }
    console.error(`HTTP ${status}:`, errors)
  } else {
    // Network error — backend unreachable
    console.error('Network error:', err.message)
  }
}
```

---

## Browsable API

During development, open any endpoint URL in a browser to get the **DRF Browsable API** —
an interactive HTML interface where you can send requests, inspect responses, and read
field documentation without any extra tools.

Example: `http://localhost:8001/api/businesses/`
