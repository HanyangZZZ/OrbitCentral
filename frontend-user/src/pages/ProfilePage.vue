<!--
  ProfilePage.vue — Account Settings (route: /profile, auth required)
  ─────────────────────────────────────────────────────────────────────────────
  Lets logged-in users view and edit their account details.

  SECTIONS
  1. Profile Info   — display name, username, email (pre-filled from API)
  2. Password       — change password with current/new/confirm fields
  3. Danger Zone    — delete account with confirmation modal

  DATA FLOW
  • On mount, calls useAuth().refresh() to fetch /api/users/me/.
  • Form fields are populated from the `user` ref.
  • Save → PATCH /api/users/me/ → success/error feedback.
  • Delete → DELETE /api/users/me/ → clears auth → redirects to Home.

  AUTH GUARD
  The router already protects this route with `meta: { requiresAuth: true }`.
  The page also shows a loading spinner while useAuth is checking the token.

  MODULAR FLOW
    useAuth singleton → user ref → form fields pre-filled
    Save button → updateMe() API → success message
    Delete button → deleteAccount() API → clear() → router.push('/')
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="settings-page">
    <div class="settings-container">
      <h1 class="settings-title">Account Settings</h1>

      <!-- Loading state -->
      <div v-if="loading || !checked" class="state-msg">
        <div class="spinner" />
        <span>Loading your profile…</span>
      </div>

      <!-- Not logged in -->
      <div v-else-if="!isLoggedIn" class="state-msg">
        <p>You need to be logged in to view account settings.</p>
        <div class="auth-buttons">
          <router-link to="/login" class="btn btn-primary">Log In</router-link>
          <router-link to="/register" class="btn btn-outline">Register</router-link>
        </div>
      </div>

      <!-- Profile loaded -->
      <template v-else>
        <!-- ── Profile Section ── -->
        <section class="settings-section">
          <h2 class="section-heading">Profile</h2>

          <div class="profile-card">
            <!-- Avatar -->
            <div class="avatar-area">
              <div class="avatar-large">
                <img v-if="user.avatar_url" :src="user.avatar_url" alt="Avatar" class="avatar-img" />
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
            </div>

            <!-- Form fields -->
            <div class="profile-fields">
              <div class="field-group">
                <label class="field-label">Display Name</label>
                <input
                  v-model="form.display_name"
                  type="text"
                  class="field-input"
                  placeholder="Your display name"
                />
              </div>

              <div class="field-group">
                <label class="field-label">Bio</label>
                <textarea
                  v-model="form.bio"
                  class="field-input field-textarea"
                  placeholder="Tell us about yourself…"
                  rows="3"
                />
              </div>

              <div class="field-group">
                <label class="field-label">Avatar URL</label>
                <input
                  v-model="form.avatar_url"
                  type="url"
                  class="field-input"
                  placeholder="https://example.com/avatar.jpg"
                />
              </div>

              <div class="field-actions">
                <button
                  class="btn btn-primary"
                  :disabled="saving"
                  @click="saveProfile"
                >
                  {{ saving ? 'Saving…' : 'Save Changes' }}
                </button>
                <span v-if="saveSuccess" class="success-msg">✓ Saved</span>
                <span v-if="saveError" class="error-msg">{{ saveError }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- ── Account Info Section ── -->
        <section class="settings-section">
          <h2 class="section-heading">Account</h2>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Username</span>
              <span class="info-value">{{ user.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Email</span>
              <span class="info-value">{{ user.email }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Email Verified</span>
              <span class="info-value" :class="user.email_verified ? 'verified' : 'unverified'">
                {{ user.email_verified ? '✓ Verified' : '✗ Not verified' }}
              </span>
              <button
                v-if="!user.email_verified"
                class="btn btn-sm btn-outline"
                :disabled="resending"
                @click="handleResendVerify"
              >
                {{ resending ? 'Sending…' : 'Resend Verification' }}
              </button>
              <span v-if="resendSuccess" class="success-msg">Email sent!</span>
            </div>
          </div>
        </section>

        <!-- ── Security Section ── -->
        <section class="settings-section">
          <h2 class="section-heading">Security</h2>

          <div class="action-card">
            <div class="action-info">
              <h3 class="action-title">Change Password</h3>
              <p class="action-desc">We'll send a password reset link to your email address.</p>
            </div>
            <button
              class="btn btn-outline"
              :disabled="changingPassword"
              @click="handleChangePassword"
            >
              {{ changingPassword ? 'Sending…' : 'Send Reset Email' }}
            </button>
          </div>
          <span v-if="passwordSuccess" class="success-msg">Reset email sent! Check your inbox.</span>
          <span v-if="passwordError" class="error-msg">{{ passwordError }}</span>

          <div class="action-card" style="margin-top: 12px;">
            <div class="action-info">
              <h3 class="action-title">Log Out</h3>
              <p class="action-desc">Sign out of your account on this device.</p>
            </div>
            <button class="btn btn-outline" :disabled="loggingOut" @click="handleLogout">
              {{ loggingOut ? 'Logging out…' : 'Log Out' }}
            </button>
          </div>
        </section>

        <!-- ── Danger Zone ── -->
        <section class="settings-section danger-zone">
          <h2 class="section-heading danger-heading">Danger Zone</h2>

          <div class="action-card danger-card">
            <div class="action-info">
              <h3 class="action-title">Delete Account</h3>
              <p class="action-desc">Permanently delete your account. Your reviews will be anonymized. This cannot be undone.</p>
            </div>
            <button
              v-if="!confirmingDelete"
              class="btn btn-danger"
              @click="confirmingDelete = true"
            >
              Delete Account
            </button>
            <div v-else class="confirm-delete">
              <span class="confirm-label">Are you sure?</span>
              <button class="btn btn-danger" :disabled="deleting" @click="handleDeleteAccount">
                {{ deleting ? 'Deleting…' : 'Yes, Delete' }}
              </button>
              <button class="btn btn-outline" @click="confirmingDelete = false">Cancel</button>
            </div>
          </div>
          <span v-if="deleteError" class="error-msg">{{ deleteError }}</span>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  updateMe, resendVerify, forgotPassword,
  logout as apiLogout, deleteAccount
} from '@/api/client'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, isLoggedIn, loading, checked, refresh, clear } = useAuth()

const form = reactive({
  display_name: '',
  bio: '',
  avatar_url: '',
})

// Profile save
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref('')

// Email verification
const resending = ref(false)
const resendSuccess = ref(false)

// Password
const changingPassword = ref(false)
const passwordSuccess = ref(false)
const passwordError = ref('')

// Logout
const loggingOut = ref(false)

// Delete
const confirmingDelete = ref(false)
const deleting = ref(false)
const deleteError = ref('')

// ── Load profile ─────────────────────────────────────────────────────────────
function prefillForm(data) {
  if (!data) return
  form.display_name = data.display_name || ''
  form.bio = data.bio || ''
  form.avatar_url = data.avatar_url || ''
}

// Watch for user data to pre-fill the form
watch(user, (val) => prefillForm(val), { immediate: true })

onMounted(async () => {
  if (!checked.value) await refresh()
})

// ── Save profile ─────────────────────────────────────────────────────────────
async function saveProfile() {
  saving.value = true
  saveSuccess.value = false
  saveError.value = ''

  try {
    const { data } = await updateMe({
      display_name: form.display_name,
      bio: form.bio,
      avatar_url: form.avatar_url || null,
    })
    // Refresh shared auth state so the header picks up changes
    await refresh()
    saveSuccess.value = true
    setTimeout(() => (saveSuccess.value = false), 3000)
  } catch (err) {
    saveError.value = err.response?.data?.detail || 'Failed to save'
  } finally {
    saving.value = false
  }
}

// ── Resend verification ──────────────────────────────────────────────────────
async function handleResendVerify() {
  resending.value = true
  resendSuccess.value = false
  try {
    await resendVerify()
    resendSuccess.value = true
    setTimeout(() => (resendSuccess.value = false), 5000)
  } catch {
    // Silently fail
  } finally {
    resending.value = false
  }
}

// ── Change password (sends reset email) ──────────────────────────────────────
async function handleChangePassword() {
  changingPassword.value = true
  passwordSuccess.value = false
  passwordError.value = ''
  try {
    await forgotPassword(user.value.email)
    passwordSuccess.value = true
    setTimeout(() => (passwordSuccess.value = false), 5000)
  } catch {
    passwordError.value = 'Could not send reset email'
  } finally {
    changingPassword.value = false
  }
}

// ── Logout ───────────────────────────────────────────────────────────────────
async function handleLogout() {
  loggingOut.value = true
  try {
    await apiLogout()
  } catch {
    // Token may already be invalid — that's fine
  }
  clear()
  router.push({ name: 'Home' })
}

// ── Delete account ───────────────────────────────────────────────────────────
async function handleDeleteAccount() {
  deleting.value = true
  deleteError.value = ''
  try {
    await deleteAccount()
    clear()
    router.push({ name: 'Home' })
  } catch (err) {
    deleteError.value = err.response?.data?.detail || 'Failed to delete account'
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.settings-page { min-height: 100vh; background: var(--color-bg); padding: 32px 24px 64px; }
.settings-container { max-width: 720px; margin: 0 auto; }
.settings-title { font-size: 28px; font-weight: 700; color: var(--color-text); margin-bottom: 32px; }

/* ── Sections ── */
.settings-section { margin-bottom: 36px; }
.section-heading {
  font-size: 16px; font-weight: 600; color: var(--color-text-muted);
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px;
}

/* ── Profile card ── */
.profile-card {
  display: flex; gap: 24px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px; padding: 24px;
}
.avatar-area { flex-shrink: 0; }
.avatar-large {
  width: 80px; height: 80px; border-radius: 50%;
  background: var(--color-border);
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-muted); overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.profile-fields { flex: 1; display: flex; flex-direction: column; gap: 16px; }
.field-actions { display: flex; align-items: center; gap: 12px; }

/* ── Info grid ── */
.info-grid {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px; padding: 20px 24px;
  display: flex; flex-direction: column; gap: 14px;
}
.info-item { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.info-label { font-size: 13px; font-weight: 500; color: var(--color-text-muted); min-width: 120px; }
.info-value { font-size: 14px; color: var(--color-text); }
.info-value.verified   { color: var(--color-success); }
.info-value.unverified { color: var(--color-warning); }

/* ── Action cards ── */
.action-card {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px; padding: 18px 24px;
}
.action-info { flex: 1; }
.action-title { font-size: 15px; font-weight: 600; color: var(--color-text); margin: 0 0 4px; }
.action-desc { font-size: 13px; color: var(--color-text-muted); margin: 0; }

/* ── Danger zone ── */
.danger-heading { color: var(--color-danger); }
.danger-card { border-color: rgba(239,68,68,0.3); }
.confirm-delete { display: flex; align-items: center; gap: 8px; }
.confirm-label { font-size: 13px; color: var(--color-warning); font-weight: 500; }

/* ── Auth prompt ── */
.auth-buttons { display: flex; gap: 12px; margin-top: 8px; }

/* ── Responsive ── */
@media (max-width: 640px) {
  .profile-card { flex-direction: column; align-items: center; text-align: center; }
  .action-card { flex-direction: column; align-items: flex-start; }
  .info-item { flex-direction: column; align-items: flex-start; gap: 4px; }
}
</style>
