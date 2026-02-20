# Orbit — Security & Production Improvements

*Generated from security audit on 2026-02-20. Items that were easy to fix have
already been applied (see commit history). The items below require more thought,
testing, or architectural changes.*

---

## Priority 1 — Should Address Soon

### 1. Add `Content-Security-Policy` Header
**Where:** [nginx/nginx.conf](nginx/nginx.conf) — all `server` blocks  
**Risk:** Without CSP, any XSS vector can load arbitrary scripts, exfiltrate
auth tokens from localStorage, and hijack sessions.  
**Action:** Add to every server block:
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://www.google.com; font-src 'self';" always;
```
**Effort:** ~30 min. Test thoroughly — CSP can break inline styles, Google Maps
embeds, GCS images, etc. May need iterative tuning.

### 2. Add Redis Authentication
**Where:** [docker-compose.yml](docker-compose.yml) — redis service  
**Risk:** Any container on the Docker network can read/write Redis (including
Adminer, a third-party image). Celery task payloads are accessible.  
**Action:**
1. Add `--requirepass ${REDIS_PASSWORD}` to the redis `command`
2. Update `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to include password:
   `redis://:${REDIS_PASSWORD}@redis:6379/0`
3. Add `REDIS_PASSWORD` to `.env.example`

### 3. Add `Permissions-Policy` Header
**Where:** [nginx/nginx.conf](nginx/nginx.conf)  
**Risk:** Without it, the page can access camera, microphone, etc. Geolocation
is used intentionally; everything else should be denied.  
**Action:** Add to server blocks:
```nginx
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(self), payment=()" always;
```

### 4. Remove Deprecated `X-XSS-Protection` Header
**Where:** [nginx/nginx.conf](nginx/nginx.conf)  
**Risk:** Low. The header is ignored by modern browsers and can introduce
vulnerabilities in some edge cases. Replace with CSP (item #1 above).

---

## Priority 2 — Important but Needs Design

### 5. Move Auth Tokens from localStorage to HttpOnly Cookies
**Where:** frontend-user/src/api/core.js, backend auth views  
**Risk:** Tokens in localStorage are accessible to any JS on the page. If XSS
exists (especially without CSP), tokens can be stolen.  
**Current state:** HttpOnly cookie mechanism exists but is opt-in based on
cookie consent. The default path uses localStorage.  
**Action:** Make HttpOnly cookie the primary auth mechanism for web. Only fall
back to localStorage for Capacitor/native builds where cookies don't work.
**Effort:** ~2-4 hours. Requires changing the auth flow in `core.js`, `useAuth`,
and the backend `_set_auth_cookie` logic. Must handle CSRF for cookie-based auth.

### 6. Implement Account Lockout After Failed Logins
**Where:** backend/api/viewsets/auth.py — `login` action  
**Risk:** Login endpoint allows unlimited brute-force attempts (bounded only by
200/hour anon throttle + reCAPTCHA). At 200 attempts/hour, a targeted attack is
feasible.  
**Options:**
- Use `django-axes` (easiest, full-featured)
- Custom: track failed attempts by username in Redis, exponential backoff
- Progressive CAPTCHA: only require captcha after N failures  
**Effort:** ~2-3 hours with django-axes; ~4-6 hours custom.

### 7. Add AI Endpoint-Specific Rate Limits
**Where:** backend/api/viewsets/businesses.py (`personalized`), backend/api/viewsets/ (AI review endpoints)  
**Risk:** Each call triggers paid OpenAI API calls (GPT-4.1 + embeddings). A
single compromised account can run up thousands of dollars.  
**Already done:** Global user throttle (500/hour) added. But AI endpoints should
have tighter per-user limits (e.g. 20/hour).  
**Action:** Create a custom `AIRateThrottle` class and apply it to the
`personalized` and `ai-reviews/*/message/` endpoints:
```python
class AIRateThrottle(throttling.UserRateThrottle):
    rate = '20/hour'
    scope = 'ai'
```

### 8. Default Permission to `IsAuthenticated`
**Where:** backend/server/settings/base.py  
**Risk:** Every new ViewSet is public by default (`AllowAny`). If a developer
forgets to add `permission_classes`, the endpoint is silently exposed.  
**Action:** Change default to `IsAuthenticated` and explicitly set `AllowAny`
on public endpoints (search, categories, tags, business detail, login, register).
**Effort:** ~1-2 hours. Need to audit every ViewSet and add explicit permissions.

---

## Priority 3 — Nice to Have

### 9. Enable OCSP Stapling
**Where:** nginx/ssl/ssl-params.conf  
**Current state:** Commented out.  
**Action:** Uncomment and test:
```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

### 10. Add 404 Catch-All Route in Vue Router
**Where:** frontend-user/src/router/index.js  
**Risk:** Navigating to a non-existent route shows a blank page.  
**Action:** Add a catch-all route with a NotFoundPage component:
```javascript
{ path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/pages/NotFoundPage.vue') }
```

### 11. Remove Postgres Port from Production docker-compose
**Where:** [docker-compose.yml](docker-compose.yml) — postgres `ports`  
**Current:** `127.0.0.1:5432:5432` — accessible from host.  
**Action:** Move port mapping to `docker-compose.override.yml` (dev only).
Django connects via the Docker network and doesn't need the host binding.

### 12. Improve Frontend Password Validation
**Where:** frontend-user/src/pages/RegisterPage.vue  
**Current:** Only checks length ≥ 8. Django backend enforces stronger rules but
errors surface as generic server errors.  
**Action:** Add client-side checks for uppercase, lowercase, number, and
non-common-password, matching Django's validators. Show inline feedback.

### 13. Reset Password CAPTCHA
**Where:** backend/api/viewsets/auth.py — `reset_password` action  
**Risk:** While `forgot_password` requires CAPTCHA, `reset_password` does not.
Low risk since it requires a valid token, but adds defense-in-depth.

### 14. Flower Healthcheck Password Exposure
**Where:** [docker-compose.yml](docker-compose.yml) — flower healthcheck  
**Risk:** Password visible in `docker inspect` and `/proc/<pid>/cmdline`.  
**Action:** Use a Flower healthcheck endpoint that doesn't need auth, or use
`curl --netrc-file` with a mounted secrets file.

---

## Already Fixed (This Commit)

| Fix | File(s) | Description |
|-----|---------|-------------|
| Captcha fail-closed | `backend/api/services/captcha.py` | Changed from fail-open to fail-closed when Google is unreachable |
| Email enumeration leak | `backend/api/viewsets/auth.py` | Removed `email` field from forgot-password response |
| Authenticated rate limiting | `backend/server/settings/base.py` | Added `UserRateThrottle` at 500/hour |
| Photo proxy int parsing | `backend/api/viewsets/businesses.py` | Wrapped `idx` and `maxHeight` in try/except |
| Dev proxy to localhost | `frontend-user/vite.config.js` | Changed from `http://orbitcentral.ca` to `http://localhost:8000` |
| HTTPS default for email links | `docker-compose.yml` | Changed `FRONTEND_BASE_URL` default to `https://` |
| Removed hardcoded personal email | `base.py`, `docker-compose.yml` | Changed default to `noreply@orbitcentral.ca` |
| Account deletion requires password | `backend/api/viewsets/auth.py` | Added `check_password()` confirmation |
| `.env` files removed from git | `.gitignore` | Added `.env` patterns, created `.env.example` |
