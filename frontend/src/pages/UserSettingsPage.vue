<template>
  <section class="settings-page">
    <!-- Header -->
    <TopBar :show-search="false" :show-location="false" />

    <!-- Content -->
    <div class="settings-content">
      <h1 class="settings-title">Account Settings</h1>

      <!-- ─── Profile Information ─── -->
      <div class="settings-card">
        <h2 class="card-heading">Profile Information</h2>
        <p class="card-description">Manage how you appear to other users.</p>

        <div class="avatar-section">
          <div class="avatar-preview">
            <img v-if="avatarUrl" :src="avatarUrl" alt="Profile photo" class="avatar-img" />
            <div v-else class="avatar-placeholder">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="8" r="4" fill="#8fabd4"/>
                <path d="M4 20c0-3.314 3.582-6 8-6s8 2.686 8 6" fill="#8fabd4"/>
              </svg>
            </div>
          </div>
          <div class="avatar-actions">
            <button class="btn-secondary" @click="triggerUpload">Upload Photo</button>
            <button v-if="avatarUrl" class="btn-ghost" @click="avatarUrl = ''">Remove</button>
            <input ref="fileInput" type="file" accept="image/*" class="sr-only" @change="handleUpload" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Display Name</label>
          <input v-model="displayName" type="text" class="form-input" placeholder="Your display name" />
        </div>

        <div class="form-group">
          <label class="form-label">Email Address</label>
          <div class="input-row">
            <input v-model="email" type="email" class="form-input" placeholder="you@example.com" disabled />
            <span class="verified-badge">Verified</span>
          </div>
          <p class="form-hint">Contact support to change your email address.</p>
        </div>

        <button class="btn-primary" @click="saveProfile">Save Changes</button>
        <transition name="fade">
          <span v-if="profileSaved" class="save-confirmation">✓ Saved</span>
        </transition>
      </div>

      <!-- ─── Security ─── -->
      <div class="settings-card">
        <h2 class="card-heading">Security</h2>
        <p class="card-description">Keep your account safe.</p>

        <!-- Change Password -->
        <h3 class="sub-heading">Change Password</h3>
        <div class="form-group">
          <label class="form-label">Current Password</label>
          <div class="password-wrapper">
            <input
              v-model="currentPassword"
              :type="showCurrentPw ? 'text' : 'password'"
              class="form-input"
              placeholder="Enter current password"
            />
            <button class="pw-toggle" type="button" @click="showCurrentPw = !showCurrentPw" aria-label="Toggle password visibility">
              {{ showCurrentPw ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">New Password</label>
          <div class="password-wrapper">
            <input
              v-model="newPassword"
              :type="showNewPw ? 'text' : 'password'"
              class="form-input"
              placeholder="Enter new password"
            />
            <button class="pw-toggle" type="button" @click="showNewPw = !showNewPw" aria-label="Toggle password visibility">
              {{ showNewPw ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Confirm New Password</label>
          <div class="password-wrapper">
            <input
              v-model="confirmPassword"
              :type="showConfirmPw ? 'text' : 'password'"
              class="form-input"
              placeholder="Confirm new password"
            />
            <button class="pw-toggle" type="button" @click="showConfirmPw = !showConfirmPw" aria-label="Toggle password visibility">
              {{ showConfirmPw ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p v-if="passwordMismatch" class="form-error">Passwords do not match.</p>
        </div>

        <button class="btn-primary" @click="changePassword" :disabled="!canChangePassword">Update Password</button>
        <transition name="fade">
          <span v-if="passwordSaved" class="save-confirmation">✓ Password updated</span>
        </transition>

        <!-- Two-Factor Authentication -->
        <div class="divider"></div>
        <h3 class="sub-heading">Two-Factor Authentication</h3>
        <p class="card-description">Add an extra layer of security to your account.</p>

        <div class="tfa-row">
          <div class="tfa-info">
            <span class="tfa-status" :class="{ active: tfaEnabled }">
              {{ tfaEnabled ? 'Enabled' : 'Disabled' }}
            </span>
            <span class="tfa-detail">
              {{ tfaEnabled ? 'Your account is protected with 2FA.' : 'We recommend enabling 2FA for additional security.' }}
            </span>
          </div>
          <button
            class="tfa-toggle"
            :class="{ on: tfaEnabled }"
            type="button"
            role="switch"
            :aria-checked="tfaEnabled"
            @click="tfaEnabled = !tfaEnabled"
          >
            <span class="tfa-knob"></span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { TopBar } from '@/components'

// Profile
const displayName = ref('')
const email = ref('user@example.com')
const avatarUrl = ref('')
const fileInput = ref(null)
const profileSaved = ref(false)

function triggerUpload() {
  fileInput.value?.click()
}

function handleUpload(e) {
  const file = e.target.files?.[0]
  if (file) {
    avatarUrl.value = URL.createObjectURL(file)
  }
}

function saveProfile() {
  profileSaved.value = true
  setTimeout(() => { profileSaved.value = false }, 2000)
}

// Security
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showCurrentPw = ref(false)
const showNewPw = ref(false)
const showConfirmPw = ref(false)
const passwordSaved = ref(false)
const tfaEnabled = ref(false)

const passwordMismatch = computed(() => {
  return confirmPassword.value.length > 0 && newPassword.value !== confirmPassword.value
})

const canChangePassword = computed(() => {
  return currentPassword.value.length > 0
    && newPassword.value.length >= 8
    && newPassword.value === confirmPassword.value
})

function changePassword() {
  if (!canChangePassword.value) return
  passwordSaved.value = true
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  setTimeout(() => { passwordSaved.value = false }, 2000)
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  background: #fff;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  color: #0f172a;
}

/* ─── Content ─── */
.settings-content {
  width: 100%;
  max-width: 640px;
  padding: 2rem 1.5rem 4rem;
}

.settings-title {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #0f172a;
}

/* ─── Cards ─── */
.settings-card {
  background: #fff;
  border: 1px solid #efece3;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
}

.card-heading {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: #0f172a;
}

.card-description {
  font-size: 0.8125rem;
  font-weight: 200;
  color: #64748b;
  margin: 0 0 1.5rem;
}

.sub-heading {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #0f172a;
  margin: 0 0 1rem;
}

.divider {
  height: 1px;
  background: #efece3;
  margin: 2rem 0;
}

/* ─── Avatar ─── */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
}

.avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  background: #efece3;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder svg {
  width: 40px;
  height: 40px;
}

.avatar-actions {
  display: flex;
  gap: 0.75rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* ─── Form ─── */
.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 400;
  color: #0f172a;
  margin-bottom: 0.375rem;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d7d2c8;
  border-radius: 0.5rem;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #0f172a;
  background: #fff;
  outline: none;
  transition: border-color 0.15s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #4a70a9;
}

.form-input:disabled {
  background: #f8f8f8;
  color: #64748b;
  cursor: not-allowed;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-row .form-input {
  flex: 1;
}

.verified-badge {
  font-size: 0.6875rem;
  font-weight: 500;
  color: #16a34a;
  background: #f0fdf4;
  padding: 0.25rem 0.625rem;
  border-radius: 999px;
  white-space: nowrap;
}

.form-hint {
  font-size: 0.75rem;
  font-weight: 200;
  color: #94a3b8;
  margin-top: 0.375rem;
}

.form-error {
  font-size: 0.75rem;
  font-weight: 400;
  color: #dc2626;
  margin-top: 0.375rem;
}

/* ─── Password ─── */
.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper .form-input {
  padding-right: 3.5rem;
}

.pw-toggle {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.75rem;
  font-weight: 400;
  color: #4a70a9;
  cursor: pointer;
  padding: 0;
}

/* ─── Buttons ─── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1.25rem;
  background: #4a70a9;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 0.4375rem 1rem;
  background: #efece3;
  color: #0f172a;
  border: none;
  border-radius: 0.5rem;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.8125rem;
  font-weight: 400;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-secondary:hover {
  opacity: 0.85;
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  padding: 0.4375rem 1rem;
  background: transparent;
  color: #64748b;
  border: 1px solid #d7d2c8;
  border-radius: 0.5rem;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.8125rem;
  font-weight: 300;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-ghost:hover {
  opacity: 0.7;
}

.save-confirmation {
  display: inline-flex;
  align-items: center;
  margin-left: 0.75rem;
  font-size: 0.8125rem;
  font-weight: 400;
  color: #16a34a;
}

/* ─── 2FA Toggle ─── */
.tfa-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: #fafaf8;
  border-radius: 0.75rem;
}

.tfa-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tfa-status {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #64748b;
}

.tfa-status.active {
  color: #16a34a;
}

.tfa-detail {
  font-size: 0.75rem;
  font-weight: 200;
  color: #94a3b8;
}

.tfa-toggle {
  width: 2.75rem;
  height: 1.5rem;
  border-radius: 999px;
  background: #d7d2c8;
  border: none;
  padding: 0.1875rem;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  transition: background 0.2s ease;
  flex-shrink: 0;
}

.tfa-toggle.on {
  background: #4a70a9;
}

.tfa-knob {
  width: 1.125rem;
  height: 1.125rem;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s ease;
  transform: translateX(0);
}

.tfa-toggle.on .tfa-knob {
  transform: translateX(1.25rem);
}

/* ─── Transitions ─── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
