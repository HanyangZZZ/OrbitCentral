/* Feature 7 — Cookies & Session Management */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-cookies',
  title: 'Cookies',
  icon: ICON.cookie,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 7 of 7</span>
      <h2 class="section-title">Cookies &amp; Session Management</h2>
      <p class="section-subtitle">Consent-based token persistence with stateless backend</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  A["First visit to Orbit"] --> B{"Cookie consent\nbanner shown"}
  B -->|"Accept"| C["Store consent\nin localStorage"]
  C --> D["Auth token persisted\nin localStorage"]
  D --> E["Next visit: auto-login\ntoken restored"]
  B -->|"Decline"| F["Session-only mode"]
  F --> G["Token in memory only\n(Axios defaults)"]
  G --> H["Tab close = logged out"]
      </pre>
      <p class="diagram-caption">Accept = persistent sessions · Decline = session-only</p>
    </div>

    <h3>Data Storage</h3>
    <table class="data-table">
      <thead><tr><th>Where</th><th>How</th></tr></thead>
      <tbody>
        <tr><td><strong>Client-side only</strong></td><td>Two <code>localStorage</code> keys: <code>fblc_cookie_consent</code> (boolean)
        and <code>fblc_auth_token</code> (string). No actual cookies set — uses localStorage exclusively</td></tr>
        <tr><td><strong>Server-side</strong></td><td>Fully stateless — DRF Token auth. No session table, no session cookies.
        Token transmitted as <code>Authorization: Token</code> header over HTTPS</td></tr>
      </tbody>
    </table>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Tool</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><strong>localStorage API</strong></td><td>Persistent consent flag + auth token — survives browser restarts if accepted</td></tr>
        <tr><td><strong>Axios interceptor</strong></td><td>Automatically attaches <code>Authorization: Token</code> header to every API request</td></tr>
        <tr><td><strong>DRF Token Auth</strong></td><td>Opaque token — no sensitive data encoded (unlike JWT). One token per user in DB</td></tr>
        <tr><td><strong>HTTPS only</strong></td><td>Let's Encrypt SSL — token never transmitted in cleartext</td></tr>
      </tbody>
    </table>
  `,
});
