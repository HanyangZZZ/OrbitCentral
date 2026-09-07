# OrbitCentral — Known Issues & Remaining Work

Prioritised backlog of issues discovered during the security audit (Feb 19, 2026).  
Items marked **FIXED** have already been resolved and deployed.

---

## Critical — FIXED ✅

| # | Issue | Fix applied |
|---|-------|-------------|
| C1 | **CategoryViewSet open to public writes** | Added `get_permissions()` — admin required for create/update/delete |
| C2 | **Flower dashboard unauthenticated** | Flower now uses `--basic-auth` (credentials in `.env`) |
| C3 | **Adminer publicly accessible** | Nginx basic auth (`auth_basic`) in front of Adminer vhost |
| C4 | **Insecure default SECRET_KEY** | `production.py` now raises `ImproperlyConfigured` if the key is the insecure default |
| C5 | **Auth tokens never expire** | Custom `ExpiringTokenAuthentication` — 72h TTL (configurable via `TOKEN_TTL_HOURS` env) |
| C6 | **Review aggregates never recalculated** | Bayesian `post_save`/`post_delete` signals already present in code (verified) |

## Critical — Previously Fixed ✅

| # | Issue | Fix applied |
|---|-------|-------------|
| — | **BusinessViewSet open to public writes** | `get_permissions()` — admin for create/update/delete, public read |

---

## High Priority — Needs Attention Before Production

### H1. No rate limiting on authentication endpoints
- **File**: `api/viewsets/auth.py`
- **Risk**: Brute-force password guessing (200 attempts/hour with current anon throttle).
- **Fix**: Add custom throttle scopes:
  ```python
  # settings
  'DEFAULT_THROTTLE_RATES': {
      'anon': '200/hour',
      'login': '5/minute',
      'register': '3/minute',
      'password_reset': '3/minute',
  }
  ```
  Then set `throttle_classes` on each auth action.

### H2. No throttling for authenticated users — **FIXED** ✅
Added `UserRateThrottle` to `DEFAULT_THROTTLE_CLASSES` with `'user': '500/hour'` in `base.py`.

### H3. Anonymous users can trigger expensive Google+OpenAI imports
- **File**: `api/viewsets/businesses.py` (vector_search action)
- **Risk**: Each search with coordinates triggers `ensure_area_covered_task` → Google Places API (20+ calls) + OpenAI embeddings + GPT-4o-mini classification. An attacker searching many distinct coordinates can drain API credits rapidly.
- **Fix**: Require authentication for searches that provide `lat`/`lng`, OR heavily throttle the import task (e.g., max 5 new areas per hour).

### H4. Mass assignment on UserProfile `metadata` field
- **File**: `api/serializers/auth.py`
- **Risk**: `metadata` (JSONField) is writable via `PATCH /api/auth/me/`. No size limit or schema validation — attacker could store arbitrarily large payloads.
- **Fix**: Add `metadata` to `read_only_fields`, or add `validate_metadata` with a size cap (e.g., 10 KB).

### H6. Email enumeration via registration
- **File**: `api/serializers/auth.py`
- **Risk**: Registration returns `"A user with this email already exists"` — allows account enumeration.
- **Fix**: Accept silently and send a "this email is already in use" notification to the existing email, OR rate-limit registration requests heavily (already mitigated by H1).

### H8. Redis without authentication
- **File**: `docker-compose.yml`
- **Risk**: Any compromised container on the Docker network can access Redis, read Celery task data (tokens, user IDs), or flush the broker.
- **Fix**: Add `--requirepass ${REDIS_PASSWORD}` to the Redis command and update `CELERY_BROKER_URL` to include the password.

### H9. No HTTPS / HSTS — **FIXED** ✅
SSL termination via Let's Encrypt (Certbot auto-renewal). HSTS with `max-age=31536000; includeSubDomains` on all server blocks. HTTP → HTTPS 301 redirect.

---

## High Priority — FIXED ✅

| # | Issue | Fix applied |
|---|-------|-------------|
| H5 | **Uncapped base64 photo upload** | 5 MB limit enforced in `_upload_photo()` |
| H7 | **HTML injection in email templates** | `html_escape()` applied to `recipient_name` in both email tasks |

---

## Medium Priority

### M1. Global default permission is `AllowAny`
- **File**: `server/settings/base.py` (L130)
- **Risk**: Any new viewset added without explicit permissions will be publicly writable (fail-open).
- **Fix**: Change default to `IsAuthenticatedOrReadOnly` and explicitly set `AllowAny` on endpoints that need it.

### M3. Integer parsing can raise unhandled ValueError — **FIXED** ✅
Wrapped `int()` calls in try/except for `limit` params in businesses, tags, and bookmarks.

