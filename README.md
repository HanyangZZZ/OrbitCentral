# FBLC — Local Business Cross-Platform App

> By Abby and Hanyang

## Tech Stack

| Layer     | Technology                                  |
| --------- | ------------------------------------------- |
| Frontend  | Vue 3 + Vite + Vue Router                   |
| Backend   | Django 5 + Django REST Framework             |
| Database  | MySQL 8.0 (Docker)                           |
| Mobile    | Capacitor 6 (iOS)                            |
| API Style | RESTful, paginated, filterable               |

## Project Structure

```
FBLC/
├── backend/
│   ├── .env                          # Environment variables (git-ignored)
│   ├── manage.py                     # Django management (uses development settings)
│   ├── requirements.txt              # Python dependencies
│   ├── api/
│   │   ├── models/                   # One file per domain
│   │   │   ├── user.py               # User, UserProfile
│   │   │   ├── business.py           # Category, Business
│   │   │   ├── review.py             # Review
│   │   │   ├── bookmark.py           # Bookmark
│   │   │   ├── reward.py             # Reward, UserCoupon
│   │   │   └── automation.py         # AutomationLog
│   │   ├── serializers.py            # DRF serializers (validation, JSON ↔ model)
│   │   ├── viewsets.py               # DRF ModelViewSets (full CRUD)
│   │   ├── urls.py                   # DRF Router → auto-generates all routes
│   │   ├── pagination.py             # Paginated responses (50 per page)
│   │   ├── exceptions.py             # Structured error logging
│   │   └── admin.py                  # Django admin registrations
│   └── server/
│       ├── settings/
│       │   ├── base.py               # Shared config (DRF, logging, DB)
│       │   ├── development.py        # DEBUG=True, loose CORS, no throttle
│       │   └── production.py         # DEBUG=False, strict CORS, security headers
│       ├── urls.py                   # Root URL config (admin + api)
│       ├── wsgi.py                   # Production WSGI entry point
│       └── asgi.py                   # Production ASGI entry point
├── frontend/
│   ├── src/
│   │   ├── api/client.js             # Axios client — all API functions
│   │   ├── pages/HomePage.vue        # Data portal UI
│   │   ├── router.js                 # Vue Router config
│   │   ├── App.vue                   # Shell layout + nav
│   │   └── main.js                   # App entry point
│   ├── capacitor.config.json         # Capacitor config for iOS builds
│   ├── vite.config.js                # Vite + proxy config
│   └── package.json                  # Node dependencies
└── .gitignore
```

## Quick Start

### 1. Backend

```bash
# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start MySQL
docker run -d --name fblc-mysql \
  -p 3306:3306 \
  -e MYSQL_DATABASE=fblc \
  -e MYSQL_USER=fblc \
  -e MYSQL_PASSWORD=fblc_password \
  -e MYSQL_ROOT_PASSWORD=root_password \
  mysql:8.0

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver 0.0.0.0:8001
```

The API is at `http://localhost:8001/api/`.
The browsable API (interactive docs) is at `http://localhost:8001/api/` in a browser.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` → `http://localhost:8001`.

### 3. Adminer (MySQL web GUI)

```bash
docker run -d --name fblc-adminer -p 8090:8080 adminer
```

Open `http://localhost:8090`:
- System: **MySQL**
- Server: **host.docker.internal** (or `127.0.0.1` on Linux)
- Database: `fblc`
- Username: `fblc`
- Password: `fblc_password`

## API Overview

All endpoints support **GET, POST, PUT, PATCH, DELETE**. List responses are paginated.

| Resource         | Endpoint                    | Filter fields                                | Search fields                      |
| ---------------- | --------------------------- | -------------------------------------------- | ---------------------------------- |
| Users            | `/api/users/`               | `role`, `is_verified_human`                  | `email`                            |
| Profiles         | `/api/profiles/`            | `high_contrast`, `keyboard_only_nav`         | `display_name`, `user__email`      |
| Categories       | `/api/categories/`          | —                                            | `name`, `slug`                     |
| Businesses       | `/api/businesses/`          | `category`, `owner`, `onboarding_status`     | `name`, `contact_email`, `google_place_id` |
| Reviews          | `/api/reviews/`             | `business`, `user`, `rating`, `is_visible`   | `content`                          |
| Bookmarks        | `/api/bookmarks/`           | `user`, `business`                           | —                                  |
| Rewards          | `/api/rewards/`             | `provider_business`, `trigger_business`, `reward_type` | `title`                  |
| Coupons          | `/api/coupons/`             | `user`, `reward`, `status`                   | —                                  |
| Automation Logs  | `/api/automation-logs/`     | `business`, `action_type`, `status`          | —                                  |

### Pagination

```
GET /api/users/?page=2&page_size=10
```

Response:
```json
{
  "count": 42,
  "next": "http://localhost:8001/api/users/?page=3&page_size=10",
  "previous": "http://localhost:8001/api/users/?page=1&page_size=10",
  "results": [ ... ]
}
```

### Filtering, Search & Ordering

```
GET /api/businesses/?category=1&onboarding_status=active
GET /api/businesses/?search=cafe
GET /api/businesses/?ordering=-avg_rating
```

## Environment Variables

Defined in `backend/.env` (git-ignored):

| Variable             | Default            | Description              |
| -------------------- | ------------------ | ------------------------ |
| `DJANGO_SECRET_KEY`  | (insecure default) | Change in production!    |
| `DJANGO_DEBUG`       | `true`             | Set `false` in prod      |
| `MYSQL_DATABASE`     | `fblc`             | MySQL database name      |
| `MYSQL_USER`         | `fblc`             | MySQL user               |
| `MYSQL_PASSWORD`     | `fblc_password`    | MySQL password           |
| `MYSQL_HOST`         | `127.0.0.1`        | MySQL host               |
| `MYSQL_PORT`         | `3306`             | MySQL port               |

## Settings

| File               | Used when                          |
| ------------------ | ---------------------------------- |
| `development.py`   | `manage.py runserver` (default)    |
| `production.py`    | WSGI/ASGI (gunicorn, uvicorn)      |

Override with: `DJANGO_SETTINGS_MODULE=server.settings.production`

## Capacitor (iOS)

```bash
cd frontend
npm run build
npx cap sync ios
npx cap open ios
```

## Django Admin

```bash
python manage.py createsuperuser
# Then open http://localhost:8001/admin/
```
