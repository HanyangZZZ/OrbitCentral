# FBLC Deployment Guide

How to deploy FBLC to a cloud server. This guide uses Google Compute Engine (GCE), but the steps work on any Linux server with Docker installed.

## Server Overview

| Detail | Value |
|--------|-------|
| Instance name | `fblc` |
| OS | Debian 12 |
| Specs | 2 vCPU, 3.8 GB RAM |
| Region | `northamerica-northeast2-b` |
| External IP | `34.130.223.201` |
| Domain | `orbitcentral.ca` |
| Frontend + API | `http://orbitcentral.ca` |
| Admin panel | `http://orbitcentral.ca/admin/` |
| DB portal (Adminer) | `http://admin.orbitcentral.ca` |
| Task monitor (Flower) | `http://flower.orbitcentral.ca` |

### DNS Records

| Type | Name | Value |
|------|------|-------|
| A | `orbitcentral.ca` | `34.130.223.201` |
| A | `admin.orbitcentral.ca` | `34.130.223.201` |
| A | `flower.orbitcentral.ca` | `34.130.223.201` |

## What Gets Deployed

Seven Docker containers run together:

```
Internet
  │
  ▼  :80
[ Nginx ] ── virtual-host routing
  ├── orbitcentral.ca         → Vue SPA + /api/ → [ Django/Gunicorn :8000 ] → [ PostgreSQL :5432 ]
  ├── admin.orbitcentral.ca   → [ Adminer :8080 ]                            (pgvector + PostGIS)
  ├── flower.orbitcentral.ca  → [ Flower :5555 ]
  └── unknown Host           → 444 (drop)
                                       │
                           task.delay() │
                                       ▼
                                 [ Redis :6379 ] → [ Celery Worker ]
```

- **Nginx** — virtual-host reverse proxy; builds Vue frontend into the image; serves static files
- **Django/Gunicorn** — runs the Python API (3 workers, 2 threads each)
- **PostgreSQL** — stores all data (with pgvector for AI search, PostGIS for geography)
- **Redis** — message broker for Celery background tasks
- **Celery Worker** — processes background tasks (Google Places import, AI classification)
- **Flower** — web dashboard for monitoring Celery tasks (port 5555)

## Prerequisites

On your server, install:
- **Docker Engine** + **Docker Compose** (v2)
- **Git** (optional, for pulling code)

On GCE, Docker can be installed with:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Log out and back in for group to take effect
```

## First-Time Deployment

### 1. Copy Files to the Server

```bash
# From your local machine
gcloud compute scp --recurse \
  backend/ frontend/ postgres/ nginx/ docker-compose.yml .env.production.example Makefile \
  fblc:~/FBLC/
```

Or if using Git:
```bash
gcloud compute ssh fblc
cd ~
git clone <your-repo-url> FBLC
cd FBLC
```

### 2. Create the Environment File

```bash
cd ~/FBLC
cp .env.production.example .env
nano .env
```

Fill in **all** the values. The important ones:

| Variable | What to Set |
|----------|------------|
| `DJANGO_SECRET_KEY` | A long random string (generate one below) |
| `PG_PASSWORD` | A strong database password |
| `ALLOWED_HOSTS` | Your domain, e.g. `orbitcentral.ca,34.130.223.201,localhost` |
| `CORS_ALLOWED_ORIGINS` | Your frontend URL, e.g. `http://orbitcentral.ca` |
| `OPENAI_API_KEY` | Your OpenAI key (for semantic search) |
| `GOOGLE_PLACES_API_KEY` | Your Google Places API key (for auto-import) |

**Generate a Django secret key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Build and Start

```bash
sudo docker compose build
sudo docker compose up -d
```

### 4. Set Up the Database

```bash
# Create tables
sudo docker compose exec django python manage.py migrate

# Create an admin account
sudo docker compose exec django python manage.py createsuperuser
```

### 5. Verify

```bash
# Check containers are running
sudo docker compose ps

# Test the API
curl http://orbitcentral.ca/api/categories/
curl http://orbitcentral.ca/health
```

### 6. Generate Embeddings (Optional)

If you've added businesses and want semantic search:
```bash
sudo docker compose exec django python manage.py generate_embeddings
```

## Re-deploying After Code Changes

```bash
# Option A: Copy updated files
gcloud compute scp --recurse backend/ fblc:~/FBLC/

# Option B: Pull from Git
gcloud compute ssh fblc
cd ~/FBLC && git pull
```

Then rebuild and restart:
```bash
sudo docker compose up -d --build
```

