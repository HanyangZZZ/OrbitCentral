<!--
  AppHeader.vue — Global Sticky Navigation Bar
  ─────────────────────────────────────────────────────────────────────────────
  Persistent header rendered on every page via App.vue.

  LAYOUT (left → right)
  ┌──────────────────────────────────────────────────────────┐
  │  Logo │  Search Bar (optional)  │  Discover  About  👤  │
  └──────────────────────────────────────────────────────────┘

  KEY FEATURES
  • `hideSearch` prop — when true the search bar is hidden (used on HomePage
    which has its own HeroSearch).
  • Search bar syncs with route query `?q=` so the value persists across
    navigation. Submitting always pushes to SearchPage.
  • Profile dropdown (logged in): Account Settings, Favorites, Coupons,
    Missions, Log Out. Uses a click-away overlay (z-index 99) so clicking
    outside closes the menu.
  • Auth state comes from the shared `useAuth()` singleton composable.

  MODULAR FLOW
    useAuth → user/isLoggedIn reactive refs
    Router → push to Search on submit, push to Login/Home on logout
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <header class="app-header">
    <!-- Left: Logo -->
    <router-link to="/" class="logo">
      <span class="logo-text">Orbit</span>
    </router-link>

    <!-- Center: Search bar (hidden on pages with their own search, e.g. HomePage) -->
    <form v-if="!hideSearch" class="search-bar" @submit.prevent="onSearch">
      <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input
        v-model="query"
        type="text"
        placeholder="Search businesses, cuisines, vibes…"
        class="search-input"
        @focus="onSearchFocus"
      />
    </form>

    <!-- Right group: Nav links + Profile -->
    <div class="header-right">
      <!-- Nav links -->
      <router-link to="/search" class="nav-link">Discover</router-link>
      <router-link to="/about" class="nav-link">About</router-link>

      <!-- Auth area -->
      <div v-if="isLoggedIn" class="profile-wrapper" ref="profileRef">
        <button class="profile-btn" @click="toggleProfileMenu">
          <div class="avatar-placeholder" :class="{ active: profileMenuOpen }">
            <img v-if="user?.avatar_url" :src="user.avatar_url" alt="Avatar" class="avatar-img" />
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
        </button>

        <Transition name="dropdown">
          <div v-if="profileMenuOpen" class="profile-dropdown">
            <!-- User info row -->
            <div class="dropdown-user">
              <span class="dropdown-username">{{ user?.display_name || user?.username }}</span>
              <span class="dropdown-email">{{ user?.email }}</span>
            </div>
            <div class="dropdown-divider" />

            <router-link to="/profile" class="dropdown-item" @click="profileMenuOpen = false">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <span>Account Settings</span>
            </router-link>
            <router-link to="/bookmarks" class="dropdown-item" @click="profileMenuOpen = false">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              <span>Favorites</span>
            </router-link>
            <button class="dropdown-item" @click="openCoupons">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
              <span>Coupons</span>
            </button>
            <router-link to="/missions" class="dropdown-item" @click="profileMenuOpen = false">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>
              <span>Missions</span>
            </router-link>

            <div class="dropdown-divider" />
            <button class="dropdown-item dropdown-logout" @click="handleLogout">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              <span>Log Out</span>
            </button>
          </div>
        </Transition>
      </div>

      <!-- Not logged in: show Login / Sign Up -->
      <div v-else class="auth-links">
        <router-link to="/login" class="nav-link">Log In</router-link>
        <router-link to="/register" class="btn-signup">Sign Up</router-link>
      </div>
    </div>

    <!-- Click-away overlay to close profile dropdown -->
    <div v-if="profileMenuOpen" class="click-away" @click="profileMenuOpen = false" />
  </header>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { logout as apiLogout } from '@/api/client'

const props = defineProps({
  initialQuery: { type: String, default: '' },
  hideSearch: { type: Boolean, default: false }
})

const emit = defineEmits(['search'])

const router = useRouter()
const route = useRoute()

const query = ref(props.initialQuery)

// Keep header search bar in sync with route ?q= param
watch(() => route.query.q, (newQ) => {
  query.value = newQ || ''
})

