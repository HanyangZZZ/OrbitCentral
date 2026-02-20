# Orbit — User Frontend

The user-facing Vue 3 single-page application for discovering local businesses. Deployed to **https://orbitcentral.ca**.

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Vue 3 | 3.5.x | Reactive UI framework (Composition API + `<script setup>`) |
| Vite | 7.x | Dev server & production bundler |
| Vue Router | 4.x | Client-side routing with auth guards |
| Axios | 1.x | HTTP client for API calls |
| Capacitor | 6.x | iOS native wrapper (optional) |

## Features

| Feature | Description |
|---------|-------------|
| **Vibe Search** | Semantic search ("cozy coffee") powered by AI embeddings |
| **Reverse Geocoding** | Auto-detects user city from GPS coordinates |
| **AI Review Writing** | Chat-based review assistant generates reviews from conversation |
| **Photo Upload** | Drag-and-drop image upload on reviews (base64 → GCS) |
| **Bookmarks** | Save businesses for later |
| **AI Summary** | AI-generated personalized descriptions on business pages |
| **Cookie Consent** | GDPR-style banner; declining prevents localStorage token persistence |
| **reCAPTCHA v3** | Invisible bot protection on login/register (score-based) |
| **Email Verification** | Verify email via token link after registration |
| **Password Reset** | Forgot password flow with email token |

## Project Structure

```
frontend-user/
├── index.html                    Entry HTML
├── vite.config.js                Vite config (proxy /api → backend)
├── capacitor.config.json         iOS native config
├── src/
│   ├── App.vue                   Root component (router-view + CookieConsent)
│   ├── main.js                   App bootstrap
│   ├── router.js                 Routes + auth navigation guards
│   ├── style.css                 Global styles
│   ├── api/                      API layer
│   │   ├── core.js               Axios instance, token management, consent-aware persistence
│   │   ├── client.js             Re-exports all API functions
│   │   ├── auth.js               Login, register, profile, password reset
│   │   ├── businesses.js         Search, nearby, detail, categories
│   │   ├── reviews.js            CRUD reviews, votes
│   │   ├── aiReviews.js          AI review chat sessions
│   │   ├── bookmarks.js          Bookmark CRUD
│   │   └── taxonomy.js           Categories & tags
│   ├── composables/              Reusable logic (Vue composables)
│   │   ├── useAuth.js            Singleton auth state (user, isLoggedIn, refresh)
│   │   ├── useCaptcha.js         reCAPTCHA v3 (lazy load, action-based execute)
│   │   ├── useSearchApi.js       Search API integration
│   │   ├── useSearchState.js     Search query/filter state management
│   │   ├── useFilterBar.js       Category & distance filter logic
│   │   ├── useUserLocation.js    GPS geolocation
│   │   ├── useBusinessDetail.js  Business detail page data fetching
│   │   ├── useNearbyForYou.js    "Nearby for you" recommendations
│   │   └── useAiSummary.js       AI business summary fetching
│   ├── components/
│   │   ├── AppHeader.vue         Top navigation bar
│   │   ├── BusinessCard.vue      Business list item card
│   │   ├── CategorySidebar.vue   Category navigation sidebar
│   │   ├── CookieConsent.vue     Cookie consent banner + hasCookieConsent() export
│   │   ├── FilterBar.vue         Search filters (category, distance, sort)
│   │   ├── NearbyForYou.vue      Nearby businesses carousel
│   │   ├── AiSummary.vue         AI-generated business summary
│   │   ├── PhotoGallery.vue      Business photo gallery
│   │   ├── business/
│   │   │   ├── BusinessHero.vue       Business header/hero section
│   │   │   ├── ContactBar.vue         Phone, website, directions
│   │   │   ├── ReviewsSection.vue     Reviews list with pagination
│   │   │   ├── ReviewCard.vue         Single review display (with photo)
│   │   │   ├── WriteReviewModal.vue   AI-assisted review writing + photo upload
│   │   │   ├── ActivitiesModal.vue    Business activities/events
│   │   │   └── CouponsModal.vue       Business coupons
│   │   ├── home/
│   │   │   ├── HeroSearch.vue         Homepage search bar
│   │   │   └── CategoryGrid.vue       Category browsing grid
│   │   ├── icons/
│   │   │   └── BaseIcon.vue           SVG icon wrapper
│   │   └── ui/
│   │       ├── BaseModal.vue          Reusable modal wrapper
│   │       ├── StarRating.vue         Star rating display
│   │       └── TemplateNotice.vue     Placeholder notice
│   └── pages/
│       ├── HomePage.vue               Landing page (search + categories + nearby)
│       ├── SearchPage.vue             Search results with filters
│       ├── BusinessDetailPage.vue     Full business page (info, reviews, photos)
│       ├── LoginPage.vue              Login with reCAPTCHA v3
│       ├── RegisterPage.vue           Registration with reCAPTCHA v3
│       ├── ProfilePage.vue            User profile management
│       ├── BookmarksPage.vue          Saved businesses
│       ├── VerifyEmailPage.vue        Email verification handler
│       ├── ResetPasswordPage.vue      Password reset form
│       ├── AboutPage.vue              About page
│       ├── MissionsPage.vue           Gamification missions
│       ├── CouponsPage.vue            User coupons
│       └── IconLibraryPage.vue        Icon reference page
└── ios/                               Capacitor iOS project
```

## Development

```bash
# Install dependencies
npm install

# Start dev server (proxies /api to backend at localhost:8000)
npm run dev

# Build for production
npm run build
```

## Authentication Flow

1. User clicks **Log In** → reCAPTCHA v3 runs invisibly → token sent to backend
2. Backend verifies captcha score ≥ 0.5 → returns auth token + user data
3. If cookie consent was accepted: token saved to `localStorage` → survives refresh
4. If cookie consent was declined: token stays in memory only → lost on refresh
5. On page load: `useAuth().refresh()` checks `localStorage` → calls `/api/auth/me/` → restores session

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |
| `VITE_RECAPTCHA_SITE_KEY` | (hardcoded fallback) | Google reCAPTCHA v3 site key |

## Build & Deploy

The user frontend is built inside the **nginx Docker image** (3-stage build):

1. **Stage 1** — `frontend-user/` → `npm ci && npm run build` → `/app/frontend/`
2. **Stage 2** — `frontend-demo/` → `npm ci && npm run build` → `/app/frontend-demo/`
3. **Stage 3** — Nginx serves both SPAs via virtual-host routing

No separate deployment step needed — just rebuild nginx:
```bash
sudo docker compose up -d --build nginx
```

---

*Built by Abby & Hanyang · 2025–2026*
