/**
 * useAuth.js — Singleton Authentication Composable
 * ==================================================
 * PURPOSE:
 *   Manages global auth state (who's logged in, their profile data).
 *   Any component can call useAuth() to check login status or get
 *   user info — they all share the exact same reactive data.
 *
 * MODULAR LOGIC:
 *   This uses the "Singleton Pattern" — the refs (user, isLoggedIn, etc.)
 *   are declared at the MODULE level (outside the function), so every
 *   component that calls useAuth() gets the SAME refs, not copies.
 *   This is how Vue composables share global state without Vuex/Pinia.
 *
 * OOP FLOW:
 *   App boots → useAuth().refresh() checks for saved token →
 *   If valid token → fetches user from /api/auth/me/ → sets state →
 *   Components reactively update (header shows avatar, etc.)
 *
 * KEY METHODS:
 *   refresh()  — Re-fetch user from API (call after token changes)
 *   setUser()  — Directly set user data after login (skips API call)
 *   clear()    — Wipe auth state on logout
 */
import { ref, readonly } from 'vue'
import { getMe, setAuthToken, getSavedToken } from '@/api/client'

// ── Module-level state (shared across ALL components) ────────────────────
const user = ref(null)          // The current user object from the API
const isLoggedIn = ref(false)   // Whether a user is authenticated
const loading = ref(false)      // True while checking auth status
const checked = ref(false)      // True once we've attempted to load user

/** Fetch the current user from /api/auth/me/ using the saved token. */
async function refresh() {
  const token = getSavedToken()
  if (!token) {
    user.value = null
    isLoggedIn.value = false
    checked.value = true
    return
  }

  loading.value = true
  try {
    const { data } = await getMe()
    user.value = data
    isLoggedIn.value = true
  } catch {
    // Token invalid or expired
    user.value = null
    isLoggedIn.value = false
    setAuthToken(null)
  } finally {
    loading.value = false
    checked.value = true
  }
}

/** Set user after login/register (avoids an extra API call). */
function setUser(userData, token) {
  setAuthToken(token)
  user.value = userData
  isLoggedIn.value = true
  checked.value = true
}

/** Clear auth state (logout). */
function clear() {
  setAuthToken(null)
  user.value = null
  isLoggedIn.value = false
}

/**
 * The composable function — every component calls this to access auth state.
 * Returns readonly refs so components can read but not accidentally mutate.
 */
export function useAuth() {
  return {
    user:       readonly(user),
    isLoggedIn: readonly(isLoggedIn),
    loading:    readonly(loading),
    checked:    readonly(checked),
    refresh,
    setUser,
    clear,
  }
}