### M4. `google_place_id` uniqueness + `ignore_conflicts`
- **File**: `api/services/import_pipeline.py`
- **Risk**: `null` + `unique=True` allows multiple NULL rows. `ignore_conflicts=True` silently suppresses uniqueness errors.
- **Fix**: Log when conflicts are suppressed; consider replacing `ignore_conflicts` with `update_or_create`.

### M5. N+1 query on Business list — **FIXED** ✅
Added `prefetch_related('tags')` to `BusinessViewSet.queryset`.

### M6. `photo_references` exposed in API response
- **File**: `api/serializers/business.py`
- **Risk**: Exposes Google Places internal resource names. Information disclosure.
- **Fix**: Remove `photo_references` from `BusinessSerializer.fields`.

### M7. `reviews_data` may violate Google TOS
- **File**: `api/serializers/business.py`
- **Risk**: Republishing Google review data without attribution may violate Google Places API Terms of Service.
- **Fix**: Add Google attribution or use `reviews_data` only internally.

### M8. Deprecated `.extra()` in import pipeline
- **File**: `api/services/import_pipeline.py`
- **Risk**: `.extra()` is deprecated and bypasses ORM safety.
- **Fix**: Replace with PostGIS `DWithin` lookup.

### M9. Users can vote on their own reviews — **FIXED** ✅
Added self-vote check in `ReviewViewSet.vote()`.

### M10. OpenAI client created per-request
- **File**: `api/viewsets/businesses.py`
- **Risk**: No HTTP connection reuse to OpenAI API.
- **Fix**: Create a module-level cached client instance.

---

## Low Priority

| # | Issue | Details |
|---|-------|---------|
| L1 | Unused signal imports | `post_delete`, `post_save` imports in `business.py` — actually used (not dead code) |
| L2 | `_import_locks` grows unbounded | Per-area locks dict in `import_pipeline.py` never evicted. Use LRU cache. |
| L3 | GCS client singleton lacks thread safety | `_get_gcs_client()` global var without lock. Low risk. Use `functools.lru_cache`. |
| L4 | No `Content-Security-Policy` header | Add CSP to `nginx.conf`. |
| L5 | Missing index on `onboarding_status` | Add `db_index=True` if filtering at scale. |
| L6 | Gunicorn timeout reduced | **FIXED** — reduced from 600s to 120s. |
| L7 | Nginx proxy timeout reduced | **FIXED** — reduced from 600s to 120s. |
| L8 | No password confirmation in registration | UX concern — can be handled client-side. |
| L9 | Review `description` has no max length | Add `max_length=10000` to model or serializer. |
| L10 | `BrowsableAPIRenderer` in base settings | Only include in `development.py`. Already JSON-only in production. |

---

## Informational / Best Practices

| # | Topic | Notes |
|---|-------|-------|
| I1 | **Token strategy** | Consider `django-rest-knox` or `simplejwt` for per-device tokens and refresh flow. Current `ExpiringTokenAuthentication` is a stopgap. |
| I2 | **Brute-force protection** | Add `django-axes` for automated account lockout after N failed logins. |
| I3 | **Stale token cleanup** | `EmailVerificationToken` and `PasswordResetToken` rows accumulate. Add periodic Celery task to delete expired rows. |
| I4 | **Search embedding caching** | Cache OpenAI embeddings for repeated queries in Redis (TTL-based). |
| I5 | **`contact_email` exposure** | Business `contact_email` is publicly visible. Consider consent/opt-in. |
| I6 | **Celery task argument sensitivity** | User IDs and tokens appear in Flower/Redis/logs. Use `argsrepr`/`kwargsrepr` to redact. |
| I7 | **Test coverage** | No backend tests exist. Add unit tests for auth flows, permissions, and aggregate calculations. |
| I8 | **`metadata` JSON fields** | Both `Business.metadata` and `UserProfile.metadata` are unstructured. Migrate frequently-used keys to dedicated columns over time. |
| I9 | **OPENAI_API_KEY not reaching container** | Vector search and tag semantic search return errors. Set `OPENAI_API_KEY` in `.env`. |

---

## Legacy Fixes (already done in prior session)

| Fix | Description |
|-----|-------------|
| Removed `path('api/auth/token/', obtain_auth_token)` | Legacy DRF token endpoint (M2) |
| Deleted `frontend/src/router.js` | Dead code after frontend simplification |
| Simplified `App.vue` and `main.js` | Removed vue-router, single-page API demo |
| Replaced `HomePage.vue` | Clean API reference page (~400 lines) covering all endpoints |
