<!--
  LoginPage.vue — User Login (route: /login)
  ─────────────────────────────────────────────────────────────────────────────
  Simple auth card with email + password fields.

  FLOW
  1. User submits the form → calls login() from the API layer.
  2. On success, token is saved (via setAuthToken in api/core.js), then
     useAuth().refresh() fetches the user profile.
  3. Redirects to the page the user was trying to visit (from ?redirect=
     query param) or to the Home page.
  4. If the account isn't email-verified, redirects to /verify-email instead.

  LINKS
  • "Sign up" → /register
  • "Forgot password?" → /reset-password
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <router-link to="/" class="auth-logo">Orbit</router-link>

      <h1 class="auth-title">Welcome back</h1>
      <p class="auth-subtitle">Log in to access your favorites, reviews, and personalized recommendations.</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="field-group">
          <label class="field-label">Username or Email</label>
          <input
            v-model="username"
            type="text"
            class="field-input"
            placeholder="janedoe or jane@example.com"
            required
            autofocus
          />
        </div>

        <div class="field-group">
          <label class="field-label">Password</label>
          <input
            v-model="password"
            type="password"
            class="field-input"
            placeholder="••••••••"
            required
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <!-- Invisible reCAPTCHA widget anchor -->
        <div :id="captchaId"></div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="submitting">
          {{ submitting ? 'Logging in…' : 'Log In' }}
        </button>
      </form>

      <div class="auth-footer">
        <router-link to="/register" class="auth-link">Don't have an account? <strong>Sign up</strong></router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '@/api/client'
import { useAuth } from '@/composables/useAuth'
import useCaptcha from '@/composables/useCaptcha'

const router = useRouter()
const route  = useRoute()
const { setUser } = useAuth()
const { containerId: captchaId, execute: executeCaptcha } = useCaptcha('recaptcha-login')

const username   = ref('')
const password   = ref('')
const submitting = ref(false)
const error      = ref('')

async function handleLogin() {
  submitting.value = true
  error.value = ''

  try {
    const captchaToken = await executeCaptcha()
    const { data } = await login(username.value.trim(), password.value, captchaToken)
    setUser(data.user, data.token)
    // Redirect to the page the user was trying to reach, or Home
    router.push(route.query.redirect || { name: 'Home' })
  } catch (err) {
    const detail = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0]
    error.value = detail || 'Invalid username or password.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* Layout — auth pages share this card structure */
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
.auth-form { display: flex; flex-direction: column; gap: 18px; }
.auth-footer { margin-top: 24px; text-align: center; }
.auth-link { font-size: 14px; color: var(--color-text-muted); text-decoration: none; }
.auth-link strong { color: var(--color-primary); }
.auth-link:hover strong { text-decoration: underline; }
</style>