> **Tip:** If you only changed backend code, you can rebuild just Django:
> ```bash
> sudo docker compose up -d --build django
> sudo docker compose restart nginx
> ```
> If you only changed frontend code, rebuild just nginx:
> ```bash
> sudo docker compose up -d --build nginx
> ```

> **Important:** Use `up -d` (not just `restart`) when environment variables change — `restart` does NOT reload the env file.

## Daily Operations

### Check Status
```bash
sudo docker compose ps
```

### View Logs
```bash
# All services
sudo docker compose logs -f

# Just Django
sudo docker compose logs -f django

# Just Nginx
sudo docker compose logs -f nginx
```

### Run Migrations
```bash
sudo docker compose exec django python manage.py migrate
```

### Open a Shell
```bash
# Django Python shell
sudo docker compose exec django python manage.py shell

# PostgreSQL shell
sudo docker compose exec postgres psql -U fblc -d fblc
```

### Backup the Database
```bash
mkdir -p ~/backups
sudo docker compose exec postgres \
  pg_dump -U fblc fblc | gzip > ~/backups/fblc_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore from Backup
```bash
gunzip -c ~/backups/fblc_20250101.sql.gz | \
  sudo docker compose exec -T postgres psql -U fblc -d fblc
```

## GCE Firewall Rules

Only port 80 needs to be open — all services (API, Adminer, Flower) route through Nginx virtual hosts:
```bash
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 --target-tags http-server
```

Ensure the instance has the `http-server` network tag:
```bash
gcloud compute instances add-tags fblc --tags http-server --zone northamerica-northeast2-b
```

## Setting Up HTTPS (When Ready)

Once you're ready for production/beta:

### 1. Install Certbot
```bash
sudo apt install -y certbot
sudo docker compose down
sudo certbot certonly --standalone \
  -d orbitcentral.ca \
  -d admin.orbitcentral.ca \
  -d flower.orbitcentral.ca
```

### 2. Update Nginx Config
Add SSL server blocks to `nginx/nginx.conf` for each domain:
```nginx
server {
    listen 443 ssl;
    server_name orbitcentral.ca;

    ssl_certificate     /etc/letsencrypt/live/orbitcentral.ca/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/orbitcentral.ca/privkey.pem;

    # ... existing location blocks ...
}

server {
    listen 80;
    server_name orbitcentral.ca admin.orbitcentral.ca flower.orbitcentral.ca;
    return 301 https://$host$request_uri;
}
```

### 3. Update Environment
In `.env`:
```
SECURE_SSL_REDIRECT=true
ALLOWED_HOSTS=orbitcentral.ca,34.130.223.201,localhost
CORS_ALLOWED_ORIGINS=https://orbitcentral.ca
```

### 4. Mount Certificates in Docker
Add to the nginx service in `docker-compose.yml`:
```yaml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

### 5. Rebuild
```bash
sudo docker compose up -d --build
```

### 6. Open Port 443
```bash
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 --target-tags https-server
gcloud compute instances add-tags fblc --tags https-server --zone northamerica-northeast2-b
```

### 7. Auto-renew Certificates
```bash
sudo crontab -e
# Add this line:
0 3 * * * certbot renew --quiet && docker compose -f ~/FBLC/docker-compose.yml restart nginx
```

## Using Supabase Instead of Local PostgreSQL

If you prefer a managed database, you can use [Supabase](https://supabase.com):

1. Create a Supabase project
2. In the SQL Editor, run the contents of `supabase/schema.sql` to enable extensions
3. Get your connection string from **Settings → Database → Connection string**
4. Set `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
5. Remove (or comment out) the `postgres` service from `docker-compose.yml`
6. Rebuild: `sudo docker compose up -d --build`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Container won't start | Check logs: `sudo docker compose logs django` |
| Database connection error | Make sure PostgreSQL container is healthy: `sudo docker compose ps` |
| "ALLOWED_HOSTS" error | Add your domain/IP to `ALLOWED_HOSTS` in `.env` |
| Static files not loading | Run: `docker compose exec django python manage.py collectstatic --noinput` |
| Permission denied on Docker | Use `sudo` or add your user to the docker group |
| CORS errors in browser | Check `CORS_ALLOWED_ORIGINS` matches your frontend URL exactly |
| Embeddings not working | Make sure `OPENAI_API_KEY` is set and valid |
| Celery not processing tasks | Check: `docker compose logs celery` — verify Redis connection |
| Flower shows no workers | Celery may still be starting — wait 30s and refresh |
