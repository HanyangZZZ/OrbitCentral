/* ==========================================================================
   Navigation — TOC Builder, Scroll Spy, Progress Bar
   ========================================================================== */

const Nav = {
  init() {
    this.buildTOC();
    this.setupScrollSpy();
    this.setupProgressBar();
  },

  buildTOC() {
    const list = document.getElementById('toc-list');
    const sections = window.SECTIONS || [];

    list.innerHTML = sections.map(s => `
      <li>
        <a href="#${s.id}" data-section="${s.id}">
          <span class="toc-icon">${s.icon}</span>
          <span>${s.title}</span>
          ${s.weight ? `<span class="toc-weight">${s.weight}</span>` : ''}
        </a>
      </li>
    `).join('');

    list.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const target = document.getElementById(a.dataset.section);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  },

  setupScrollSpy() {
    const links = document.querySelectorAll('#toc-list a');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          links.forEach(l => l.classList.remove('active'));
          const active = document.querySelector(
            `#toc-list a[data-section="${entry.target.id}"]`
          );
          if (active) active.classList.add('active');
        }
      });
    }, { threshold: 0.15, rootMargin: '-5% 0px -75% 0px' });

    document.querySelectorAll('.section[id]').forEach(s => observer.observe(s));
  },

  setupProgressBar() {
    const bar = document.getElementById('progress-bar');
    window.addEventListener('scroll', () => {
      const h = document.documentElement;
      const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = `${Math.min(pct, 100)}%`;
    });
  }
};
