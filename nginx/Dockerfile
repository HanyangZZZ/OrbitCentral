# =============================================================================
# Nginx + Frontend build
# Stage 1: Build Vue SPA with Node
# Stage 2: Serve with Nginx (also proxies API, Adminer, Flower)
# =============================================================================

# ── Stage 1: Build frontend ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend/ .
RUN npm run build

# ── Stage 2: Nginx ───────────────────────────────────────────────────────────
FROM nginx:1.27-alpine
COPY --from=frontend-build /build/dist /app/frontend
