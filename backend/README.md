# FBLC Backend — Django REST API

The backend provides a REST API for local business discovery with AI-powered semantic search, auto-import from Google Places, and intelligent tagging.

## Architecture

```
Request → Nginx :80 → Gunicorn/Django :8000 → PostgreSQL :5432
                                  │
                                  ├── OpenAI API (embeddings + classification)
                                  └── task.delay() → Redis :6379 → Celery Worker
                                                          │
                                                          ├── Google Places auto-import
                                                          ├── AI classification + tagging
                                                          └── Retries (3×, crash-safe)
```

## Files at a Glance

| File | Purpose |
|------|---------|
| `manage.py` | Django CLI tool |
| `Dockerfile` | Production image (Python 3.12, multi-stage, non-root) |
| `docker-entrypoint.sh` | Startup: wait for DB → migrate → seed categories → Gunicorn |
| `requirements.txt` | Python dependencies |

### `api/` — Main Application

| File | Purpose |
|------|---------|
| `models/business.py` | Category, Tag, SearchedArea, Business models |
| `models/user.py` | UserProfile, EmailVerificationToken, PasswordResetToken |
| `serializers/` | DRF serializers (auth, business, review, bookmark) |
| `viewsets/` | API logic — Auth, Business, Review, Bookmark, Category, Tag, AIReview |
| `services/` | Google Places import, AI classification, captcha, geocoding, personalization |
| `tasks/` | Celery tasks — email sending, auto-import |
| `urls.py` | URL routing (DRF router) |
| `pagination.py` | Page-based + cursor pagination |
| `permissions.py` | IsEmailVerified, IsOwnerOrReadOnly |
| `authentication.py` | ExpiringTokenAuthentication (72h TTL) + HttpOnly cookie |
| `exceptions.py` | Consistent error response formatting |
| `admin.py` | Django admin panel registration |

### `api/management/commands/`

| Command | Purpose |
|---------|---------|
| `seed_categories` | Seeds 22 categories (5 parent + 17 sub), idempotent |
| `generate_embeddings` | Generates OpenAI embeddings for businesses |
| `import_places` | Manual Google Places import for a location |
| `import_small_businesses` | Bulk import with AI classification |

### `server/settings/`

| File | Used When |
|------|-----------|
| `base.py` | Shared settings (database, apps, logging, Celery) |
| `development.py` | Local dev — DEBUG on, relaxed security |
| `production.py` | Production — DEBUG off, strict security |

---

## Database Models

### Category

Hierarchical business categories (5 parent + 17 subcategories seeded on startup).

| Field | Type | Notes |
|-------|------|-------|
| `name` | varchar(50) | Unique |
| `slug` | slug(50) | Unique, URL-friendly |
| `icon_name` | varchar(50) | Optional icon identifier |
| `parent` | FK → Category | Self-referential for hierarchy |
| `updated_at` | timestamp | Auto-updated |

### Tag

AI-generated semantic tags with vector embeddings for deduplication.

| Field | Type | Notes |
|-------|------|-------|
| `name` | varchar(100) | Unique, e.g. "pet-friendly", "cozy" |
| `embedding` | vector(1536) | OpenAI embedding for semantic search |
| `created_at` | timestamp | Auto |

HNSW index on `embedding` for fast cosine similarity search.

### Business

| Field | Type | Notes |
|-------|------|-------|
| `name` | varchar(255) | Business name |
| `description` | text | AI-generated or manual |
| `category` | FK → Category | Nullable |
| `tags` | M2M → Tag | AI-generated semantic tags |
| `address` | text | Street address |
| `phone` | varchar(30) | Phone number |
| `website_url` | URL(2000) | Website |
| `contact_email` | email | Contact info |
| `google_place_id` | varchar(255) | Unique Google Maps ID |
| `google_types` | JSON | Google Places type array |
| `price_level` | int | 0=Free → 4=Very Expensive |
| `photo_references` | JSON | Google Places photo references |
| `business_status` | varchar(30) | e.g. OPERATIONAL, CLOSED_TEMPORARILY |
| `location` | geography(Point) | PostGIS lat/lng |
| `embedding` | vector(1536) | OpenAI embedding for search |
| `onboarding_status` | choice | `discovered`, `contacted`, `active` |
| `avg_rating` | decimal(3,2) | Average rating (0–5) |
| `review_count` | int | Number of reviews |
| `user_rating_count` | int | Google rating count |
| `metadata` | JSON | Flexible extra data |
| `created_at` / `updated_at` | timestamps | Auto-managed |

