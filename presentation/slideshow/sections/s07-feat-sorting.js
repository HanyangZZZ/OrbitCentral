/* Feature 2 — Sorting by Reviews / Ratings */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-sorting',
  title: 'Review & Rating Sorting',
  icon: ICON.star,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 2 of 7</span>
      <h2 class="section-title">Sorting Businesses by Reviews or Ratings</h2>
      <p class="section-subtitle">Bayesian-weighted ratings for fair, trustworthy sorting</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  A["User visits Search page"] --> B["Select sort option\nfrom dropdown"]
  B --> C{"Which sort?"}
  C -->|"Rating"| D["ORDER BY avg_rating DESC\n(Bayesian weighted)"]
  C -->|"Review count"| E["ORDER BY review_count DESC"]
  C -->|"Name A-Z"| F["ORDER BY name ASC"]
  C -->|"Newest"| G["ORDER BY created_at DESC"]
  D --> H["API: GET /api/businesses/\n?ordering=-avg_rating"]
  E --> H
  F --> H
  G --> H
  H --> I{"User submits\na review?"}
  I -->|"Yes"| J["Django post_save signal\non Review model"]
  J --> K["Recalculate\nBayesian avg_rating\non Business row"]
  K --> L["Next query reflects\nupdated rating"]
  I -->|"No"| M["Results render\nin BusinessGrid"]
  L --> M
      </pre>
      <p class="diagram-caption">Sort selection → indexed DB query → signal-driven rating recomputation</p>
    </div>

    <h3>Bayesian Weighted Rating</h3>
    <div class="highlight-box highlight-box--gold">
      Ratings aren't a simple average. A <strong>Bayesian weighted formula</strong> ensures a
      business with 1 review at 5★ doesn't outrank one with 200 reviews at 4.5★. The
      formula blends three inputs:<br><br>
      <strong>1.</strong> The business's user reviews (our community)<br>
      <strong>2.</strong> The global average across all businesses<br>
      <strong>3.</strong> Google's imported rating (external credibility)<br><br>
      The <code>avg_rating</code> column is <strong>pre-computed</strong> by a Django
      <code>post_save</code> / <code>post_delete</code> signal on the Review model — sorting
      <strong>10,000+</strong> rows is just <code>ORDER BY</code> on an indexed column. No aggregation at read time.
    </div>

    <h3>Data Storage</h3>
    <table class="data-table">
      <thead><tr><th>Field</th><th>How</th></tr></thead>
      <tbody>
        <tr><td><code>avg_rating</code></td><td>Pre-computed Bayesian score on Business row — updated by signal, indexed for fast ORDER BY</td></tr>
        <tr><td><code>review_count</code></td><td>Denormalized count — avoids <code>COUNT(*)</code> subquery at read time</td></tr>
        <tr><td><code>google_rating</code></td><td>Imported from Google Places — gives credibility baseline for new businesses</td></tr>
        <tr><td><strong>Review model</strong></td><td>FK user + FK business, unique constraint <code>(user, business)</code>. 1-5 rating + text + vote counts</td></tr>
      </tbody>
    </table>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Tool / API</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><code>GET /api/businesses/?ordering=-avg_rating</code></td><td>DRF <code>ordering_fields</code> whitelist — prevents arbitrary ORDER BY injection</td></tr>
        <tr><td><strong>Django Signals</strong></td><td><code>post_save</code> / <code>post_delete</code> on Review → Bayesian recalc. No cron or read-time aggregation</td></tr>
        <tr><td><strong>Review voting</strong></td><td>Helpful / funny / cool counters on each review — surfaces best community content</td></tr>
      </tbody>
    </table>

    <h3>Live Sorting Demo</h3>
    <div class="demo-label">Live from API</div>
    <div id="sort-demo">
      <div class="sort-bar">
        <button class="sort-btn active" data-sort="-avg_rating">★ Rating</button>
        <button class="sort-btn" data-sort="-review_count">${ICON.chat} Most Reviewed</button>
        <button class="sort-btn" data-sort="name">A → Z</button>
        <button class="sort-btn" data-sort="-created_at">${ICON.sparkle} Newest</button>
      </div>
      <div id="sort-results" class="biz-grid loading-pulse">
        <div class="biz-card"><div class="biz-card-body"><p class="biz-card-name">Loading…</p></div></div>
      </div>
    </div>
  `,

  init(el) {
    const grid = el.querySelector('#sort-results');
    const btns = el.querySelectorAll('.sort-btn');
    let current = '-avg_rating';

    function renderBiz(businesses) {
      grid.classList.remove('loading-pulse');
      grid.classList.add('live-data');
      if (!businesses.length) { grid.innerHTML = '<p class="demo-placeholder">No businesses found</p>'; return; }
      grid.innerHTML = businesses.map(b => {
        const tags = (b.tags || []).slice(0, 3).map(t =>
          '<span class="tag-pill">' + (t.name || t) + '</span>'
        ).join('');
        const rating = b.avg_rating ? parseFloat(b.avg_rating).toFixed(1) + ' ★' : '—';
        const img = b.image_url
          ? '<img class="biz-card-img" src="' + b.image_url + '" alt="" loading="lazy">'
          : '<div class="biz-card-img" style="background:var(--color-bg);display:flex;align-items:center;justify-content:center;color:var(--color-text-muted)">' + ICON.pin + '</div>';
        return '<div class="biz-card">'
          + img
          + '<div class="biz-card-body">'
          + '<p class="biz-card-name">' + b.name + '</p>'
          + '<p class="biz-card-meta">' + rating
          + (b.review_count ? ' · ' + b.review_count + ' reviews' : '')
          + (b.category_detail ? ' · ' + b.category_detail.name : '') + '</p>'
          + '<div class="biz-card-tags">' + tags + '</div>'
          + '</div></div>';
      }).join('');
    }

    function loadSort(ordering) {
      grid.innerHTML = '<div class="biz-card"><div class="biz-card-body"><p class="biz-card-name">Loading…</p></div></div>';
      grid.classList.add('loading-pulse');
      API.getBusinesses('ordering=' + ordering).then(data => {
        renderBiz(data?.results || []);
      }).catch(err => {
        grid.innerHTML = '<p class="demo-placeholder">Could not load businesses</p>';
        console.warn('[s07]', err);
      });
    }

    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        current = btn.dataset.sort;
        loadSort(current);
      });
    });

    loadSort(current);
  },
});
