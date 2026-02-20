# =============================================================================
# FBLC Makefile — Docker Compose commands for development & deployment
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
	docker compose exec postgres psql -U $${PG_USER:-fblc} -d $${PG_DATABASE:-fblc}

db-reset: ## Reset database (DROP + CREATE schema, re-apply migrations, seed)
	docker compose exec postgres psql -U $${PG_USER:-fblc} -d $${PG_DATABASE:-fblc} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS pg_trgm;"
	docker compose exec django python manage.py migrate
	docker compose exec django python manage.py seed_categories
	@echo "Database reset complete"

backup: ## Backup database to ./backups/
	@mkdir -p backups
	docker compose exec postgres pg_dump -U $${PG_USER:-fblc} $${PG_DATABASE:-fblc} | gzip > backups/fblc_$$(date +%Y%m%d_%H%M%S).sql.gz
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
deploy-frontend: ## Rebuild and deploy the frontend (nginx)
	@echo "Validating frontend source..."
	@grep -q 'src="/src/main.js"' frontend/index.html \
		|| (echo "\033[31mERROR: frontend/index.html is corrupted — missing /src/main.js entry point.\033[0m" && exit 1)
	@echo "Building nginx (--no-cache)..."
	docker compose build --no-cache nginx
	@echo "Restarting nginx..."
	docker compose up -d nginx
	@echo "Verifying build output..."
	@JS_FILE=$$(docker compose exec nginx ls /app/frontend/assets/ | grep '\.js$$' | head -1) \
		&& docker compose exec nginx grep -q 'createApp' /app/frontend/assets/$$JS_FILE \
		&& echo "\033[32m✓ Frontend deployed successfully.\033[0m" \
		|| (echo "\033[31m✗ Build verification failed — JS bundle may be corrupt.\033[0m" && exit 1)

# ── Cleanup ──────────────────────────────────────────────────────────────────
clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi local
	@echo "Cleaned up all containers, volumes, and local images"

prune: ## Remove unused Docker resources
	docker system prune -f
