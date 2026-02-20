# FBLC Frontend — Handover Document

## For Frontend Developers

The backend API is fully deployed, tested, and ready for UI integration. **126 real businesses** (cafés, restaurants, shops) are already imported with AI tags, Google reviews, hours, and photos.

| Resource | URL |
|----------|-----|
| **Live API Demo** | http://orbitcentral.ca |
| **API Base URL** | http://business.orbitcentral.ca/api/ |
| **API Reference** | [API.md](API.md) — every endpoint documented with request/response examples |
| **API Client** | [src/api/client.js](src/api/client.js) — 31 ready-to-use functions with JSDoc |
| **Adminer (DB)** | http://admin.orbitcentral.ca — basic auth: `admin` / `fblcAdmin2026!` |

---

## Quick Start

```bash
npm install
npm run dev        # http://localhost:5173 — proxies /api to the live backend
```

To point at the live API without running the backend locally:
```bash
# .env.development
VITE_API_BASE_URL=http://business.orbitcentral.ca/api
```

---

## Authentication

```js
import { register, login, setAuthToken, getSavedToken, getMe, logout } from './api/client'

// Register
const { data } = await register({ email, username, password })
setAuthToken(data.token)  // persists to localStorage

// Login
const { data } = await login(username, password)
setAuthToken(data.token)

// On app load — restore session
const saved = getSavedToken()
if (saved) {
  try { const { data } = await getMe(); /* use data */ }
  catch { setAuthToken(null) }  // expired
}

// Logout
await logout()
setAuthToken(null)
```

**Key rules:**
- Tokens expire after **72 hours** — handle 401 responses with re-login
- Email verification is required before reviews/bookmarks (403 until verified)
- `setAuthToken()` saves to `localStorage` and sets the `Authorization` header for all requests
- On register, a verification email is sent via Brevo (check spam folder)

---

## API Endpoints — Quick Reference

| Function | Method | Endpoint | Auth | Notes |
|----------|--------|----------|------|-------|
| `getStats()` | GET | `/businesses/stats/` | No | Dashboard stats |
| `getCategories()` | GET | `/categories/` | No | 22 categories |
| `getTags(params)` | GET | `/tags/` | No | `?q=`, `?min_usage=` |
| `searchTags(params)` | GET | `/tags/search/` | No | AI vector search `?q=relaxing` |
| `getBusinesses(params)` | GET | `/businesses/` | No | Paginated: `?page_size=10` |
| `getBusiness(id)` | GET | `/businesses/:id/` | No | Full detail |
| `getBusinessPhotoUrl(id)` | — | `/businesses/:id/photo/` | No | Returns URL string for `<img src>` |
| `searchBusinesses(params)` | GET | `/businesses/search/` | No | AI vibe search `?q=cozy coffee` |
| `register(payload)` | POST | `/auth/register/` | No | `{email, username, password}` |
| `login(user, pass)` | POST | `/auth/login/` | No | Returns `{token, user}` |
| `getMe()` | GET | `/auth/me/` | Token | User profile |
| `logout()` | POST | `/auth/logout/` | Token | Deletes token server-side |
| `verifyEmail(token)` | POST | `/auth/verify-email/` | No | Token from email link |
| `forgotPassword(email)` | POST | `/auth/forgot-password/` | No | Sends reset email |
| `resetPassword(token, pw)` | POST | `/auth/reset-password/` | No | From reset email link |
| `getReviews(params)` | GET | `/reviews/` | No | `?business=ID` (cursor pagination) |
| `createReview(payload)` | POST | `/reviews/` | Token+Verified | `{business, rating, description}` |
| `deleteReview(id)` | DELETE | `/reviews/:id/` | Token (owner) | |
| `voteReview(id, type)` | POST | `/reviews/:id/vote/` | Token+Verified | `useful\|funny\|cool` |
| `getBookmarks()` | GET | `/bookmarks/` | Token+Verified | User's bookmarks |
| `getBookmarkIds()` | GET | `/bookmarks/ids/` | Token+Verified | `{business_ids: [1,2,3]}` |
| `toggleBookmark(bizId)` | POST | `/bookmarks/toggle/` | Token+Verified | `added` or `removed` |
| `checkBookmark(bizId)` | GET | `/bookmarks/check/` | Token+Verified | `{bookmarked: bool}` |
| `deleteBookmark(id)` | DELETE | `/bookmarks/:id/` | Token+Verified | |
| `getNextPage(nextUrl)` | GET | — | — | Follows cursor/page `next` URLs |

See [API.md](API.md) for full request/response examples.

---

## ⚠️  Important Gotchas

### 1. Pagination — Two Different Styles

| Endpoint | Style | Params | Response shape |
|----------|-------|--------|---------------|
| Businesses list | Page number | `?page_size=10&page=2` | `{count, next, previous, results}` |
| Reviews list | **Cursor** (infinite scroll) | `?page_size=10` | `{next, previous, results}` — **no count!** |
| Search | Flat array | `?limit=10` | `[...results]` (no wrapper) |
| Categories, Tags, Bookmarks | Page number | `?page_size=10&page=2` | `{count, next, previous, results}` |

