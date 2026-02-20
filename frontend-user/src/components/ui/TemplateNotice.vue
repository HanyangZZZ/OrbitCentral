<!--
  TemplateNotice.vue — Yellow Info Banner
  ─────────────────────────────────────────────────────────────────────────────
  Small warning/info bar used on features that are demo-only (not yet live).
  Shown inside ActivitiesModal, CouponsModal, and the standalone Coupons page.

  USAGE
    <TemplateNotice>Your message here</TemplateNotice>

  Renders an info (ⓘ) SVG icon + the slot text on a warm amber background.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="template-notice">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>
    <span><slot /></span>
  </div>
</template>

<style scoped>
.template-notice {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; margin: 16px 0 0; border-radius: 8px;
  background: rgba(234,179,8,0.08); border: 1px solid rgba(234,179,8,0.2);
  font-size: 12px; color: #92400e; line-height: 1.4;
}
</style>
