/**
 * useCaptcha.js — Centralized reCAPTCHA v2 Invisible Composable
 * ══════════════════════════════════════════════════════════════════════════════
 * PURPOSE:
 *   Provides a single, reusable interface for reCAPTCHA across the entire app.
 *   Any form that needs bot protection just calls:
 *
 *     const { execute } = useCaptcha('recaptcha-login')
 *     const token = await execute()           // silent for humans, challenge for bots
 *
 * MULTI-LAYER VERIFICATION:
 *   Layer 1 — Invisible analysis: reCAPTCHA silently evaluates mouse movement,
 *             browsing patterns, and device signals. Legitimate users pass instantly.
 *   Layer 2 — Visual challenge: If the invisible score is ambiguous, Google
 *             automatically shows an image/click/drag challenge.
 *
 * INFRASTRUCTURE:
 *   • Script loaded lazily — only fetched on first use, not on page load.
 *   • Singleton pattern — the reCAPTCHA JS is loaded once no matter how
 *     many components call useCaptcha().
 *   • Site key from env (VITE_RECAPTCHA_SITE_KEY) with fallback.
 *   • Each form gets its own widget instance via a unique container ID.
 *
 * USAGE IN A PAGE:
 *   <template>
 *     <form @submit.prevent="onSubmit">
 *       ...fields...
 *       <div :id="containerId"></div>   ← invisible widget anchor
 *     </form>
 *   </template>
 *
 *   <script setup>
 *   import useCaptcha from '@/composables/useCaptcha'
 *   const { containerId, execute } = useCaptcha('recaptcha-login')
 *
 *   async function onSubmit() {
 *     const token = await execute()
 *     await login(user, pass, token)  // send token to backend
 *   }
 *   </script>
 * ══════════════════════════════════════════════════════════════════════════════
 */

// ── Configuration ────────────────────────────────────────────────────────────
const SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '6LfjM3AsAAAAAHRcfPYW3kGl9XLcawICgGwSjQlE'
const SCRIPT_URL = 'https://www.google.com/recaptcha/api.js?onload=onRecaptchaLoaded&render=explicit'

// ── Singleton script loader ──────────────────────────────────────────────────
let scriptPromise = null     // resolves when grecaptcha is ready
let grecaptchaReady = false

function loadRecaptchaScript() {
  if (scriptPromise) return scriptPromise

  scriptPromise = new Promise((resolve) => {
    // If already loaded (e.g. from a CDN in index.html), resolve immediately
    if (window.grecaptcha && window.grecaptcha.render) {
      grecaptchaReady = true
      resolve()
      return
    }

    // Global callback that reCAPTCHA calls once the library is ready
    window.onRecaptchaLoaded = () => {
      grecaptchaReady = true
      resolve()
    }

    const script = document.createElement('script')
    script.src = SCRIPT_URL
    script.async = true
    script.defer = true
    document.head.appendChild(script)
  })

  return scriptPromise
}


// ── Composable ───────────────────────────────────────────────────────────────
/**
 * @param {string} containerId  — unique DOM id for the invisible widget (e.g. 'recaptcha-login')
 * @returns {{ containerId: string, execute: () => Promise<string> }}
 */
export default function useCaptcha(containerId = 'recaptcha-container') {
  let widgetId = null

  /**
   * Render the invisible widget into the container element.
   * Called once, on the first execute() invocation.
   */
  function renderWidget(resolve, reject) {
    const el = document.getElementById(containerId)
    if (!el) {
      reject(new Error(`reCAPTCHA container #${containerId} not found in DOM`))
      return
    }

    try {
      widgetId = window.grecaptcha.render(containerId, {
        sitekey: SITE_KEY,
        size: 'invisible',
        callback: (token) => resolve(token),
        'error-callback': () => reject(new Error('reCAPTCHA challenge failed')),
        'expired-callback': () => reject(new Error('reCAPTCHA token expired, please try again')),
      })
      // Kick off the invisible check immediately after rendering
      window.grecaptcha.execute(widgetId)
    } catch (err) {
      reject(err)
    }
  }

  /**
   * Execute the invisible captcha. Returns a token string.
   * – First call: loads script + renders widget + executes.
   * – Subsequent calls: resets and re-executes.
   * – If user is suspicious, Google shows a visual challenge automatically.
   */
  function execute() {
    return new Promise(async (resolve, reject) => {
      try {
        await loadRecaptchaScript()
      } catch (err) {
        // Script load failed — fail open so users aren't blocked
        resolve('')
        return
      }

      if (widgetId !== null) {
        // Widget already rendered — reset and re-execute
        try {
          // Re-bind callback for this execution
          window.grecaptcha.reset(widgetId)
          // We need to re-render to bind a new callback, so destroy and recreate
          const el = document.getElementById(containerId)
          if (el) el.innerHTML = ''
          widgetId = null
          renderWidget(resolve, reject)
        } catch (err) {
          reject(err)
        }
      } else {
        renderWidget(resolve, reject)
      }
    })
  }

  return {
    containerId,
    execute,
    /** Expose for testing */
    get siteKey() { return SITE_KEY },
  }
}

/**
 * Check if reCAPTCHA is configured (site key is present).
 * Components can use this to conditionally render the container.
 */
export function isCaptchaEnabled() {
  return !!SITE_KEY
}
