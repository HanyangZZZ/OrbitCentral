<template>
<div class="api-demo">
  <header>
    <h1>FBLC API Reference</h1>
    <p class="subtitle">Interactive API demo — every endpoint is callable below. Frontend devs: use <code>src/api/client.js</code> for integration.</p>
    <nav class="toc">
      <a href="#stats">Stats</a>
      <a href="#categories">Categories</a>
      <a href="#tags">Tags</a>
      <a href="#search">Search</a>
      <a href="#businesses">Businesses</a>
      <a href="#auth">Auth</a>
      <a href="#reviews">Reviews</a>
      <a href="#bookmarks">Bookmarks</a>
      <a href="#ai-reviews">AI Reviews</a>
      <a href="#ai-personalization">AI Personalization</a>
    </nav>
  </header>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- STATS                                                              -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="stats" class="endpoint">
    <h2>GET /api/businesses/stats/</h2>
    <p class="desc">Database overview — totals, embeddings, top tags.</p>
    <div class="actions"><button @click="callStats">Run</button></div>
    <ResponseBox :data="res.stats" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- CATEGORIES                                                         -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="categories" class="endpoint">
    <h2>GET /api/categories/</h2>
    <p class="desc">22 hierarchical categories (5 parent + 17 sub). Returned as flat list with <code>parent</code> and <code>parent_name</code>.</p>
    <div class="actions"><button @click="callCategories">Run</button></div>
    <ResponseBox :data="res.categories" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- TAGS                                                               -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="tags" class="endpoint">
    <h2>GET /api/tags/ <span class="params">?q= &amp; min_usage=</span></h2>
    <p class="desc">List tags, optionally filtered by name and minimum usage count.</p>
    <div class="fields">
      <input v-model="tagQ" placeholder="q (name filter)" />
      <input v-model.number="tagMinUsage" type="number" placeholder="min_usage" />
      <button @click="callTags">Run</button>
    </div>
    <TagPills :tags="tagList" :selected="selectedTagIds" @toggle="toggleTag" />
    <ResponseBox :data="res.tags" />
  </section>

  <section class="endpoint">
    <h2>GET /api/tags/search/ <span class="params">?q= &amp; limit= &amp; min_usage=</span></h2>
    <p class="desc">Semantic vector search — finds related tags even if query doesn't match name. e.g. "outdoor dining" finds "patio".</p>
    <div class="fields">
      <input v-model="tagSearchQ" placeholder="q (semantic search)" />
      <input v-model.number="tagSearchLimit" type="number" placeholder="limit (default 20)" />
      <button @click="callTagSearch">Run</button>
    </div>
    <TagPills :tags="tagSearchList" :selected="selectedTagIds" @toggle="toggleTag" />
    <ResponseBox :data="res.tagSearch" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- SEARCH                                                             -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="search" class="endpoint">
    <h2>GET /api/businesses/search/ <span class="params">?q= &amp; lat= &amp; lng= &amp; category= &amp; tag= &amp; sort= &amp; limit=</span></h2>
    <p class="desc">AI-powered "vibe search". Score = 0.70 x similarity + 0.15 x proximity + 0.15 x rating.<br/>First search in a new area auto-imports from Google Places via Celery.</p>
    <div class="fields">
      <input v-model="sq" placeholder="q (required) e.g. cozy coffee" class="wide" />
      <input v-model.number="slat" type="number" step="any" placeholder="lat" />
      <input v-model.number="slng" type="number" step="any" placeholder="lng" />
      <button type="button" @click="slat=43.6532;slng=-79.3832" class="small">Toronto</button>
      <select v-model="scat">
        <option value="">All categories</option>
        <option v-for="c in categoryList" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select v-model="ssort">
        <option value="">Weighted (default)</option>
        <option value="distance">Distance</option>
        <option value="rating">Rating</option>
      </select>
      <input v-model.number="slimit" type="number" min="1" max="50" placeholder="limit" />
      <input v-model="stagIds" placeholder="tag IDs (optional) e.g. 1,4,29" style="width:220px" />
      <button @click="callSearch" :disabled="!sq || searching">{{ searching ? 'Searching...' : 'Run' }}</button>
    </div>
    <div v-if="searchResults.length" class="results-grid">
      <div v-for="r in searchResults" :key="r.id" class="result-card">
        <img v-if="r.image_url || r.photo_references?.length" :src="r.image_url || photoUrl(r.id)" class="result-img" alt="" @error="$event.target.style.display='none'" />
        <div class="result-body">
          <strong>#{{ r.id }} {{ r.name }}</strong>
          <span class="meta">{{ r.category_detail?.name ?? 'Uncategorized' }} · {{ r.avg_rating }}★ · {{ r.price_level != null ? '$'.repeat(r.price_level) : '—' }}</span>
          <div v-if="r.tags?.length" class="result-tags">
            <span v-for="t in r.tags" :key="t.id" class="pill small">{{ t.name }}</span>
          </div>
          <span class="meta">
            <template v-if="r.score != null">score: {{ r.score.toFixed(3) }} · </template>
            <template v-if="r.similarity != null">sim: {{ (r.similarity*100).toFixed(1) }}% · </template>
            <template v-if="r.distance_km != null">{{ r.distance_km.toFixed(2) }} km</template>
          </span>
        </div>
      </div>
    </div>
    <ResponseBox :data="res.search" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- BUSINESSES LIST                                                    -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="businesses" class="endpoint">
    <h2>GET /api/businesses/ <span class="params">(paginated)</span></h2>
    <p class="desc">List all businesses. Supports <code>?category=</code>, <code>?onboarding_status=</code>, <code>?search=</code>, <code>?ordering=</code>.</p>
    <div class="actions"><button @click="callBusinesses">Run</button></div>
    <ResponseBox :data="res.businesses" />
  </section>

  <section class="endpoint">
    <h2>GET /api/businesses/:id/</h2>
    <p class="desc">Full business detail with all Google Places data, tags, opening hours, etc.</p>
    <div class="fields">
      <input v-model.number="bizDetailId" type="number" placeholder="Business ID" />
      <button @click="callBusinessDetail" :disabled="!bizDetailId">Run</button>
    </div>
    <ResponseBox :data="res.businessDetail" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- AUTH                                                               -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="auth" class="endpoint">
    <h2>Auth <span class="params">/api/auth/*</span></h2>
    <p class="desc">Token-based auth. Register -> verify email -> login. Token goes in <code>Authorization: Token xxx</code> header.</p>

    <div v-if="authToken" class="auth-status">
      Logged in as <strong>{{ userProfile?.username }}</strong>
      <span class="badge" :class="userProfile?.email_verified ? 'ok' : 'warn'">{{ userProfile?.email_verified ? 'verified' : 'unverified' }}</span>
      <code class="token">Token {{ authToken.slice(0, 12) }}...</code>
      <button @click="doLogout" class="small danger">Logout</button>
    </div>

    <!-- Register -->
    <h3>POST /api/auth/register/</h3>
    <div class="fields">
      <input v-model="regEmail" type="email" placeholder="email" />
      <input v-model="regUsername" placeholder="username" />
      <input v-model="regPass" type="password" placeholder="password (min 8)" />
      <input v-model="regDisplayName" placeholder="display_name (optional)" />
      <button @click="doRegister">Run</button>
    </div>
    <ResponseBox :data="res.register" />

    <!-- Login -->
    <h3>POST /api/auth/login/</h3>
    <div class="fields">
      <input v-model="loginUser" placeholder="username or email" />
      <input v-model="loginPass" type="password" placeholder="password" />
      <button @click="doLogin">Run</button>
    </div>
    <ResponseBox :data="res.login" />

    <!-- Me -->
    <h3>GET /api/auth/me/ <span class="params">(auth required)</span></h3>
    <div class="actions"><button @click="callMe">Run</button></div>
    <ResponseBox :data="res.me" />

    <!-- Verify Email -->
    <h3>POST /api/auth/verify-email/</h3>
    <div class="fields">
      <input v-model="verifyToken" placeholder="token from email" class="wide" />
      <button @click="doVerifyEmail">Run</button>
    </div>
    <ResponseBox :data="res.verifyEmail" />

    <!-- Resend Verify -->
    <h3>POST /api/auth/resend-verify/ <span class="params">(auth required)</span></h3>
    <div class="actions"><button @click="doResendVerify">Run</button></div>
    <ResponseBox :data="res.resendVerify" />

    <!-- Forgot Password -->
    <h3>POST /api/auth/forgot-password/</h3>
    <div class="fields">
      <input v-model="forgotEmail" type="email" placeholder="email" />
      <button @click="doForgotPw">Run</button>
    </div>
    <ResponseBox :data="res.forgotPw" />

    <!-- Reset Password -->
    <h3>POST /api/auth/reset-password/</h3>
    <div class="fields">
      <input v-model="resetToken" placeholder="reset token" />
      <input v-model="resetNewPw" type="password" placeholder="new password" />
      <button @click="doResetPw">Run</button>
    </div>
    <ResponseBox :data="res.resetPw" />

    <!-- Logout -->
    <h3>POST /api/auth/logout/ <span class="params">(auth required)</span></h3>
    <p class="desc">Deletes the server-side token. Called automatically by the Logout button above.</p>
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- REVIEWS                                                            -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="reviews" class="endpoint">
    <h2>Reviews <span class="params">/api/reviews/*</span></h2>
    <p class="desc">CRUD + helpfulness votes. Auth + verified email required for write operations.</p>

    <h3>GET /api/reviews/ <span class="params">?business= &amp; user= &amp; rating=</span></h3>
    <div class="fields">
      <input v-model.number="reviewBizId" type="number" placeholder="business (ID)" />
      <button @click="callReviews">Run</button>
    </div>
    <ResponseBox :data="res.reviews" />

    <h3>POST /api/reviews/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Submit a review. Optional <code>photo</code> field accepts base64-encoded image -> stored in GCS.</p>
    <div class="fields">
      <input v-model.number="newReviewBiz" type="number" placeholder="business (ID)" />
      <select v-model.number="newReviewRating">
        <option :value="0" disabled>rating</option>
        <option v-for="n in 5" :key="n" :value="n">{{ n }} star</option>
      </select>
      <input v-model="newReviewDesc" placeholder="description (optional)" class="wide" />
      <label class="file-label">
        Photo
        <input type="file" accept="image/*" @change="onReviewPhoto" hidden />
      </label>
      <span v-if="newReviewPhoto" class="note">photo attached</span>
      <button @click="doCreateReview">Run</button>
    </div>
    <ResponseBox :data="res.createReview" />

    <h3>DELETE /api/reviews/:id/ <span class="params">(owner only)</span></h3>
    <div class="fields">
      <input v-model.number="deleteReviewId" type="number" placeholder="review ID" />
      <button @click="doDeleteReview">Run</button>
    </div>
    <ResponseBox :data="res.deleteReview" />

    <h3>POST /api/reviews/:id/vote/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Toggle helpfulness vote. Types: <code>useful</code>, <code>funny</code>, <code>cool</code>.</p>
    <div class="fields">
      <input v-model.number="voteReviewId" type="number" placeholder="review ID" />
      <select v-model="voteType">
        <option value="useful">useful</option>
        <option value="funny">funny</option>
        <option value="cool">cool</option>
      </select>
      <button @click="doVoteReview">Run</button>
    </div>
    <ResponseBox :data="res.voteReview" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- BOOKMARKS                                                          -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="bookmarks" class="endpoint">
    <h2>Bookmarks <span class="params">/api/bookmarks/*</span></h2>
    <p class="desc">Save businesses. Auth + verified email required.</p>

    <h3>GET /api/bookmarks/ <span class="params">(auth + verified)</span></h3>
    <div class="actions"><button @click="callBookmarks">Run</button></div>
    <ResponseBox :data="res.bookmarks" />

    <h3>GET /api/bookmarks/ids/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Returns just the business IDs the user has bookmarked — for quick "is this bookmarked?" checks.</p>
    <div class="actions"><button @click="callBookmarkIds">Run</button></div>
    <ResponseBox :data="res.bookmarkIds" />

    <h3>POST /api/bookmarks/toggle/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Add or remove a bookmark in one call. Returns <code>{ status: "added" | "removed" }</code>.</p>
    <div class="fields">
      <input v-model.number="toggleBizId" type="number" placeholder="business (ID)" />
      <button @click="doToggleBookmark">Run</button>
    </div>
    <ResponseBox :data="res.toggleBookmark" />

    <h3>GET /api/bookmarks/check/ <span class="params">?business= (auth + verified)</span></h3>
    <div class="fields">
      <input v-model.number="checkBizId" type="number" placeholder="business (ID)" />
      <button @click="doCheckBookmark">Run</button>
    </div>
    <ResponseBox :data="res.checkBookmark" />

    <h3>DELETE /api/bookmarks/:id/ <span class="params">(auth + verified)</span></h3>
    <div class="fields">
      <input v-model.number="deleteBookmarkId" type="number" placeholder="bookmark ID" />
      <button @click="doDeleteBookmark">Run</button>
    </div>
    <ResponseBox :data="res.deleteBookmark" />
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- AI REVIEWS                                                         -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="ai-reviews" class="endpoint">
    <h2>AI Reviews <span class="params">/api/ai-reviews/*</span></h2>
    <p class="desc">GPT-5 powered conversational review writer. Chat naturally, AI adds/removes tags, then generates a polished review.<br/>
      Flow: <strong>Start</strong> → <strong>Message</strong> (repeat) → <strong>Generate</strong> → <strong>Confirm</strong>. Auth + verified email required.</p>

    <h3>GET /api/ai-reviews/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">List your AI review chat sessions.</p>
    <div class="actions"><button @click="callAISessions">Run</button></div>
    <ResponseBox :data="res.aiSessions" />

    <h3>POST /api/ai-reviews/start/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Start a new AI-guided review. Returns session with AI's opening message.</p>
    <div class="fields">
      <input v-model.number="aiStartBiz" type="number" placeholder="business ID" />
      <select v-model.number="aiStartRating">
        <option :value="0" disabled>rating</option>
        <option v-for="n in 5" :key="n" :value="n">{{ n }} star{{ n > 1 ? 's' : '' }}</option>
      </select>
      <button @click="doAIStart" :disabled="!aiStartBiz || !aiStartRating">Start Chat</button>
    </div>
    <ResponseBox :data="res.aiStart" />

    <!-- Chat interface -->
    <template v-if="aiSessionId">
      <div class="ai-chat-header">
        <strong>Session:</strong> <code>{{ aiSessionId.slice(0, 8) }}...</code>
        <span v-if="aiSessionBiz" class="meta"> — {{ aiSessionBiz }}</span>
        <button @click="doAIAbandon" class="small danger" style="margin-left:auto">Abandon</button>
      </div>

      <div class="ai-chat-box">
        <div v-for="(m, i) in aiConversation" :key="i" :class="['ai-msg', m.role]">
          <span class="ai-role">{{ m.role === 'assistant' ? 'AI' : 'You' }}</span>
          <span class="ai-text">{{ m.content }}</span>
        </div>
      </div>

      <div v-if="aiTagsAdded.length || aiTagsRemoved.length" class="ai-tags-info">
        <span v-if="aiTagsAdded.length" class="tag-added">+{{ aiTagsAdded.join(', +') }}</span>
        <span v-if="aiTagsRemoved.length" class="tag-removed">-{{ aiTagsRemoved.join(', -') }}</span>
      </div>

      <h3>POST /api/ai-reviews/:id/message/ <span class="params">(auth + verified)</span></h3>
      <div class="fields">
        <input v-model="aiMessage" placeholder="Type your reply..." class="wide" @keyup.enter="doAISend" />
        <button @click="doAISend" :disabled="!aiMessage || aiSending">{{ aiSending ? 'Sending...' : 'Send' }}</button>
      </div>
      <ResponseBox :data="res.aiMessage" />

      <h3>POST /api/ai-reviews/:id/generate/ <span class="params">(auth + verified)</span></h3>
      <p class="desc">When the chat feels complete, generate the review text.</p>
      <div class="actions">
        <button @click="doAIGenerate" :disabled="aiSending">{{ aiSending ? 'Generating...' : 'Generate Review' }}</button>
      </div>
      <div v-if="aiGeneratedDesc" class="ai-generated">
        <strong>Generated review:</strong>
        <p>{{ aiGeneratedDesc }}</p>
      </div>
      <ResponseBox :data="res.aiGenerate" />

      <h3>POST /api/ai-reviews/:id/confirm/ <span class="params">(auth + verified)</span></h3>
      <p class="desc">Happy with the review? Confirm to create the actual Review and apply all tag changes.</p>
      <div class="actions">
        <button @click="doAIConfirm" :disabled="!aiGeneratedDesc" class="confirm-btn">Confirm &amp; Publish</button>
      </div>
      <ResponseBox :data="res.aiConfirm" />
    </template>
  </section>

  <!-- ════════════════════════════════════════════════════════════════════ -->
  <!-- AI PERSONALIZATION                                                 -->
  <!-- ════════════════════════════════════════════════════════════════════ -->
  <section id="ai-personalization" class="endpoint">
    <h2>AI Personalization <span class="params">/api/businesses/personalized/</span></h2>
    <p class="desc">GPT-4.1 analyzes your recent reviews &amp; bookmarks, generates a taste-based search query, then runs the full weighted vibe search to discover new businesses you'll love.<br/>
      Auth + verified email required. Excludes businesses you've already reviewed or bookmarked.</p>

    <h3>GET /api/businesses/personalized/ <span class="params">(auth + verified)</span></h3>
    <p class="desc">Returns AI-generated query plus top matching businesses based on your activity.</p>
    <div class="fields">
      <input v-model.number="persLat" type="number" step="0.0001" placeholder="lat (e.g. 43.651)" />
      <input v-model.number="persLng" type="number" step="0.0001" placeholder="lng (e.g. -79.347)" />
      <input v-model.number="persLimit" type="number" placeholder="limit (default 5)" style="width:100px" />
      <button @click="callPersonalized" :disabled="persLoading">{{ persLoading ? 'Thinking...' : 'Get Recommendations' }}</button>
    </div>

    <div v-if="persQuery" class="ai-generated" style="margin:10px 0">
      <strong>AI-generated query:</strong>
      <p>"{{ persQuery }}" <small style="color:#64748b">(profile size: {{ persProfileSize }} businesses)</small></p>
    </div>

    <div v-if="persResults.length" class="results-grid">
      <div v-for="b in persResults" :key="b.id" class="result-card">
        <img v-if="b.image_url || b.photo_references?.length" :src="b.image_url || photoUrl(b.id)" class="result-img" alt="" @error="$event.target.style.display='none'" />
        <div class="result-body">
          <strong>#{{ b.id }} {{ b.name }}</strong>
          <span class="meta">{{ b.category_detail?.name ?? 'Uncategorized' }} · {{ b.avg_rating }}★ · {{ b.price_level != null ? '$'.repeat(b.price_level) : '—' }}</span>
          <div v-if="b.tags?.length" class="result-tags">
            <span v-for="t in b.tags" :key="t.id" class="pill small">{{ t.name }}</span>
          </div>
          <span class="meta">
            <template v-if="b.score != null">score: {{ b.score.toFixed(3) }} · </template>
            <template v-if="b.similarity != null">sim: {{ (b.similarity*100).toFixed(1) }}% · </template>
            <template v-if="b.distance_km != null">{{ b.distance_km.toFixed(2) }} km</template>
          </span>
        </div>
      </div>
    </div>

    <ResponseBox :data="res.personalized" />
  </section>

</div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import api from '../api/client'
import {
  getStats, getCategories, getTags, searchTags, getBusinesses, getBusiness,
  searchBusinesses, register, login, verifyEmail, getMe, resendVerify,
  forgotPassword, resetPassword, logout, setAuthToken, getSavedToken,
  getReviews, createReview, deleteReview, voteReview,
  getBookmarks, toggleBookmark, checkBookmark, deleteBookmark, getBookmarkIds,
  getAIReviewSessions, startAIReview, sendAIReviewMessage,
  generateAIReview, confirmAIReview, abandonAIReview,
  getPersonalized,
} from '../api/client'

// ── Shared response store — every endpoint writes here for display ────────────
const res = reactive({
  stats: null, categories: null, tags: null, tagSearch: null,
  search: null, businesses: null, businessDetail: null,
  register: null, login: null, me: null, verifyEmail: null,
  resendVerify: null, forgotPw: null, resetPw: null,
  reviews: null, createReview: null, deleteReview: null, voteReview: null,
  bookmarks: null, bookmarkIds: null, toggleBookmark: null,
  checkBookmark: null, deleteBookmark: null,
  aiSessions: null, aiStart: null, aiMessage: null, aiGenerate: null, aiConfirm: null,
  personalized: null,
})

/** Call an API and store result or error in res[key]. */
async function call(key, fn) {
  res[key] = { _loading: true }
  try {
    const r = await fn()
    res[key] = r.data
  } catch (e) {
    res[key] = { _error: true, status: e.response?.status, data: e.response?.data || e.message }
  }
}

