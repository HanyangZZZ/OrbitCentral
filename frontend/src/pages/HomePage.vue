<template>
  <div style="max-width:1100px;margin:0 auto;padding:20px;font-family:system-ui;color:#e2e8f0;background:#0a1220;min-height:100vh">
    <h1>FBLC API Demo</h1>
    <p style="color:#94a3b8">Minimal frontend showing all available APIs. For frontend devs to reference.</p>

    <!-- ── Stats ──────────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>GET /api/businesses/stats/</h2>
      <button @click="loadStats">Load Stats</button>
      <pre v-if="stats" style="overflow-x:auto;font-size:12px;background:#1e293b;padding:12px;border-radius:6px">{{ JSON.stringify(stats, null, 2) }}</pre>
    </section>

    <!-- ── Categories ─────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>GET /api/categories/</h2>
      <button @click="loadCategories">Load Categories</button>
      <div v-if="categories.length" style="margin-top:8px;font-size:13px">
        <div v-for="c in categories" :key="c.id" style="padding:4px 0;border-bottom:1px solid #1e293b">
          <b>#{{ c.id }}</b> {{ c.name }} ({{ c.slug }}) {{ c.parent_name ? '← ' + c.parent_name : '' }}
          <span style="color:#64748b"> icon: {{ c.icon_name || '—' }}</span>
        </div>
      </div>
    </section>

    <!-- ── Tags ───────────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>GET /api/tags/ <span style="color:#94a3b8;font-size:14px">?q=&amp;min_usage=</span> &nbsp; GET /api/tags/search/ <span style="color:#94a3b8;font-size:14px">(vector)</span></h2>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
        <input v-model="tagSearch" placeholder="Search tags (q=)" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <input v-model.number="tagMinUsage" type="number" placeholder="Min usage" style="width:100px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <button @click="loadTags">Search Tags</button>
      </div>
      <div v-if="tags.length" style="font-size:13px">
        <span style="color:#94a3b8">{{ tagTotal }} tags found. </span>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
          <span v-for="t in tags" :key="t.id"
            @click="toggleTag(t)"
            :style="{
              padding:'4px 10px',borderRadius:'999px',fontSize:'12px',cursor:'pointer',
              background: selectedTagIds.includes(t.id) ? 'rgba(99,102,241,0.4)' : 'rgba(99,102,241,0.1)',
              border: selectedTagIds.includes(t.id) ? '1px solid #6366f1' : '1px solid rgba(99,102,241,0.25)',
              color:'#a5b4fc'
            }">
            {{ t.name }} <span style="color:#64748b">({{ t.usage_count }})</span>
          </span>
        </div>
        <p v-if="selectedTagIds.length" style="font-size:12px;color:#fbbf24;margin-top:6px">
          Selected tag IDs: {{ selectedTagIds.join(', ') }} — these will be applied to search
        </p>
      </div>
    </section>

    <!-- ── Search ─────────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>GET /api/businesses/search/ <span style="color:#94a3b8;font-size:14px">?q=&amp;lat=&amp;lng=&amp;category=&amp;tag=&amp;sort=&amp;limit=</span></h2>
      <form @submit.prevent="runSearch" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px">
        <input v-model="sq" placeholder="Query (q=) e.g. cozy coffee" required style="flex:2;min-width:200px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <input v-model.number="slat" type="number" step="any" placeholder="lat" style="width:110px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <input v-model.number="slng" type="number" step="any" placeholder="lng" style="width:110px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <select v-model="scat" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px">
          <option value="">All categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="ssort" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px">
          <option value="">Weighted</option>
          <option value="distance">Distance</option>
          <option value="rating">Rating</option>
        </select>
        <input v-model.number="slimit" type="number" min="1" max="50" placeholder="limit" style="width:70px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <button type="submit" :disabled="searching">{{ searching ? 'Searching...' : 'Search' }}</button>
        <button type="button" @click="slat=43.6532;slng=-79.3832" style="font-size:12px">📍 Toronto</button>
      </form>

      <!-- Tag filter picker -->
      <div style="margin-bottom:10px;padding:10px;background:#1e293b;border-radius:6px">
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">
          <span style="font-size:12px;color:#94a3b8;white-space:nowrap">Filter by tags <span style="color:#6366f1">(vector search)</span>:</span>
          <input v-model="searchTagQ" @input="searchTagsInline" placeholder="Semantic search e.g. 'outdoor dining', 'live music'..." style="flex:1;background:#0f172a;border:1px solid #475569;color:#e2e8f0;padding:5px 10px;border-radius:4px;font-size:12px" />
          <button v-if="selectedTagIds.length" @click="selectedTagIds=[]" style="font-size:11px;color:#f87171;background:none;border:1px solid rgba(248,113,113,0.3);border-radius:4px;padding:3px 8px;cursor:pointer">Clear all</button>
        </div>
        <!-- Selected tags -->
        <div v-if="selectedTagIds.length" style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px">
          <span v-for="tid in selectedTagIds" :key="'sel-'+tid" @click="removeTag(tid)"
            style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:999px;font-size:11px;cursor:pointer;background:rgba(99,102,241,0.35);border:1px solid #6366f1;color:#c7d2fe">
            {{ tagNameById(tid) }} ✕
          </span>
          <span style="font-size:10px;color:#fbbf24;align-self:center;margin-left:4px">AND filter ({{ selectedTagIds.length }})</span>
        </div>
        <!-- Inline search results -->
        <div v-if="inlineTags.length" style="display:flex;flex-wrap:wrap;gap:4px">
          <span v-for="t in inlineTags" :key="'it-'+t.id" @click="addTag(t)"
            :style="{
              padding:'3px 9px',borderRadius:'999px',fontSize:'11px',cursor:'pointer',
              background: selectedTagIds.includes(t.id) ? 'rgba(99,102,241,0.35)' : 'rgba(99,102,241,0.08)',
              border: selectedTagIds.includes(t.id) ? '1px solid #6366f1' : '1px solid rgba(99,102,241,0.2)',
              color: selectedTagIds.includes(t.id) ? '#c7d2fe' : '#a5b4fc',
              opacity: selectedTagIds.includes(t.id) ? 0.5 : 1
            }">
            {{ t.name }} <span style="color:#64748b">({{ t.usage_count }}<span v-if="t.similarity"> · {{ (t.similarity*100).toFixed(0) }}%</span>)</span>
          </span>
        </div>
        <p v-if="searchTagQ && !inlineTags.length && !tagLoading" style="font-size:11px;color:#64748b;margin:4px 0 0">No tags found</p>
      </div>

      <p v-if="searchTime" style="font-size:12px;color:#94a3b8">{{ searchResults.length }} results in {{ searchTime }}ms</p>
      <p v-if="searchErr" style="color:#f87171;font-size:13px">{{ searchErr }}</p>

      <!-- Results table showing ALL fields -->
      <div v-if="searchResults.length" style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:11px;margin-top:8px">
          <thead>
            <tr style="border-bottom:1px solid #334155;color:#94a3b8;text-align:left">
              <th style="padding:6px">#</th>
              <th style="padding:6px">ID</th>
              <th style="padding:6px">Name</th>
              <th style="padding:6px">Category</th>
              <th style="padding:6px">Tags</th>
              <th style="padding:6px">Rating</th>
              <th style="padding:6px">Reviews</th>
              <th style="padding:6px">Price</th>
              <th style="padding:6px">Similarity</th>
              <th style="padding:6px">Distance</th>
              <th style="padding:6px">Score</th>
              <th style="padding:6px">Phone</th>
              <th style="padding:6px">Website</th>
              <th style="padding:6px">Address</th>
              <th style="padding:6px">Status</th>
              <th style="padding:6px">Lat/Lng</th>
              <th style="padding:6px">Google ID</th>
              <th style="padding:6px">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in searchResults" :key="r.id" style="border-bottom:1px solid #1e293b">
              <td style="padding:6px">{{ i+1 }}</td>
              <td style="padding:6px">{{ r.id }}</td>
              <td style="padding:6px;white-space:nowrap"><b>{{ r.name }}</b></td>
              <td style="padding:6px;white-space:nowrap">{{ r.category_detail?.name || '—' }} <span style="color:#64748b">{{ r.category_detail?.parent_name ? '(' + r.category_detail.parent_name + ')' : '' }}</span></td>
              <td style="padding:6px"><span v-for="t in r.tags" :key="t.id" style="display:inline-block;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);border-radius:999px;padding:1px 6px;margin:1px 2px;font-size:10px;color:#7dd3fc">{{ t.name }}</span></td>
              <td style="padding:6px">{{ r.avg_rating ?? '—' }}★</td>
              <td style="padding:6px">{{ r.user_rating_count ?? r.review_count ?? 0 }}</td>
              <td style="padding:6px">{{ r.price_level != null ? '$'.repeat(r.price_level) : '—' }}</td>
              <td style="padding:6px">{{ r.similarity != null ? (r.similarity*100).toFixed(1)+'%' : '—' }}</td>
              <td style="padding:6px">{{ r.distance_km != null ? r.distance_km.toFixed(2)+' km' : '—' }}</td>
              <td style="padding:6px">{{ r.score != null ? r.score.toFixed(3) : '—' }}</td>
              <td style="padding:6px;white-space:nowrap">{{ r.phone || '—' }}</td>
              <td style="padding:6px"><a v-if="r.website_url" :href="r.website_url" target="_blank" style="color:#38bdf8;font-size:10px">link</a><span v-else>—</span></td>
              <td style="padding:6px;max-width:200px;overflow:hidden;text-overflow:ellipsis">{{ r.address || '—' }}</td>
              <td style="padding:6px;white-space:nowrap">{{ r.business_status || r.onboarding_status || '—' }}</td>
              <td style="padding:6px;font-size:10px;color:#64748b">{{ r.lat?.toFixed(4) }}, {{ r.lng?.toFixed(4) }}</td>
              <td style="padding:6px;font-size:9px;color:#64748b;max-width:80px;overflow:hidden;text-overflow:ellipsis">{{ r.google_place_id || '—' }}</td>
              <td style="padding:6px;max-width:200px;overflow:hidden;text-overflow:ellipsis;color:#94a3b8">{{ r.description || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Raw JSON toggle -->
      <div v-if="searchResults.length" style="margin-top:8px">
        <button @click="showRaw=!showRaw" style="font-size:11px">{{ showRaw ? 'Hide' : 'Show' }} Raw JSON</button>
        <pre v-if="showRaw" style="font-size:10px;background:#1e293b;padding:12px;border-radius:6px;max-height:400px;overflow:auto">{{ JSON.stringify(searchResults, null, 2) }}</pre>
      </div>
    </section>

    <!-- ── Businesses List ────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>GET /api/businesses/ <span style="color:#94a3b8;font-size:14px">(paginated)</span></h2>
      <button @click="loadBusinesses">Load Businesses</button>
      <p v-if="businesses.length" style="font-size:12px;color:#94a3b8">Showing {{ businesses.length }} of {{ bizTotal }}</p>
      <div v-if="businesses.length" style="max-height:300px;overflow-y:auto;font-size:12px;margin-top:8px">
        <div v-for="b in businesses" :key="b.id" style="padding:4px 0;border-bottom:1px solid #1e293b">
          <b>#{{ b.id }}</b> {{ b.name }}
          <span style="color:#64748b"> · {{ b.avg_rating }}★ ({{ b.user_rating_count }}) · {{ b.category_detail?.name || '—' }} · {{ b.address || '—' }}</span>
          <span v-if="b.phone" style="color:#475569"> · {{ b.phone }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCategories, getTags, searchTags, getBusinesses, getStats, searchBusinesses } from '../api/client'

const stats = ref(null)
const categories = ref([])
const tags = ref([])
const tagTotal = ref(0)
const tagSearch = ref('')
const tagMinUsage = ref(2)
const selectedTagIds = ref([])
const businesses = ref([])
const bizTotal = ref(0)

const sq = ref('')
const slat = ref(null)
const slng = ref(null)
const scat = ref('')
const ssort = ref('')
const slimit = ref(10)
const searching = ref(false)
const searchResults = ref([])
const searchErr = ref('')
const searchTime = ref(null)
const showRaw = ref(false)
const searchTagQ = ref('')
const inlineTags = ref([])
const tagLoading = ref(false)
const tagCache = ref({})

const loadStats = async () => { stats.value = (await getStats()).data }
const loadCategories = async () => { categories.value = (await getCategories()).data.results ?? [] }

const loadTags = async () => {
  const params = {}
  if (tagSearch.value) params.q = tagSearch.value
  if (tagMinUsage.value) params.min_usage = tagMinUsage.value
  const res = await getTags(params)
  tags.value = res.data.results ?? []
  tagTotal.value = res.data.count ?? tags.value.length
  tags.value.forEach(t => { tagCache.value[t.id] = t.name })
}

const toggleTag = (t) => {
  const idx = selectedTagIds.value.indexOf(t.id)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(t.id)
  tagCache.value[t.id] = t.name
}

const addTag = (t) => {
  if (!selectedTagIds.value.includes(t.id)) {
    selectedTagIds.value.push(t.id)
    tagCache.value[t.id] = t.name
  }
}

const removeTag = (tid) => {
  selectedTagIds.value = selectedTagIds.value.filter(id => id !== tid)
}

const tagNameById = (tid) => tagCache.value[tid] || `#${tid}`

let searchTagTimer = null
const searchTagsInline = () => {
  clearTimeout(searchTagTimer)
  searchTagTimer = setTimeout(async () => {
    if (!searchTagQ.value.trim()) { inlineTags.value = []; return }
    tagLoading.value = true
    try {
      // Vector semantic search — finds related tags even if query doesn't match name
      const res = await searchTags({ q: searchTagQ.value, min_usage: 1, limit: 30 })
      inlineTags.value = res.data ?? res.data.results ?? []
      inlineTags.value.forEach(t => { tagCache.value[t.id] = t.name })
    } catch { inlineTags.value = [] }
    tagLoading.value = false
  }, 350)
}

const loadBusinesses = async () => {
  const res = await getBusinesses()
  businesses.value = res.data.results ?? []
  bizTotal.value = res.data.count ?? businesses.value.length
}

const runSearch = async () => {
  searching.value = true
  searchErr.value = ''
  searchResults.value = []
  searchTime.value = null
  const t0 = performance.now()
  try {
    const params = { q: sq.value, limit: slimit.value || 10 }
    if (slat.value != null) params.lat = slat.value
    if (slng.value != null) params.lng = slng.value
    if (scat.value) params.category = scat.value
    if (ssort.value) params.sort = ssort.value
    if (selectedTagIds.value.length) params.tag = selectedTagIds.value
    searchResults.value = (await searchBusinesses(params)).data
    searchTime.value = Math.round(performance.now() - t0)
    loadStats()
  } catch (e) {
    searchErr.value = e.response?.data?.detail || 'Search failed'
  } finally {
    searching.value = false
  }
}

onMounted(() => {
  loadStats(); loadCategories(); loadTags()
  // Pre-populate inline tag picker with popular tags
  getTags({ min_usage: 5 }).then(res => {
    inlineTags.value = res.data.results ?? []
    inlineTags.value.forEach(t => { tagCache.value[t.id] = t.name })
  }).catch(() => {})
})
</script>
