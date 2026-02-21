/* Section 4 — Software Concept (10%) */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'concept',
  title: 'Software Concept',
  icon: ICON.lightbulb,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Section 3</span>
      <h2 class="section-title">Software Concept</h2>
      <p class="section-subtitle">What makes Orbit fundamentally different</p>
    </div>

    <p class="concept-lead">Orbit refines discovery by shifting from a <strong>static search-and-list
    model</strong> to a <strong>dynamic, context-aware ecosystem</strong>.</p>

    <!-- Orbit animation: user is the star, businesses orbit -->
    <div class="orbit-solar">
      <div class="orbit-ring orbit-ring--1">
        <span class="orbit-planet" style="--delay:0s;--duration:12s" title="Café">${ICON.coffee}</span>
        <span class="orbit-planet" style="--delay:-3s;--duration:12s" title="Restaurant">${ICON.utensils}</span>
      </div>
      <div class="orbit-ring orbit-ring--2">
        <span class="orbit-planet" style="--delay:-1s;--duration:18s" title="Retail">${ICON.shopBag}</span>
        <span class="orbit-planet" style="--delay:-7s;--duration:18s" title="Salon">${ICON.scissors}</span>
        <span class="orbit-planet" style="--delay:-13s;--duration:18s" title="Gym">${ICON.dumbbell}</span>
      </div>
      <div class="orbit-ring orbit-ring--3">
        <span class="orbit-planet" style="--delay:-2s;--duration:25s" title="Bookstore">${ICON.bookOpen}</span>
        <span class="orbit-planet" style="--delay:-9s;--duration:25s" title="Bakery">${ICON.cakeSlice}</span>
        <span class="orbit-planet" style="--delay:-16s;--duration:25s" title="Studio">${ICON.paintbrush}</span>
        <span class="orbit-planet" style="--delay:-22s;--duration:25s" title="Clinic">${ICON.hospital}</span>
      </div>
      <div class="orbit-star">
        <span class="orbit-star-icon">${ICON.user}</span>
        <span class="orbit-star-label">You</span>
      </div>
    </div>

    <!-- Keyword pills -->
    <div class="concept-keywords">
      <span class="concept-kw">Highly Personalized</span>
      <span class="concept-kw">Context-Aware</span>
      <span class="concept-kw">AI-Powered</span>
      <span class="concept-kw">Community-Driven</span>
      <span class="concept-kw">Dynamic</span>
    </div>

    <!-- Three highlight cards — horizontal -->
    <div class="feature-cards">
      <div class="feature-card">
        <span class="feature-card-icon">${ICON.search}</span>
        <h4 class="feature-card-title">Vibe Search</h4>
        <p class="feature-card-desc">Natural-language queries ranked by
        <strong>semantic similarity + proximity + rating</strong> — search by vibe, not keywords.</p>
      </div>
      <div class="feature-card">
        <span class="feature-card-icon">${ICON.bot}</span>
        <h4 class="feature-card-title">Hyper-Personalization</h4>
        <p class="feature-card-desc">A <strong>RAG pipeline</strong> retrieves your real reviews
        &amp; bookmarks, then GPT-4.1 distills them into a
        <strong>taste-capturing query</strong> — every recommendation is uniquely yours.</p>
      </div>
      <div class="feature-card">
        <span class="feature-card-icon">${ICON.chat}</span>
        <h4 class="feature-card-title">AI Review System</h4>
        <p class="feature-card-desc">Chat post-visit and GPT <strong>auto-tags businesses
        via function calling</strong> — effortless reviews that enrich discovery for everyone.</p>
      </div>
    </div>

    <h3>How Does This Help Student Involvement?</h3>
    <div class="involvement-answer">
      <div class="involvement-flow">
        <div class="involvement-step">
          <span class="involvement-icon">${ICON.search}</span>
          <span class="involvement-label">Vibe Search</span>
          <span class="involvement-desc">Find spots that match your mood</span>
        </div>
        <span class="involvement-arrow">→</span>
        <div class="involvement-step">
          <span class="involvement-icon">${ICON.bot}</span>
          <span class="involvement-label">Personalization</span>
          <span class="involvement-desc">AI learns your interests</span>
        </div>
        <span class="involvement-arrow">→</span>
        <div class="involvement-step">
          <span class="involvement-icon">${ICON.chat}</span>
          <span class="involvement-label">AI Reviews</span>
          <span class="involvement-desc">Share experiences effortlessly</span>
        </div>
        <span class="involvement-arrow">→</span>
        <div class="involvement-step involvement-step--result">
          <span class="involvement-icon">${ICON.target}</span>
          <span class="involvement-label">Student Involvement</span>
          <span class="involvement-desc">Effortless local community engagement</span>
        </div>
      </div>
      <p class="involvement-summary">Orbit uses <strong>hyper-personalization</strong> to learn
      each student's interests and behavior, then continuously pulls the most relevant nearby
      spots into a <strong>tailored feed</strong> — making it effortless to get involved.</p>
    </div>

    <!-- Live demo call-to-action -->
    <div class="cta-visit" style="margin-top:2.5rem;padding:2rem 2.5rem;border-radius:1rem;background:#F5F5F7;text-align:center;">
      <p style="font-size:1.1rem;color:#86868B;margin:0 0 0.5rem;">Try it yourself — visit our live site</p>
      <a href="https://orbitcentral.ca" target="_blank" rel="noopener"
         style="font-size:2rem;font-weight:700;color:#0071E3;text-decoration:none;letter-spacing:.02em;">
        ${ICON.globe} orbitcentral.ca
      </a>
      <p style="font-size:0.95rem;color:#86868B;margin:0.75rem 0 0;">Explore the full experience on your own device</p>
    </div>

    <!-- Website Preview Gallery -->
    <h3 style="margin-top:3rem;">What Our Website Looks Like</h3>
    <p style="color:#86868B;margin-bottom:1.5rem;">Live screenshots from <strong>orbitcentral.ca</strong> — the full user experience in action.</p>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:2rem;">
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-1.png" alt="Orbit Homepage"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Homepage — hero with natural-language search bar</figcaption>
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-6.png" alt="About Orbit"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">About page — project mission and overview</figcaption>
      </figure>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:2rem;">
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-2.png" alt="Nearby For You"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Nearby For You — personalized suggestions based on location and time</figcaption>
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-5.png" alt="Category Browse"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Category browser — filter by Entertainment, Food & Drink, and more</figcaption>
      </figure>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:2rem;">
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-3.png" alt="Vibe Search — cozy dinner"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Vibe Search — "I like a warm and cozy dinner" with AI-powered Orbit Scout summary</figcaption>
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-4.png" alt="Vibe Search — hangout"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Vibe Search — "I like a place to hangout with friends" with category breakdown</figcaption>
      </figure>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:2rem;">
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-8.png" alt="Business Detail — reviews"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">Business detail — star ratings, reviews, and "Customers Say" AI summary</figcaption>
      </figure>
      <figure style="margin:0; text-align:center;">
        <img src="images/site-preview-7.png" alt="AI Review Chat"
             style="width:100%; border-radius:12px; border:2px solid var(--border); box-shadow:0 6px 24px rgba(0,0,0,.3); cursor:pointer;"
             onclick="this.classList.toggle('zoomed')" />
        <figcaption style="margin-top:.6rem; font-size:.85rem; opacity:.7;">AI Review System — chat with GPT to craft your review effortlessly</figcaption>
      </figure>
    </div>
  `,
});