// ── Inline components ─────────────────────────────────────────────────────────
function fmt(d) { return typeof d === 'string' ? d : JSON.stringify(d, null, 2) }

const ResponseBox = {
  props: ['data'],
  setup(props) {
    return () => {
      if (!props.data) return null
      if (props.data?._loading) return h('div', { class: 'response-box' }, h('div', { class: 'loading' }, 'Loading...'))
      if (props.data?._error) return h('div', { class: 'response-box error-resp' }, [
        h('span', { class: 'error-badge' }, String(props.data.status || 'ERR')),
        h('pre', null, fmt(props.data.data)),
      ])
      return h('div', { class: 'response-box' }, h('pre', null, fmt(props.data)))
    }
  }
}

const TagPills = {
  props: ['tags', 'selected'],
  emits: ['toggle'],
  setup(props, { emit }) {
    return () => {
      if (!props.tags?.length) return null
      return h('div', { class: 'tag-pills' }, props.tags.map(t =>
        h('span', {
          class: ['pill', { active: props.selected.includes(t.id) }],
          onClick: () => emit('toggle', t),
        }, [
          t.name + ' ',
          h('small', null, `(${t.usage_count}${t.similarity ? ' · ' + (t.similarity * 100).toFixed(0) + '%' : ''})`)
        ])
      ))
    }
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────────
const callStats = () => call('stats', getStats)

// ── Categories ────────────────────────────────────────────────────────────────
const categoryList = ref([])
const callCategories = async () => {
  await call('categories', getCategories)
  if (!res.categories?._error) categoryList.value = res.categories?.results ?? []
}

// ── Tags ──────────────────────────────────────────────────────────────────────
const tagQ = ref('')
const tagMinUsage = ref(2)
const tagList = ref([])
const selectedTagIds = ref([])
const tagCache = ref({})

const callTags = async () => {
  const params = {}
  if (tagQ.value) params.q = tagQ.value
  if (tagMinUsage.value) params.min_usage = tagMinUsage.value
  await call('tags', () => getTags(params))
  if (!res.tags?._error) {
    tagList.value = res.tags?.results ?? []
    tagList.value.forEach(t => { tagCache.value[t.id] = t.name })
  }
}

const tagSearchQ = ref('')
const tagSearchLimit = ref(20)
const tagSearchList = ref([])

const callTagSearch = async () => {
  const params = { q: tagSearchQ.value || 'coffee', limit: tagSearchLimit.value || 20, min_usage: 1 }
  await call('tagSearch', () => searchTags(params))
  if (!res.tagSearch?._error) {
    // Fix: check results first, then fall back to array response
    tagSearchList.value = res.tagSearch?.results ?? (Array.isArray(res.tagSearch) ? res.tagSearch : [])
    tagSearchList.value.forEach(t => { tagCache.value[t.id] = t.name })
  }
}

const toggleTag = (t) => {
  const idx = selectedTagIds.value.indexOf(t.id)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(t.id)
  tagCache.value[t.id] = t.name
}

// ── Search ────────────────────────────────────────────────────────────────────
const sq = ref(''); const slat = ref(null); const slng = ref(null)
const scat = ref(''); const ssort = ref(''); const slimit = ref(10)
const stagIds = ref(''); const searching = ref(false); const searchResults = ref([])

const callSearch = async () => {
  searching.value = true
  const params = { q: sq.value, limit: slimit.value || 10 }
  if (slat.value != null) params.lat = slat.value
  if (slng.value != null) params.lng = slng.value
  if (scat.value) params.category = scat.value
  if (ssort.value) params.sort = ssort.value
  const parsedTags = stagIds.value.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n))
  if (parsedTags.length) params.tag = parsedTags
  await call('search', () => searchBusinesses(params))
  if (!res.search?._error) searchResults.value = Array.isArray(res.search) ? res.search : (res.search?.results ?? [])
  searching.value = false
}

