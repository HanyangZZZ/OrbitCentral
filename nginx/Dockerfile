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

# Guard: index.html must reference source entry point, not a previous build artifact.
# If this fails, the source index.html was overwritten by a dist/index.html.
RUN grep -q 'src="/src/main.js"' index.html \
    || (echo "ERROR: index.html does not reference /src/main.js — it may have been overwritten by a build artifact." && exit 1)

RUN npm run build \
    && MODULES=$(grep -oP '\d+(?= modules transformed)' /tmp/build.log 2>/dev/null || echo '') \
    && echo "Build complete."

# ── Stage 2: Nginx ───────────────────────────────────────────────────────────
FROM nginx:1.27-alpine
COPY --from=frontend-build /build/dist /app/frontend
COPY nginx/.htpasswd /etc/nginx/.htpasswd
