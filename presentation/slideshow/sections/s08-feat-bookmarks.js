/* Feature 3 — Bookmarking */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-bookmarks',
  title: 'Bookmarking',
  icon: ICON.bookmark,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 3 of 7</span>
      <h2 class="section-title">Saving &amp; Bookmarking Favourite Businesses</h2>
      <p class="section-subtitle">One-tap save with optimistic UI — also feeds AI personalisation</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
sequenceDiagram
  actor U as User
  participant FE as Frontend
  participant API as Django API
  participant DB as PostgreSQL
  Note over FE: App loads
  FE->>API: GET /api/bookmarks/ids/
  API-->>FE: [3, 42, 99]
  FE->>FE: Store in reactive Set
  Note over U: Clicks ♡ on business 42
  U->>FE: Toggle bookmark
  FE->>FE: Optimistic UI — fill heart instantly
  FE->>API: POST /api/bookmarks/toggle/ business 42
  API->>DB: Exists? DELETE else CREATE
  API-->>FE: status removed
  FE->>FE: Update Set — rollback on failure
      </pre>
      <p class="diagram-caption">Optimistic UI — heart fills instantly before API confirms</p>
    </div>

    <h3>Data Storage</h3>
    <table class="data-table">
      <thead><tr><th>Field</th><th>How</th></tr></thead>
      <tbody>
        <tr><td><strong>Bookmark model</strong></td><td>FK to User + FK to Business, optional <code>notes</code> text, <code>created_at</code></td></tr>
        <tr><td><strong>Unique constraint</strong></td><td><code>(user, business)</code> at DB level — prevents duplicates</td></tr>
        <tr><td><strong>Privacy</strong></td><td>Bookmark counts not exposed on Business — user behaviour data stays private</td></tr>
      </tbody>
    </table>
    <div class="highlight-box">
      <strong>Dual purpose:</strong> Bookmarks aren't just for saving — they're also input to
      AI personalisation. The <code>gather_user_profile()</code> service collects the user's <strong>20
      most recent</strong> bookmarks (with notes) and passes them to GPT-4.1, which generates a
      personalised search query capturing their taste.
    </div>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Endpoint</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><code>GET /api/bookmarks/ids/</code></td><td>Lightweight bulk ID fetch — powers the reactive heart state across the app</td></tr>
        <tr><td><code>POST /api/bookmarks/toggle/</code></td><td>Single toggle endpoint replaces separate create/delete — <strong>50% fewer</strong> round trips</td></tr>
        <tr><td><code>GET /api/bookmarks/</code></td><td>Full list with business details + notes for the Bookmarks page</td></tr>
        <tr><td><code>PATCH /api/bookmarks/{id}/</code></td><td>Update notes ("Try the oat milk latte")</td></tr>
      </tbody>
    </table>

    <h3>Live Bookmark Demo</h3>
    <div class="demo-label">Live from API — click hearts to toggle</div>
    <div id="bookmark-demo" class="biz-grid loading-pulse">
      <div class="biz-card"><div class="biz-card-body"><p class="biz-card-name">Loading…</p></div></div>
    </div>
  `,

  init(el) {
    const grid = el.querySelector('#bookmark-demo');
    let bookmarkedIds = new Set();

    async function load() {
      try {
        const [bizData, bkData] = await Promise.all([
          API.getBusinesses('ordering=-avg_rating'),
          API.getBookmarkIds()
        ]);
        if (!bizData?.results) return;
        bookmarkedIds = new Set(bkData?.business_ids || []);
        grid.classList.remove('loading-pulse');
        grid.classList.add('live-data');
        render(bizData.results);
      } catch (e) {
        grid.innerHTML = '<p class="demo-placeholder">Could not load bookmarks</p>';
        console.warn('[s08]', e);
      }
    }

    function render(businesses) {
      grid.innerHTML = businesses.map(b => {
        const isBookmarked = bookmarkedIds.has(b.id);
        const tags = (b.tags || []).slice(0, 3).map(t =>
          '<span class="tag-pill">' + (t.name || t) + '</span>'
        ).join('');
        const rating = b.avg_rating ? parseFloat(b.avg_rating).toFixed(1) + ' ★' : '—';
        const img = b.image_url
          ? '<img class="biz-card-img" src="' + b.image_url + '" alt="" loading="lazy">'
          : '<div class="biz-card-img" style="background:var(--color-bg);display:flex;align-items:center;justify-content:center;color:var(--color-text-muted)">' + ICON.pin + '</div>';
        return '<div class="biz-card">'
          + '<button class="bookmark-heart' + (isBookmarked ? ' active' : '') + '" data-id="' + b.id + '">'
          + (isBookmarked ? ICON.heartFill : ICON.heartEmpty) + '</button>'
          + img
          + '<div class="biz-card-body">'
          + '<p class="biz-card-name">' + b.name + '</p>'
          + '<p class="biz-card-meta">' + rating
          + (b.category_detail ? ' · ' + b.category_detail.name : '') + '</p>'
          + '<div class="biz-card-tags">' + tags + '</div>'
          + '</div></div>';
      }).join('');

      grid.querySelectorAll('.bookmark-heart').forEach(btn => {
        btn.addEventListener('click', async () => {
          const bizId = parseInt(btn.dataset.id);
          // Optimistic UI
          const wasActive = btn.classList.contains('active');
          btn.classList.toggle('active');
          btn.innerHTML = wasActive ? ICON.heartEmpty : ICON.heartFill;
          if (wasActive) bookmarkedIds.delete(bizId);
          else bookmarkedIds.add(bizId);

          const result = await API.toggleBookmark(bizId);
          if (!result) {
            // Rollback
            btn.classList.toggle('active');
            btn.innerHTML = wasActive ? ICON.heartFill : ICON.heartEmpty;
            if (wasActive) bookmarkedIds.add(bizId);
            else bookmarkedIds.delete(bizId);
          }
        });
      });
    }

    load();
  },
});