// ── Businesses ────────────────────────────────────────────────────────────────
const photoUrl = (bizId) => `${api.defaults.baseURL}/businesses/${bizId}/photo/`

// ── Businesses ────────────────────────────────────────────────────────────────
const callBusinesses = () => call('businesses', getBusinesses)
const bizDetailId = ref(null)
const callBusinessDetail = () => call('businessDetail', () => getBusiness(bizDetailId.value))

// ── Auth ──────────────────────────────────────────────────────────────────────
const authToken = ref('')
const userProfile = ref(null)
const loginUser = ref(''); const loginPass = ref('')
const regEmail = ref(''); const regUsername = ref(''); const regPass = ref(''); const regDisplayName = ref('')
const verifyToken = ref('')
const forgotEmail = ref('')
const resetToken = ref(''); const resetNewPw = ref('')

const doRegister = async () => {
  await call('register', () => register({
    email: regEmail.value, username: regUsername.value,
    password: regPass.value, display_name: regDisplayName.value || undefined,
  }))
  if (!res.register?._error && res.register?.token) {
    authToken.value = res.register.token
    setAuthToken(authToken.value)
    userProfile.value = res.register.user || null
  }
}

const doLogin = async () => {
  await call('login', () => login(loginUser.value, loginPass.value))
  if (!res.login?._error && res.login?.token) {
    authToken.value = res.login.token
    setAuthToken(authToken.value)
    userProfile.value = res.login.user || null
  }
}

