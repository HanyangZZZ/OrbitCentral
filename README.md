# FBLC — Local Business Discovery Platform

A cross-platform app for discovering local businesses using AI-powered semantic search, built by **Abby & Hanyang**.

## What Is This?

FBLC helps users find local businesses using AI-powered **"vibe search"**. Instead of matching keywords, it understands meaning — searching "cozy place for coffee" finds relevant cafés even if they don't use those exact words.

**Key capabilities:**

- **Weighted vibe search** — `score = 0.70 × vibe_similarity + 0.15 × proximity + 0.15 × rating`
- **Smart auto-import** — first search in a new area automatically imports businesses from Google Places
- **AI classification** — GPT-4o-mini categorizes businesses and generates semantic tags
- **Tag consolidation** — AI-powered deduplication merges similar tags (e.g. "pet-friendly" + "dog-friendly" → one tag)
- **Vector tag search** — users can search tags by meaning, not just text matching
- **Hierarchical categories** — 22 seeded categories (5 parent + 17 subcategories)

## Architecture

```
Browser / iOS app
      │
      ▼
  Nginx :80  (virtual-host routing)
      │
      ├── orbitcentral.ca          →  Vue SPA (built into image) + /api/ proxy
      ├── admin.orbitcentral.ca    →  Adminer (DB portal)
      ├── flower.orbitcentral.ca   →  Flower (Celery dashboard)
      └── unknown Host             →  444 (connection drop)
      │
      ▼
  Django/Gunicorn :8000
      │
      ├── REST API (DRF)
      ├── AI classification & tagging (GPT-4o-mini)
      └── Vector embeddings (text-embedding-3-small)
      │                              │
      │                  task.delay() │
      ▼                              ▼
  PostgreSQL :5432            Redis :6379 ──► Celery Worker
      ├── pgvector                              ├── Google Places auto-import
      ├── PostGIS                               ├── AI classification
      └── pg_trgm                               └── Retries (3×, crash-safe)
```

## Project Structure

```
FBLC/
├── backend/                 Django REST API                → see backend/README.md
├── frontend/                Vue 3 + Capacitor app          → see frontend/README.md
├── postgres/                Custom PostgreSQL image (pgvector + PostGIS)
├── nginx/                   Reverse proxy + frontend build (Dockerfile)
├── docker-compose.yml       7 containers: postgres, redis, django, celery, nginx, adminer, flower
├── Makefile                 Shortcut commands (run make help)
├── DEPLOYMENT.md            Server deployment guide
└── .env.production.example  Template for secrets / API keys
```

## Quick Start

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.

```bash
# 1. Copy the environment template and fill in your values
cp .env.production.example .env
# → Set OPENAI_API_KEY, GOOGLE_PLACES_API_KEY, PG_PASSWORD, DJANGO_SECRET_KEY

# 2. Build and start everything
make build && make up

# 3. Verify it's working
make status
curl http://localhost/api/categories/

# 4. Try a search (auto-imports businesses on first search in an area)
curl "http://localhost/api/businesses/search/?q=cozy+coffee&lat=43.6532&lng=-79.3832"
```

**Access points:**

| Service | URL |
|---------|-----|
| Frontend | `http://orbitcentral.ca` (prod) · `http://localhost:5173` (dev) |
| API | `http://orbitcentral.ca/api/` (prod) · `http://localhost/api/` (dev) |
| Admin panel | `http://orbitcentral.ca/admin/` |
| Adminer (DB portal) | `http://admin.orbitcentral.ca` |
| Flower (task monitor) | `http://flower.orbitcentral.ca` |
| Health check | `http://orbitcentral.ca/health` |

## Useful Commands

Run `make help` to see all available commands.

| Command | What It Does |
|---------|-------------|
| `make build` | Build all Docker images |
| `make up` / `make down` | Start / stop all containers |
| `make restart` | Restart all services |
| `make logs` | Stream live logs from all services |
| `make logs-django` | Django logs only |
| `make logs-celery` | Celery worker logs only |
| `make migrate` | Apply database migrations |
| `make createsuperuser` | Create an admin login |
| `make db-shell` | Open a PostgreSQL terminal |
| `make django-shell` | Open a Django Python shell |
| `make backup` | Save a database backup to `backups/` |
| `make embed` | Generate AI embeddings for businesses without one |
| `make embed-all` | Regenerate ALL embeddings |
| `make clean` | Remove all containers, volumes, and images |

## Environment Variables

Key variables in `.env` (see `.env.production.example` for the full list):

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings + AI classification |
| `GOOGLE_PLACES_API_KEY` | Yes | Google Places API key for auto-import |
| `PG_PASSWORD` | Yes | PostgreSQL password |
| `DJANGO_SECRET_KEY` | Yes | Django secret key for security |
| `ALLOWED_HOSTS` | Prod | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | Prod | Allowed frontend origins |

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Vue 3, Vite, Vue Router | Web UI |
| Mobile | Capacitor 6 | iOS native wrapper |
| Backend | Django 5, Django REST Framework | REST API + business logic |
| Task Queue | Celery 5, Redis 7 | Background task processing (imports, AI) |
| Monitoring | Flower | Celery task dashboard (port 5555) |
| Database | PostgreSQL 16 | Data storage |
| Vector Search | pgvector + OpenAI `text-embedding-3-small` | 1536-dim semantic search |
| Geography | PostGIS (GeoDjango) | Location/distance queries |
| AI | GPT-4o-mini | Business classification + tag generation/consolidation |
| Auto-import | Google Places API (New) | Bulk business discovery |
| Proxy | Nginx 1.27 | Reverse proxy, rate limiting, static files |
| DB Portal | Adminer | Web-based database management |
| Deployment | Docker Compose | 7 containers orchestrated |

## Documentation

| Doc | Covers |
|-----|--------|
| **[backend/README.md](backend/README.md)** | API endpoints, models, services, management commands |
| **[frontend/README.md](frontend/README.md)** | Vue app, API client reference, Capacitor (iOS) |
| **[frontend/API.md](frontend/API.md)** | Complete API reference with examples |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Server setup, deployment steps, HTTPS, backups |

---

*Built by Abby & Hanyang · 2025–2026*