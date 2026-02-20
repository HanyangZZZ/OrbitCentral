/**
 * useUserLocation.js — Browser Geolocation Composable (Singleton)
 * =================================================================
 * PURPOSE:
 *   Gets the user's real-world location using the browser's Geolocation
 *   API, then reverse-geocodes it into a human-readable label like
 *   "Queen West, Toronto" using OpenStreetMap's free Nominatim service.
 *
 * MODULAR LOGIC:
 *   Singleton pattern (same as useAuth) — the location refs are
 *   module-level, so every component shares the same coordinates.
 *   Once we've detected the location, we don't re-detect unless asked.
 *
 * OOP FLOW:
 *   Component calls detect() → browser prompts for permission →
 *   Geolocation API returns lat/lng → Nominatim returns city/suburb →
 *   label ref updates → NearbyForYou shows "Near Queen West, Toronto"
 *
 * WHY SINGLETON:
 *   We only want to ask for location permission ONCE. If NearbyForYou
 *   and SearchPage both need location, they share the same result.
 */
import { ref, readonly } from 'vue'

// ── Singleton state (shared across all consumers) ────────────────────────────
const latitude    = ref(null)
const longitude   = ref(null)
const label       = ref('Your Location')   // human-readable
const loading     = ref(false)
const error       = ref(null)
const resolved    = ref(false)              // true once we've attempted geolocation

// ── Reverse geocode via Nominatim ────────────────────────────────────────────
async function reverseGeocode(lat, lng) {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&zoom=14&addressdetails=1`
    const res = await fetch(url, {
      headers: { 'Accept-Language': 'en' }   // English results
    })
    const data = await res.json()
    const addr = data.address || {}

    // Build a short, readable label: neighbourhood / suburb + city
    const neighbourhood = addr.neighbourhood || addr.suburb || addr.hamlet || addr.village || ''
    const city          = addr.city || addr.town || addr.municipality || ''

    if (neighbourhood && city) return `${neighbourhood}, ${city}`
    if (city) return city
    if (neighbourhood) return neighbourhood
    // Fallback to the one-line display_name (first two parts)
    if (data.display_name) {
      return data.display_name.split(',').slice(0, 2).join(',').trim()
    }
    return 'Your Location'
  } catch {
    return 'Your Location'
  }
}

// ── Request location ─────────────────────────────────────────────────────────
async function requestLocation() {
  if (!navigator.geolocation) {
    error.value = 'Geolocation is not supported by your browser'
    return
  }

  loading.value = true
  error.value   = null

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        latitude.value  = position.coords.latitude
        longitude.value = position.coords.longitude
        console.log('[UserLocation] Got coords:', latitude.value, longitude.value)
        label.value     = await reverseGeocode(latitude.value, longitude.value)
        console.log('[UserLocation] Nominatim label:', label.value)
        loading.value   = false
        resolved.value  = true
        resolve(true)
      },
      (err) => {
        console.warn('[UserLocation] Geolocation error:', err.code, err.message)
        error.value   = err.message || 'Location permission denied'
        loading.value = false
        resolved.value = true
        resolve(false)
      },
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 300_000 }
    )
  })
}

// ── Public composable ────────────────────────────────────────────────────────
export function useUserLocation() {
  return {
    latitude:  readonly(latitude),
    longitude: readonly(longitude),
    label:     readonly(label),
    loading:   readonly(loading),
    error:     readonly(error),
    resolved:  readonly(resolved),
    requestLocation,
  }
}
