/**
 * useCaptcha.js — reCAPTCHA v3 Composable
 * ══════════════════════════════════════════════════════════════════════════════
 * PURPOSE:
 *   Provides a single, reusable interface for reCAPTCHA v3 across the app.
 *   Any form that needs bot protection just calls:
 *
 *     const { execute } = useCaptcha()
 *     const token = await execute('login')    // 100% invisible, no UI needed
 *
 * HOW IT WORKS:
 *   reCAPTCHA v3 runs entirely in the background — no widget, no challenge,
 *   no user interaction. Google scores each request from 0.0 (bot) to 1.0
 *   (human). The backend checks `score >= threshold` (default 0.5).
 *
 *   The `action` string (e.g. 'login', 'register') is sent to Google so
 *   the backend can verify the token was generated for the correct form.
 *
 * INFRASTRUCTURE:
 *   • Script loaded lazily — only fetched on first execute(), not on page load.
 *   • Singleton pattern — the reCAPTCHA JS is loaded once for all callers.
 *   • Site key from env (VITE_RECAPTCHA_SITE_KEY) with fallback.
 *   • No DOM elements needed (v3 is fully invisible).
 *
 * USAGE IN A PAGE:
 *   <script setup>
 *   import useCaptcha from '@/composables/useCaptcha'
 *   const { execute } = useCaptcha()
 *
 *   async function onSubmit() {
 *     const token = await execute('login')
 *     await login(user, pass, token)
 *   }
 *   </script>
 * ══════════════════════════════════════════════════════════════════════════════
 */

// ── Configuration ────────────────────────────────────────────────────────────
const SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '6Lda7XcsAAAAACWfEzuG3qKVSCMdPCwqNWA5_jaL'

// ── Singleton script loader ──────────────────────────────────────────────────
let scriptPromise = null

function loadRecaptchaScript() {
  if (scriptPromise) return scriptPromise

  scriptPromise = new Promise((resolve, reject) => {
    // Already loaded (e.g. from a previous call)
    if (window.grecaptcha && window.grecaptcha.execute) {
      resolve()
      return
    }

    const script = document.createElement('script')
    // v3 uses render=SITE_KEY (not render=explicit)
    script.src = `https://www.google.com/recaptcha/api.js?render=${SITE_KEY}`
    script.async = true
    script.defer = true
    script.onload = () => {
      // grecaptcha.ready fires once the library is fully initialized
      window.grecaptcha.ready(() => resolve())
    }
    script.onerror = () => reject(new Error('Failed to load reCAPTCHA script'))
    document.head.appendChild(script)
  })

  return scriptPromise
}

// ── Composable ───────────────────────────────────────────────────────────────
/**
 * @returns {{ execute: (action: string) => Promise<string> }}
 */
export default function useCaptcha() {
  /**
   * Execute reCAPTCHA v3 for the given action.
   * Returns a token string to send to the backend.
   *
   * @param {string} action — e.g. 'login', 'register', 'forgot_password'
   */
  async function execute(action = 'submit') {
    try {
      await loadRecaptchaScript()
      const token = await window.grecaptcha.execute(SITE_KEY, { action })
      return token
    } catch (err) {
      console.warn('reCAPTCHA execute failed, proceeding without token:', err)
      // Fail open — don't block users if reCAPTCHA script fails
      return ''
    }
  }

  return { execute }
}

/**
 * Check if reCAPTCHA is configured (site key is present).
 */
export function isCaptchaEnabled() {
  return !!SITE_KEY
}