const callMe = async () => {
  await call('me', getMe)
  if (!res.me?._error) userProfile.value = res.me
}

const doVerifyEmail = async () => {
  await call('verifyEmail', () => verifyEmail(verifyToken.value))
  if (!res.verifyEmail?._error) callMe()
}

const doResendVerify = () => call('resendVerify', resendVerify)
const doForgotPw = () => call('forgotPw', () => forgotPassword(forgotEmail.value))
const doResetPw = () => call('resetPw', () => resetPassword(resetToken.value, resetNewPw.value))

const doLogout = async () => {
  try { await logout() } catch { /* ignore if token already expired */ }
  authToken.value = ''
  userProfile.value = null
  setAuthToken(null)
}

// ── Reviews ───────────────────────────────────────────────────────────────────
const reviewBizId = ref(null)
const callReviews = () => call('reviews', () => getReviews({ business: reviewBizId.value }))

const newReviewBiz = ref(null); const newReviewRating = ref(0)
const newReviewDesc = ref(''); const newReviewPhoto = ref(null)

const onReviewPhoto = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { newReviewPhoto.value = reader.result }
  reader.readAsDataURL(file)
}

const doCreateReview = () => {
  const payload = { business: newReviewBiz.value, rating: newReviewRating.value, description: newReviewDesc.value }
  if (newReviewPhoto.value) payload.photo = newReviewPhoto.value
  call('createReview', () => createReview(payload))
}

