<!--
  AboutPage.vue — About Orbit (route: /about)
  ─────────────────────────────────────────────────────────────────────────────
  Static informational page with three sections:

  1. HERO        — "About Orbit" heading + mission statement
  2. HOW IT WORKS — three-step explanation (Search → Discover → Connect)
  3. OUR VALUES   — four value cards (Community, Innovation, Trust, Impact)

  No API calls or dynamic data — purely presentational.
  All styling is scoped to this component.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="about-us-page">

    <div class="about-content">
      <!-- Hero -->
      <div class="about-hero">
        <div class="hero-logo">
          <img src="@/components/icons/orbit-logo.png" alt="Orbit" />
        </div>
        <h1 class="about-title">About Orbit</h1>
        <p class="about-tagline">The best spots gravitate to you.</p>
      </div>

      <!-- Mission -->
      <div class="about-section">
        <h2 class="section-heading">Our Mission</h2>
        <p class="section-text">
          Orbit was built on a simple belief: the best places in your city are often the ones you haven't found yet.
          We help you discover and support the small, local businesses that make your community unique — powered by
          a gravity-based recommendation system that puts <strong>you</strong> at the center.
        </p>
      </div>

      <!-- How It Works -->
      <div class="about-section">
        <h2 class="section-heading">How It Works</h2>
        <div class="how-grid">
          <div class="how-card">
            <div class="how-icon-circle">
              <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/><path d="M12 2a14.5 14.5 0 0 0 0 20M12 2a14.5 14.5 0 0 1 0 20M2 12h20" stroke="currentColor" stroke-width="1.5"/></svg>
            </div>
            <h3 class="how-label">You're the Center</h3>
            <p class="how-desc">Like a planet with its own gravitational pull, you attract the businesses most relevant to your location, time, and preferences.</p>
          </div>
          <div class="how-card">
            <div class="how-icon-circle">
              <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 3"/><circle cx="19" cy="8" r="2" fill="currentColor"/></svg>
            </div>
            <h3 class="how-label">Businesses Orbit You</h3>
            <p class="how-desc">Nearby businesses orbit around you — the closer they are, the stronger their gravitational pull. Highly rated spots appear in your inner orbit.</p>
          </div>
          <div class="how-card">
            <div class="how-icon-circle">
              <svg viewBox="0 0 24 24" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
            </div>
            <h3 class="how-label">Your Reviews Shape Gravity</h3>
            <p class="how-desc">Every review you leave adjusts the gravitational field. Rate a coffee shop highly, and similar spots will drift closer into your orbit.</p>
          </div>
          <div class="how-card">
            <div class="how-icon-circle">
              <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="3" fill="currentColor"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" stroke-width="1.5"/></svg>
            </div>
            <h3 class="how-label">Context-Aware Discovery</h3>
            <p class="how-desc">Morning? We surface coffee shops. Friday evening? Restaurants and entertainment. Orbit adapts to your rhythm automatically.</p>
          </div>
        </div>
      </div>

      <!-- Values -->
      <div class="about-section">
        <h2 class="section-heading">What We Value</h2>
        <div class="values-grid">
          <div class="value-item">
            <div class="value-bar"></div>
            <h3 class="value-label">Community First</h3>
            <p class="value-desc">We prioritize small, independent businesses over chains. Every feature is designed to strengthen local economies.</p>
          </div>
          <div class="value-item">
            <div class="value-bar"></div>
            <h3 class="value-label">Authentic Discovery</h3>
            <p class="value-desc">No paid placements. Business visibility is earned through genuine community engagement and quality.</p>
          </div>
          <div class="value-item">
            <div class="value-bar"></div>
            <h3 class="value-label">Personalized, Not Invasive</h3>
            <p class="value-desc">We use context (time, location, preferences) to personalize — but your data stays yours.</p>
          </div>
        </div>
      </div>

      <!-- Team -->
      <div class="about-section about-section-last">
        <h2 class="section-heading">Built By</h2>
        <p class="section-text">
          Orbit is a project created for the FBLC 2026 Byte-Sized Business Boost challenge. Our team is passionate
          about using technology to connect people with the businesses that make their neighborhoods special.
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
// AppHeader is now provided globally by App.vue
</script>

<style scoped>
/* ─── About-page-specific design tokens (light theme for this page) ─── */
.about-us-page {
  --about-primary: #4a70a9;
  --about-primary-dark: #1e3a8a;
  --about-accent: #4338ca;
  --about-text: #0f172a;
  --about-text-muted: #64748b;
  --about-text-light: #475569;
  --about-bg: #ffffff;
  --about-bg-alt: #f8fafc;
  --about-bg-warm: #efece3;
  --about-border: #e2e8f0;
  --about-radius-lg: 1rem;
  --about-shadow-sm: 0 4px 12px rgba(15, 23, 42, 0.06);

  background: var(--about-bg);
  font-family: var(--font-ui);
  min-height: 100vh;
}

.about-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
}

/* ─── Hero ─── */
.about-hero {
  text-align: center;
  padding: 3rem 0 2rem;
}

.hero-logo {
  width: 140px;
  height: 140px;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.about-title {
  font-family: var(--font-brand);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--about-text);
  margin: 0 0 0.5rem;
}

.about-tagline {
  font-size: 1.125rem;
  font-weight: 300;
  font-style: italic;
  color: var(--about-text-muted);
  margin: 0;
}

/* ─── Sections ─── */
.about-section {
  margin-top: 3rem;
}

.about-section-last {
  padding-bottom: 2rem;
}

.section-heading {
  font-family: var(--font-brand);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--about-text);
  margin: 0 0 1rem;
}

.section-text {
  font-size: 1rem;
  font-weight: 300;
  color: var(--about-text-light);
  line-height: 1.7;
  margin: 0;
}

.section-text strong {
  font-weight: 600;
  color: var(--about-text);
}

/* ─── How It Works Grid ─── */
.how-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.how-card {
  padding: 1.5rem;
  background: var(--about-bg);
  border: 1px solid var(--about-border);
  border-radius: var(--about-radius-lg);
  transition: all 0.2s ease;
}

.how-card:hover {
  border-color: var(--about-primary);
  box-shadow: var(--about-shadow-sm);
  transform: translateY(-2px);
}

.how-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--about-bg-warm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
  color: var(--about-primary);
}

.how-icon-circle svg {
  width: 22px;
  height: 22px;
}

.how-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--about-text);
  margin: 0 0 0.5rem;
}

.how-desc {
  font-size: 0.875rem;
  font-weight: 300;
  color: var(--about-text-light);
  line-height: 1.6;
  margin: 0;
}

/* ─── Values Grid ─── */
.values-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.value-bar {
  width: 40px;
  height: 4px;
  background: linear-gradient(90deg, var(--about-primary), var(--about-accent));
  border-radius: 2px;
  margin-bottom: 1rem;
}

.value-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--about-text);
  margin: 0 0 0.5rem;
}

.value-desc {
  font-size: 0.85rem;
  font-weight: 300;
  color: var(--about-text-light);
  line-height: 1.6;
  margin: 0;
}

/* ─── Responsive ─── */
@media (max-width: 768px) {
  .about-content { padding: 0 1rem 3rem; }
  .about-title { font-size: 2rem; }
  .how-grid { grid-template-columns: 1fr; }
  .values-grid { grid-template-columns: 1fr; }
}
</style>
