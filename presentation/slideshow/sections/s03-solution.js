/* Section 3 — Our Solution (5%) */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'solution',
  title: 'Our Solution',
  icon: ICON.rocket,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Section 2</span>
      <h2 class="section-title" style="display:flex;align-items:center;gap:12px;justify-content:center">
        Our Solution:
        <img src="images/orbit-logo-removebg-preview.png" alt="Orbit Logo" style="height:1.4em;vertical-align:middle">
        Orbit
      </h2>
      <p class="section-subtitle">"The Best Spots Gravitate Towards You"</p>
    </div>

    <div class="two-col">
      <div>
        <h3>How We Solve the Problem</h3>
        <div class="highlight-box highlight-box--accent">
          Orbit applies <strong>AI hyper-personalization</strong> to bridge the
          digital-physical disconnect. It learns each user's taste from their reviews
          and bookmarks, then surfaces the most relevant nearby spots —
          so the best local businesses <em>gravitate</em> to the right people.
        </div>

        <h3>Unique Selling Proposition</h3>
        <p>We are not just another review app — we are a <strong>service</strong>.</p>
        <p>Orbit is the <strong>only</strong> local discovery service that makes the
        best nearby spots gravitate to students through
        <strong>hyper-personalized recommendations</strong> — powered by AI that
        learns your taste, not just your keywords.</p>
      </div>
      <div>
        <h3>Brand Positioning</h3>
        <div class="diagram-container diagram-container--wide">
          <pre class="mermaid">
quadrantChart
    title Brand Positioning
    x-axis "Low Personalization" --> "High Personalization"
    y-axis "Low Community Focus" --> "High Community Focus"
    quadrant-1 "Orbit's Space"
    quadrant-2 "Community-Driven"
    quadrant-3 "Generic Discovery"
    quadrant-4 "Algorithm-Driven"
    "Google Maps": [0.25, 0.30]
    "Yelp": [0.30, 0.60]
    "Instagram": [0.65, 0.35]
    "TripAdvisor": [0.35, 0.50]
    "Orbit": [0.82, 0.85]
          </pre>
        </div>
      </div>
    </div>

    <div class="highlight-box">
      <strong>Key Insight:</strong> Orbit occupies the top-right quadrant —
      <strong>High Personalization × High Community Focus</strong> — a market space
      that Google Maps, Yelp, Instagram, and TripAdvisor leave entirely unoccupied.
    </div>
  `,
});