**Note:** the pagination param is `page_size` (not `limit`) for list endpoints. Search uses `limit`.

For infinite scroll on reviews, use the `next` URL:
```js
import { getReviews, getNextPage } from './api/client'

const { data } = await getReviews({ business: 42 })
let reviews = data.results
if (data.next) {
  const page2 = await getNextPage(data.next)
  reviews = [...reviews, ...page2.data.results]
}
```

### 2. Business Photos

Most businesses have `image_url: null` because GCS upload isn't configured yet. **Use the photo proxy instead:**

```js
import { getBusinessPhotoUrl } from './api/client'

// Returns a URL that 302-redirects to the Google Places photo
const src = getBusinessPhotoUrl(businessId)           // default: first photo, 400px
const src = getBusinessPhotoUrl(businessId, { idx: 2, maxHeight: 800 })

// In Vue template:
// <img :src="getBusinessPhotoUrl(business.id)" @error="handleNoPhoto" />
```

Check `photo_references` array length to know if a business has photos:
```js
const hasPhotos = business.photo_references?.length > 0
```

### 3. Null Safety — Fields That Can Be Null

Always use optional chaining for these fields:
- `category_detail` → use `business.category_detail?.name ?? 'Uncategorized'`
- `image_url` → usually null; use `getBusinessPhotoUrl()` instead
- `price_level` — many businesses don't have this
- `phone`, `website_url`, `description` — can all be null
- `opening_hours` — not all businesses have hours data

### 4. Review Text Field Is `description` (Not `text`)

```js
createReview({ business: 42, rating: 5, description: 'Great place!' })
```

### 5. Bookmark Field Is `business` (Not `business_id`)

```js
toggleBookmark(businessId)  // client.js handles this correctly
// Raw: POST /bookmarks/toggle/  { "business": 42 }
```

### 6. Search Returns a Flat Array

```js
const { data } = await searchBusinesses({ q: 'cozy coffee', lat: 43.65, lng: -79.38 })
// data is [...businesses] — NOT { results: [...] }
```

### 7. Search Takes ~1 Second

AI search calls OpenAI embeddings, so expect ~1s latency. Always show a loading spinner.

First search in a new geographic area auto-imports businesses from Google Places via Celery. Imported businesses appear in subsequent searches.

### 8. Self-Vote Prevention

Users cannot vote on their own reviews — the API returns 400.

---

## Pages to Build

| Page | Key API Calls | Notes |
|------|--------------|-------|
| **Home / Explore** | `getStats()`, `getCategories()`, featured businesses | Dashboard feel |
| **Search** | `searchBusinesses({q, lat, lng, category, tag, sort, limit})` | Loading spinner, result cards with photos |
| **Business Detail** | `getBusiness(id)`, `getReviews({business: id})`, `checkBookmark(id)` | Hours, reviews, map, bookmark toggle |
| **Auth (Register/Login)** | `register()`, `login()`, `setAuthToken()` | Handle email verification flow |
| **Profile** | `getMe()`, `updateMe()`, `deleteAccount()` | Show verify status badge |
| **My Bookmarks** | `getBookmarks()`, `getBookmarkIds()` | Paginated list |
| **Write Review** | `createReview({business, rating, description, photo?})` | Star picker, optional base64 photo |

---

## CORS

`business.orbitcentral.ca` allows `Access-Control-Allow-Origin: *`. The frontend can be hosted anywhere and call the API directly — no proxy needed in production.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Vue 3** | UI framework (Composition API + `<script setup>`) |
| **Vite 7** | Dev server + build tool |
| **Axios** | HTTP client |
| **Capacitor 6** | Native iOS wrapper |

## Project Structure

```
frontend/
├── src/
│   ├── main.js           App entry point
│   ├── App.vue           Root component (renders HomePage)
│   ├── style.css         Base resets
│   ├── api/
│   │   └── client.js     31 API functions + auth helpers + pagination
│   ├── pages/
│   │   └── HomePage.vue  API demo page (all endpoints testable)
│   └── utils/            (empty — for shared utilities)
├── index.html            HTML shell
├── package.json          Dependencies (vue, axios, capacitor)
├── vite.config.js        Vite config (dev proxy to backend)
├── API.md                Complete API reference
└── tests/                Test files
```

## Build & Deploy

```bash
npm run build     # Creates dist/ — served by nginx in Docker
```

## iOS (Capacitor)

```bash
npm run build
npm run cap:sync
npx cap open ios
```

## Known Limitations

- **HTTP only** — needs Let's Encrypt / Cloudflare for HTTPS before public launch
- **CORS is wildcard** — should be restricted to specific origins for production
- **No rate limiting on auth** — consider adding client-side throttling on login/register
- See [ISSUES.md](../ISSUES.md) for the full backlog