### SearchedArea

Tracks areas already imported from Google Places to avoid duplicate imports.

| Field | Type | Notes |
|-------|------|-------|
| `center` | geography(Point) | Center of searched circle |
| `radius_km` | float | Search radius (default 5 km) |
| `business_count` | int | How many businesses were found |
| `searched_at` | timestamp | When the import happened |

---

## API Endpoints

### Tags

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/tags/` | List tags (paginated) |
| `GET` | `/api/tags/{id}/` | Get a single tag |
| `GET` | `/api/tags/search/?q=...` | **Vector semantic search** for tags |

**List parameters:**

| Param | Description |
|-------|-------------|
| `q` | Text filter (case-insensitive substring match) |
| `min_usage` | Only tags used by ≥ N businesses |

**Vector search parameters (`/api/tags/search/`):**

| Param | Description |
|-------|-------------|
| `q` | Natural language query (required) — embedded and compared by cosine similarity |
| `limit` | Max results (default 20, max 50) |
| `min_usage` | Only tags used by ≥ N businesses |

Response includes `similarity` score (0–1). Falls back to text search if embedding fails.

```bash
# Find tags related to "outdoor dining" by meaning
curl "http://localhost/api/tags/search/?q=outdoor+dining&limit=5"

# Response:
# [
#   {"id": 98, "name": "outdoor-seating", "usage_count": 70, "similarity": 0.7924},
#   {"id": 236, "name": "outdoor-living", "usage_count": 9, "similarity": 0.6701},
#   {"id": 248, "name": "dine-in", "usage_count": 9, "similarity": 0.5975},
#   ...
# ]
```

### Categories

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/categories/` | List all categories |
| `POST` | `/api/categories/` | Create a category |
| `GET` | `/api/categories/{id}/` | Get one category |
| `PUT/PATCH` | `/api/categories/{id}/` | Update a category |
| `DELETE` | `/api/categories/{id}/` | Delete a category |

### Businesses

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/businesses/` | List businesses (paginated) |
| `POST` | `/api/businesses/` | Create a business |
| `GET` | `/api/businesses/{id}/` | Get one business |
| `PUT/PATCH` | `/api/businesses/{id}/` | Update a business |
| `DELETE` | `/api/businesses/{id}/` | Delete a business |

**Filters:** `?category=1`, `?onboarding_status=active`
**Search:** `?search=cafe` (name, email, Google Place ID)
**Ordering:** `?ordering=-avg_rating` (options: `avg_rating`, `review_count`, `name`, `created_at`)
**Pagination:** `?page=2&page_size=10` (default 50/page, max 100)

### Weighted Vibe Search

```
GET /api/businesses/search/?q=cozy+coffee&lat=43.6532&lng=-79.3832
```

| Param | Required | Description |
|-------|----------|-------------|
| `q` | Yes | Natural language query |
| `lat`, `lng` | No | User location (enables proximity scoring + auto-import) |
| `category` | No | Category ID filter |
| `tag` | No | Tag ID(s) — AND filter. `?tag=1&tag=2` or `?tag=1,2` |
| `sort` | No | `distance` or `rating` (default: weighted) |
| `limit` | No | Max results 1–50 (default 10) |

**Scoring formula (default weighted mode):**

```
score = 0.70 × vibe_similarity
      + 0.15 × proximity_score     (1 / (1 + distance_km / 5.0))
      + 0.15 × rating_score        (avg_rating / 5.0)
