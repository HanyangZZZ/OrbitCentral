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

    <!-- ── Auth: Register / Login / Profile ───────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>Auth <span style="color:#94a3b8;font-size:14px">/api/auth/*</span></h2>

      <!-- Not logged in -->
      <div v-if="!authToken">
        <!-- Mode toggle -->
        <div style="display:flex;gap:8px;margin-bottom:12px">
          <button @click="authMode='login'" :style="{fontWeight: authMode==='login' ? 700 : 400, borderBottom: authMode==='login' ? '2px solid #6366f1' : 'none', background:'none', color:'#e2e8f0', padding:'4px 12px', cursor:'pointer'}">Login</button>
          <button @click="authMode='register'" :style="{fontWeight: authMode==='register' ? 700 : 400, borderBottom: authMode==='register' ? '2px solid #6366f1' : 'none', background:'none', color:'#e2e8f0', padding:'4px 12px', cursor:'pointer'}">Register</button>
        </div>

        <!-- Login form -->
        <div v-if="authMode==='login'" style="display:flex;gap:8px;flex-wrap:wrap">
          <input v-model="authUser" placeholder="Username or email" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;min-width:180px" />
          <input v-model="authPass" type="password" placeholder="Password" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;min-width:140px" />
          <button @click="doLogin" :disabled="!authUser || !authPass">Login</button>
        </div>

        <!-- Register form -->
        <div v-if="authMode==='register'" style="display:flex;flex-direction:column;gap:8px;max-width:400px">
          <input v-model="regEmail" type="email" placeholder="Email" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
          <input v-model="regUsername" placeholder="Username" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
          <input v-model="regDisplayName" placeholder="Display name (optional)" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
          <input v-model="regPass" type="password" placeholder="Password (min 8 chars)" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
          <button @click="doRegister" :disabled="!regEmail || !regUsername || !regPass" style="align-self:flex-start">Register</button>
        </div>

        <p v-if="authErr" style="color:#f87171;font-size:13px;margin-top:8px">{{ authErr }}</p>
        <p v-if="authOk" style="color:#4ade80;font-size:13px;margin-top:8px">{{ authOk }}</p>
      </div>

      <!-- Logged in: user profile -->
      <div v-else>
        <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
          <span style="color:#4ade80;font-size:13px">Logged in as <b>{{ userProfile?.username || authUser }}</b></span>
          <span style="color:#64748b;font-size:11px">(Token {{ authToken.slice(0, 8) }}...)</span>
          <span v-if="userProfile?.email_verified" style="color:#4ade80;font-size:11px;border:1px solid rgba(74,222,128,0.3);border-radius:4px;padding:2px 6px">✓ Verified</span>
          <span v-else style="color:#fbbf24;font-size:11px;border:1px solid rgba(251,191,36,0.3);border-radius:4px;padding:2px 6px">✉ Unverified</span>
          <button @click="doLogout" style="font-size:12px;color:#f87171;background:none;border:1px solid rgba(248,113,113,0.3);border-radius:4px;padding:3px 8px;cursor:pointer">Logout</button>
        </div>

        <!-- Profile details -->
        <div v-if="userProfile" style="margin-top:12px;padding:12px;background:#1e293b;border-radius:8px;font-size:13px">
          <div style="display:grid;grid-template-columns:auto 1fr;gap:4px 12px;color:#94a3b8">
            <span>Email:</span><span style="color:#e2e8f0">{{ userProfile.email }}</span>
            <span>Display:</span><span style="color:#e2e8f0">{{ userProfile.display_name || '—' }}</span>
            <span>Bio:</span><span style="color:#e2e8f0">{{ userProfile.bio || '—' }}</span>
          </div>
        </div>

        <!-- Verification actions -->
        <div v-if="!userProfile?.email_verified" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <button @click="doResendVerify" style="font-size:12px">Resend Verification Email</button>
          <input v-model="verifyTokenInput" placeholder="Paste verification token" style="flex:1;min-width:200px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;font-size:12px" />
          <button @click="doVerifyEmail" :disabled="!verifyTokenInput" style="font-size:12px">Verify</button>
        </div>

        <p v-if="authErr" style="color:#f87171;font-size:13px;margin-top:4px">{{ authErr }}</p>
        <p v-if="authOk" style="color:#4ade80;font-size:13px;margin-top:4px">{{ authOk }}</p>
        <!-- Forgot / Reset Password -->
        <div style="margin-top:16px;padding:12px;border:1px dashed #475569;border-radius:8px">
          <h3 style="margin:0 0 8px;font-size:14px;color:#94a3b8">Forgot / Reset Password</h3>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
            <input v-model="forgotEmail" type="email" placeholder="Email for password reset" style="flex:1;min-width:200px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;font-size:12px" />
            <button @click="doForgotPassword" :disabled="!forgotEmail" style="font-size:12px">Send Reset Email</button>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:8px">
            <input v-model="resetTokenInput" placeholder="Paste reset token" style="flex:1;min-width:160px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;font-size:12px" />
            <input v-model="resetNewPassword" type="password" placeholder="New password" style="flex:1;min-width:140px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px;font-size:12px" />
            <button @click="doResetPassword" :disabled="!resetTokenInput || !resetNewPassword" style="font-size:12px">Reset Password</button>
          </div>
          <p v-if="resetMsg" :style="{fontSize:'12px',marginTop:'6px',color: resetMsg.startsWith('Error') ? '#f87171' : '#4ade80'}">{{ resetMsg }}</p>
        </div>      </div>
    </section>

    <!-- ── Reviews ────────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>Reviews <span style="color:#94a3b8;font-size:14px">GET/POST /api/reviews/?business=</span></h2>

      <!-- Load reviews for a business -->
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
        <input v-model.number="reviewBizId" type="number" placeholder="Business ID" style="width:120px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
        <button @click="loadReviews" :disabled="!reviewBizId">Load Reviews</button>
      </div>

      <!-- Review list -->
      <div v-if="reviews.length" style="margin-bottom:16px">
        <p style="font-size:12px;color:#94a3b8;margin-bottom:8px">{{ reviews.length }} review{{ reviews.length > 1 ? 's' : '' }} for business #{{ reviewBizId }}</p>
        <div v-for="r in reviews" :key="r.id" style="padding:12px;margin-bottom:8px;background:#1e293b;border-radius:8px;border:1px solid #334155">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <span style="color:#fbbf24;font-size:14px">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
              <span style="color:#e2e8f0;font-weight:600;margin-left:8px">{{ r.username }}</span>
              <span style="color:#64748b;font-size:11px;margin-left:8px">{{ new Date(r.created_at).toLocaleDateString() }}</span>
            </div>
            <button v-if="authToken" @click="removeReview(r.id)" style="font-size:11px;color:#f87171;background:none;border:1px solid rgba(248,113,113,0.3);border-radius:4px;padding:2px 6px;cursor:pointer">Delete</button>
          </div>
          <p v-if="r.description" style="color:#cbd5e1;margin:6px 0 0;font-size:13px">{{ r.description }}</p>
          <img v-if="r.image_url" :src="r.image_url" alt="Review photo" style="margin-top:8px;max-width:200px;max-height:150px;border-radius:6px;object-fit:cover" />
          <!-- Vote buttons -->
          <div v-if="authToken" style="display:flex;gap:10px;margin-top:8px">
            <button v-for="vt in ['useful','funny','cool']" :key="vt" @click="doVoteReview(r, vt)"
              :style="{fontSize:'11px',padding:'3px 10px',borderRadius:'999px',cursor:'pointer',
                background: (r.user_votes||[]).includes(vt) ? 'rgba(99,102,241,0.35)' : 'rgba(99,102,241,0.08)',
                border: (r.user_votes||[]).includes(vt) ? '1px solid #6366f1' : '1px solid rgba(99,102,241,0.2)',
                color: (r.user_votes||[]).includes(vt) ? '#c7d2fe' : '#a5b4fc'}">
              {{ vt === 'useful' ? '👍' : vt === 'funny' ? '😂' : '😎' }} {{ vt }}
              <span style="margin-left:4px;color:#64748b">({{ (r.vote_counts || {})[vt] || 0 }})</span>
            </button>
          </div>
        </div>
      </div>
      <p v-else-if="reviewsLoaded" style="color:#64748b;font-size:13px">No reviews yet for this business.</p>

      <!-- Submit review form (requires auth) -->
      <div v-if="authToken" style="padding:12px;border:1px dashed #475569;border-radius:8px;margin-top:8px">
        <h3 style="margin:0 0 8px;font-size:14px;color:#94a3b8">Submit a Review</h3>
        <div style="display:flex;flex-direction:column;gap:8px">
          <div style="display:flex;gap:8px;align-items:center">
            <label style="font-size:12px;color:#94a3b8;white-space:nowrap">Business ID:</label>
            <input v-model.number="newReviewBizId" type="number" placeholder="Business ID" style="width:100px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
            <label style="font-size:12px;color:#94a3b8;white-space:nowrap;margin-left:8px">Rating:</label>
            <div style="display:flex;gap:2px">
              <span v-for="s in 5" :key="s" @click="newReviewRating = s"
                :style="{cursor:'pointer',fontSize:'20px',color: s <= newReviewRating ? '#fbbf24' : '#475569'}">★</span>
            </div>
          </div>
          <textarea v-model="newReviewDesc" placeholder="Write your review..." rows="3" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:8px 10px;border-radius:4px;resize:vertical"></textarea>
          <div style="display:flex;gap:8px;align-items:center">
            <label style="font-size:12px;color:#94a3b8;cursor:pointer;padding:4px 10px;border:1px solid #475569;border-radius:4px">
              📷 Attach Photo
              <input type="file" accept="image/*" @change="onPhotoSelect" style="display:none" />
            </label>
            <span v-if="newReviewPhoto" style="font-size:11px;color:#4ade80">Photo attached ✓</span>
            <button v-if="newReviewPhoto" @click="newReviewPhoto = null" style="font-size:11px;color:#f87171;background:none;border:none;cursor:pointer">Remove</button>
          </div>
          <button @click="submitReview" :disabled="!newReviewBizId || !newReviewRating || submittingReview" style="align-self:flex-start">
            {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
          </button>
          <p v-if="reviewSubmitErr" style="color:#f87171;font-size:12px">{{ reviewSubmitErr }}</p>
          <p v-if="reviewSubmitOk" style="color:#4ade80;font-size:12px">{{ reviewSubmitOk }}</p>
        </div>
      </div>
      <p v-else style="color:#64748b;font-size:12px;margin-top:8px">Register &amp; verify your email above to submit a review.</p>
    </section>
    <!-- ── Bookmarks ────────────────────────────────────────────────────── -->
    <section style="margin:24px 0;padding:16px;border:1px solid #334155;border-radius:8px">
      <h2>Bookmarks <span style="color:#94a3b8;font-size:14px">/api/bookmarks/*</span></h2>

      <div v-if="authToken && userProfile?.email_verified">
        <!-- Toggle bookmark -->
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <input v-model.number="bookmarkBizId" type="number" placeholder="Business ID" style="width:120px;background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:6px 10px;border-radius:4px" />
          <button @click="doToggleBookmark" :disabled="!bookmarkBizId">Toggle Bookmark</button>
          <button @click="doCheckBookmark" :disabled="!bookmarkBizId">Check</button>
          <button @click="loadBookmarks">Load My Bookmarks</button>
          <button @click="loadBookmarkIds">Get Bookmark IDs</button>
        </div>
        <p v-if="bookmarkMsg" :style="{fontSize:'13px',marginTop:'6px',color: bookmarkMsg.startsWith('Error') ? '#f87171' : '#4ade80'}">{{ bookmarkMsg }}</p>

        <!-- Bookmark IDs -->
        <div v-if="bookmarkIdList.length" style="margin-top:8px;font-size:12px;color:#94a3b8">
          Bookmarked business IDs: <span style="color:#e2e8f0">{{ bookmarkIdList.join(', ') }}</span>
        </div>

        <!-- Bookmark list -->
        <div v-if="bookmarks.length" style="margin-top:10px">
          <p style="font-size:12px;color:#94a3b8">{{ bookmarks.length }} bookmark{{ bookmarks.length > 1 ? 's' : '' }}</p>
          <div v-for="bm in bookmarks" :key="bm.id" style="padding:8px 12px;margin-top:6px;background:#1e293b;border-radius:8px;border:1px solid #334155;display:flex;justify-content:space-between;align-items:center">
            <div>
              <b style="color:#e2e8f0">#{{ bm.business }}</b> <span style="color:#94a3b8">{{ bm.business_name }}</span>
              <span v-if="bm.note" style="color:#64748b;font-size:11px;margin-left:8px">— {{ bm.note }}</span>
              <span style="color:#475569;font-size:11px;margin-left:8px">{{ new Date(bm.created_at).toLocaleDateString() }}</span>
            </div>
            <button @click="doRemoveBookmark(bm.id)" style="font-size:11px;color:#f87171;background:none;border:1px solid rgba(248,113,113,0.3);border-radius:4px;padding:2px 6px;cursor:pointer">Remove</button>
          </div>
        </div>
      </div>
      <p v-else-if="authToken" style="color:#fbbf24;font-size:12px">Verify your email to use bookmarks.</p>
      <p v-else style="color:#64748b;font-size:12px">Register &amp; verify your email to bookmark businesses.</p>
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
import { getCategories, getTags, searchTags, getBusinesses, getStats, searchBusinesses, register, login, verifyEmail, getMe, resendVerify, forgotPassword, resetPassword, setAuthToken, getReviews, createReview, deleteReview, voteReview, getBookmarks, toggleBookmark, checkBookmark, deleteBookmark, getBookmarkIds } from '../api/client'

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

// ── Auth state ────────────────────────────────────────────────────────────────
const authMode = ref('login')  // 'login' | 'register'
const authUser = ref('')
const authPass = ref('')
const authToken = ref('')
const authErr = ref('')
const authOk = ref('')
const userProfile = ref(null)
// Register-specific fields
const regEmail = ref('')
const regUsername = ref('')
const regDisplayName = ref('')
const regPass = ref('')
// Email verification
const verifyTokenInput = ref('')
// Password reset
const forgotEmail = ref('')
const resetTokenInput = ref('')
const resetNewPassword = ref('')
const resetMsg = ref('')

const loadProfile = async () => {
  try {
    const res = await getMe()
    userProfile.value = res.data
  } catch { userProfile.value = null }
}

const doLogin = async () => {
  authErr.value = ''; authOk.value = ''
  try {
    const res = await login(authUser.value, authPass.value)
    authToken.value = res.data.token
    setAuthToken(authToken.value)
    userProfile.value = res.data.user || null
    authPass.value = ''
    authOk.value = 'Logged in!'
  } catch (e) {
    authErr.value = e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || 'Login failed'
  }
}

const doRegister = async () => {
  authErr.value = ''; authOk.value = ''
  try {
    const res = await register({
      email: regEmail.value,
      username: regUsername.value,
      password: regPass.value,
      display_name: regDisplayName.value || undefined,
    })
    authToken.value = res.data.token
    setAuthToken(authToken.value)
    userProfile.value = res.data.user || null
    authOk.value = 'Registered! Check your email for a verification link.'
    regEmail.value = ''; regUsername.value = ''; regPass.value = ''; regDisplayName.value = ''
  } catch (e) {
    const d = e.response?.data
    authErr.value = d?.detail || d?.email?.[0] || d?.username?.[0] || d?.password?.[0] || JSON.stringify(d) || 'Registration failed'
  }
}

const doVerifyEmail = async () => {
  authErr.value = ''; authOk.value = ''
  try {
    await verifyEmail(verifyTokenInput.value)
    authOk.value = 'Email verified!'
    verifyTokenInput.value = ''
    await loadProfile()
  } catch (e) {
    authErr.value = e.response?.data?.detail || 'Verification failed'
  }
}

const doResendVerify = async () => {
  authErr.value = ''; authOk.value = ''
  try {
    const res = await resendVerify()
    authOk.value = res.data?.detail || 'Verification email sent!'
  } catch (e) {
    authErr.value = e.response?.data?.detail || 'Could not resend'
  }
}

const doForgotPassword = async () => {
  resetMsg.value = ''
  try {
    const res = await forgotPassword(forgotEmail.value)
    resetMsg.value = res.data?.detail || 'If that email exists, a reset link was sent.'
    forgotEmail.value = ''
  } catch (e) {
    resetMsg.value = 'Error: ' + (e.response?.data?.detail || 'Request failed')
  }
}

const doResetPassword = async () => {
  resetMsg.value = ''
  try {
    const res = await resetPassword(resetTokenInput.value, resetNewPassword.value)
    resetMsg.value = res.data?.detail || 'Password reset! Please log in with your new password.'
    resetTokenInput.value = ''; resetNewPassword.value = ''
    // Force logout since all tokens are invalidated
    doLogout()
  } catch (e) {
    const d = e.response?.data
    resetMsg.value = 'Error: ' + (d?.detail || d?.new_password?.[0] || JSON.stringify(d) || 'Reset failed')
  }
}

const doLogout = () => {
  authToken.value = ''
  userProfile.value = null
  setAuthToken(null)
  authErr.value = ''; authOk.value = ''
}

// ── Bookmarks state ───────────────────────────────────────────────────────────
const bookmarkBizId = ref(null)
const bookmarks = ref([])
const bookmarkIdList = ref([])
const bookmarkMsg = ref('')

const loadBookmarks = async () => {
  bookmarkMsg.value = ''
  try {
    const res = await getBookmarks()
    bookmarks.value = res.data.results ?? res.data ?? []
  } catch (e) {
    bookmarkMsg.value = 'Error: ' + (e.response?.data?.detail || 'Failed to load bookmarks')
  }
}

const loadBookmarkIds = async () => {
  bookmarkMsg.value = ''
  try {
    const res = await getBookmarkIds()
    bookmarkIdList.value = res.data.business_ids ?? []
    bookmarkMsg.value = `${bookmarkIdList.value.length} bookmarked business(es)`
  } catch (e) {
    bookmarkMsg.value = 'Error: ' + (e.response?.data?.detail || 'Failed')
  }
}

const doToggleBookmark = async () => {
  bookmarkMsg.value = ''
  try {
    const res = await toggleBookmark(bookmarkBizId.value)
    bookmarkMsg.value = res.data.status === 'added' ? 'Bookmarked!' : 'Bookmark removed.'
    if (bookmarks.value.length) loadBookmarks()
  } catch (e) {
    bookmarkMsg.value = 'Error: ' + (e.response?.data?.detail || 'Toggle failed')
  }
}

const doCheckBookmark = async () => {
  bookmarkMsg.value = ''
  try {
    const res = await checkBookmark(bookmarkBizId.value)
    bookmarkMsg.value = res.data.bookmarked ? `Business #${bookmarkBizId.value} is bookmarked ✓` : `Business #${bookmarkBizId.value} is NOT bookmarked`
  } catch (e) {
    bookmarkMsg.value = 'Error: ' + (e.response?.data?.detail || 'Check failed')
  }
}

const doRemoveBookmark = async (id) => {
  try {
    await deleteBookmark(id)
    bookmarks.value = bookmarks.value.filter(b => b.id !== id)
    bookmarkMsg.value = 'Bookmark removed.'
  } catch (e) {
    bookmarkMsg.value = 'Error: ' + (e.response?.data?.detail || 'Delete failed')
  }
}

// ── Reviews state ─────────────────────────────────────────────────────────────
const reviewBizId = ref(null)
const reviews = ref([])
const reviewsLoaded = ref(false)
const newReviewBizId = ref(null)
const newReviewRating = ref(0)
const newReviewDesc = ref('')
const newReviewPhoto = ref(null)
const submittingReview = ref(false)
const reviewSubmitErr = ref('')
const reviewSubmitOk = ref('')

const loadReviews = async () => {
  if (!reviewBizId.value) return
  reviewsLoaded.value = false
  try {
    const res = await getReviews({ business: reviewBizId.value })
    reviews.value = res.data.results ?? res.data ?? []
    reviewsLoaded.value = true
    // Pre-fill the submission form with the same business ID
    newReviewBizId.value = reviewBizId.value
  } catch (e) {
    reviews.value = []
    reviewsLoaded.value = true
  }
}

const onPhotoSelect = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { newReviewPhoto.value = reader.result }
  reader.readAsDataURL(file)
}

const submitReview = async () => {
  submittingReview.value = true
  reviewSubmitErr.value = ''
  reviewSubmitOk.value = ''
  try {
    const payload = {
      business: newReviewBizId.value,
      rating: newReviewRating.value,
      description: newReviewDesc.value,
    }
    if (newReviewPhoto.value) payload.photo = newReviewPhoto.value
    await createReview(payload)
    reviewSubmitOk.value = 'Review submitted successfully!'
    newReviewRating.value = 0
    newReviewDesc.value = ''
    newReviewPhoto.value = null
    // Reload reviews if we're viewing the same business
    if (reviewBizId.value === newReviewBizId.value) loadReviews()
  } catch (e) {
    reviewSubmitErr.value = e.response?.data?.detail
      || e.response?.data?.non_field_errors?.[0]
      || JSON.stringify(e.response?.data) || 'Submission failed'
  } finally {
    submittingReview.value = false
  }
}

const removeReview = async (id) => {
  try {
    await deleteReview(id)
    reviews.value = reviews.value.filter(r => r.id !== id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Delete failed')
  }
}

const doVoteReview = async (review, voteType) => {
  try {
    const res = await voteReview(review.id, voteType)
    // Update the review's local state optimistically
    if (!review.vote_counts) review.vote_counts = { useful: 0, funny: 0, cool: 0 }
    if (!review.user_votes) review.user_votes = []
    if (res.data.status === 'added') {
      review.vote_counts[voteType] = (review.vote_counts[voteType] || 0) + 1
      review.user_votes.push(voteType)
    } else {
      review.vote_counts[voteType] = Math.max(0, (review.vote_counts[voteType] || 1) - 1)
      review.user_votes = review.user_votes.filter(v => v !== voteType)
    }
  } catch (e) {
    alert(e.response?.data?.detail || 'Vote failed')
  }
}

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
