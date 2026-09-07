# Orbit — Business Discovery System: Technical Deep-Dive

> **Scope:** This document covers the backend systems for **discovering, importing, classifying, tagging, searching, filtering, and sorting businesses**. Review, bookmark, and authentication systems are out of scope.

---

## Table of Contents

1. [The Blueprint (Design & Logic)](#1-the-blueprint-design--logic)
2. [The Toolbox (Tech Stack)](#2-the-toolbox-tech-stack)
3. [The Safeguards (Quality & Growth)](#3-the-safeguards-quality--growth)
4. [The Process (Workflow & Launch)](#4-the-process-workflow--launch)

---

# 1. The Blueprint (Design & Logic)

## 1.1 Logic Overview & Data Flow

### The Core Question

> *"A user opens the app near downtown Montreal and types 'cozy coffee shop with wifi'. What happens?"*

The answer involves an **8-step pipeline** that spans 6 service modules, 3 external APIs, and 2 database extensions.

### Master Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                                     │
│         GET /api/businesses/search/?q=cozy+coffee&lat=45.5&lng=-73.6   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │     BusinessViewSet          │
              │     .vector_search()         │
              └──────┬───────────┬───────────┘
                     │           │
          ┌──────────┘           └──────────────┐
          ▼                                      ▼
  ┌───────────────────┐               ┌─────────────────────────────┐
  │ BACKGROUND (async) │               │ FOREGROUND (sync, ~200ms)   │
  │ Celery Worker      │               │ Django Request Thread        │
  │                    │               │                              │
  │ ensure_area_       │               │ 1. Generate query embedding  │
  │ covered_task()     │               │    (OpenAI text-embed-3)     │
  │                    │               │                              │
  │ Steps 1→8:        │               │ 2. pgvector cosine search    │
  │ Google → AI →     │               │    + category/tag filters    │
  │ Tags → DB →       │               │                              │
  │ Images → Embed    │               │ 3. Annotate distance (PostGIS)│
  │                    │               │                              │
  │ (runs if area     │               │ 4. Weighted scoring:         │
  │  not yet covered)  │               │    70% vibe + 15% proximity  │
  └────────────────────┘               │    + 15% rating              │
                                       │                              │
                                       │ 5. Return top-N results      │
                                       └──────────────┬───────────────┘
                                                      │
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │   JSON Response               │
                                       │   {results, similarity,       │
                                       │    distance_km, score}        │
                                       └──────────────────────────────┘
```

### The Auto-Import Pipeline (Background)

When a user searches from a **new location**, a Celery background task triggers the full import pipeline. This is the most complex data flow in the system:

```
Step 1: Google Places API ──────────────────────────────────────────────────
   │  Grid search: 5km radius, 2.5km spacing → ~13 grid points
   │  × 16 business types = ~208 API calls
   │  Concurrency: 8 ThreadPoolExecutor workers
   │  Deduplication: in-memory set of Google Place IDs
   │  Output: ~200–400 raw place dicts
   ▼
Step 2: Filter Existing ────────────────────────────────────────────────────
   │  SELECT google_place_id FROM businesses WHERE google_place_id IN (...)
   │  Remove already-imported places
   │  Cap at MAX_BUSINESSES_PER_IMPORT (100)
   ▼
Step 3: AI Classification (GPT-4o-mini) ───────────────────────────────────
   │  Batch size: 10 places per API call
   │  Concurrency: 20 ThreadPoolExecutor workers
   │  For each business, AI returns:
   │    • is_small: boolean (chain detection)
   │    • category: exact subcategory name from DB
   │    • tags: 3–5 descriptive tags
   │  Temperature: 0.2 (deterministic)
   ▼
Step 4: Chain Filter ──────────────────────────────────────────────────────
   │  Keep only is_small=true businesses
   │  Drops: McDonald's, Starbucks, Walmart, Tim Hortons, etc.
   ▼
Step 5: Tag Resolution (GPT-4o-mini + OpenAI Embeddings) ─────────────────
   │  5a. Normalize: lowercase, strip suffixes (-atmosphere, -vibes, etc.)
   │  5b. Blocklist: remove 100+ banned quality/generic words
   │  5c. AI Consolidation: merge synonyms via GPT-4o-mini
   │      ("comfy"→"cozy", "hip"→"trendy", "eatery"→"restaurant")
   │  5d. get_or_create Tag objects in DB
   │  5e. Generate 1536-dim embeddings for new tags
   │  Output: {original_name → Tag model} mapping
   ▼
Step 6: Bulk Create Businesses ────────────────────────────────────────────
   │  Business.objects.bulk_create(batch_size=100, ignore_conflicts=True)
   │  Category resolution: exact match → slug match → keyword fallback
   │  M2M tag assignment via ThroughModel.objects.bulk_create()
   ▼
Step 6.5: Image Pipeline ─────────────────────────────────────────────────
   │  For each business with photo_references:
   │    • GET Google Places Photo API → resolve redirect → download bytes
   │    • Upload to GCS bucket (orbit-media-prod)
   │    • Update Business.image_url to public GCS URL
   │  Concurrency: 8 workers
   ▼
Step 7: Embedding Generation (OpenAI text-embedding-3-small) ─────────────
   │  Text formula per business:
   │    "{name}. Category: {parent} > {child}. {description} Tags: {tags}. Located at {address}"
   │  Batch size: 100, Concurrency: 4 workers
   │  Stored in: Business.embedding (1536-dim VectorField)
   ▼
Step 8: Mark Area Covered ─────────────────────────────────────────────────
      SearchedArea.objects.create(center=Point, radius_km=5.0)
      (Only recorded AFTER full success — crash = retry from scratch)
```

### Search Scoring Formula

The weighted search uses three signals combined into a single score:

$$\text{score} = 0.70 \times V + 0.15 \times P + 0.15 \times R$$

| Signal | Symbol | Calculation | Range |
|--------|--------|-------------|-------|
| **Vibe** (semantic relevance) | $V$ | $1 - \text{cosine\_distance}(\vec{q}, \vec{b})$ | 0.0 – 1.0 |
| **Proximity** | $P$ | $\dfrac{1}{1 + d_{km} / 5.0}$ | 0.0 – 1.0 |
| **Rating** | $R$ | $\dfrac{\text{avg\_rating}}{5.0}$ | 0.0 – 1.0 |

Where:
- $\vec{q}$ = query embedding (1536-dim), $\vec{b}$ = business embedding (1536-dim)
- $d_{km}$ = geodesic distance from user to business (PostGIS `ST_Distance`)
- `avg_rating` = Bayesian weighted average blending Google and user ratings

**Proximity decay curve:**

```
Score │ 1.0 ─·
      │       ·
      │        ·
      │          ·
  0.5 │────────────·─────────── at 5km
      │              ·
      │                ·
      │                   ·
  0.0 │─────────────────────·── distance (km)
      0    5    10   15   20
```

### Bayesian Rating Formula

Businesses start with Google's established rating as a prior, and user reviews gradually take over:

$$W = \frac{v \cdot R + m \cdot C}{v + m}$$

| Variable | Meaning | Source |
|----------|---------|--------|
| $v$ | # of user reviews | `Review.count` |
| $R$ | Average user rating | `Review.avg(rating)` |
| $m$ | Confidence threshold | `10` (constant) |
| $C$ | Google rating (prior) | `google_rating` (immutable) |

| $v$ (user reviews) | Weight on user scores | Weight on Google |
|--------------------:|----------------------:|-----------------:|
| 0 | 0% | 100% |
| 5 | 33% | 67% |
| 10 | 50% | 50% |
| 50 | 83% | 17% |
| 100 | 91% | 9% |

Updated automatically via Django signals on every Review save/delete.

---

## 1.2 Modularity & Modular Design

The business system is decomposed into **7 independent service modules** connected through a single orchestrator:

```
┌──────────────────────────────────────────────────────────────────────┐
│                      import_pipeline.py                              │
│                   (Orchestrator — the ONLY file that                  │
│                    imports from other service modules)                │
│                                                                      │
│   ensure_area_covered(lat, lng)                                      │
│     ├── google_places._fetch_google_places()                         │
│     ├── classification._ai_classify_and_tag()                        │
│     ├── tags._resolve_tags()                                         │
│     ├── businesses._create_businesses()                              │
│     ├── images._download_and_store_images()                          │
│     └── embeddings._generate_embeddings()                            │
└──────────────────────────────────────────────────────────────────────┘
```

### Module Dependency Graph

```
                    ┌─────────────┐
                    │ import_     │
                    │ pipeline.py │
                    └──────┬──────┘
          ┌────────┬───────┼───────┬──────────┬───────────┐
          ▼        ▼       ▼       ▼          ▼           ▼
     google_   classifi- tags.py  busi-    images.py  embed-
     places.py cation.py          nesses.py            dings.py
                  │         │                  │
                  ▼         ▼                  ▼
              OpenAI    OpenAI             gcs.py
              Client    Client           (GCS upload)
```

**Key design decisions:**
- Each module has a **single public function** prefixed with `_` (private by convention, only called by the orchestrator)
- No circular imports — dependency arrows only point downward
- Each module can be tested independently by mocking its external dependency
- The orchestrator (`import_pipeline.py`) is the only file that knows the execution order

### Layer Separation

| Layer | Files | Responsibility |
|-------|-------|----------------|
| **URL Routing** | `urls.py` | Map URL patterns to ViewSets via `DefaultRouter` |
| **ViewSets** | `viewsets/businesses.py`, `categories.py`, `tags.py` | HTTP handling, permissions, request validation |
| **Serializers** | `serializers/business.py` | Data validation, transformation, JSON output shaping |
| **Models** | `models/business.py` | Schema, constraints, indexes, signals |
| **Services** | `services/*.py` | Business logic, external API calls, ML pipelines |
| **Tasks** | `tasks/import_task.py` | Async Celery wrappers with retry logic |

---

## 1.3 Clean Logic & Data Types

### Model Field Types — Why Each Was Chosen

| Field | Type | Why Not Alternatives |
|-------|------|---------------------|
| `location` | `PointField(geography=True)` | Geography (not geometry) uses meters on a sphere — accurate distance calc at any latitude. PostGIS handles the math. |
| `embedding` | `VectorField(dimensions=1536)` | pgvector's native type supports HNSW indexing for sub-10ms ANN search. Storing in DB (not a vector DB) keeps joins simple. |
| `tags` | `ManyToManyField(Tag)` | Tags are shared across businesses (not duplicated). M2M through-table enables `COUNT` aggregation per tag. |
| `google_types` | `JSONField` | Google returns a variable-length array of type strings. JSON is the natural fit — no need for a normalized table. |
| `price_level` | `IntegerField(0–4)` | Maps directly to Google's 5-level enum. Integer enables `ORDER BY` and range filters. |
| `avg_rating` | `DecimalField(3,2)` | Exact decimal (not float) prevents rounding drift in aggregations. 3 digits, 2 decimal (0.00–9.99). |
| `opening_hours` | `JSONField` | Google returns a nested object with `periods[]` and `weekdayDescriptions[]`. Storing raw preserves all structure for flexible frontend rendering. |

### Tag Normalization Pipeline

Raw AI output goes through a **5-stage cleanup** before becoming a Tag:

```
"Cozy-Atmosphere"
     │
     ▼  Stage 1: lowercase
"cozy-atmosphere"
     │
     ▼  Stage 2: strip suffixes (-atmosphere, -vibes, -style, etc.)
"cozy"
     │
     ▼  Stage 3: blocklist check (100+ banned words)
 ✅ PASS (not in blocklist)
     │
     ▼  Stage 4: AI consolidation (GPT-4o-mini)
     │  "comfy" → "cozy"  (merged as synonym)
     │  "hip" → "trendy"  (merged as synonym)
     │  "cozy" → "cozy"   (kept as-is, it's already canonical)
"cozy"
     │
     ▼  Stage 5: get_or_create Tag + generate 1536-dim embedding
Tag(id=42, name="cozy", embedding=[0.023, -0.118, ...])
```

### Category Resolution (4-Level Fallback)

When the AI returns a category name, resolution uses cascading precision:

```python
ai_response = "Coffee House"   # AI's category guess

# Level 1: Exact name match (case-insensitive)
cat_name_map.get("coffee house")         # → None ❌

# Level 2: Slug match
cat_name_map.get(slugify("coffee house")) # → "coffee-house" → None ❌

# Level 3: Keyword fallback (100+ mappings)
_KEYWORD_FALLBACK.get("coffee house")    # → "restaurants" → Category(id=5) ✅

# Level 4: Partial match (substring)
# Only tried if levels 1-3 all fail
```

---

# 2. The Toolbox (Tech Stack)

## 2.1 Data Storage Method & Structure

### Primary Database: PostgreSQL 16 + Extensions

| Extension | Purpose | Used By |
|-----------|---------|---------|
| **pgvector** | 1536-dim vector storage + HNSW ANN index | Business embeddings, Tag embeddings |
| **PostGIS** | Geography point storage + `ST_Distance` | Business locations, SearchedArea circles |
| **pg_trgm** | Trigram indexes for fuzzy text search | Name search, tag text search |

### Schema Overview (Business Domain Only)

```
┌──────────────────────────────────────────────────────────────────┐
│                         businesses                                │
├──────────────────────────────────────────────────────────────────┤
│ id              SERIAL PRIMARY KEY                                │
│ name            VARCHAR(255)                                      │
│ description     TEXT                                              │
│ address         TEXT                                              │
│ location        GEOGRAPHY(POINT, 4326)    ← PostGIS              │
│ embedding       VECTOR(1536)              ← pgvector             │
│ category_id     FK → categories           ← nullable             │
│ image_url       TEXT                      ← GCS public URL       │
│ google_place_id VARCHAR(255) UNIQUE                               │
│ avg_rating      DECIMAL(3,2)             ← Bayesian, auto-updated│
│ review_count    INTEGER                  ← signal-updated        │
│ google_rating   DECIMAL(3,2)             ← immutable after import│
│ price_level     INTEGER (0–4)                                     │
│ opening_hours   JSONB                                             │
│ ... (20+ Google Places attribute fields)                          │
│ created_at      TIMESTAMPTZ                                       │
│ updated_at      TIMESTAMPTZ                                       │
├──────────────────────────────────────────────────────────────────┤
│ INDEXES:                                                          │
│   idx_business_embedding  HNSW(embedding vector_cosine_ops)       │
│   idx_business_rating     BTREE(avg_rating)                       │
│   idx_business_google_pid UNIQUE(google_place_id)                 │
└──────────────────────────────────────────────────────────────────┘
         │                              │
         │ FK (category_id)             │ M2M (businesses_tags)
         ▼                              ▼
┌─────────────────────┐    ┌────────────────────────────┐
│     categories       │    │    businesses_tags          │
├─────────────────────┤    ├────────────────────────────┤
│ id    SERIAL PK      │    │ business_id  FK→businesses  │
│ name  VARCHAR(50)    │    │ tag_id       FK→tags        │
│ slug  VARCHAR(50)    │    │ UNIQUE(business_id, tag_id) │
│ parent_id FK→self    │    └────────────────────────────┘
│ icon_name VARCHAR    │                 │
└─────────────────────┘                 │
                                         ▼
                               ┌──────────────────────┐
                               │       tags            │
                               ├──────────────────────┤
                               │ id         SERIAL PK  │
                               │ name       VARCHAR(100)│
                               │ embedding  VECTOR(1536)│
                               │ created_at TIMESTAMPTZ │
                               ├──────────────────────┤
                               │ idx_tag_embedding HNSW│
                               └──────────────────────┘

┌──────────────────────────────────┐
│        searched_areas             │
├──────────────────────────────────┤
│ id           SERIAL PK           │
│ center       GEOGRAPHY(POINT)    │
│ radius_km    FLOAT (default 5.0) │
│ business_count INTEGER           │
│ searched_at  TIMESTAMPTZ         │
└──────────────────────────────────┘
```

### Category Hierarchy (Seeded, 22 Total)

```
Food & Drink
  ├── Restaurants
  └── Sweets

Retail
  ├── Apparel & Accessories
  ├── Gifts & Hobbies
  ├── Electronics
  └── Home

Personal Services
  ├── Beauty
  ├── Health
  ├── Pet Care
  └── Education

Home Services
  ├── Auto
  ├── Maintenance
  └── Cleaning

Entertainment
  ├── Arts
  ├── Recreation
  └── Entertainment
```

5 parent categories, 17 subcategories. Seeded via `manage.py seed_categories`.

---

## 2.2 API & Libraries Used

### REST API Endpoints (Business Domain)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/businesses/` | Public | Paginated list (page_size=50, max 100) |
| `GET` | `/api/businesses/:id/` | Public | Single business detail |
| `GET` | `/api/businesses/search/?q=&lat=&lng=` | Public | Weighted vector search |
| `GET` | `/api/businesses/stats/` | Public | Dashboard statistics |
| `GET` | `/api/businesses/:id/photo/?idx=0&maxHeight=400` | Public | Google photo proxy (302 redirect) |
| `POST` | `/api/businesses/` | Admin | Create business |
| `PATCH` | `/api/businesses/:id/` | Admin | Update business |
| `DELETE` | `/api/businesses/:id/` | Admin | Delete business |
| `GET` | `/api/categories/` | Public | List all 22 categories |
| `GET` | `/api/tags/` | Public | List tags with `?q=` and `?min_usage=` filters |
| `GET` | `/api/tags/search/?q=` | Public | Semantic vector tag search |

### Search Query Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `q` | string | *required* | Natural language search query |
| `lat` | float | – | User latitude (enables proximity scoring) |
| `lng` | float | – | User longitude |
| `category` | int | – | Filter by category ID |
| `tag` | int[] | – | Filter by tag ID(s) — AND logic |
| `sort` | string | `weighted` | Override: `"distance"` or `"rating"` |
| `limit` | int | 10 | Max results (1–50) |

### External APIs

| API | Purpose | Model/Tier | Concurrency |
|-----|---------|------------|-------------|
| **Google Places API v1** | Discover businesses by location + type | `searchNearby` | 8 workers |
| **Google Places Photo API** | Download business photos | `places/{ref}/media` | 8 workers |
| **OpenAI Embeddings** | Generate 1536-dim vectors for search | `text-embedding-3-small` | 4 workers |
| **OpenAI Chat** | Classify businesses + generate/consolidate tags | `gpt-4o-mini` | 20 workers |
| **Google Cloud Storage** | Store business + review images | `orbit-media-prod` bucket | 8 workers |

### Key Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Django | 5.x | Web framework |
| Django REST Framework | 3.x | API serialization, viewsets, permissions |
| psycopg2 | – | PostgreSQL adapter |
| pgvector-django | – | VectorField + CosineDistance + HnswIndex |
| django.contrib.gis | – | PostGIS integration (PointField, Distance) |
| celery | 5.6 | Async task queue (import pipeline) |
| redis | – | Celery broker + result backend |
| openai | – | Embeddings + GPT-4o-mini |
| google-cloud-storage | – | GCS bucket operations |
| gunicorn (gthread) | – | WSGI server (3 workers) |

---

## 2.3 Tools Used

| Tool | Purpose |
|------|---------|
| **Docker Compose** | 7-container orchestration (postgres, redis, django, celery, flower, nginx, adminer) |
| **Nginx** | Reverse proxy, virtual hosts, rate limiting, SPA serving |
| **Flower** | Celery task monitoring dashboard |
| **Adminer** | Database web portal (basic auth protected) |
| **VS Code** | Primary IDE |
| **gcloud CLI** | GCP VM management, SSH, disk operations |
| **rsync** | File synchronization (local → GCP VM) |
| **curl** | API testing |
| **Vite** | Frontend build tool |

---

# 3. The Safeguards (Quality & Growth)

## 3.1 Security & Privacy

### Permission Matrix

| Endpoint | Anonymous | Authenticated | Email Verified | Admin |
|----------|:---------:|:-------------:|:--------------:|:-----:|
| List businesses | ✅ | ✅ | ✅ | ✅ |
| Search businesses | ✅ | ✅ | ✅ | ✅ |
| View stats | ✅ | ✅ | ✅ | ✅ |
| Business photo proxy | ✅ | ✅ | ✅ | ✅ |
| List categories/tags | ✅ | ✅ | ✅ | ✅ |
| Create/edit/delete business | ❌ | ❌ | ❌ | ✅ |
| Create/edit/delete category | ❌ | ❌ | ❌ | ✅ |

### Security Measures

| Threat | Mitigation |
|--------|------------|
| **API abuse** | Nginx rate limiting: 20 req/s per IP for API, burst=40 |
| **Photo proxy abuse** | Proxies through backend — Google API key never exposed to frontend |
| **SQL injection** | Django ORM (parameterized queries), no raw SQL in viewsets |
| **Data enumeration** | Pagination (max 100 per page), search capped at 50 results |
| **Concurrent import storms** | Per-area threading locks + Celery deduplication |
| **Google API key exposure** | Stored in env vars, only accessed server-side |
| **OpenAI key exposure** | Stored in env vars, only accessed in service modules |
| **Clickjacking** | `X-Frame-Options: DENY` on all responses |
| **MIME sniffing** | `X-Content-Type-Options: nosniff` |

### Area Coverage Deduplication

```
User A searches (45.50, -73.60)  →  Import runs, creates SearchedArea(5km radius)
User B searches (45.51, -73.59)  →  PostGIS: "Within 5km of existing area" → SKIP
User C searches (45.55, -73.70)  →  Outside all areas → Import runs
```

Prevents: redundant Google API calls ($$), duplicate businesses, wasted AI classification tokens.

---

## 3.2 Scalability

### Current Bottlenecks & Scaling Paths

| Component | Current | Bottleneck At | Scaling Path |
|-----------|---------|---------------|--------------|
| **Search queries** | pgvector HNSW on single Postgres | ~10k concurrent queries | Read replicas, or graduate to dedicated vector DB (Qdrant/Pinecone) |
| **Import pipeline** | Single Celery worker, 2 concurrency | Many simultaneous new-area imports | Add Celery workers, increase `concurrency` |
| **Google API calls** | 8 concurrent workers | Rate limits (QPM) | Increase grid step (fewer points), cache responses |
| **AI classification** | 20 concurrent GPT-4o-mini workers | Token cost at scale | Batch more aggressively, cache classified places |
| **Image storage** | GCS bucket, public read | Bandwidth cost | CDN (Cloud CDN or Cloudflare) in front of GCS |
| **Database size** | 126 businesses currently | ~100k before index tuning needed | Partition by region, tune HNSW params (m, ef) |

### HNSW Index Parameters

```sql
CREATE INDEX idx_business_embedding ON businesses
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

| Parameter | Value | Effect |
|-----------|-------|--------|
| `m` | 16 | Graph connectivity (higher = better recall, more memory) |
| `ef_construction` | 64 | Build-time search depth (higher = better index quality) |
| `opclass` | `vector_cosine_ops` | Optimized for cosine distance queries |

Current settings are optimized for **< 10k vectors**. For 100k+, increase `m` to 32 and `ef_construction` to 128.

### Area Coverage Strategy

```
┌──────────────────────────────────┐
│      5km radius search area      │
│                                  │
│     ·  ·  ·  ·  ·               │
│     ·  ·  ·  ·  ·    Grid:      │
│     ·  ·  ✕  ·  ·    2.5km step │
│     ·  ·  ·  ·  ·    ~13 points │
│     ·  ·  ·  ·  ·               │
│                       ✕ = center │
└──────────────────────────────────┘

Each · = a Google API call with 16 business types
Total: ~13 × 16 = ~208 API calls per new area
```

---

## 3.3 User Engagement

### How the Backend Drives Discovery

| Feature | Backend Logic | User Benefit |
|---------|--------------|--------------|
| **Semantic search** | OpenAI embeddings understand "cozy" = warm, intimate, comfortable | Users describe *vibes*, not just keywords |
| **Auto-import** | New areas populate automatically on first search | Every location "just works" |
| **Tag filtering** | AND logic: `?tag=42&tag=17` → must have both tags | Precise narrowing ("wifi AND pet-friendly") |
| **Weighted scoring** | 70% vibe + 15% proximity + 15% rating | Relevant results, not just closest or highest-rated |
| **Sort overrides** | `sort=distance` or `sort=rating` | Power users control their feed |
| **Chain filtering** | AI removes McDonald's, Starbucks, etc. | Only local, independent businesses |
| **Rich metadata** | 20+ boolean attributes (outdoor seating, wifi, pet-friendly, etc.) | Frontend can build rich filter UIs |
| **Photo proxy** | Backend resolves Google photo URLs | Fast, secure image loading without API key exposure |

### Tag-Based Discovery Funnel

```
User types: "brunch spot"
     │
     ▼ Vector search finds businesses with similar embeddings
     │
     ▼ Results include tags like: brunch, mimosas, outdoor-seating, trendy
     │
     ▼ User clicks "outdoor-seating" tag to filter
     │
     ▼ Refined results: only brunch spots WITH outdoor seating
     │
     ▼ User discovers a hidden gem they wouldn't have found with keyword search
```

---

# 4. The Process (Workflow & Launch)

## 4.1 Development Workflow

### Code Organization

```
backend/
├── api/
│   ├── models/business.py      ← Schema + signals (data layer)
│   ├── serializers/business.py ← JSON shaping (presentation layer)
│   ├── viewsets/               ← HTTP handling (controller layer)
│   │   ├── businesses.py       
│   │   ├── categories.py       
│   │   └── tags.py             
│   ├── services/               ← Business logic (service layer)
│   │   ├── import_pipeline.py  ← Orchestrator
│   │   ├── google_places.py    ← Google API client
│   │   ├── classification.py   ← GPT-4o-mini classifier
│   │   ├── tags.py             ← Tag normalization + dedup
│   │   ├── businesses.py       ← Bulk creation
│   │   ├── embeddings.py       ← Vector generation
│   │   ├── images.py           ← Image download orchestrator
│   │   └── gcs.py              ← GCS upload helpers
│   ├── tasks/import_task.py    ← Celery async wrapper
│   ├── management/commands/    ← CLI tools
│   │   ├── import_places.py    ← Manual import
│   │   ├── generate_embeddings.py
│   │   └── seed_categories.py  
│   ├── pagination.py           ← PageNumber + Cursor pagination
│   ├── permissions.py          ← IsEmailVerified, IsOwnerOrReadOnly
│   └── urls.py                 ← DefaultRouter registration
```

### Adding a New Feature (Example: "Trending Businesses")

1. **Model**: Add `trending_score` field to `Business` in `models/business.py`
2. **Migration**: `python manage.py makemigrations`
3. **Serializer**: Add `trending_score` to `BusinessSerializer.Meta.fields`
4. **ViewSet**: Add `@action(detail=False)` method in `businesses.py`
5. **Service**: Create `services/trending.py` with the calculation logic
6. **Task**: Optionally add a periodic Celery task to recalculate scores
7. **Test**: `curl` the endpoint locally, then against cloud

---

## 4.2 Deployment Method

### Infrastructure Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     GCP VM (e2-medium)                            │
│                     <YOUR_SERVER_IP>                                │
│                     20GB disk                                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Docker Compose                             │ │
│  │                                                              │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐      │ │
│  │  │ nginx   │  │ django  │  │ celery  │  │ postgres │      │ │
│  │  │ :80     │──│ :8000   │  │ worker  │  │ :5432    │      │ │
│  │  │         │  │ gunicorn│  │         │  │ + pgvec  │      │ │
│  │  │ 4 vhosts│  │ 3 wrk  │  │ 2 conc  │  │ + postgis│      │ │
│  │  └─────────┘  └─────────┘  └────┬────┘  └──────────┘      │ │
│  │       │                          │                           │ │
│  │       │       ┌─────────┐  ┌─────┴────┐  ┌──────────┐      │ │
│  │       │       │ adminer │  │  redis   │  │ flower   │      │ │
│  │       │───────│ :8080   │  │  :6379   │  │ :5555    │      │ │
│  │       │       └─────────┘  └──────────┘  └──────────┘      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
          │                          │
          ▼                          ▼
    ┌───────────┐            ┌───────────────┐
    │ Internet  │            │ GCS Bucket    │
    │ Port 80   │            │ orbit-media-  │
    │           │            │ prod (public) │
    └───────────┘            └───────────────┘
```

### Deployment Steps

```bash
# 1. Edit code locally (VS Code)
# 2. Sync to server
rsync -avz -e ssh --exclude='.git' --exclude='node_modules' \
  /local/OrbitCentral/ gcp-vm:~/OrbitCentral/

# 3. Build + restart (on server)
docker compose build django nginx
docker compose up -d

# 4. Force-recreate if env vars changed
docker compose up -d --force-recreate celery
```

### Virtual Host Routing

| Domain | Target | Purpose |
|--------|--------|---------|
| `orbitcentral.ca` | nginx → `/app/frontend/` (static) | Vue SPA |
| `business.orbitcentral.ca` | nginx → `django:8000` | REST API |
| `admin.orbitcentral.ca` | nginx → `adminer:8080` | DB portal (basic auth) |
| `flower.orbitcentral.ca` | nginx → `flower:5555` | Celery monitor (basic auth) |

---

## 4.3 Production Method

### How the Service Gets Called

**Typical search request lifecycle:**

```
Browser (orbitcentral.ca)
    │
    │  GET /api/businesses/search/?q=cozy+coffee&lat=45.5&lng=-73.6&limit=10
    │
    ▼
Nginx (orbitcentral.ca, port 80)
    │  proxy_pass http://django:8000
    │  rate_limit: 20r/s, burst=40
    ▼
Gunicorn (3 gthread workers)
    │
    ▼
BusinessViewSet.vector_search()
    │
    ├── [ASYNC] Celery: ensure_area_covered_task.delay(45.5, -73.6)
    │     └── If area not covered → full 8-step import pipeline
    │
    ├── [SYNC] OpenAI: text-embedding-3-small("cozy coffee")
    │     └── Returns 1536-dim vector, ~100ms
    │
    ├── [SYNC] PostgreSQL:
    │     SELECT *, 1 - (embedding <=> $query_vec) AS similarity,
    │            ST_Distance(location, ST_MakePoint(-73.6, 45.5)) AS distance_m
    │     FROM businesses
    │     WHERE embedding IS NOT NULL
    │     ORDER BY similarity DESC
    │     LIMIT 30;
    │     └── HNSW index scan, ~5ms
    │
    ├── [SYNC] Python: weighted scoring + sort top 10
    │
    └── [SYNC] DRF: BusinessSearchSerializer → JSON response
         └── Includes: similarity, distance_km, score, tags[], category_detail{}
```

**Response time breakdown (typical):**

| Stage | Duration |
|-------|----------|
| Nginx → Gunicorn routing | ~1ms |
| OpenAI embedding call | ~100–200ms |
| pgvector ANN search + PostGIS distance | ~5–15ms |
| Python scoring + serialization | ~5–10ms |
| **Total** | **~120–230ms** |

### Monitoring

| Tool | What It Shows | URL |
|------|--------------|-----|
| **Flower** | Celery task status, success/failure rates, worker health | `flower.orbitcentral.ca` |
| **Adminer** | Direct database inspection, query execution | `admin.orbitcentral.ca` |
| **Django logs** | Request logs, import pipeline timing, errors | `docker compose logs django` |
| **Celery logs** | Task execution details, retries | `docker compose logs celery` |
| **Stats endpoint** | Business/tag/embedding counts, avg rating | `GET /api/businesses/stats/` |

### Key Production Numbers (Current)

| Metric | Value |
|--------|-------|
| Total businesses | 126 |
| With embeddings | 126 (100%) |
| With tags | 126 (100%) |
| With images (GCS) | 125 (99.2%) |
| Unique tags | ~180 |
| Searched areas | 1 (downtown Montreal) |
| Avg response time (search) | ~200ms |
| Avg response time (list) | ~50ms |
