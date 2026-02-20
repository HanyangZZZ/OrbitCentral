# =============================================================================
# Nginx + Frontend builds
# Stage 1: Build user-facing SPA (orbitcentral.ca)      from frontend-user/
# Stage 2: Build API demo SPA   (test.orbitcentral.ca)  from frontend-demo/
# Stage 3: Serve both with Nginx
# =============================================================================

# ── Stage 1: Build user frontend (orbitcentral.ca) ───────────────────────────
FROM node:20-alpine AS user-build
WORKDIR /build
COPY frontend-user/package.json frontend-user/package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend-user/ .
RUN grep -q 'src="/src/main.js"' index.html \
    || (echo "ERROR: frontend-user/index.html missing /src/main.js entry" && exit 1)
RUN npm run build && echo "User frontend build complete."

# ── Stage 2: Build API demo frontend (test.orbitcentral.ca) ──────────────────
FROM node:20-alpine AS demo-build
WORKDIR /build
COPY frontend-demo/package.json frontend-demo/package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend-demo/ .
RUN grep -q 'src="/src/main.js"' index.html \
    || (echo "ERROR: frontend-demo/index.html missing /src/main.js entry" && exit 1)
RUN npm run build && echo "API demo frontend build complete."

# ── Stage 3: Nginx ───────────────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Install openssl for self-signed default cert
RUN apk add --no-cache openssl

COPY --from=user-build /build/dist /app/frontend
COPY --from=demo-build /build/dist /app/frontend-demo
COPY nginx/.htpasswd /etc/nginx/.htpasswd
COPY nginx/ssl/ssl-params.conf /etc/nginx/ssl/ssl-params.conf

# Generate self-signed cert for the default_server (rejects unknown hosts)
RUN mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
       -keyout /etc/nginx/ssl/default.key \
       -out /etc/nginx/ssl/default.crt \
       -subj '/CN=localhost'
