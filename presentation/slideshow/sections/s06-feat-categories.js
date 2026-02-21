/* Feature 1 — Category Filtering, Vibe Search & Auto-Import */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-categories',
  title: 'Category & Vibe Search',
  icon: ICON.folder,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 1 of 7</span>
      <h2 class="section-title">Sorting Businesses by Category &amp; Vibe Search</h2>
      <p class="section-subtitle">FK categories, M2M tags, vector search, and automatic area imports</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  A["User opens Search Page"] --> B["Load category tree\nGET /api/categories/"]
  B --> C["Sidebar renders\nparent → child tree"]
  C --> D{"User clicks\ncategory"}
  D --> E["GET /api/businesses/\n?category=6\n&amp;ordering=-avg_rating"]
  E --> F["Results grid"]

  C --> G{"User types\nvibe query"}
  G --> H["GET /api/businesses/search/\n?q=cozy+brunch&amp;lat=43&amp;lng=-79"]
  H --> IMPORT{"SearchedArea\ncovers this\nlocation?"}
  IMPORT -->|"Yes"| RUN["Weighted SQL\nvibe 70% · proximity 15% · rating 15%"]
  IMPORT -->|"No"| CELERY["Celery .delay()\nimport pipeline\n(background)"]
  CELERY --> RUN
  RUN --> F

  C --> T{"User searches\ntag"}
  T --> TS["GET /api/tags/search/?q=romantic\ncosine similarity on tag embeddings"]
  TS --> TP["Tag pills displayed"]
  TP --> J["Click pills → AND filter"]
  J --> E
      </pre>
      <p class="diagram-caption">Category drill-down, vibe search (with auto-import), and tag filtering</p>
    </div>

    <h3>Live Categories</h3>
    <div class="demo-label">Live from API</div>
    <div id="live-categories" class="stats-grid loading-pulse">
      <div class="stat-card"><div class="stat-value">—</div><div class="stat-label">Loading…</div></div>
    </div>

    <h3>Live Tag Cloud</h3>
    <div class="demo-label">Live from API</div>
    <div id="live-tags" class="tag-cloud loading-pulse">
      <span class="tag-cloud-pill">Loading…</span>
    </div>

    <h3>How Categories &amp; Tags Enter the Database</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph LR
  GP["Google Places\n(raw data)"] --> GPT["GPT-4o-mini\nclassify → category\ngenerate → 3-5 tags"]
  GPT --> TAGS["Tag Service\nnormalise · blocklist\nGPT dedup synonyms"]
  TAGS --> PG["PostgreSQL\nFK category_id\nM2M junction table"]
  PG --> FE["Frontend\nSidebar + Tag Pills"]
  RC["AI Review Chat\n(crowd-sourced)"] -->|"add_tag()\nfunction call"| PG
      </pre>
      <p class="diagram-caption">Two pathways: AI import pipeline + user review chat both enrich tags</p>
    </div>

    <h3>Data Storage — FK Categories &amp; M2M Tags</h3>
    <table class="data-table">
      <thead><tr><th>Relationship</th><th>Type</th><th>How It Works</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>Business → Category</strong></td>
          <td>FK (Foreign Key)</td>
          <td>Each business has one <code>category_id</code> column pointing to the Category table.
          One category holds many businesses. Category itself has a self-referential FK
          (<code>parent_id</code>) creating the parent → child tree (e.g. Food &amp; Drink → Restaurants)</td>
        </tr>
        <tr>
          <td><strong>Business ↔ Tag</strong></td>
          <td>M2M (Many-to-Many)</td>
          <td>A <strong>junction table</strong> (<code>business_tags</code>) links <code>business_id</code>
          ↔ <code>tag_id</code>. One business can have many tags ("cozy", "wifi", "outdoor-seating")
          and one tag can belong to many businesses. Bulk-assigned via
          <code>bulk_create</code> during import</td>
        </tr>
        <tr>
          <td><strong>Business.embedding</strong></td>
          <td>pgvector (<strong>1536-dim</strong>)</td>
          <td>Stored directly on the business row. Composed from name + category + description + tags.
          Enables cosine-distance search in a single SQL query alongside category and geo filters</td>
        </tr>
        <tr>
          <td><strong>Tag.embedding</strong></td>
          <td>pgvector (<strong>1536-dim</strong>)</td>
          <td>Each tag also has its own embedding for semantic tag search
          (e.g. searching "romantic" matches "candle-lit" and "date-night")</td>
        </tr>
      </tbody>
    </table>

    <h3>SearchedArea — Automatic Business Import</h3>
    <div class="highlight-box highlight-box--accent">
      <strong>How it works:</strong> When a user triggers a vibe search or opens the personalised
      feed with a <code>lat/lng</code>, the backend checks whether a <strong>SearchedArea</strong>
      circle already covers that coordinate (PostGIS <code>ST_Distance</code>). If not, a Celery task
      fires the <strong>8-step</strong> import pipeline in the background:
    </div>

    <div class="pipeline-steps">
      <div class="pipeline-step">
        <span class="pipeline-num">1</span>
        <div class="pipeline-body">
          <strong>Google Places API</strong><br>
          Fetch businesses in a <strong>5 km</strong> radius — <strong>8 concurrent workers</strong>, <strong>20 business types</strong> × grid
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">2</span>
        <div class="pipeline-body">
          <strong>Filter Duplicates</strong><br>
          Check <code>google_place_id</code> against existing DB records
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">3</span>
        <div class="pipeline-body">
          <strong>GPT-4o-mini Classify</strong><br>
          Is it small/independent? Which category? Generate <strong>3–5 tags</strong>
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">4</span>
        <div class="pipeline-body">
          <strong>Filter Chains</strong><br>
          Remove franchises &amp; large chains — keep independents only
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">5</span>
        <div class="pipeline-body">
          <strong>Normalise &amp; Deduplicate Tags</strong><br>
          Blocklist + GPT synonym consolidation
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">6</span>
        <div class="pipeline-body">
          <strong>Bulk-Create Records</strong><br>
          Business rows with FK categories + M2M tags
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">6.5</span>
        <div class="pipeline-body">
          <strong>Photos → GCS</strong><br>
          Download Google photos → upload to Cloud Storage bucket
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step">
        <span class="pipeline-num">7</span>
        <div class="pipeline-body">
          <strong>Generate Embeddings</strong><br>
          text-embedding-3-small → <strong>1536-dim</strong> pgvector column
        </div>
      </div>
      <div class="pipeline-arrow">${ICON.arrowDown}</div>
      <div class="pipeline-step pipeline-step--final">
        <span class="pipeline-num">8</span>
        <div class="pipeline-body">
          <strong>Record SearchedArea</strong><br>
          PostGIS circle (<strong>5 km</strong>) — <em>only on full success</em>
        </div>
      </div>
    </div>
    <div class="highlight-box" style="margin-top:1.5rem;text-align:center;">
      The user sees <strong>instant results</strong> from existing data. New businesses appear on their next search.
    </div>

    <h3>Weighted Vibe Search — Scoring Formula</h3>
    <table class="data-table">
      <thead><tr><th>Component</th><th>Weight</th><th>How It's Calculated</th></tr></thead>
      <tbody>
        <tr><td><strong>Vibe similarity</strong></td><td><strong>70%</strong></td><td>Cosine distance between query embedding and business embedding (pgvector)</td></tr>
        <tr><td><strong>Proximity</strong></td><td><strong>15%</strong></td><td><code>1 / (1 + distance_km / 5.0)</code> — PostGIS <code>ST_Distance</code></td></tr>
        <tr><td><strong>Rating</strong></td><td><strong>15%</strong></td><td><code>avg_rating / 5.0</code> — Bayesian weighted average</td></tr>
      </tbody>
    </table>
    <p>All three components are computed in a <strong>single SQL query</strong> — annotate similarity,
    annotate distance, fetch top <strong>3×</strong> limit, score in Python, return top N.</p>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>API / Tool</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><code>GET /api/categories/</code></td><td>Full parent → child tree for sidebar</td></tr>
        <tr><td><code>GET /api/businesses/?category=6</code></td><td>Filter by category (DRF <code>filterset_fields</code>)</td></tr>
        <tr><td><code>GET /api/businesses/search/?q=cozy</code></td><td>Weighted vibe search with embeddings</td></tr>
        <tr><td><code>GET /api/tags/search/?q=romantic</code></td><td>Semantic tag search (cosine on tag embeddings)</td></tr>
        <tr><td><strong>Google Places API</strong></td><td>Source of raw business data — 30+ field mask</td></tr>
        <tr><td><strong>OpenAI GPT-4o-mini</strong></td><td>Classification + tag generation during import</td></tr>
        <tr><td><strong>OpenAI text-embedding-3-small</strong></td><td><strong>1536-dim</strong> embeddings for businesses + tags</td></tr>
        <tr><td><strong>PostGIS ST_Distance</strong></td><td>Geographic proximity scoring + SearchedArea coverage check</td></tr>
      </tbody>
    </table>
  `,

  init(el) {
    API.getCategories().then(data => {
      if (!data?.results) return;
      const grid = el.querySelector('#live-categories');
      grid.classList.remove('loading-pulse');
      grid.classList.add('live-data');
      const parents  = data.results.filter(c => !c.parent);
      const children = data.results.filter(c => c.parent);
      grid.innerHTML = parents.map(p => {
        const kids = children.filter(c => c.parent === p.id);
        return '<div class="stat-card">'
          + '<div class="stat-value" style="font-size:1.3rem">' + p.name + '</div>'
          + '<div class="stat-label">' + kids.length + ' subcategories</div>'
          + '<div style="margin-top:8px">' + kids.map(k =>
            '<span class="tag-pill">' + k.name + '</span>').join(' ') + '</div>'
          + '</div>';
      }).join('');
    });

    API.getTags(36).then(data => {
      if (!data?.results) return;
      const cloud = el.querySelector('#live-tags');
      cloud.classList.remove('loading-pulse');
      cloud.classList.add('live-data');
      const maxCount = Math.max(...data.results.map(t => t.usage_count || 1));
      cloud.innerHTML = data.results.map(t => {
        const scale = 0.75 + 0.55 * ((t.usage_count || 1) / maxCount);
        return '<span class="tag-cloud-pill" style="font-size:' + scale.toFixed(2) + 'rem">'
          + t.name + ' <span class="tag-cloud-count">' + (t.usage_count || 0) + '</span></span>';
      }).join('');
    });
  },
});
