# =============================================================================
# OrbitCentral Makefile — Docker Compose commands for development & deployment
# =============================================================================
# Services: postgres, redis, django, celery, nginx, adminer, flower
# Run "make help" to see all commands.
# =============================================================================

.PHONY: help build up down restart logs django-shell db-shell migrate createsuperuser status backup celery-logs celery-restart flower deploy-frontend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Lifecycle ────────────────────────────────────────────────────────────────
build: ## Build all images
	docker compose build

up: ## Start all services (detached)
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

restart-django: ## Rebuild and restart Django only
	docker compose up -d --build django && docker compose restart nginx

status: ## Show container status
	docker compose ps

# ── Logs ─────────────────────────────────────────────────────────────────────
logs: ## Tail logs from all services
	docker compose logs -f

logs-django: ## Tail Django logs only
	docker compose logs -f django

logs-nginx: ## Tail Nginx logs only
	docker compose logs -f nginx

logs-postgres: ## Tail PostgreSQL logs only
	docker compose logs -f postgres

# ── Django management ────────────────────────────────────────────────────────
django-shell: ## Open Django shell
	docker compose exec django python manage.py shell

migrate: ## Run Django migrations
	docker compose exec django python manage.py migrate

makemigrations: ## Create new migrations
	docker compose exec django python manage.py makemigrations

createsuperuser: ## Create Django superuser
	docker compose exec django python manage.py createsuperuser

collectstatic: ## Collect static files
	docker compose exec django python manage.py collectstatic --noinput

seed: ## Seed categories (idempotent)
	docker compose exec django python manage.py seed_categories

embed: ## Generate embeddings for all businesses missing them
	docker compose exec django python manage.py generate_embeddings

embed-all: ## Re-generate embeddings for ALL businesses
	docker compose exec django python manage.py generate_embeddings --all

# ── Database ─────────────────────────────────────────────────────────────────
db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U $${PG_USER:-orbitcentral} -d $${PG_DATABASE:-orbitcentral}

db-reset: ## Reset database (DROP + CREATE schema, re-apply migrations, seed)
	docker compose exec postgres psql -U $${PG_USER:-orbitcentral} -d $${PG_DATABASE:-orbitcentral} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS pg_trgm;"
	docker compose exec django python manage.py migrate
	docker compose exec django python manage.py seed_categories
	@echo "Database reset complete"

backup: ## Backup database to ./backups/
	@mkdir -p backups
	docker compose exec postgres pg_dump -U $${PG_USER:-orbitcentral} $${PG_DATABASE:-orbitcentral} | gzip > backups/orbitcentral_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup saved to backups/"

# ── Celery (background tasks) ────────────────────────────────────────────────
logs-celery: ## Tail Celery worker logs
	docker compose logs -f celery

logs-redis: ## Tail Redis logs
	docker compose logs -f redis

celery-restart: ## Rebuild and restart Celery worker only
	docker compose up -d --build celery

celery-purge: ## Purge all pending Celery tasks
	docker compose exec celery celery -A server purge -f

celery-inspect: ## Show active Celery tasks
	docker compose exec celery celery -A server inspect active

flower: ## Open Flower dashboard (starts if not running)
	@echo "Flower dashboard: http://localhost:5555"
	@docker compose up -d flower

# ── Frontend / Nginx deploy ──────────────────────────────────────────────────
deploy-frontend: ## Rebuild and deploy both frontends (user + demo) via nginx
	@echo "Validating frontend sources..."
	@grep -q 'src="/src/main.js"' frontend-user/index.html \
		|| (echo "\033[31mERROR: frontend-user/index.html is corrupted — missing /src/main.js entry point.\033[0m" && exit 1)
	@grep -q 'src="/src/main.js"' frontend-demo/index.html \
		|| (echo "\033[31mERROR: frontend-demo/index.html is corrupted — missing /src/main.js entry point.\033[0m" && exit 1)
	@echo "Building nginx (--no-cache)..."
	docker compose build --no-cache nginx
	@echo "Restarting nginx..."
	docker compose up -d nginx
	@echo "Verifying user frontend (orbitcentral.ca)..."
	@JS_FILE=$$(docker compose exec nginx ls /app/frontend/assets/ | grep '\.js$$' | head -1) \
		&& docker compose exec nginx grep -q 'createApp' /app/frontend/assets/$$JS_FILE \
		&& echo "\033[32m✓ User frontend deployed.\033[0m" \
		|| (echo "\033[31m✗ User frontend build verification failed.\033[0m" && exit 1)
	@echo "Verifying demo frontend (test.orbitcentral.ca)..."
	@JS_FILE=$$(docker compose exec nginx ls /app/frontend-demo/assets/ | grep '\.js$$' | head -1) \
		&& docker compose exec nginx grep -q 'createApp' /app/frontend-demo/assets/$$JS_FILE \
		&& echo "\033[32m✓ Demo frontend deployed.\033[0m" \
		|| (echo "\033[31m✗ Demo frontend build verification failed.\033[0m" && exit 1)

# ── SSL / Certbot ────────────────────────────────────────────────────────────
ssl-init: ## First-time SSL cert issuance (run once)
	@echo "Step 1: Creating placeholder certs so nginx can start..."
	docker compose run --rm --entrypoint "" certbot sh -c " \
		mkdir -p /etc/letsencrypt/live/orbitcentral.ca && \
		openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
			-keyout /etc/letsencrypt/live/orbitcentral.ca/privkey.pem \
			-out /etc/letsencrypt/live/orbitcentral.ca/fullchain.pem \
			-subj '/CN=orbitcentral.ca' 2>/dev/null && \
		echo 'Placeholder certs created.'"
	@echo "Step 2: Starting nginx (HTTP + placeholder HTTPS)..."
	docker compose up -d nginx
	@sleep 3
	@echo "Step 3: Requesting real certificates from Let's Encrypt..."
	docker compose run --rm certbot certonly --webroot \
		-w /var/www/certbot \
		-d orbitcentral.ca \
		-d business.orbitcentral.ca \
		-d admin.orbitcentral.ca \
		-d test.orbitcentral.ca \
		-d flower.orbitcentral.ca \
		--email $${CERTBOT_EMAIL:?Set CERTBOT_EMAIL in .env} \
		--agree-tos --no-eff-email --force-renewal
	@echo "Step 4: Reloading nginx with real certs..."
	docker compose exec nginx nginx -s reload
	@echo "\033[32m✓ SSL certificates installed successfully.\033[0m"

ssl-renew: ## Renew SSL certificates
	docker compose run --rm certbot renew
	docker compose exec nginx nginx -s reload
	@echo "\033[32m✓ SSL certificates renewed.\033[0m"

ssl-status: ## Show SSL certificate status
	docker compose run --rm certbot certificates

# ── Cleanup ──────────────────────────────────────────────────────────────────
clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi local
	@echo "Cleaned up all containers, volumes, and local images"

prune: ## Remove unused Docker resources
	docker system prune -f
