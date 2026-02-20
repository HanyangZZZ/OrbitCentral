# Authentication

User system with email verification via Brevo (Sendinblue). All auth endpoints are under `/api/auth/`.

## Register

```
POST /api/auth/register/
```

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Unique email address |
| `username` | string | Yes | Unique username |
| `password` | string | Yes | Min 8 characters, Django validators applied |
| `display_name` | string | No | Profile display name |

```json
{
  "email": "jane@example.com",
  "username": "janedoe",
  "password": "secret123!",
  "display_name": "Jane"
}
```

**Response:** `201 Created`

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "username": "janedoe",
    "email": "jane@example.com",
    "display_name": "Jane",
    "avatar_url": null,
    "bio": "",
    "email_verified": false,
    "metadata": {}
  }
}
```

A verification email is sent asynchronously via Celery + Brevo.

## Login

```
POST /api/auth/login/
```

**Request body:**

```json
{
  "username": "janedoe",
  "password": "secret123!"
}
```

The `username` field accepts either a username or an email address.

**Response:** `200 OK`

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "username": "janedoe",
    "email": "jane@example.com",
    "display_name": "Jane",
    "avatar_url": null,
    "bio": "",
    "email_verified": true,
    "metadata": {}
  }
}
```

## Verify Email

```
POST /api/auth/verify-email/
```

**Request body:**

```json
{ "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890" }
```

**Response:** `200 OK`

```json
{ "detail": "Email verified successfully." }
```

Tokens expire after 24 hours and are single-use.

## Get / Update Profile

```
GET  /api/auth/me/
PATCH /api/auth/me/
```

**Requires authentication.**

GET returns the current user's profile. PATCH accepts:

| Field | Type | Description |
|-------|------|-------------|
| `display_name` | string | Display name |
| `avatar_url` | string | Avatar URL |
| `bio` | string | Bio text |
| `metadata` | object | Arbitrary JSON (extensible) |

## Resend Verification Email

```
POST /api/auth/resend-verify/
```

**Requires authentication.** Invalidates previous unused tokens and sends a new verification email.

**Response:** `200 OK`

```json
{ "detail": "Verification email sent." }
```

## Legacy Token Endpoint

```
POST /api/auth/token/
```

Still available for backward compatibility. Accepts `{ username, password }` and returns `{ token }`.

## Forgot Password

```
POST /api/auth/forgot-password/
```

**No authentication required.** Initiates a password-reset flow by sending an email with a reset link.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | The registered email address |

```json
{ "email": "jane@example.com" }
```

**Response:** Always `200 OK` — prevents email enumeration.

```json
{ "detail": "If an account with that email exists, a reset link has been sent." }
```

The email contains a link to `{FRONTEND_BASE_URL}/reset-password?token=<uuid>`. Tokens expire in **1 hour**.

## Reset Password

```
POST /api/auth/reset-password/
```

**No authentication required.** Resets the user's password using a token from the reset email.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `token` | string | Yes | UUID from the reset email |
| `new_password` | string | Yes | New password (Django validators applied) |

```json
{
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "new_password": "newSecure123!"
}
```

**Response:** `200 OK`

```json
{ "detail": "Password reset successfully. Please log in." }
```

**Side effects:**
- The reset token is marked as used (single-use)
- **All existing auth tokens are deleted** — the user is logged out on all devices and must log in again with the new password

**Error responses:**

| Status | Detail |
|--------|--------|
| `400` | `"token is required."` / `"new_password is required."` |
| `400` | `"Invalid or expired reset token."` |
| `400` | `["This password is too short. It must contain at least 8 characters."]` (Django password validators) |

## Client Functions

```javascript
import {
  register, login, verifyEmail, getMe, updateMe, resendVerify,
  forgotPassword, resetPassword, setAuthToken
} from '@/api/client'

// Register
const { data } = await register({ email: 'j@ex.com', username: 'jane', password: 'secret123!' })
setAuthToken(data.token)

// Login (username or email)
const { data } = await login('jane', 'secret123!')
setAuthToken(data.token)

// Verify email
await verifyEmail('a1b2c3d4-e5f6-7890-abcd-ef1234567890')

// Get profile
const { data: profile } = await getMe()

// Update profile
await updateMe({ display_name: 'Jane D.', bio: 'Coffee lover' })

// Resend verification
await resendVerify()

// Forgot password — always returns 200
await forgotPassword('jane@example.com')

// Reset password with token from email
await resetPassword('a1b2c3d4-e5f6-...', 'newSecure123!')
// User must log in again after this
```

## Permissions

| Endpoint | Auth Required | Email Verified |
|----------|:------------:|:--------------:|
| `GET /api/reviews/` | No | No |
| `POST /api/reviews/` | Yes | **Yes** |
| `PATCH/DELETE /api/reviews/{id}/` | Yes (owner) | **Yes** |
| `POST /api/reviews/{id}/vote/` | Yes | **Yes** |
| `GET/POST /api/bookmarks/*` | Yes | **Yes** |
| `PATCH/DELETE /api/bookmarks/{id}/` | Yes (owner) | **Yes** |
| `GET /api/auth/me/` | Yes | No |
| `POST /api/auth/forgot-password/` | No | No |
| `POST /api/auth/reset-password/` | No | No |
| `GET/POST /api/ai-reviews/*` | Yes | **Yes** |
| `DELETE /api/ai-reviews/{id}/` | Yes (owner) | **Yes** |
| All other read endpoints | No | No |
