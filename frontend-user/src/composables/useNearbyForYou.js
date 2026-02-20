/**
 * useNearbyForYou.js — Personalized Recommendations Engine
 * ==========================================================
 * PURPOSE:
 *   Powers the "Nearby For You" section on the homepage. Tries the
 *   AI personalization API first, then falls back to time-based search.
 *
 * MODULAR LOGIC:
 *   This is the most complex composable — it coordinates:
 *   1. User geolocation (via useUserLocation)
 *   2. AI personalization (analyzes reviews + bookmarks via GPT)
 *   3. Fallback search (time-based like "coffee" in the morning)
 *   4. Reverse geocoding (lat/lng → "Queen West, Toronto")
 *
 *   The fallback chain ensures SOMETHING always shows up, even if
 *   the user isn't logged in or geolocation is denied.
 *
 * OOP FLOW:
 *   HomePage mounts → useNearbyForYou().load() →
 *   detect location → try AI API → if fails, search by time context →
 *   return businesses + contextual message for the UI.
 *
 * FALLBACK STRATEGY:
 *   AI personalized → time-based search → empty state with message
 */
import { ref, computed, watch } from 'vue'
import {
  getPersonalized,
  reverseGeocode as apiReverseGeocode,
  searchBusinesses,
  getSavedToken,
} from '@/api/client'
import { getTimeContext } from '@/config/homepage'
import { useUserLocation } from './useUserLocation'
import { useAuth } from './useAuth'

