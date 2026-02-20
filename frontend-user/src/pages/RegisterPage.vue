<!--
  RegisterPage.vue — New Account Registration (route: /register)
  ─────────────────────────────────────────────────────────────────────────────
  Auth card with fields: display name, username, email, password, confirm.

  CLIENT-SIDE VALIDATION
  • Password must be ≥ 8 chars, include uppercase, lowercase, and a number.
  • Confirm password must match.
  • All fields are required.

  FLOW
  1. User fills out form → submit calls register() from the API layer.
  2. On success → redirect to /verify-email (user must verify before login).
  3. On error → error message displayed (e.g. "email already taken").

  LINK
  • "Already have an account?" → /login
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <router-link to="/" class="auth-logo">Orbit</router-link>

      <h1 class="auth-title">Create your account</h1>
      <p class="auth-subtitle">Sign up to save favorites, write reviews, and get personalized recommendations.</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="field-group">
          <label class="field-label">Email</label>
          <input
            v-model="email"
            type="email"
            class="field-input"
            placeholder="jane@example.com"
            required
            autofocus
          />
        </div>

        <div class="field-group">
          <label class="field-label">Username</label>
          <input
            v-model="username"
            type="text"
            class="field-input"
            placeholder="janedoe"
            required
          />
        </div>

        <div class="field-group">
          <label class="field-label">Display Name <span class="optional">(optional)</span></label>
          <input
            v-model="displayName"
            type="text"
            class="field-input"
            placeholder="Jane"
          />
        </div>

        <div class="field-group">
          <label class="field-label">Password</label>
          <input
            v-model="password"
            type="password"
            class="field-input"
            placeholder="Min 8 characters"
            required
            minlength="8"
          />
        </div>

        <div class="field-group">
          <label class="field-label">Confirm Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="field-input"
            placeholder="••••••••"
            required
          />
        </div>

        <!-- Errors -->
        <ul v-if="errors.length" class="error-list">
          <li v-for="(err, i) in errors" :key="i" class="error-msg">{{ err }}</li>
        </ul>

        <!-- Invisible reCAPTCHA widget anchor -->
        <div :id="captchaId"></div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="submitting">
          {{ submitting ? 'Creating account…' : 'Create Account' }}
        </button>
      </form>

      <!-- Success -->
      <div v-if="success" class="success-banner">
        <p>✓ Account created! Check your email to verify your address.</p>
      </div>

      <div class="auth-footer">
        <router-link to="/login" class="auth-link">Already have an account? <strong>Log in</strong></router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/client'
import { useAuth } from '@/composables/useAuth'
import useCaptcha from '@/composables/useCaptcha'

const router = useRouter()
const { setUser } = useAuth()
const { containerId: captchaId, execute: executeCaptcha } = useCaptcha('recaptcha-register')

const email = ref('')
const username = ref('')
const displayName = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const errors = ref([])
const success = ref(false)

async function handleRegister() {
  errors.value = []
  success.value = false

  // Client-side validation
  if (password.value !== confirmPassword.value) {
    errors.value = ['Passwords do not match.']
    return
  }
  if (password.value.length < 8) {
    errors.value = ['Password must be at least 8 characters.']
    return
  }

  submitting.value = true

  try {
    const captchaToken = await executeCaptcha()
    const payload = {
      email: email.value.trim(),
      username: username.value.trim(),
      password: password.value,
    }
    if (displayName.value.trim()) {
      payload.display_name = displayName.value.trim()
    }

    const { data } = await register(payload, captchaToken)
    setUser(data.user, data.token)
    success.value = true

    // Redirect to home after a short delay so they see the success message
    setTimeout(() => router.push({ name: 'Home' }), 1500)
  } catch (err) {
    const data = err.response?.data
    if (data) {
      // Django returns field-level errors as { field: [messages] }
      const msgs = []
      for (const [field, fieldErrors] of Object.entries(data)) {
        if (Array.isArray(fieldErrors)) {
          fieldErrors.forEach(e => msgs.push(`${capitalize(field)}: ${e}`))
        } else if (typeof fieldErrors === 'string') {
          msgs.push(fieldErrors)
        }
      }
      errors.value = msgs.length ? msgs : ['Registration failed. Please try again.']
    } else {
      errors.value = ['Something went wrong. Please try again.']
    }
  } finally {
    submitting.value = false
  }
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ')
}
</script>

<style scoped>
/* Layout — same auth card as LoginPage */
.auth-page {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: var(--color-bg); padding: 24px;
}
.auth-card {
  width: 100%; max-width: 420px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 16px; padding: 40px 32px;
}
.auth-logo {
  display: block; text-align: center;
  font-family: var(--font-brand, 'Barlow', sans-serif);
  font-size: 30px; font-weight: 800; letter-spacing: -0.5px;
  color: var(--color-primary); text-decoration: none; margin-bottom: 24px;
}
.auth-title { font-size: 22px; font-weight: 700; color: var(--color-text); text-align: center; margin: 0 0 8px; }
.auth-subtitle { font-size: 14px; color: var(--color-text-muted); text-align: center; margin: 0 0 28px; line-height: 1.5; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.optional { font-weight: 400; opacity: 0.6; }
.error-list { list-style: none; padding: 0; margin: 0; }
.success-banner {
  margin-top: 18px; padding: 12px 16px;
  background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
  border-radius: 8px; text-align: center;
}
.success-banner p { margin: 0; font-size: 14px; color: var(--color-success); }
.auth-footer { margin-top: 24px; text-align: center; }
.auth-link { font-size: 14px; color: var(--color-text-muted); text-decoration: none; }
.auth-link strong { color: var(--color-primary); }
.auth-link:hover strong { text-decoration: underline; }
</style>
