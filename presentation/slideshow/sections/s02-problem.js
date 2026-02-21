/* Section 2 — Problem & Opportunity (5%) */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'problem',
  title: 'Problem & Opportunity',
  icon: ICON.barChart,
  weight: '',
  html: `
    <div class="section-header">
      <span class="section-label">Section 1</span>
      <h2 class="section-title">Problem &amp; Opportunity</h2>
    </div>

    <!-- 1. Market Analysis — Pie Chart -->
    <h3>The Market <a href="https://ised-isde.canada.ca/site/sme-research-statistics/en/key-small-business-statistics/key-small-business-statistics-2024" target="_blank" class="cite-link">ISED Canada, 2024</a></h3>
    <div class="diagram-container diagram-container--wide">
      <pre class="mermaid">
pie title Small Business Segmentation (Canada)
  "Professional &amp; Technical" : 18
  "Construction" : 14
  "Other Services" : 9.5
  "Retail Trade" : 9
  "Health Care" : 7
  "All Other" : 42.5
      </pre>
    </div>

    <!-- 2. The Need — bridge visual -->
    <h3>The Need</h3>
    <div class="bridge-visual">
      <div class="bridge-badge">Our platform: Orbit</div>
      <div class="bridge-connector"></div>

      <div class="bridge-cliff bridge-cliff--left">
        <div class="bridge-cliff-label bridge-cliff-label--primary">Digital World &amp;<br>High-Intent Users</div>
        <div class="bridge-cliff-list">• <strong>44%</strong> scroll <strong>3+ min</strong> to find results<br>• <strong>41%</strong> must reformulate searches<br><a href="https://cxm.world/customer-experience/44-of-shoppers-spend-3-minutes-finding-what-they-need-in-search-results/" target="_blank" class="cite-link">CXM World, 2024</a></div>
      </div>

      <div class="bridge-deck"></div>
      <div class="bridge-pillar bridge-pillar--left"></div>
      <div class="bridge-pillar bridge-pillar--right"></div>
      <div class="bridge-cable bridge-cable--left"></div>
      <div class="bridge-cable bridge-cable--right"></div>

      <div class="bridge-cliff bridge-cliff--right">
        <div class="bridge-cliff-label bridge-cliff-label--success">Local World</div>
        <div class="bridge-cliff-list">• <strong>50%+</strong> struggle to find customers<br>• <strong>60%</strong> say acquisition is #1 challenge<br><a href="https://news.constantcontact.com/2024-04-23-New-Research-from-Constant-Contact-Reveals-Small-Businesses-Struggle-to-Market-Effectively-Due-to-Low-Confidence,-Limited-Time,-and-Lack-of-Knowledge" target="_blank" class="cite-link">Constant Contact, 2024</a></div>
      </div>

      <div class="bridge-caption">
        <div class="bridge-caption-title">AI-powered local discovery</div>
        <div class="bridge-caption-sub">for Gen Z shoppers</div>
      </div>
    </div>

    <!-- 3. Why Gen Z — target audience -->
    <h3>Why Gen Z?</h3>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">63%</div>
        <div class="stat-label">prefer in-store over online</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">$450 B+</div>
        <div class="stat-label">global spending power</div>
      </div>
    </div>

    <!-- 4. Sample Persona -->
    <h3>Target Audience Persona</h3>
    <div class="persona-card">
      <div class="persona-header">
        <div class="persona-avatar">S</div>
        <div>
          <div class="persona-name">Sally Chen</div>
          <div class="persona-meta">19 · University student · Markham, ON</div>
        </div>
      </div>
      <div class="persona-body">
        <div class="persona-section">
          <strong>Behaviour</strong>
          <ul>
            <li>Mobile-first, researches online, buys in person</li>
            <li>Prefers local over chains</li>
          </ul>
        </div>
        <div class="persona-section">
          <strong>Frustration</strong>
          <ul>
            <li>"Maps shows the nearest, not the <em>best</em>"</li>
            <li>"I want vibes, not just star ratings"</li>
          </ul>
        </div>
      </div>
    </div>
  `,
});

