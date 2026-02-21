/* Feature 5 — Deals & Coupons */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-deals',
  title: 'Deals & Coupons',
  icon: ICON.tag,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 5 of 7</span>
      <h2 class="section-title">Display Special Deals / Coupons</h2>
      <p class="section-subtitle">Gamified mission system with loyalty tiers and business partnerships</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  A["User browses\nCoupons page"] --> B["View available deals\nsorted by expiry"]
  B --> C{"Complete missions"}
  C --> D["Earn loyalty points"]
  D --> E["Points unlock\nhigher tiers"]
  E --> F["Tiers expose\nexclusive coupons"]
  F --> G["Redeem at business"]
  G --> H["Business gets\nfoot traffic"]
  H -->|"Feedback loop"| C
      </pre>
      <p class="diagram-caption">Gamification flywheel: missions → points → tiers → coupons → traffic</p>
    </div>

    <h3>Business Portal Concept</h3>
    <div class="highlight-box highlight-box--gold">
      <strong>Win-win for businesses:</strong> Businesses get foot traffic from missions
      ("Visit this hidden gem") and coupon redemptions — they pay nothing upfront. A future
      <strong>Business Owner Portal</strong> will let merchants create and manage their own deals,
      respond to reviews, and update their business info.
    </div>

    <h3>Data Storage</h3>
    <table class="data-table">
      <thead><tr><th>Current / Planned</th><th>How</th></tr></thead>
      <tbody>
        <tr><td><strong>Current</strong></td><td>Dedicated Coupons page queries businesses. Expiry timestamps indexed —
        <code>expiry__gt=now()</code> auto-filters without a cron job</td></tr>
        <tr><td><strong>Planned: Deal model</strong></td><td>Expiry, redemption limit, tier requirement, FK to business</td></tr>
        <tr><td><strong>Planned: Mission model</strong></td><td>Type, requirements, point reward. AI-personalised per user interest</td></tr>
        <tr><td><strong>Planned: Redemption model</strong></td><td>User → deal tracking. One-time-use codes prevent double redemption</td></tr>
      </tbody>
    </table>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Endpoint</th><th>Purpose</th></tr></thead>
      <tbody>
        <tr><td><code>GET /api/businesses/</code></td><td>Current: Coupons page fetches businesses with deals</td></tr>
        <tr><td><em>Future: /api/missions/</em></td><td>Personalised mission feed</td></tr>
        <tr><td><em>Future: /api/loyalty/</em></td><td>Points, tiers, redemption history</td></tr>
      </tbody>
    </table>
  `,
});
