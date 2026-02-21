/* Section 13 — Conclusion */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'conclusion',
  title: 'Conclusion',
  icon: ICON.flag,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Conclusion</span>
      <h2 class="section-title">SWOT Analysis, Timeline &amp; Future Vision</h2>
    </div>

    <!-- SWOT Grid -->
    <div class="swot-grid">
      <div class="swot-card swot-s">
        <h4 class="swot-heading">${ICON.checkCircle} Strengths</h4>
        <ul>
          <li>AI-powered personalization (RAG + GPT-4.1)</li>
          <li>Natural-language Vibe Search via embeddings</li>
          <li>Effortless AI conversational reviews</li>
          <li>Real-time SSE deal updates</li>
          <li>Production-grade Dockerized infrastructure</li>
          <li>Community-driven discovery loop</li>
        </ul>
      </div>
      <div class="swot-card swot-w">
        <h4 class="swot-heading">${ICON.alertTri} Weaknesses</h4>
        <ul>
          <li>Web-only — no native mobile app yet</li>
          <li>No business self-service portal</li>
          <li>Manual data import for new areas</li>
          <li>No in-app phone booking</li>
        </ul>
      </div>
      <div class="swot-card swot-o">
        <h4 class="swot-heading">${ICON.trendUp} Opportunities</h4>
        <ul>
          <li>Cross-platform via Capacitor (already configured)</li>
          <li>Business outreach automation to grow collaborators</li>
          <li>Gamified missions to boost engagement</li>
          <li>AI voice agent for phone bookings</li>
        </ul>
      </div>
      <div class="swot-card swot-t">
        <h4 class="swot-heading">${ICON.shieldAlert} Threats</h4>
        <ul>
          <li>Competing platforms (Google Maps, Yelp)</li>
          <li>OpenAI API cost scaling with users</li>
          <li>User adoption / cold-start in new areas</li>
          <li>Data privacy regulations for AI profiles</li>
        </ul>
      </div>
    </div>

    <!-- Detailed: Strengths → Advantages -->
    <h3>Strengths in Detail</h3>
    <table class="data-table">
      <thead><tr><th>Advantage</th><th>Detail</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>AI-Powered Personalization</strong></td>
          <td>RAG pipeline + GPT-4.1 builds a unique taste profile per user — recommendations improve with every review and bookmark</td>
        </tr>
        <tr>
          <td><strong>Vibe Search</strong></td>
          <td>Natural-language queries matched via vector embeddings — users search by mood, not rigid keywords</td>
        </tr>
        <tr>
          <td><strong>Effortless Reviews</strong></td>
          <td>Conversational AI chat replaces traditional forms — auto-tags businesses, lowers the barrier to contribute</td>
        </tr>
        <tr>
          <td><strong>Real-Time Updates</strong></td>
          <td>Server-Sent Events push live deal timers and notifications without polling</td>
        </tr>
        <tr>
          <td><strong>Cross-Platform Ready</strong></td>
          <td>Single Vue 3 codebase wraps to native iOS / Android via Capacitor — write once, deploy everywhere</td>
        </tr>
        <tr>
          <td><strong>Production-Grade Infrastructure</strong></td>
          <td>Dockerized stack with Nginx, Celery, Redis, SSL, reCAPTCHA — scalable and secure from day one</td>
        </tr>
        <tr>
          <td><strong>Community-Driven</strong></td>
          <td>AI-generated tags and reviews feed back into discovery — every user action makes the platform smarter for everyone</td>
        </tr>
      </tbody>
    </table>

    <!-- Detailed: Weaknesses → Limitations & Mitigations -->
    <h3>Weaknesses &amp; Mitigations</h3>
    <table class="data-table">
      <thead><tr><th>Limitation</th><th>Impact</th><th>Mitigation</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>Web-only</strong></td>
          <td>No native mobile app yet</td>
          <td>Capacitor wraps Vue codebase → iOS / Android. Already configured</td>
        </tr>
        <tr>
          <td><strong>No business portal</strong></td>
          <td>Businesses can't self-manage</td>
          <td>Planned dashboard: update hours, post deals, respond to reviews</td>
        </tr>
        <tr>
          <td><strong>Manual import</strong></td>
          <td>New-area coverage needs admin</td>
          <td>AI auto-detect from user searches → import → email business owners</td>
        </tr>
        <tr>
          <td><strong>No phone booking</strong></td>
          <td>Users must call businesses</td>
          <td>AI voice agent handles booking — removes social anxiety</td>
        </tr>
      </tbody>
    </table>

    <!-- Future Vision — presented first -->
    <h3>Future Vision</h3>
    <div class="vision-cards">
      <div class="vision-card">
        <span class="vision-icon">${ICON.smartphone}</span>
        <h4>Native Mobile Apps</h4>
        <p>Ship Orbit on iOS &amp; Android via Capacitor. Build native push notifications, offline caching, and App Store distribution.</p>
        <span class="vision-tag">Capacitor · Swift · Kotlin</span>
      </div>
      <div class="vision-card">
        <span class="vision-icon">${ICON.store}</span>
        <h4>Business Portal</h4>
        <p>Self-service dashboard where business owners update hours, post deals, respond to reviews, and view analytics.</p>
        <span class="vision-tag">New API · Vue Dashboard · Auth Roles</span>
      </div>
      <div class="vision-card">
        <span class="vision-icon">${ICON.mail}</span>
        <h4>Business Outreach Automation</h4>
        <p>Auto-detect nearby businesses via Google Places, generate personalized outreach emails, and migrate Google/Yelp data — growing the number of local business collaborators on the platform.</p>
        <span class="vision-tag">Celery Pipeline · Brevo API · Google Places</span>
      </div>
      <div class="vision-card">
        <span class="vision-icon">${ICON.gamepad}</span>
        <h4>Gamified Missions</h4>
        <p>Turn local discovery into a game — missions to visit businesses, unlock exclusive coupons. AI personalizes by interest + campus.</p>
        <span class="vision-tag">Missions API · Reward System · GPT</span>
      </div>
      <div class="vision-card">
        <span class="vision-icon">${ICON.phone}</span>
        <h4>AI Phone Booking</h4>
        <p>Voice agent books restaurants &amp; services by phone on behalf of the user — removes anxiety and time cost.</p>
        <span class="vision-tag">OpenAI Realtime API · Twilio · Webhooks</span>
      </div>
    </div>

    <!-- Development Roadmap — derived from the future vision -->
    <h3>Development Roadmap</h3>
    <div class="roadmap">
      <!-- Completed phases -->
      <div class="roadmap-phase roadmap-done">
        <div class="roadmap-marker"><span class="roadmap-dot"></span></div>
        <div class="roadmap-content">
          <span class="roadmap-date">Sep 2025 – Feb 2026</span>
          <h4>Phase 1 — MVP &amp; Launch <span class="roadmap-badge badge-done">Completed</span></h4>
          <ul>
            <li>Feature design &amp; UX wireframes</li>
            <li>Django REST API + PostgreSQL + pgvector</li>
            <li>Vue 3 frontend with Vite</li>
            <li>AI integration (embeddings, personalization, review chat)</li>
            <li>Production deploy — Docker, Nginx, SSL, GCP</li>
          </ul>
        </div>
      </div>

      <!-- Current -->
      <div class="roadmap-phase roadmap-active">
        <div class="roadmap-marker"><span class="roadmap-dot"></span></div>
        <div class="roadmap-content">
          <span class="roadmap-date">Feb 2026</span>
          <h4>Current — Presentation &amp; Feedback <span class="roadmap-badge badge-active">In Progress</span></h4>
          <ul>
            <li>Final QA &amp; user testing</li>
            <li>Presentation preparation</li>
          </ul>
        </div>
      </div>

      <!-- Future phases -->
      <div class="roadmap-phase roadmap-future">
        <div class="roadmap-marker"><span class="roadmap-dot"></span></div>
        <div class="roadmap-content">
          <span class="roadmap-date">Mar – May 2026</span>
          <h4>Phase 2 — Mobile &amp; Business Portal</h4>
          <ul>
            <li>Capacitor builds → iOS &amp; Android apps</li>
            <li>Push notification service (APNs / FCM)</li>
            <li>Business portal API: owner auth roles, deal management, review replies</li>
            <li>Business analytics dashboard (Vue)</li>
          </ul>
        </div>
      </div>

      <div class="roadmap-phase roadmap-future">
        <div class="roadmap-marker"><span class="roadmap-dot"></span></div>
        <div class="roadmap-content">
          <span class="roadmap-date">Jun – Aug 2026</span>
          <h4>Phase 3 — Outreach &amp; Gamification</h4>
          <ul>
            <li>Business outreach automation pipeline (Places API → Celery → Brevo)</li>
            <li>Gamified missions API &amp; reward system</li>
            <li>Coupon / loyalty integration with business portal</li>
          </ul>
        </div>
      </div>

      <div class="roadmap-phase roadmap-future">
        <div class="roadmap-marker"><span class="roadmap-dot"></span></div>
        <div class="roadmap-content">
          <span class="roadmap-date">Sep – Nov 2026</span>
          <h4>Phase 4 — AI Voice Booking &amp; Scale</h4>
          <ul>
            <li>AI phone booking agent (OpenAI Realtime API + Twilio)</li>
            <li>Horizontal scaling &amp; cost optimisation</li>
            <li>Expansion to additional Canadian campuses</li>
          </ul>
        </div>
      </div>
    </div>

    <h3>Technology Stack Summary</h3>
    <table class="data-table">
      <thead><tr><th>Layer</th><th>Technology</th></tr></thead>
      <tbody>
        <tr><td><strong>Frontend</strong></td><td>Vue 3 (Composition API), JavaScript, Vite, Capacitor</td></tr>
        <tr><td><strong>Backend</strong></td><td>Python 3.12, Django + Django REST Framework</td></tr>
        <tr><td><strong>Database</strong></td><td>PostgreSQL 16 + pgvector + PostGIS</td></tr>
        <tr><td><strong>AI / LLM</strong></td><td>OpenAI GPT-4.1, text-embedding-3-small</td></tr>
        <tr><td><strong>Infrastructure</strong></td><td>Docker Compose, Nginx, Gunicorn, Celery, Redis</td></tr>
        <tr><td><strong>Security</strong></td><td>Let's Encrypt SSL, reCAPTCHA v3, Token Auth</td></tr>
        <tr><td><strong>Cloud</strong></td><td>Google Cloud Storage (images), Brevo (email)</td></tr>
      </tbody>
    </table>

    <div class="highlight-box" style="text-align:center; margin-top:3rem;">
      <strong>Thank you for your time and attention.</strong><br>
      We appreciate the opportunity to present Orbit.
    </div>
  `,
});
