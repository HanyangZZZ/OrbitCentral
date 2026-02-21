/* Feature 6 — reCAPTCHA Verification */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-captcha',
  title: 'reCAPTCHA Verification',
  icon: ICON.shield,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 6 of 7</span>
      <h2 class="section-title">reCAPTCHA Verification to Prevent Bot Activity</h2>
      <p class="section-subtitle">Invisible behavioural scoring with Nginx rate-limiting as first defence</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
graph TD
  A["User submits form\n(Register / Login)"] --> NG{"Nginx rate limit\n20 req/s API\n5 req/s admin"}
  NG -->|"Exceeded"| R429["429 Too Many Requests"]
  NG -->|"Pass"| B["Frontend\nreCAPTCHA v3 generates\ntoken invisibly"]
  B --> C["Token sent with\nform data to Django"]
  C --> D{"Backend\nverify_captcha()"}
  D --> V3{"v3 score\navailable?"}
  V3 -->|"Yes"| S{"Score ≥ 0.5?"}
  S -->|"Yes"| OK["Proceed with\nregistration / login"]
  S -->|"No"| FAIL["403 Forbidden\n+ log attempt"]
  V3 -->|"Token looks\nlike v2"| V2["Verify as\nreCAPTCHA v2"]
  V2 -->|"Pass"| OK
  V2 -->|"Fail"| FAIL
  D -->|"No token\nor invalid"| FAIL
      </pre>
      <p class="diagram-caption">Two-layer defence: Nginx rate limiting → reCAPTCHA v3 score verification</p>
    </div>

    <h3>How It Works — What's Actually Implemented</h3>
    <div class="highlight-box highlight-box--accent">
      <strong>Layer 1 — Nginx rate limiting:</strong> Configured with two zones:
      <code>limit_req_zone</code> at <strong>20 req/s</strong> for API endpoints and <strong>5 req/s</strong> for admin. Blocks
      brute-force attacks before they reach Django.<br><br>
      <strong>Layer 2 — reCAPTCHA v3 score:</strong> The <code>verify_captcha()</code> service sends
      the client token to Google's <code>siteverify</code> endpoint. It auto-detects whether the
      token is v3 (has a <code>score</code> field) or v2 (checkbox challenge). For v3, the score must be
      ≥ <strong>0.5</strong> (scale 0.0–1.0 where 1.0 = definitely human). On failure, the response is a
      <strong>403 Forbidden</strong>.<br><br>
      <strong>Fail-closed design:</strong> If Google's API is unreachable or returns an error, the
      request is rejected — not allowed through. Sensitive data is never exposed: the
      <code>RECAPTCHA_SECRET_KEY</code> stays server-side only.
    </div>

    <h3>Data Storage</h3>
    <p><strong>No database writes.</strong> reCAPTCHA tokens are verified in real-time via Google's
    API and not stored. Pass/fail results are logged to application logs (structured logging with
    IP and action name) for monitoring, but don't create database records. This avoids write
    overhead on every form submission.</p>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Tool</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><strong>Google reCAPTCHA v3</strong></td><td>Invisible behavioural scoring — no user friction. Client: <code>grecaptcha.execute()</code>,
        server: POST to <code>google.com/recaptcha/api/siteverify</code></td></tr>
        <tr><td><strong>reCAPTCHA v2 fallback</strong></td><td>Auto-detected from token format. Covers edge cases where v3 widget fails to load</td></tr>
        <tr><td><strong>Nginx rate limiting</strong></td><td><strong>20 req/s</strong> API, <strong>5 req/s</strong> admin — first defence layer before any Python code runs</td></tr>
        <tr><td><strong>HTTPS (Let's Encrypt)</strong></td><td>All traffic encrypted — tokens can't be intercepted in transit</td></tr>
      </tbody>
    </table>
  `,
});
