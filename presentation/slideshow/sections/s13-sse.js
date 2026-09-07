/* Section 13 — Scalability, Security & User Engagement (standalone) */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'sse',
  title: 'Scalability · Security · Engagement',
  icon: ICON.lock,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Cross-Cutting Concerns</span>
      <h2 class="section-title">Scalability, Security &amp; User Engagement</h2>
      <p class="section-subtitle">How these three pillars are addressed across every feature</p>
    </div>

    <!-- ── SCALABILITY ──────────────────────────────────────────────────── -->
    <h3>Scalability</h3>
    <figure style="margin:0 0 1.5rem 0; text-align:center;">
      <img src="images/flower-dashboard.png" alt="Flower Celery Task Monitor"
           style="width:100%; border-radius:10px; border:2px solid var(--border); box-shadow:0 4px 16px rgba(0,0,0,.25); cursor:pointer;"
           onclick="this.classList.toggle('zoomed')" />
      <figcaption style="margin-top:.5rem; font-size:.85rem; opacity:.7;">Flower — real-time Celery worker monitoring at celery.orbitcentral.ca (task counts, success/fail, load avg)</figcaption>
    </figure>
    <table class="data-table">
      <thead><tr><th>Layer</th><th>How It Scales</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>Web traffic</strong></td>
          <td>Gunicorn runs <strong>3 workers × 2 threads</strong>. Nginx reverse-proxies and load-balances.
          More workers = more concurrent requests — scale by adding containers</td>
        </tr>
        <tr>
          <td><strong>Background tasks</strong></td>
          <td>Celery workers scale independently of the web server. Import pipeline, email sends,
          and AI calls run in the background — API stays fast. Workers use <code>acks_late</code>
          so tasks survive worker crashes</td>
        </tr>
        <tr>
          <td><strong>Database</strong></td>
          <td>All sorting uses indexed columns (<code>avg_rating</code>, <code>review_count</code>,
          <code>created_at</code>) — never aggregates at read time. Signal-driven denormalisation
          pre-computes Bayesian ratings on write. pgvector HNSW index for sub-ms similarity search</td>
        </tr>
        <tr>
          <td><strong>Search &amp; import</strong></td>
          <td>SearchedArea cache prevents redundant Google Places imports. Per-area locking prevents
          duplicate concurrent imports. Import uses <strong>8–20 concurrent workers</strong> per step</td>
        </tr>
        <tr>
          <td><strong>Category tree</strong></td>
          <td><strong>22 categories</strong> fetched once, cached client-side. Tag search uses pgvector cosine similarity
          — sub-ms for <strong>264+ tags</strong></td>
        </tr>
        <tr>
          <td><strong>AI chat</strong></td>
          <td>Conversation stored in <code>JSONField</code> — any Gunicorn worker can handle any request.
          No in-memory session state</td>
        </tr>
        <tr>
          <td><strong>Auth &amp; cookies</strong></td>
          <td>Token-based auth — server is fully stateless. Consent + storage handled client-side.
          Zero session table overhead</td>
        </tr>
        <tr>
          <td><strong>Future</strong></td>
          <td>Docker → Kubernetes for horizontal scaling. PostgreSQL read replicas. CDN offload for
          static files and GCS images</td>
        </tr>
      </tbody>
    </table>

    <!-- ── SECURITY ─────────────────────────────────────────────────────── -->
    <h3>Security</h3>
    <table class="data-table">
      <thead><tr><th>Measure</th><th>Where Applied</th><th>How</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>HTTPS everywhere</strong></td>
          <td>All traffic</td>
          <td>Let's Encrypt SSL via Certbot container. Auto-renewal. Nginx rejects unknown hosts with 444</td>
        </tr>
        <tr>
          <td><strong>Nginx rate limiting</strong></td>
          <td>All API endpoints</td>
          <td><strong>20 req/s</strong> API, <strong>5 req/s</strong> admin — blocks brute-force before Django processes the request</td>
        </tr>
        <tr>
          <td><strong>reCAPTCHA v3</strong></td>
          <td>Register &amp; Login</td>
          <td>Invisible behavioural scoring (≥ <strong>0.5</strong> threshold). Fail-closed: if Google is unreachable, request is denied</td>
        </tr>
        <tr>
          <td><strong>Token auth</strong></td>
          <td>All write endpoints</td>
          <td>DRF Token auth — opaque, server-stored. No JWT decode risks. <code>Authorization: Token</code> header</td>
        </tr>
        <tr>
          <td><strong>Email verification</strong></td>
          <td>Reviews, bookmarks, personalisation</td>
          <td>Custom <code>IsEmailVerified</code> permission. Unverified users can browse but not write.
          Verification link expires in <strong>5 minutes</strong></td>
        </tr>
        <tr>
          <td><strong>One review per user</strong></td>
          <td>Reviews</td>
          <td>DB-level unique constraint <code>(user, business)</code> — impossible to bypass from any client</td>
        </tr>
        <tr>
          <td><strong>Admin-only CRUD</strong></td>
          <td>Categories, tags, business create/edit</td>
          <td><code>IsAdminUser</code> permission on write endpoints. Public read-only for browsing</td>
        </tr>
        <tr>
          <td><strong>Ownership isolation</strong></td>
          <td>Bookmarks, review chats</td>
          <td>Querysets filtered by <code>user=request.user</code> — users can only see their own data</td>
        </tr>
        <tr>
          <td><strong>Tag isolation</strong></td>
          <td>AI review chat</td>
          <td>Tags queued during chat but only applied on confirm — abandoned sessions leave no trace</td>
        </tr>
        <tr>
          <td><strong>Consent-based persistence</strong></td>
          <td>Cookie / token storage</td>
          <td>Token only persisted in localStorage if user accepts. Decline = session-only (memory)</td>
        </tr>
        <tr>
          <td><strong>Ordering injection prevention</strong></td>
          <td>Sort endpoints</td>
          <td>DRF <code>ordering_fields</code> whitelist — only pre-approved columns can be sorted on</td>
        </tr>
        <tr>
          <td><strong>Secrets management</strong></td>
          <td>All external APIs</td>
          <td>API keys in environment variables, never in code. <code>RECAPTCHA_SECRET_KEY</code>,
          <code>OPENAI_API_KEY</code>, <code>GOOGLE_PLACES_API_KEY</code>, <code>BREVO_API_KEY</code></td>
        </tr>
      </tbody>
    </table>

    <!-- ── USER ENGAGEMENT ──────────────────────────────────────────────── -->
    <h3>User Engagement</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph LR
  DISCOVER["Discover\nVibe Search\nCategory drill-down\nTag pills"] --> SAVE["Save\nOne-tap bookmark\nOptimistic UI\nPersonal notes"]
  SAVE --> REVIEW["Review\nAI chat assistant\nLow-barrier writing\nAuto tag detection"]
  REVIEW --> ENRICH["Enrich\nTags improve search\nBayesian ratings\nBetter recommendations"]
  ENRICH --> PERSONALISE["Personalise\nGPT-4.1 analyses history\nTailored search query\nNew discovery"]
  PERSONALISE -->|"Engagement flywheel"| DISCOVER
      </pre>
      <p class="diagram-caption">Discover → Save → Review → Enrich → Personalise → Discover again</p>
    </div>

    <table class="data-table">
      <thead><tr><th>Feature</th><th>Engagement Driver</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>Category drill-down</strong></td>
          <td><strong>100+ businesses</strong> to ~<strong>20</strong> — reduces decision fatigue</td>
        </tr>
        <tr>
          <td><strong>Tag filtering</strong></td>
          <td>"cozy AND outdoor-seating" — precision that Google Maps doesn't offer</td>
        </tr>
        <tr>
          <td><strong>Optimistic bookmark</strong></td>
          <td>Heart fills instantly before API responds — zero perceived latency</td>
        </tr>
        <tr>
          <td><strong>AI review chat</strong></td>
          <td>Chatting beats staring at a blank text box — lower barrier to write</td>
        </tr>
        <tr>
          <td><strong>Review voting</strong></td>
          <td>Helpful / funny / cool — surfaces best community content</td>
        </tr>
        <tr>
          <td><strong>Gamified deals</strong></td>
          <td>Missions → points → tiers → exclusive coupons — purpose-driven exploration</td>
        </tr>
        <tr>
          <td><strong>AI personalisation</strong></td>
          <td>Returns businesses the user hasn't tried but would love — drives continued discovery</td>
        </tr>
        <tr>
          <td><strong>Invisible reCAPTCHA</strong></td>
          <td>No "click traffic lights" — trust that reviews are genuine, not bot-generated</td>
        </tr>
        <tr>
          <td><strong>Cookie consent</strong></td>
          <td>Non-intrusive banner, seamless auto-login for consenting users, full functionality even if declined</td>
        </tr>
      </tbody>
    </table>

    <div class="highlight-box highlight-box--gold">
      <strong>The flywheel effect:</strong> More reviews → better tags → better vibe search → more users
      → more reviews. AI personalisation accelerates the loop by surfacing businesses users are
      likely to review. Each action compounds the value for everyone on the platform.
    </div>
  `,
});