// ── Auth state ───────────────────────────────────────────────────────────────
const { user, isLoggedIn, checked, refresh, clear } = useAuth()

onMounted(() => {
  if (!checked.value) refresh()
})

// ── Profile dropdown ─────────────────────────────────────────────────────────
const profileMenuOpen = ref(false)

function toggleProfileMenu() {
  profileMenuOpen.value = !profileMenuOpen.value
}

function openCoupons() {
  profileMenuOpen.value = false
  router.push({ name: 'Coupons' })
}

async function handleLogout() {
  profileMenuOpen.value = false
  try { await apiLogout() } catch { /* token may be invalid */ }
  clear()
  router.push({ name: 'Home' })
}

function onSearch() {
  const q = query.value.trim()
  if (!q) return

  // Always push route — SearchPage watches route.query.q for changes.
  // Add a timestamp param so a re-search of the same term still triggers a refresh.
  router.push({ name: 'Search', query: { q, t: Date.now() } })
}

function onSearchFocus() {
  // If user focuses the search bar and we're not on SearchPage, navigate there
  if (route.name !== 'Search') {
    router.push({ name: 'Search', query: query.value.trim() ? { q: query.value.trim() } : {} })
  }
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  padding: 10px 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(15,23,42,0.04);
}

/* ── Left group: profile + nav ── */
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: auto;
}

/* ── 1. Logo (left-aligned) ── */
.logo {
  text-decoration: none;
  flex-shrink: 0;
}
.logo-text {
  font-family: var(--font-brand, 'Barlow', sans-serif);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--color-primary);
}

/* ── 2. Search bar (centered) ── */
.search-bar {
  flex: 1;
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--search-bg);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-bar:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(74,112,169,0.12);
}
.search-icon {
  flex-shrink: 0;
  color: var(--search-icon-color);
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--search-text-color);
  padding: 10px 0;
  font-size: 14px;
  outline: none;
}
.search-input::placeholder {
  color: var(--search-placeholder-color);
}

/* ── 4 & 5. Nav links ── */
.nav-link {
  font-family: var(--font-ui);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
  flex-shrink: 0;
  white-space: nowrap;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
  background: rgba(74,112,169,0.06);
}

/* ── 6. Profile dropdown ── */
.profile-wrapper {
  position: relative;
  flex-shrink: 0;
  z-index: 101;
}
.profile-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}
.avatar-placeholder {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-bg-warm, #efece3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  transition: background 0.2s, box-shadow 0.2s;
}
.avatar-placeholder:hover,
.avatar-placeholder.active {
  box-shadow: 0 0 0 2px var(--color-primary);
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

/* Dropdown panel */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 6px 0;
  box-shadow: var(--shadow-lg, 0 8px 28px rgba(15,23,42,0.12));
  z-index: 200;
}
.dropdown-user {
  padding: 10px 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dropdown-username {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}
.dropdown-email {
  font-size: 12px;
  color: var(--color-text-muted);
}
.dropdown-divider {
  height: 1px;
  background: var(--color-border);
  margin: 4px 0;
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  background: none;
  border: none;
  color: var(--color-text-light, #475569);
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.dropdown-item:hover {
  background: rgba(74,112,169,0.06);
  color: var(--color-text);
}
.dropdown-item svg {
  flex-shrink: 0;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Click-away overlay */
.click-away {
  position: fixed;
  inset: 0;
  z-index: 99;
}

/* Logout item */
.dropdown-logout {
  color: var(--color-danger);
}
.dropdown-logout:hover {
  background: rgba(239, 68, 68, 0.06);
  color: var(--color-danger);
}

/* ── Auth links (logged out) ── */
.auth-links {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.btn-signup {
  display: inline-flex;
  align-items: center;
  padding: 7px 16px;
  background: var(--color-primary);
  color: #fff;
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s;
}
.btn-signup:hover {
  background: var(--color-primary-hover);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .app-header {
    padding: 10px 12px;
  }
  .nav-link {
    font-size: 13px;
    padding: 6px 8px;
  }
  .search-bar {
    max-width: none;
  }
}

@media (max-width: 480px) {
  .header-right .nav-link {
    display: none;
  }
}
</style>