```

**Auto-import:** When `lat`/`lng` is provided and the area hasn't been searched before, a Celery task is dispatched to import businesses from Google Places, classify them with GPT-4o-mini, generate tags, and create embeddings. The task runs in a separate worker process with automatic retries (3×, 30s delay) and crash recovery.

### Stats

```
GET /api/businesses/stats/
```

Returns: `total_businesses`, `with_embeddings`, `with_tags`, `tag_count`, `searched_areas`, `avg_rating`, `top_tags` (top 15 by usage).

### Authentication

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `POST` | `/api/auth/register/` | Public | Create account (+ reCAPTCHA v3) |
| `POST` | `/api/auth/login/` | Public | Log in (+ reCAPTCHA v3) → returns token |
| `POST` | `/api/auth/logout/` | Token | Delete token + clear cookie |
| `GET` | `/api/auth/me/` | Token | Get current user profile |
| `PATCH` | `/api/auth/me/` | Token | Update profile |
| `DELETE` | `/api/auth/me/` | Token | Delete account (requires password confirmation) |
| `POST` | `/api/auth/verify-email/` | Public | Verify email with token |
| `POST` | `/api/auth/resend-verify/` | Token | Resend verification email |
| `POST` | `/api/auth/forgot-password/` | Public | Request reset email (+ reCAPTCHA) |
| `POST` | `/api/auth/reset-password/` | Public | Reset password with token |

Token auth: `Authorization: Token <key>` header. Tokens expire after 72 hours.

### Reviews

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET` | `/api/reviews/?business=<id>` | Public | List reviews for a business |
| `POST` | `/api/reviews/` | Verified | Create review (optional base64 photo) |
| `PATCH` | `/api/reviews/{id}/` | Owner | Update review |
| `DELETE` | `/api/reviews/{id}/` | Owner | Delete review |
| `POST` | `/api/reviews/{id}/vote/` | Verified | Toggle vote (useful/funny/cool) |

### Bookmarks

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET` | `/api/bookmarks/` | Verified | List user's bookmarks |
| `POST` | `/api/bookmarks/toggle/` | Verified | Toggle bookmark on/off |
| `GET` | `/api/bookmarks/check/?business=<id>` | Verified | Check if bookmarked |
| `GET` | `/api/bookmarks/ids/` | Verified | List bookmarked business IDs |

### AI Reviews

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `POST` | `/api/ai-reviews/` | Verified | Start AI review session |
| `POST` | `/api/ai-reviews/{id}/message/` | Verified | Send message in review chat |
| `POST` | `/api/ai-reviews/{id}/confirm/` | Verified | Confirm and post the AI-generated review |

---

## AI Pipeline

When a new area is searched, the following pipeline runs as a Celery task:

1. **Google Places fetch** — 20 search types, 8 concurrent workers, grid-based coverage
2. **AI classification** — GPT-4o-mini assigns categories and generates semantic tags (batches of 10, 20 workers)
3. **Tag resolution** — normalize names, check blocklist (~90 words), create/reuse tags
4. **Tag consolidation** — GPT-4o-mini merges similar tags in batches of ~100 with cross-batch reference
5. **Embedding generation** — OpenAI `text-embedding-3-small` for businesses and tags (batches of 100, 4 workers)

**Tag consolidation details:**
- Processes candidates in batches for bounded context
- Each batch's canonical tags become reference for the next batch
- Post-processing: blocklist filter, plural normalization, forbidden canonicals check
- Typical result: ~64% merge rate (e.g. 870 candidates → 340 final tags)

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `DJANGO_SETTINGS_MODULE` | `server.settings.development` or `server.settings.production` |
| `DJANGO_SECRET_KEY` | Security key (required in production) |
| `PG_DATABASE`, `PG_USER`, `PG_PASSWORD` | Database credentials |
| `DATABASE_URL` | Alternative single connection string (overrides PG_* vars) |
| `ALLOWED_HOSTS` | Allowed domains |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `OPENAI_API_KEY` | For embeddings + AI classification |
| `GOOGLE_PLACES_API_KEY` | For auto-import |
| `GUNICORN_WORKERS` | Worker processes (default 3) |
| `GUNICORN_THREADS` | Threads per worker (default 2) |
| `CELERY_BROKER_URL` | Redis URL for Celery broker (default `redis://redis:6379/0`) |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results (default `redis://redis:6379/1`) |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **pgvector** HNSW indexes | Vector similarity search inside PostgreSQL — no separate service needed |
| **PostGIS** geography | Industry-standard spatial DB for distance queries |
| **Celery background tasks** | Non-blocking search via Redis + Celery with retries and crash recovery |
| **Per-area locking** | Prevents duplicate imports for the same location |
| **Batched AI consolidation** | Bounded context prevents token overflow, cross-batch references ensure consistency |
| **GPT-4o-mini** for classification | Fast, cheap, good enough for categorization / tag generation |
| **text-embedding-3-small** | Good quality at low cost ($0.02/M tokens) |
| **Multi-stage Docker build** | ~200 MB production image without build tools |
| **Non-root container user** | Django runs as `django` user for security |