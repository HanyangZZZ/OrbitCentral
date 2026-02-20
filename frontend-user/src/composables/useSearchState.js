/**
 * useSearchState.js — Centralized Search Page State
 * ====================================================
 * PURPOSE:
 *   Single source of truth for everything on the Search page:
 *   the search query, active filters, business results, pagination,
 *   and UI flags (loading, errors, etc.).
 *
 * MODULAR LOGIC:
 *   This composable ONLY handles state — no API calls. The companion
 *   useSearchApi.js handles actually fetching data. This separation
 *   (state vs. side effects) makes both easier to understand and test.
 *
 * OOP FLOW:
 *   SearchPage.vue → useSearchState() for reactive data →
 *   useSearchApi() reads/writes this state when fetching →
 *   FilterBar/CategorySidebar modify filters via this state.
 *
 * KEY CONCEPTS:
 *   - isSearchMode: true when user typed a query (vs just browsing)
 *   - filteredBusinesses: applies client-side rating filter on top
 *     of whatever the server returned
 *   - Route sync: query/category/tag params stay in the URL so
 *     users can share or bookmark search results
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useSearchState() {
  const route  = useRoute()
  const router = useRouter()

  // ── Query & filters ────────────────────────────────────────────────────
  const searchQuery      = ref(route.query.q || '')
  // Read category from route query (if present), convert to number
  const initialCategory  = route.query.category ? Number(route.query.category) : null
  const selectedCategory = ref(initialCategory)
  const sortOrder        = ref('')
  const minRating        = ref(0)

  // ── Tags ───────────────────────────────────────────────────────────────
  const suggestedTags  = ref([])   // GET /api/tags/search/
  const selectedTagIds = ref([])   // user-toggled subset

  // ── Data ───────────────────────────────────────────────────────────────
  const businesses  = ref([])
  const totalCount  = ref(0)
  const nextPageUrl = ref(null)

  // ── UI flags ───────────────────────────────────────────────────────────
  const loading     = ref(false)
  const loadingMore = ref(false)
  const error       = ref('')

  // ── Derived ────────────────────────────────────────────────────────────
  const isSearchMode = computed(() => !!searchQuery.value)

  const sortOptions = computed(() => {
    const base = [
      { value: '',               label: 'Default' },
      { value: '-avg_rating',    label: 'Highest Rated' },
      { value: '-review_count',  label: 'Most Reviewed' },
    ]
    if (isSearchMode.value) {
      base.push({ value: 'distance', label: 'Nearest' })
      base.push({ value: 'rating',   label: 'Best Rated' })
    }
    return base
  })

  /** Businesses filtered by the client-side min-rating slider. */
  const filteredBusinesses = computed(() => {
    if (minRating.value <= 0) return businesses.value
    return businesses.value.filter(b => (Number(b.avg_rating) || 0) >= minRating.value)
  })

  // ── Route sync ─────────────────────────────────────────────────────────
  function syncQueryToRoute(q) {
    router.replace({ query: { ...route.query, q } })
  }

  /** Reset transient filters (called on new search). */
  function resetFilters() {
    selectedTagIds.value = []
    sortOrder.value      = ''
    minRating.value      = 0
  }

  return {
    // Refs
    searchQuery, selectedCategory, sortOrder, minRating,
    suggestedTags, selectedTagIds,
    businesses, totalCount, nextPageUrl,
    loading, loadingMore, error,
    // Computed
    isSearchMode, sortOptions, filteredBusinesses,
    // Methods
    syncQueryToRoute, resetFilters,
  }
}