const deleteReviewId = ref(null)
const doDeleteReview = () => call('deleteReview', () => deleteReview(deleteReviewId.value))

const voteReviewId = ref(null); const voteType = ref('useful')
const doVoteReview = () => call('voteReview', () => voteReview(voteReviewId.value, voteType.value))

// ── Bookmarks ─────────────────────────────────────────────────────────────────
const callBookmarks = () => call('bookmarks', getBookmarks)
const callBookmarkIds = () => call('bookmarkIds', getBookmarkIds)

const toggleBizId = ref(null)
const doToggleBookmark = () => call('toggleBookmark', () => toggleBookmark(toggleBizId.value))

const checkBizId = ref(null)
const doCheckBookmark = () => call('checkBookmark', () => checkBookmark(checkBizId.value))

const deleteBookmarkId = ref(null)
const doDeleteBookmark = () => call('deleteBookmark', () => deleteBookmark(deleteBookmarkId.value))

// ── AI Reviews ────────────────────────────────────────────────────────────────
const aiStartBiz = ref(null); const aiStartRating = ref(0)
const aiSessionId = ref(''); const aiSessionBiz = ref('')
const aiConversation = ref([]); const aiMessage = ref('')
const aiSending = ref(false); const aiGeneratedDesc = ref('')
const aiTagsAdded = ref([]); const aiTagsRemoved = ref([])

