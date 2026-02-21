/* Section 5 — Architecture & Design Process (10%) */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'architecture',
  title: 'Architecture & Design',
  icon: ICON.layers,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Section 4</span>
      <h2 class="section-title">Website Structure &amp; Design Process</h2>
      <p class="section-subtitle">From requirements to a fully containerised production stack</p>
    </div>

    <h3>Phase 1 — Core Feature Set</h3>
    <table class="data-table">
      <thead><tr><th>Feature</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td><strong>Browse by Category</strong></td><td>Parent → child taxonomy (e.g. Restaurants → Cafés). Filter &amp; sort</td></tr>
        <tr><td><strong>Search &amp; Sort</strong></td><td>By name, category, rating, date, review count</td></tr>
        <tr><td><strong>Business Detail</strong></td><td>Photos, hours, contact, Google Maps, accessibility, amenities</td></tr>
        <tr><td><strong>Reviews &amp; Ratings</strong></td><td>1–5 stars with AI-assisted writing, community voting</td></tr>
        <tr><td><strong>Bookmarks</strong></td><td>Save businesses with optional notes</td></tr>
        <tr><td><strong>Deals &amp; Coupons</strong></td><td>Dedicated promotions page</td></tr>
        <tr><td><strong>User Accounts</strong></td><td>Register, login, email verify, password reset, profile</td></tr>
      </tbody>
    </table>

    <h3>Initial UI Design — Figma Prototypes</h3>
    <p>Before writing any code, we designed the frontend user experience in <strong>Figma</strong> — mapping out
    page layouts, navigation flows, and component structures to align the team on a shared vision.</p>
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.2rem; margin:1.5rem 0;">
      <figure style="margin:0; text-align:center;">
        <img src="images/figma-design-1.png" alt="Figma Design 1"
             style="width:100%; border-radius:10px; border:2px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,.25); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/figma-design-2.png" alt="Figma Design 2"
             style="width:100%; border-radius:10px; border:2px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,.25); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/figma-design-3.png" alt="Figma Design 3"
             style="width:100%; border-radius:10px; border:2px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,.25); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
      </figure>
    </div>

    <h3>Phase 2 — Architecture Selection</h3>
    <table class="data-table">
      <thead><tr><th>Decision</th><th>Choice</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><strong>Frontend</strong></td><td>Vue 3 (Composition API)</td><td>Lightweight, reactive, modular composables</td></tr>
        <tr><td><strong>Multi-platform</strong></td><td>Capacitor</td><td>One codebase → web + iOS + Android</td></tr>
        <tr><td><strong>Backend</strong></td><td>Django + DRF (Python)</td><td>Best AI/ML ecosystem, OpenAI SDK</td></tr>
        <tr><td><strong>Database</strong></td><td>PostgreSQL 16 + pgvector + PostGIS</td><td>Vector + geo queries in SQL</td></tr>
        <tr><td><strong>Task Queue</strong></td><td>Celery + Redis</td><td>Background AI tasks don't block API</td></tr>
        <tr><td><strong>Web Server</strong></td><td>Nginx → Gunicorn</td><td>SSL, rate limiting, static files</td></tr>
        <tr><td><strong>AI / LLM</strong></td><td>OpenAI GPT-4.1 + text-embedding-3-small</td><td>Personalization, reviews, <strong>1536-dim</strong> embeddings</td></tr>
        <tr><td><strong>Build</strong></td><td>Vite</td><td>Fast HMR, optimized production builds</td></tr>
      </tbody>
    </table>

    <h3>Phase 3 — Containerized Architecture (8 Services)</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TB
  subgraph Docker["Docker Compose Stack"]
    NGINX["Nginx\nSSL · Reverse Proxy · Rate Limiting"]
    WEB["Django + Gunicorn\n3 workers \u00d7 2 threads"]
    CELERY["Celery Worker\nBackground Tasks"]
    PG["PostgreSQL 16\npgvector + PostGIS"]
    REDIS["Redis\nTask Broker + Cache"]
    ADMINER["Adminer\nDB Admin"]
    FLOWER["Flower\nTask Monitor"]
    CERT["Certbot\nSSL Auto-Renew"]
  end
  NGINX --> WEB
  WEB --> PG
  WEB --> REDIS
  CELERY --> PG
  CELERY --> REDIS
  FLOWER --> REDIS
  ADMINER --> PG
  CERT --> NGINX
      </pre>
      <p class="diagram-caption"><strong>8</strong> isolated containers — <code>docker compose up</code> deploys everything</p>
    </div>

    <h3>Phase 4 — Database Design</h3>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:2rem; align-items:start; margin:1.5rem 0;">
      <div>
        <table class="data-table">
          <thead><tr><th>Extension</th><th>Purpose</th></tr></thead>
          <tbody>
            <tr><td><strong>pgvector</strong></td><td><strong>1536-dim</strong> embeddings on each business row → cosine distance in SQL</td></tr>
            <tr><td><strong>PostGIS</strong></td><td>Geographic points + <code>SearchedArea</code> circles → distance queries in SQL</td></tr>
          </tbody>
        </table>
        <div class="highlight-box">
          <strong>Key advantage:</strong> The embedding lives on the business row itself — a <strong>single SQL
          query</strong> can filter by category, compute cosine similarity, calculate geographic distance,
          and sort by weighted score — all in <strong>one pass</strong>. No external vector DB needed.
        </div>
      </div>
      <figure style="margin:0; text-align:center;">
        <img src="images/adminer-db-schema.png" alt="Adminer — PostgreSQL Database Schema"
             style="width:100%; border-radius:10px; border:2px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,.25); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.5rem; font-size:.85rem; opacity:.7;">Adminer view — <strong>24 tables</strong> in production PostgreSQL</figcaption>
      </figure>
    </div>

    <h3>Phase 5 — Celery &amp; the Service Layer</h3>
    <p><strong>Celery</strong> is a distributed task queue that runs heavy work in a
    <em>separate worker process</em>, keeping the Django API <strong>fast and responsive</strong>. 
    Tasks are published to <strong>Redis</strong> and consumed by the Celery worker container.
    All tasks use <code>acks_late=True</code> (acknowledged only after success) and automatic
    retries with exponential back-off.</p>

    <table class="data-table">
      <thead><tr><th>Celery Task</th><th>When Triggered</th><th>What It Does</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>ensure_area_covered_task</strong></td>
          <td>Vibe search or personalised feed receives a location</td>
          <td>Runs the full <strong>8-step</strong> import pipeline (see below). <strong>3 retries</strong>, 30 s delay</td>
        </tr>
        <tr>
          <td><strong>send_verification_email_task</strong></td>
          <td>User registers a new account</td>
          <td>Sends verification email via Brevo transactional API. <strong>3 retries</strong>, 10 s delay</td>
        </tr>
        <tr>
          <td><strong>send_password_reset_email_task</strong></td>
          <td>User requests a password reset</td>
          <td>Sends reset-link email via Brevo. <strong>3 retries</strong>, 10 s delay</td>
        </tr>
      </tbody>
    </table>

    <h3>Import Pipeline — How Businesses Enter the System</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  TRIGGER["User searches or opens personalised feed\nwith lat/lng"] --> CHECK{"SearchedArea\ncircle covers\nthis point?"}
  CHECK -->|"Yes"| SKIP["Skip import\nuse existing data"]
  CHECK -->|"No"| LOCK["Acquire per-area lock\n(prevent duplicate imports)"]
  LOCK --> S1["Step 1 · Google Places API\n8 concurrent workers\n20 business types × grid"]
  S1 --> S2["Step 2 · Filter duplicates\ncheck google_place_id vs DB\ncap at 100 per import"]
  S2 --> S3["Step 3 · GPT-4o-mini classify\n20 concurrent workers\nbatches of 10"]
  S3 --> S4["Step 4 · Keep small only\nfilter out chains"]
  S4 --> S5["Step 5 · Resolve tags\nnormalise + blocklist + AI\nconsolidate synonyms"]
  S5 --> S6["Step 6 · Bulk create\nbusinesses + FK category\n+ M2M tags"]
  S6 --> S65["Step 6.5 · Images → GCS\n8 concurrent workers\ndownload + upload"]
  S65 --> S7["Step 7 · Generate embeddings\ntext-embedding-3-small\n4 concurrent workers"]
  S7 --> S8["Step 8 · Record SearchedArea\nPostGIS circle (5 km)\nonly on full success"]
      </pre>
      <p class="diagram-caption"><strong>8-step</strong> import pipeline orchestrated by <strong>Celery</strong> — runs entirely in the background</p>
    </div>
    <div class="highlight-box highlight-box--gold">
      <strong>Why Celery matters:</strong> The import pipeline touches Google Places API, OpenAI,
      and Google Cloud Storage — operations that can take <strong>10–30 seconds</strong>. Celery runs them off
      the request thread via <code>ensure_area_covered_task.delay(lat, lng)</code> (fire-and-forget).
      The user sees instant search results from cached data while new businesses are imported in the background.
    </div>

    <h3>Phase 6 — Backend Service Modules</h3>
    <table class="data-table">
      <thead><tr><th>Service</th><th>File</th><th>Responsibility</th></tr></thead>
      <tbody>
        <tr><td><strong>Google Places</strong></td><td><code>google_places.py</code></td><td>Grid search, concurrent fetch, field-mask for 30+ attributes</td></tr>
        <tr><td><strong>Import Pipeline</strong></td><td><code>import_pipeline.py</code></td><td>Orchestrates all 8 steps, per-area locking, success-only recording</td></tr>
        <tr><td><strong>Classification</strong></td><td><code>classification.py</code></td><td>GPT-4o-mini classifies category + generates tags (batches of 10)</td></tr>
        <tr><td><strong>Tags</strong></td><td><code>tags.py</code></td><td>Normalise, blocklist, GPT-4o-mini dedup, embed new tags</td></tr>
        <tr><td><strong>Embeddings</strong></td><td><code>embeddings.py</code></td><td>text-embedding-3-small → pgvector column on Business</td></tr>
        <tr><td><strong>Personalization</strong></td><td><code>personalization.py</code></td><td>GPT-4.1 analyses reviews + bookmarks → search query (RAG)</td></tr>
        <tr><td><strong>AI Review</strong></td><td><code>ai_review.py</code></td><td>Conversational review chat + function-calling tag detection</td></tr>
        <tr><td><strong>CAPTCHA</strong></td><td><code>captcha.py</code></td><td>reCAPTCHA v2/v3 server-side verification</td></tr>
        <tr><td><strong>GCS</strong></td><td><code>gcs.py</code></td><td>Download Google photos → upload to Cloud Storage bucket</td></tr>
        <tr><td><strong>Geocoding</strong></td><td><code>geocoding.py</code></td><td>Reverse geocode coordinates → city name for UI display</td></tr>
      </tbody>
    </table>

    <h3>Live System Overview</h3>
    <div class="demo-label">Live from API</div>
    <div id="live-stats" class="stats-grid loading-pulse">
      <div class="stat-card"><div class="stat-value">—</div><div class="stat-label">Loading…</div></div>
    </div>
  `,

  init(el) {
    API.getStats().then(data => {
      if (!data) return;
      const grid = el.querySelector('#live-stats');
      grid.classList.remove('loading-pulse');
      grid.classList.add('live-data');
      const topTags = (data.top_tags || []).slice(0, 6).map(t =>
        '<span class="tag-pill">' + t.name + ' <small>(' + t.c + ')</small></span>'
      ).join(' ');
      grid.innerHTML =
        '<div class="stat-card"><div class="stat-value">' + data.total_businesses + '</div><div class="stat-label">Businesses</div></div>'
        + '<div class="stat-card"><div class="stat-value">' + data.with_embeddings + '</div><div class="stat-label">With Embeddings</div></div>'
        + '<div class="stat-card"><div class="stat-value">' + data.tag_count + '</div><div class="stat-label">Tags</div></div>'
        + '<div class="stat-card"><div class="stat-value">' + data.searched_areas + '</div><div class="stat-label">Searched Areas</div></div>'
        + '<div class="stat-card"><div class="stat-value">' + (data.avg_rating || 0).toFixed(1) + ' ★</div><div class="stat-label">Avg Rating</div></div>'
        + '<div class="stat-card" style="grid-column: 1 / -1"><div class="stat-label" style="margin-bottom:6px">Top Tags</div><div>' + topTags + '</div></div>';
    });
  },
});
