# OrbitCentral Deployment Guide

How to deploy OrbitCentral to a cloud server. This guide uses Google Compute Engine (GCE), but the steps work on any Linux server with Docker installed.

## Server Overview

| Detail | Value |
|--------|-------|
| Instance name | `<your-instance-name>` |
| Cloud provider | Google Compute Engine (GCE) |
| Project ID | `<your-gcp-project-id>` |
| OS | Debian 12 |
| Specs | 2 vCPU, 3.8 GB RAM |
| Region | `<your-region>` |
| External IP | `<YOUR_SERVER_IP>` |
| Domain | `orbitcentral.ca` |
| User Frontend | `https://orbitcentral.ca` |
| API Demo Frontend | `https://test.orbitcentral.ca` |
| API (external) | `https://business.orbitcentral.ca` |
| Admin panel | `https://business.orbitcentral.ca/admin/` |
| DB portal (Adminer) | `https://admin.orbitcentral.ca` |
| Task monitor (Flower) | `https://celery.orbitcentral.ca` |
| SSL cert expiry | Check with `make ssl-status` |

### Adminer (DB Portal) Credentials

Adminer is protected by nginx basic auth at `https://admin.orbitcentral.ca`.

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | *(see server `.env` or `nginx/.htpasswd`)* |
| Config file | `nginx/.htpasswd` |

To reset: `htpasswd -cb nginx/.htpasswd admin NEW_PASSWORD`, then rebuild nginx on the server.

### SSH Access

```bash
# Connect to the server
gcloud compute ssh <your-instance-name> --zone <your-region>

# Or with the full SSH host alias (from ~/.ssh/config after first gcloud ssh)
ssh <your-instance-name>.<your-region>.<your-gcp-project-id>

# Project files live at
cd ~/OrbitCentral
```

### DNS Records

| Type | Name | Value |
|------|------|-------|
| A | `orbitcentral.ca` | `<YOUR_SERVER_IP>` |
| A | `test.orbitcentral.ca` | `<YOUR_SERVER_IP>` |
| A | `business.orbitcentral.ca` | `<YOUR_SERVER_IP>` |
| A | `admin.orbitcentral.ca` | `<YOUR_SERVER_IP>` |
| A | `celery.orbitcentral.ca` | `<YOUR_SERVER_IP>` |

## What Gets Deployed

Eight Docker containers run together:

```
Internet
  │
  ▼  :80 (→ 301 HTTPS)  :443 (SSL/TLS)
[ Nginx ] ── virtual-host routing ── [ Certbot ] (cert renewal)
  ├── orbitcentral.ca          → User Vue SPA + /api/ → [ Django/Gunicorn :8000 ] → [ PostgreSQL :5432 ]
  ├── test.orbitcentral.ca     → API Demo Vue SPA                                     (pgvector + PostGIS)
  ├── business.orbitcentral.ca → Django REST API + /admin/
  ├── admin.orbitcentral.ca    → [ Adminer :8080 ]
  ├── celery.orbitcentral.ca   → [ Flower :5555 ]
  └── unknown Host             → 444 (drop)
                                          │
                              task.delay() │
                                          ▼
                                    [ Redis :6379 ] → [ Celery Worker ]
```

- **Nginx** — HTTPS termination + virtual-host reverse proxy; builds two Vue frontends (user + demo) into the image
- **Certbot** — Let's Encrypt certificate issuance and renewal
- **Django/Gunicorn** — runs the Python API (3 workers, 2 threads each)
- **PostgreSQL** — stores all data (with pgvector for AI search, PostGIS for geography)
- **Redis** — message broker for Celery background tasks
- **Celery Worker** — processes background tasks (Google Places import, email sending)
- **Flower** — web dashboard for monitoring Celery tasks (port 5555)
- **Adminer** — database web portal

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
  backend/ frontend-demo/ frontend-user/ postgres/ nginx/ docker-compose.yml .env.example Makefile \
  <your-instance-name>:~/OrbitCentral/