const callAISessions = () => call('aiSessions', getAIReviewSessions)

const doAIStart = async () => {
  aiSending.value = true
  await call('aiStart', () => startAIReview(aiStartBiz.value, aiStartRating.value))
  aiSending.value = false
  if (!res.aiStart?._error && res.aiStart?.id) {
    aiSessionId.value = res.aiStart.id
    aiSessionBiz.value = res.aiStart.business_name || ''
    aiConversation.value = res.aiStart.conversation || []
    aiTagsAdded.value = res.aiStart.tags_to_add || []
    aiTagsRemoved.value = res.aiStart.tags_to_remove || []
    aiGeneratedDesc.value = ''
  }
}

const doAISend = async () => {
  if (!aiMessage.value || aiSending.value) return
  aiSending.value = true
  const msg = aiMessage.value
  aiMessage.value = ''
  // Optimistic: show user message immediately
  aiConversation.value.push({ role: 'user', content: msg })
  await call('aiMessage', () => sendAIReviewMessage(aiSessionId.value, msg))
  aiSending.value = false
  if (!res.aiMessage?._error && res.aiMessage?.session) {
    aiConversation.value = res.aiMessage.session.conversation || []
    aiTagsAdded.value = res.aiMessage.session.tags_to_add || []
    aiTagsRemoved.value = res.aiMessage.session.tags_to_remove || []
  }
}

