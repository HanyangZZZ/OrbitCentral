/**
 * useAiSummary.js — Client-Side Search Summary Generator
 * ========================================================
 * PURPOSE:
 *   Creates "Orbit Scout" — a natural-language insight paragraph that
 *   appears above search results. It analyzes the results client-side
 *   to tell the user what was found and why it's relevant.
 *
 * MODULAR LOGIC:
 *   This does NOT call an AI API — it's entirely client-side. It
 *   synthesizes data from search results (match quality, categories,
 *   ratings, tags, distances) into a human-readable summary.
 *
 *   Why client-side? It's instant (no API latency), free (no token
 *   costs), and the data is already available from the search response.
 *
 * OOP FLOW:
 *   SearchPage fetches results → calls generate(businesses, query, stats) →
 *   this composable builds summary text → AiSummary.vue displays it.
 */
import { ref } from 'vue'

export function useAiSummary() {
  const aiSummary = ref('')

  /**
   * Build the summary string and assign it to `aiSummary`.
   * @param {Object}   opts
   * @param {string}   opts.query    – the user's search query
   * @param {Array}    opts.results  – business objects from the search endpoint
   * @param {Array}    opts.tags     – suggested tags from /api/tags/search/
   * @param {Object?}  opts.stats    – database totals from /api/businesses/stats/
   */
  function generate({ query, results, tags = [], stats = null }) {
    if (!results.length) { aiSummary.value = ''; return }

    const parts = [
      matchQuality(query, results),
      categoryBreakdown(results),
      ratingSummary(results),
      tagInsights(tags),
      distanceHint(results),
      statsContext(stats),
    ].filter(Boolean)

    aiSummary.value = parts.join(' ') 
  }

  function clear() { aiSummary.value = '' }

  return { aiSummary, generate, clear }
}

// ── Private summariser helpers ───────────────────────────────────────────────

function matchQuality(query, results) {
  const sims = results.map(r => r.similarity).filter(Boolean)
  if (!sims.length) return null
  const top = Math.max(...sims)
  const pct = (top * 100).toFixed(0)
  if (top > 0.8) return `Great news! We found some really solid matches for "${query}" and the top pick is ${pct}% on point.`
  if (top > 0.6) return `Nice, we pulled up some good options for "${query}" (up to ${pct}% match).`
  return `Here's what we found for "${query}" with the closest match at about ${pct}%.`
}

function categoryBreakdown(results) {
  const counts = {}
  results.forEach(r => {
    const name = r.category_detail?.name || 'Uncategorized'
    counts[name] = (counts[name] || 0) + 1
  })
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3)
  if (top.length === 1) return `They're all in ${top[0][0]}.`
  if (top.length > 1) return `You've got a mix across ${top.map(([n, c]) => `${n} (${c})`).join(', ')}.`
  return null
}

function ratingSummary(results) {
  const ratings = results.map(r => Number(r.avg_rating)).filter(Boolean)
  if (!ratings.length) return null
  const avg = (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(1)
  const high = ratings.filter(r => r >= 4.5).length
  if (high > results.length * 0.5) return `${high} out of ${results.length} are fan favorites with an avg of ${avg}/5 and people clearly love these spots!`
  return `Average rating sits at ${avg}/5.`
}

function tagInsights(tags) {
  if (!tags.length) return null
  return `Vibes you might like: ${tags.slice(0, 4).map(t => t.name).join(', ')}.`
}

function distanceHint(results) {
  const dists = results.map(r => r.distance_km).filter(Boolean)
  if (!dists.length) return null
  const nearest = Math.min(...dists).toFixed(1)
  return `The closest one is just ${nearest} km from you!`
}

function statsContext(stats) {
  const total = stats?.total_businesses
  return total ? `We looked through ${total.toLocaleString()} businesses to find these for you.` : null
}