```

Or if using Git:
```bash
gcloud compute ssh <your-instance-name>
cd ~
git clone <your-repo-url> OrbitCentral
cd OrbitCentral
```

### 2. Create the Environment File

```bash
cd ~/OrbitCentral
cp .env.example .env
nano .env
```

Fill in **all** the values. The important ones:

| Variable | What to Set |
|----------|------------|
| `DJANGO_SECRET_KEY` | A long random string (generate one below) |
| `PG_PASSWORD` | A strong database password |
| `ALLOWED_HOSTS` | `orbitcentral.ca,business.orbitcentral.ca,<YOUR_SERVER_IP>,localhost` |
| `CORS_ALLOWED_ORIGINS` | `https://orbitcentral.ca,https://business.orbitcentral.ca` |
| `CSRF_TRUSTED_ORIGINS` | `https://orbitcentral.ca,https://business.orbitcentral.ca` |
| `FRONTEND_BASE_URL` | `https://orbitcentral.ca` |
| `SECURE_SSL_REDIRECT` | `true` (after SSL certs are set up) |
| `CERTBOT_EMAIL` | Your email for Let's Encrypt notifications |
| `OPENAI_API_KEY` | Your OpenAI key (for semantic search) |
| `GOOGLE_PLACES_API_KEY` | Your Google Places API key (for auto-import) |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA v3 secret key (leave empty to disable) |
| `RECAPTCHA_SCORE_THRESHOLD` | Minimum score to pass (default: `0.5`) |

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
gcloud compute scp --recurse backend/ <your-instance-name>:~/OrbitCentral/

# Option B: Pull from Git
gcloud compute ssh <your-instance-name>
cd ~/OrbitCentral && git pull
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
sudo docker compose exec postgres psql -U orbitcentral -d orbitcentral
```

### Backup the Database
```bash
mkdir -p ~/backups
sudo docker compose exec postgres \
  pg_dump -U orbitcentral orbitcentral | gzip > ~/backups/orbitcentral_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore from Backup
```bash
gunzip -c ~/backups/orbitcentral_20250101.sql.gz | \
  sudo docker compose exec -T postgres psql -U orbitcentral -d orbitcentral
```

## GCE Firewall Rules

Ports 80 and 443 must be open — HTTP redirects to HTTPS:
```bash
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 --target-tags http-server
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 --target-tags https-server
gcloud compute instances add-tags <your-instance-name> \
  --tags http-server,https-server \
  --zone <your-region>
```

## Setting Up HTTPS (SSL)

HTTPS is handled by a **certbot Docker container** that obtains and renews Let's Encrypt certificates. No need to install certbot on the host.

### 1. Set `CERTBOT_EMAIL` in `.env`
```bash
CERTBOT_EMAIL=your-email@example.com
```

### 2. Open Port 443 on GCE (if not already done)
```bash
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 --target-tags https-server
gcloud compute instances add-tags <your-instance-name> --tags https-server --zone <your-region>
```

### 3. Run SSL Init
```bash
make ssl-init
```

This will:
1. Create placeholder self-signed certs so nginx can start
2. Start nginx (serves HTTP + placeholder HTTPS)
3. Request real certs from Let's Encrypt via ACME webroot challenge
4. Reload nginx with the real Let's Encrypt certs

### 4. Update `.env` for HTTPS
```bash
CORS_ALLOWED_ORIGINS=https://orbitcentral.ca,https://business.orbitcentral.ca
CSRF_TRUSTED_ORIGINS=https://orbitcentral.ca,https://business.orbitcentral.ca
FRONTEND_BASE_URL=https://orbitcentral.ca
SECURE_SSL_REDIRECT=true
```

### 5. Rebuild with HTTPS Settings
```bash
docker compose up -d --build
```

### 6. Certificate Renewal

Certificates expire every 90 days. Renew manually:
```bash
make ssl-renew
```

Or add a cron job for automatic renewal:
```bash
sudo crontab -e
# Add this line (renew daily at 3am, only acts when certs are near expiry):
0 3 * * * cd /home/$USER/OrbitCentral && docker compose run --rm certbot renew && docker compose exec nginx nginx -s reload
```

### 7. Check Certificate Status
```bash
make ssl-status
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