const doAIGenerate = async () => {
  aiSending.value = true
  await call('aiGenerate', () => generateAIReview(aiSessionId.value))
  aiSending.value = false
  if (!res.aiGenerate?._error && res.aiGenerate?.generated_description) {
    aiGeneratedDesc.value = res.aiGenerate.generated_description
  }
}

const doAIConfirm = async () => {
  await call('aiConfirm', () => confirmAIReview(aiSessionId.value))
  if (!res.aiConfirm?._error) {
    // Reset the chat state
    aiSessionId.value = ''
    aiSessionBiz.value = ''
    aiConversation.value = []
    aiMessage.value = ''
    aiGeneratedDesc.value = ''
    aiTagsAdded.value = []
    aiTagsRemoved.value = []
  }
}

const doAIAbandon = async () => {
  await call('aiConfirm', () => abandonAIReview(aiSessionId.value))
  aiSessionId.value = ''
  aiSessionBiz.value = ''
  aiConversation.value = []
  aiGeneratedDesc.value = ''
  aiTagsAdded.value = []
  aiTagsRemoved.value = []
}

// ── AI Personalization ─────────────────────────────────────────────────────────
const persLat = ref(null); const persLng = ref(null); const persLimit = ref(5)
const persLoading = ref(false); const persQuery = ref(''); const persProfileSize = ref(0)
const persResults = ref([])

const callPersonalized = async () => {
  persLoading.value = true
  persQuery.value = ''; persProfileSize.value = 0; persResults.value = []
  const params = {}
  if (persLat.value != null) params.lat = persLat.value
  if (persLng.value != null) params.lng = persLng.value
  if (persLimit.value) params.limit = persLimit.value
  await call('personalized', () => getPersonalized(params))
  if (!res.personalized?._error) {
    persQuery.value = res.personalized?.query || ''
    persProfileSize.value = res.personalized?.profile_size || 0
    persResults.value = res.personalized?.results || []
  }
  persLoading.value = false
}

// ── On mount ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  callStats(); callCategories(); callTags()
  // Restore session from localStorage
  const saved = getSavedToken()
  if (saved) {
    authToken.value = saved
    try {
      const r = await getMe()
      userProfile.value = r.data
    } catch {
      // Token expired or invalid — clear it
      authToken.value = ''
      setAuthToken(null)
    }
  }
})
</script>

