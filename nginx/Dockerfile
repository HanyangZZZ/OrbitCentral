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

# Install openssl for self-signed default cert
RUN apk add --no-cache openssl

COPY --from=frontend-build /build/dist /app/frontend
COPY nginx/.htpasswd /etc/nginx/.htpasswd
COPY nginx/ssl/ssl-params.conf /etc/nginx/ssl/ssl-params.conf

# Generate self-signed cert for the default_server (rejects unknown hosts)
RUN mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
       -keyout /etc/nginx/ssl/default.key \
       -out /etc/nginx/ssl/default.crt \
       -subj '/CN=localhost'
