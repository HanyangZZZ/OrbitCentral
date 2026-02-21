/* Feature 4 — AI-Powered Reviews */
window.SECTIONS = window.SECTIONS || [];
window.SECTIONS.push({
  id: 'feat-reviews',
  title: 'AI-Powered Reviews',
  icon: ICON.msgCircle,
  weight: '',
  className: 'section--feature',
  html: `
    <div class="section-header">
      <span class="feature-badge">Feature 4 of 7</span>
      <h2 class="section-title">Allowing Users to Leave Reviews or Ratings</h2>
      <p class="section-subtitle">Conversational AI review system with automatic tag detection via function calling</p>
    </div>

    <h3>Logical Workflow</h3>
    <div class="diagram-container">
      <pre class="mermaid">
sequenceDiagram
  actor U as User
  participant FE as Frontend
  participant API as Django API
  participant GPT as GPT-4.1
  participant DB as PostgreSQL
  rect rgba(74, 112, 169, 0.08)
  Note right of U: Step 1 — Start chat
  U->>FE: Write Review + pick 4 stars
  FE->>API: POST /ai-reviews/start/ business 42 rating 4
  API->>GPT: System prompt + business context
  GPT-->>API: What stood out most?
  API-->>FE: Chat message
  end
  rect rgba(67, 56, 202, 0.08)
  Note right of U: Step 2 — Conversation
  U->>FE: Oat milk lattes + cozy vibe
  FE->>API: POST /ai-reviews/id/message/
  API->>GPT: User msg + function tools
  Note over GPT: Calls add_tag oat-milk + add_tag cozy
  GPT-->>API: Reply + tool calls
  API-->>FE: Reply + tags_added list
  end
  rect rgba(245, 158, 11, 0.08)
  Note right of U: Step 3 — Generate
  U->>FE: Click Generate Review
  FE->>API: POST /ai-reviews/id/generate/
  API->>GPT: Conversation + generation prompt
  GPT-->>API: Polished first-person review
  API-->>FE: Preview text
  end
  rect rgba(34, 197, 94, 0.08)
  Note right of U: Step 4 — Publish
  U->>FE: Click Publish
  FE->>API: POST /ai-reviews/id/confirm/
  API->>DB: Create Review + M2M tags + recalc Bayesian
  API-->>FE: Published
  end
      </pre>
      <p class="diagram-caption">4-step flow: chat → generate → preview → publish</p>
    </div>

    <h3>How the AI Works — In Detail</h3>
    <div class="highlight-box highlight-box--accent">
      <strong>System prompt:</strong> GPT-4.1 receives full business context — name, category, address,
      price level, Google rating, current tags, <strong>16 boolean attributes</strong> (dine-in, outdoor-seating,
      live-music, etc.), and the user's star rating. It's instructed to be a "friend asking 
      how was it?" — short messages, one topic at a time, <strong>3-5 exchanges</strong>.<br><br>
      <strong>Function calling tools:</strong> Two tools are defined: <code>add_tag(tag_name, reason)</code>
      and <code>remove_tag(tag_name, reason)</code>. When the user says something like "the patio was 
      amazing", GPT autonomously calls <code>add_tag("outdoor-seating")</code>. If a user says "tagged as
      wifi but there's no wifi", GPT calls <code>remove_tag("wifi")</code>. Tags accumulate on the session
      but are <strong>only applied on confirm</strong> — abandoned chats don't pollute data.<br><br>
      <strong>Review generation:</strong> A separate GPT call takes the full conversation, strips
      system/tool messages, and generates a 2-5 sentence first-person review. The user can
      generate until satisfied.<br><br>
      <strong>Why this matters:</strong> Every review conversation enriches the tag database. The more
      users chat, the better the vibe search becomes for everyone — it's a <strong>crowd-sourced
      data flywheel</strong>.
    </div>

    <h3>Data Storage</h3>
    <table class="data-table">
      <thead><tr><th>Model</th><th>How</th></tr></thead>
      <tbody>
        <tr><td><strong>ReviewChat</strong></td><td>Stores conversation as <code>JSONField</code> array (no separate messages table).
        Tags queued in <code>tags_to_add</code> / <code>tags_to_remove</code> arrays. Linked to business + user</td></tr>
        <tr><td><strong>Review</strong></td><td>Created only on confirm. FK user + FK business. 1-5 rating + generated text.
        Unique <code>(user, business)</code> constraint. Triggers Bayesian recalc signal</td></tr>
        <tr><td><strong>Tag M2M</strong></td><td>Tags applied to business via M2M junction table on confirm. New tags created
        via <code>get_or_create</code></td></tr>
      </tbody>
    </table>

    <h3>APIs &amp; Tools</h3>
    <table class="data-table">
      <thead><tr><th>Tool</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td><strong>OpenAI GPT-4.1</strong></td><td>Powers conversation + review generation. Temperature <strong>0.8</strong> for natural chat, <strong>0.7</strong> for review writing</td></tr>
        <tr><td><strong>Function Calling</strong></td><td>Structured data extraction from unstructured conversation — GPT decides when to tag</td></tr>
        <tr><td><code>POST /ai-reviews/start/</code></td><td>Create chat session, get AI's opening message</td></tr>
        <tr><td><code>POST /ai-reviews/{id}/message/</code></td><td>Send user message, receive AI reply + any tool-call results</td></tr>
        <tr><td><code>POST /ai-reviews/{id}/generate/</code></td><td>Generate polished review text from conversation</td></tr>
        <tr><td><code>POST /ai-reviews/{id}/confirm/</code></td><td>Publish review + apply tags + recalc rating (one transaction)</td></tr>
      </tbody>
    </table>

    <h3>Recent Reviews</h3>
    <div class="demo-label">Live from API</div>
    <div id="live-reviews" class="review-cards loading-pulse">
      <div class="review-card"><p class="review-card-text">Loading…</p></div>
    </div>
  `,

  init(el) {
    const container = el.querySelector('#live-reviews');

    API.getAllReviews(5).then(async data => {
      if (!data?.results?.length) {
        container.classList.remove('loading-pulse');
        container.innerHTML = '<p class="demo-placeholder">No reviews yet</p>';
        return;
      }
      // Fetch business names for each review
      const bizIds = [...new Set(data.results.map(r => r.business))];
      const bizMap = {};
      await Promise.all(bizIds.map(async id => {
        const biz = await API.get('/businesses/' + id + '/');
        if (biz) bizMap[id] = biz.name;
      }));

      container.classList.remove('loading-pulse');
      container.classList.add('live-data');
      container.innerHTML = data.results.map(r => {
        const stars = '★'.repeat(r.rating) + '☆'.repeat(5 - r.rating);
        const votes = r.vote_counts || {};
        const voteHtml = (votes.useful || votes.funny || votes.cool)
          ? '<div class="review-card-votes">'
            + (votes.useful ? '<span>' + ICON.thumbsUp + ' ' + votes.useful + ' useful</span>' : '')
            + (votes.funny ? '<span>' + ICON.smile + ' ' + votes.funny + ' funny</span>' : '')
            + (votes.cool ? '<span>' + ICON.sunglasses + ' ' + votes.cool + ' cool</span>' : '')
            + '</div>'
          : '';
        const imgHtml = r.image_url
          ? '<img src="' + r.image_url + '" alt="" style="width:100%;max-height:140px;object-fit:cover;border-radius:6px;margin-top:8px" loading="lazy">'
          : '';
        return '<div class="review-card">'
          + '<div class="review-card-header">'
          + '<span class="review-card-user">@' + (r.username || 'anonymous') + '</span>'
          + '<span class="review-card-rating">' + stars + '</span>'
          + '</div>'
          + '<p class="review-card-text">' + (r.description || '<em>No text</em>') + '</p>'
          + imgHtml
          + '<p class="review-card-biz">' + ICON.pin + ' ' + (bizMap[r.business] || 'Business #' + r.business) + '</p>'
          + voteHtml
          + '</div>';
      }).join('');
    });
  },
});