<style scoped>
.api-demo {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #e2e8f0;
  background: #0a1220;
  min-height: 100vh;
}
header { margin-bottom: 32px; }
h1 { margin: 0 0 4px; font-size: 28px; }
.subtitle { color: #94a3b8; margin: 0 0 16px; font-size: 14px; }
.subtitle code { background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.toc { display: flex; flex-wrap: wrap; gap: 8px; }
.toc a { color: #818cf8; font-size: 13px; text-decoration: none; padding: 4px 12px; border: 1px solid #334155; border-radius: 999px; }
.toc a:hover { background: rgba(99,102,241,0.15); }

.endpoint { margin: 0 0 32px; padding: 20px; border: 1px solid #1e293b; border-radius: 12px; background: #0f172a; }
.endpoint h2 { margin: 0 0 6px; font-size: 16px; color: #f8fafc; }
.endpoint h3 { margin: 20px 0 6px; font-size: 14px; color: #cbd5e1; border-top: 1px solid #1e293b; padding-top: 14px; }
.params { color: #64748b; font-weight: 400; font-size: 13px; }
.desc { color: #94a3b8; font-size: 13px; margin: 0 0 10px; }
.desc code { background: #1e293b; padding: 1px 5px; border-radius: 3px; font-size: 12px; }
.note { color: #fbbf24; font-size: 12px; margin: 4px 0; }

.fields { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px; }
.actions { margin-bottom: 8px; }

input, select {
  background: #1e293b; border: 1px solid #334155; color: #e2e8f0;
  padding: 6px 10px; border-radius: 6px; font-size: 13px;
}
input.wide { flex: 2; min-width: 200px; }
input:focus, select:focus { outline: none; border-color: #6366f1; }

button {
  background: #334155; color: #e2e8f0; border: 1px solid #475569;
  padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px;
}
button:hover:not(:disabled) { background: #475569; }
button:disabled { opacity: 0.4; cursor: not-allowed; }
button.small { padding: 3px 10px; font-size: 12px; }
button.danger { color: #f87171; border-color: rgba(248,113,113,0.3); background: transparent; }

.file-label {
  display: inline-flex; align-items: center; gap: 4px;
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;
}

/* Response box */
.response-box {
  margin-top: 8px; background: #1e293b; border-radius: 8px;
  max-height: 400px; overflow: auto; font-size: 12px;
}
.response-box pre {
  margin: 0; padding: 12px; white-space: pre-wrap; word-break: break-word;
  color: #94a3b8; font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.response-box .loading { padding: 12px; color: #64748b; }
.error-resp { padding: 12px; }
.error-badge { display: inline-block; background: #7f1d1d; color: #fca5a5; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-bottom: 6px; }
.error-resp pre { color: #fca5a5; }

/* Tag pills */
.tag-pills { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.pill {
  padding: 4px 10px; border-radius: 999px; font-size: 12px; cursor: pointer;
  background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); color: #a5b4fc;
  transition: all 0.15s;
}
.pill:hover { background: rgba(99,102,241,0.2); }
.pill.active { background: rgba(99,102,241,0.4); border-color: #6366f1; }
.pill.small { font-size: 10px; padding: 2px 7px; cursor: default; }
.pill small { color: #64748b; }

/* Auth */
.auth-status { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; padding: 10px 14px; background: #1e293b; border-radius: 8px; margin-bottom: 14px; font-size: 13px; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.badge.ok { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.badge.warn { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.token { font-size: 11px; color: #64748b; background: #0f172a; padding: 2px 6px; border-radius: 4px; }

/* Search result cards */
.results-grid { display: flex; flex-direction: column; gap: 8px; margin: 10px 0; }
.result-card {
  display: flex; gap: 12px; padding: 10px; background: #1e293b; border-radius: 8px;
  border: 1px solid #334155;
}
.result-img { width: 80px; height: 60px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.result-body { display: flex; flex-direction: column; gap: 2px; font-size: 13px; min-width: 0; }
.result-body strong { color: #f8fafc; }
.result-body .meta { color: #64748b; font-size: 11px; }
.result-tags { display: flex; flex-wrap: wrap; gap: 3px; }

/* AI Chat */
.ai-chat-header { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #1e293b; border-radius: 8px; margin: 12px 0 8px; font-size: 13px; }
.ai-chat-header code { font-size: 11px; color: #64748b; }
.ai-chat-box { display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #0a1220; border: 1px solid #1e293b; border-radius: 8px; max-height: 400px; overflow-y: auto; margin: 8px 0; }
.ai-msg { padding: 8px 12px; border-radius: 10px; max-width: 85%; font-size: 13px; line-height: 1.5; }
.ai-msg.assistant { background: #1e293b; align-self: flex-start; color: #e2e8f0; }
.ai-msg.user { background: rgba(99,102,241,0.2); align-self: flex-end; color: #c7d2fe; }
.ai-role { font-size: 10px; font-weight: 600; text-transform: uppercase; color: #64748b; display: block; margin-bottom: 2px; }
.ai-text { display: block; }
.ai-tags-info { font-size: 12px; padding: 6px 12px; background: #1e293b; border-radius: 6px; margin: 6px 0; display: flex; gap: 8px; flex-wrap: wrap; }
.tag-added { color: #4ade80; }
.tag-removed { color: #f87171; }
.ai-generated { padding: 12px; background: #1e293b; border-radius: 8px; margin: 8px 0; border-left: 3px solid #6366f1; }
.ai-generated strong { font-size: 12px; color: #a5b4fc; }
.ai-generated p { color: #e2e8f0; font-size: 13px; margin: 6px 0 0; line-height: 1.6; }
.confirm-btn { background: rgba(74,222,128,0.15); color: #4ade80; border-color: rgba(74,222,128,0.3); }
.confirm-btn:hover:not(:disabled) { background: rgba(74,222,128,0.25); }
</style>