export function useNearbyForYou() {
  const recommendations = ref([])
  const aiMessage = ref('')
  const aiQuery = ref('')
  const locationLabel = ref('')
  const loading = ref(false)
  const error = ref('')

  const { user, isLoggedIn } = useAuth()
  const {
    latitude, longitude,
    label: browserLocationLabel,
    resolved: locationResolved,
    error: locationError,
    requestLocation,
  } = useUserLocation()

  const locationDenied = computed(() => !!locationError.value)

  // If the browser label updates later (Nominatim resolves after our fetch),
  // and we still have no locationLabel, adopt it.
  watch(browserLocationLabel, (newLabel) => {
    if (!locationLabel.value && newLabel && newLabel !== 'Your Location') {
      locationLabel.value = newLabel
    }
  })

  // ── Get user location ──────────────────────────────────────────────────────
  // Default: Toronto (most businesses in the DB are Ontario-based)
  const DEFAULT_LOCATION = { lat: 43.6532, lng: -79.3832 }

  async function getUserLocation() {
    console.log('[Location] getUserLocation — resolved:', locationResolved.value,
      'lat:', latitude.value, 'lng:', longitude.value)
    if (!locationResolved.value) {
      console.log('[Location] Requesting browser geolocation…')
      await requestLocation()
      console.log('[Location] After requestLocation — lat:', latitude.value,
        'lng:', longitude.value, 'error:', locationError.value)
    }
    if (latitude.value && longitude.value) {
      return { lat: latitude.value, lng: longitude.value }
    }
    console.warn('[Location] No coordinates — using default (Toronto)')
    return DEFAULT_LOCATION
  }

  // ── Reverse geocode via our API (falls back to Nominatim) ───────────────────
  async function fetchLocationLabel(lat, lng) {
    // 1. Try our backend geocode API
    try {
      const { data } = await apiReverseGeocode(lat, lng)
      if (data.city) {
        locationLabel.value = data.province_code || data.province
          ? `${data.city}, ${data.province_code || data.province}`
          : data.city
        console.log('[Location] Backend geocode:', locationLabel.value)
        return
      }
    } catch (e) {
      console.warn('[Location] Backend geocode failed:', e?.response?.status || e?.message)
    }

    // 2. Fallback: use the Nominatim label from useUserLocation (may already be resolved)
    const nomLabel = browserLocationLabel.value
    if (nomLabel && nomLabel !== 'Your Location') {
      locationLabel.value = nomLabel
      console.log('[Location] Browser Nominatim label:', locationLabel.value)
      return
    }

    // 3. Last resort: direct Nominatim reverse geocode
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&zoom=14&addressdetails=1`
      const res = await fetch(url, {
        headers: { 'Accept-Language': 'en', 'User-Agent': 'OrbitApp/1.0' }
      })
      if (!res.ok) throw new Error(`Nominatim HTTP ${res.status}`)
      const json = await res.json()
      const addr = json.address || {}
      const city = addr.city || addr.town || addr.municipality || ''
      const area = addr.neighbourhood || addr.suburb || ''
      if (area && city) { locationLabel.value = `${area}, ${city}`; return }
      if (city) { locationLabel.value = city; return }
      // If Nominatim returned something but no city, try display_name
      if (json.display_name) {
        locationLabel.value = json.display_name.split(',').slice(0, 2).join(',').trim()
        console.log('[Location] Nominatim display_name:', locationLabel.value)
        return
      }
    } catch (e) {
      console.warn('[Location] Nominatim direct fetch failed:', e?.message)
    }

    // All methods failed
    locationLabel.value = ''
    console.warn('[Location] All geocode methods failed')
  }

  // ── Generate humanized message ───────────────────────────────────────────────
  function generateMessage(businesses) {
    const { period } = getTimeContext()
    const loc = locationLabel.value

    if (!businesses.length) {
      return loc
        ? `Finding the best spots for you in ${loc}...`
        : `Finding the best spots near you...`
    }

    const bizA = `**${businesses[0]?.name || 'a great spot'}**`
    const bizB = businesses[1] ? `**${businesses[1].name}**` : null
    const inLoc = loc ? ` in ${loc}` : ''

    const templates = {
      morning:   bizB
        ? `Good morning${inLoc}! Great day to grab a warm drink at ${bizA}, and maybe a pastry from ${bizB} on the way.`
        : `Good morning${inLoc}! Great day to start with a warm drink at ${bizA}.`,
      lunch:     bizB
        ? `Lunchtime${inLoc}! ${bizA} has been getting great reviews. Or if you want something lighter, ${bizB} is nearby too.`
        : `Lunchtime${inLoc}! ${bizA} has been getting great reviews, worth checking out.`,
      afternoon: bizB
        ? `Good afternoon${inLoc}! How about ${bizA}, then a stop at ${bizB} after?`
        : `Good afternoon${inLoc}! ${bizA} could be a nice pick-me-up right now.`,
      evening:   bizB
        ? `Good evening${inLoc}! Dinner at ${bizA}? Then you could check out ${bizB} to wind down.`
        : `Good evening${inLoc}! ${bizA} looks like a solid dinner spot tonight.`,
      night:     bizB
        ? `Still up${inLoc}? ${bizA} is open late, or try ${bizB} for some late-night vibes.`
        : `Still up${inLoc}? ${bizA} is open late if you need a bite.`,
    }

    return templates[period] || templates.evening
  }

  // ── Main fetch function ────────────────────────────────────────────────────
  async function fetchRecommendations() {
    loading.value = true
    error.value = ''

    try {
      // 1. Get location
      console.log('[NearbyForYou] Starting fetchRecommendations…')
      const location = await getUserLocation()
      console.log('[NearbyForYou] Location result:', location)

      // Fetch city label via reverse geocode API (await so it's ready for display)
      console.log('[NearbyForYou] Calling fetchLocationLabel…')
      await fetchLocationLabel(location.lat, location.lng)
      console.log('[NearbyForYou] locationLabel after geocode:', locationLabel.value)

      // 2. Try personalized API if authenticated
      const token = getSavedToken()
      let isPersonalized = false

      if (token && isLoggedIn.value) {
        try {
          const params = {
            limit: 3,
            lat: location.lat,
            lng: location.lng,
          }
          const { data } = await getPersonalized(params)
          recommendations.value = (data.results || []).slice(0, 3)
          aiQuery.value = data.query || ''
          isPersonalized = true
        } catch (personalizedErr) {
          // 400 = no activity, 403 = not verified — fall through to search
          console.warn('Personalized API unavailable, falling back to search:', personalizedErr?.response?.status)
        }
      }

      // 3. Fallback: time-based search
      if (!isPersonalized || recommendations.value.length === 0) {
        const timeContext = getTimeContext()
        const searchParams = {
          q: timeContext.queries[0],
          limit: 3,
          lat: location.lat,
          lng: location.lng,
        }
        const { data: results } = await searchBusinesses(searchParams)
        recommendations.value = (results || []).slice(0, 3)
        aiQuery.value = ''
      }

      // 4. Generate message
      aiMessage.value = generateMessage(recommendations.value)

    } catch (err) {
      console.error('Failed to fetch recommendations:', err)
      error.value = 'Unable to load recommendations'
      aiMessage.value = ''
    } finally {
      loading.value = false
    }
  }

  // ── Computed ───────────────────────────────────────────────────────────────
  const hasRecommendations = computed(() => recommendations.value.length > 0)
  const timeContext = computed(() => getTimeContext())
  const userLocation = computed(() =>
    latitude.value && longitude.value ? { lat: latitude.value, lng: longitude.value } : null
  )

  return {
    recommendations,
    aiMessage,
    aiQuery,
    locationLabel,
    loading,
    error,
    userLocation,
    locationDenied,
    hasRecommendations,
    timeContext,
    fetchRecommendations,
    user,
    isLoggedIn,
  }
}
