# FBLC Frontend — Vue 3 + Capacitor

The frontend is a Vue 3 single-page app that demonstrates all backend APIs. It also runs natively on iOS using Capacitor.

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Vue 3** | UI framework (Composition API + `<script setup>`) |
| **Vite** | Dev server + build tool (HMR) |
| **Vue Router** | Client-side routing |
| **Axios** | HTTP client for API calls |
| **Capacitor 6** | Native iOS wrapper |

## Project Structure

```
frontend/
├── src/
│   ├── main.js           App entry point
│   ├── App.vue           Root component with nav bar + <router-view>
│   ├── router.js         Routes: / → HomePage
│   ├── style.css         Global styles
│   ├── api/
│   │   └── client.js     All API functions (see API.md for full reference)
│   └── pages/
│       └── HomePage.vue  Demo page — stats, search, tags, categories, businesses
├── index.html            HTML shell
├── package.json          Dependencies
├── vite.config.js        Vite config (dev proxy to backend)
├── vitest.config.js      Test config
├── capacitor.config.json Capacitor settings
├── API.md                Complete API reference with examples
├── ios/                  Generated iOS project (Xcode)
└── tests/                Test files
```

## Running Locally

```bash
# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app runs at **http://localhost:5173**. API calls are proxied to the backend.

### Connecting to the Backend

Vite proxies `/api` to the backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': { target: 'http://localhost:80', changeOrigin: true }
  }
}
```

To point at a different backend, set `VITE_API_BASE_URL` in `.env.development`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Base URL for all API calls |

> Variables **must** start with `VITE_` for Vite to expose them to the app.

## API Client

All API calls live in `src/api/client.js`. See **[API.md](API.md)** for the complete reference.

Quick overview:

| Function | Endpoint | Description |
|----------|----------|-------------|
| `getCategories()` | `GET /categories/` | List categories |
| `getTags(params)` | `GET /tags/` | List/filter tags by text |
| `searchTags(params)` | `GET /tags/search/` | **Vector semantic** tag search |
| `getBusinesses()` | `GET /businesses/` | List businesses (paginated) |
| `searchBusinesses(params)` | `GET /businesses/search/` | Weighted vibe search |
| `getStats()` | `GET /businesses/stats/` | Database statistics |

## Building for Production

```bash
npm run build
```

Creates `dist/` with optimized static files.

## Running Tests

```bash
npm run test
```

Uses [Vitest](https://vitest.dev/).

## iOS (Capacitor)

```bash
# Build web assets first
npm run build

# Sync to iOS project
npm run cap:sync

# Open in Xcode
npx cap open ios
```

Capacitor config:
```json
{
  "appId": "com.fblc.app",
  "appName": "FBLC",
  "webDir": "dist"
}
```