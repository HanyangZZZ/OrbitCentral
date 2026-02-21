/* Section 15 — References & Credits */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'references',
  title: 'References & Credits',
  icon: ICON.book,
  weight: '',
  html: `
    <div class="section-header">
      <h2 class="section-title">References &amp; Credits</h2>
      <p class="section-subtitle">Fonts, packages, and image sources used in this project</p>
    </div>

    <!-- Fonts -->
    <h3>Fonts</h3>
    <div class="ref-grid">
      <div class="ref-card">
        <span class="ref-icon">${ICON.type}</span>
        <div>
          <strong>SF Pro</strong>
          <p>Apple Inc. — used as the primary system typeface on iOS / macOS.<br>
          <a href="https://developer.apple.com/fonts/" target="_blank" rel="noopener">developer.apple.com/fonts</a></p>
        </div>
      </div>
      <div class="ref-card">
        <span class="ref-icon">${ICON.type}</span>
        <div>
          <strong>Barlow</strong>
          <p>Jeremy Tribby — Google Fonts, SIL Open Font License.<br>
          <a href="https://fonts.google.com/specimen/Barlow" target="_blank" rel="noopener">fonts.google.com/specimen/Barlow</a></p>
        </div>
      </div>
    </div>

    <!-- Backend Packages -->
    <h3>Backend Packages (Python)</h3>
    <div class="ref-table-wrap">
      <table class="ref-table">
        <thead><tr><th>Package</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Django</td><td>High-level Python web framework</td></tr>
          <tr><td>django-cors-headers</td><td>CORS header management for Django</td></tr>
          <tr><td>djangorestframework</td><td>Toolkit for building REST APIs</td></tr>
          <tr><td>django-filter</td><td>Dynamic queryset filtering for DRF</td></tr>
          <tr><td>python-dotenv</td><td>Environment variable management from .env files</td></tr>
          <tr><td>dj-database-url</td><td>Database URL configuration utility</td></tr>
          <tr><td>psycopg2-binary</td><td>PostgreSQL adapter for Python</td></tr>
          <tr><td>pgvector</td><td>Vector similarity search for PostgreSQL</td></tr>
          <tr><td>openai</td><td>OpenAI API client (GPT-4.1, embeddings)</td></tr>
          <tr><td>requests</td><td>HTTP library for Python</td></tr>
          <tr><td>Celery</td><td>Distributed task queue with Redis broker</td></tr>
          <tr><td>Redis</td><td>In-memory data store / message broker</td></tr>
          <tr><td>Flower</td><td>Real-time Celery monitoring tool</td></tr>
          <tr><td>google-cloud-storage</td><td>Google Cloud Storage client library</td></tr>
          <tr><td>sib-api-v3-sdk</td><td>Brevo (Sendinblue) transactional email SDK</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Frontend Packages -->
    <h3>Frontend Packages (JavaScript)</h3>
    <div class="ref-table-wrap">
      <table class="ref-table">
        <thead><tr><th>Package</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Vue 3</td><td>Progressive JavaScript framework for UI</td></tr>
          <tr><td>Vue Router</td><td>Official client-side router for Vue</td></tr>
          <tr><td>Axios</td><td>Promise-based HTTP client</td></tr>
          <tr><td>Vite</td><td>Next-generation frontend build tool</td></tr>
          <tr><td>Vitest</td><td>Blazing-fast unit testing framework for Vite</td></tr>
          <tr><td>@vitejs/plugin-vue</td><td>Official Vue plugin for Vite</td></tr>
          <tr><td>Capacitor (Core)</td><td>Cross-platform native runtime for web apps</td></tr>
          <tr><td>@capacitor/ios</td><td>iOS platform support for Capacitor</td></tr>
          <tr><td>@capacitor/cli</td><td>Capacitor command-line interface</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Infrastructure -->
    <h3>Infrastructure &amp; Services</h3>
    <div class="ref-table-wrap">
      <table class="ref-table">
        <thead><tr><th>Service / Tool</th><th>Purpose</th></tr></thead>
        <tbody>
          <tr><td>Docker &amp; Docker Compose</td><td>Containerisation and orchestration</td></tr>
          <tr><td>Nginx</td><td>Reverse proxy and static file serving</td></tr>
          <tr><td>PostgreSQL</td><td>Primary relational database</td></tr>
          <tr><td>Google Cloud Compute Engine</td><td>Virtual machine hosting</td></tr>
          <tr><td>Google Cloud Storage</td><td>Object/media storage</td></tr>
          <tr><td>Mermaid.js</td><td>Diagram rendering in this slideshow</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Image / Content Sources -->
    <h3>Image &amp; Content Sources</h3>
    <div class="ref-grid">
      <div class="ref-card ref-card--link">
        <span class="ref-icon">${ICON.image}</span>
        <div>
          <a href="https://potatorolls.com/blog/summer-food-and-drink-pairings/" target="_blank" rel="noopener">
            potatorolls.com — Summer Food &amp; Drink Pairings
          </a>
        </div>
      </div>
      <div class="ref-card ref-card--link">
        <span class="ref-icon">${ICON.image}</span>
        <div>
          <a href="https://thokmandee.com/what-is-retail-and-why-does-it-matter-in-todays-economy/" target="_blank" rel="noopener">
            thokmandee.com — What Is Retail?
          </a>
        </div>
      </div>
      <div class="ref-card ref-card--link">
        <span class="ref-icon">${ICON.image}</span>
        <div>
          <a href="https://www.linkedin.com/company/live-nation/" target="_blank" rel="noopener">
            LinkedIn — Live Nation
          </a>
        </div>
      </div>
      <div class="ref-card ref-card--link">
        <span class="ref-icon">${ICON.image}</span>
        <div>
          <a href="https://safedesignateddriver.com/airport-service.html" target="_blank" rel="noopener">
            Safe Designated Driver — Airport Service
          </a>
        </div>
      </div>
      <div class="ref-card ref-card--link">
        <span class="ref-icon">${ICON.image}</span>
        <div>
          <a href="https://www.joehillmanconstruction.com/residential-repairs/" target="_blank" rel="noopener">
            Joe Hillman Construction — Residential Repairs
          </a>
        </div>
      </div>
    </div>
  `,
});
