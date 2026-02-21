/* ==========================================================================
   Main — App Initialization
   Injects section HTML, initializes Mermaid, scroll reveal, and live data.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const content = document.getElementById('content');
  const sections = window.SECTIONS || [];

  // 1. Inject all section HTML into #content
  sections.forEach(s => {
    const el = document.createElement('section');
    el.id = s.id;
    el.className = `section ${s.className || ''}`;
    el.innerHTML = `<div class="section-inner">${s.html}</div>`;
    content.appendChild(el);
  });

  // 2. Initialize Mermaid with Orbit color theme
  mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
      primaryColor: '#e8eef7',
      primaryTextColor: '#0f172a',
      primaryBorderColor: '#4a70a9',
      lineColor: '#64748b',
      secondaryColor: '#f0f4fa',
      tertiaryColor: '#f8fafc',
      fontFamily: "'Barlow', -apple-system, BlinkMacSystemFont, sans-serif",
      fontSize: '12px',
      pieTitleTextSize: '16px',
      pieSectionTextSize: '14px',
      pieLegendTextSize: '13px',
      pie1: '#7ba1d1',
      pie2: '#6b92c7',
      pie3: '#93b4dc',
      pie4: '#a3bfdf',
      pie5: '#bdd2ea',
      pie6: '#dbe8f4',
      pieTitleTextColor: '#0f172a',
      pieSectionTextColor: '#0f172a',
      pieLegendTextColor: '#475569',
      pieOuterStrokeWidth: '0',
      pieStrokeWidth: '1px',
      pieOuterStrokeColor: 'transparent',
      pieOpacity: '1',
      quadrant1Fill: '#e0eaf5',
      quadrant2Fill: '#eef2f9',
      quadrant3Fill: '#f8fafc',
      quadrant4Fill: '#f0f4fa',
      quadrant1TextFill: '#4a70a9',
      quadrant2TextFill: '#64748b',
      quadrant3TextFill: '#94a3b8',
      quadrant4TextFill: '#64748b',
      quadrantPointFill: '#4a70a9',
      quadrantPointTextFill: '#0f172a',
      quadrantXAxisTextFill: '#0f172a',
      quadrantYAxisTextFill: '#0f172a',
      quadrantTitleFill: '#0f172a',
      quadrantInternalBorderStrokeFill: '#cbd5e1',
      quadrantExternalBorderStrokeFill: '#4a70a9',
    },
  });

  // Explicitly render all mermaid diagrams (injected dynamically)
  mermaid.run({ querySelector: '.mermaid' }).catch(e =>
    console.warn('[Orbit] Mermaid render:', e.message)
  );

  // 3. Build the TOC sidebar + scroll spy + progress bar
  Nav.init();

  // 4. Scroll-reveal animation for .reveal elements
  const reveals = document.querySelectorAll('.reveal');
  const revealObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        revealObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  reveals.forEach(el => revealObs.observe(el));

  // 5. Call each section's init() for live API data
  sections.forEach(s => {
    if (typeof s.init === 'function') {
      const el = document.getElementById(s.id);
      if (el) s.init(el);
    }
  });
});
