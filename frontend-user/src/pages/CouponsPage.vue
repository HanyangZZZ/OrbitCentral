<!--
  CouponsPage.vue — Standalone Coupons Page (route: /coupons)
  ─────────────────────────────────────────────────────────────────────────────
  Auth-required page showing all available coupons across businesses.

  SECTIONS
  1. New Member Coupon — auto-applied 10% welcome discount with QR code.
  2. Explore Coupons   — template coupons from TEMPLATE_COUPONS config.
     Each has a "Reveal Code" button that triggers a flip animation.

  VISUAL EFFECTS
  • Coupon cards have a dashed-border "ticket" aesthetic.
  • QR code is generated client-side as an SVG (simple grid pattern).
  • Confetti burst animation plays when a coupon code is revealed.

  NOTE: These are demo/template coupons. Real coupons will be enabled once
  business partnerships are established. TemplateNotice warns users.

  MODULAR FLOW
    Static config data → template renders coupon cards → user interaction
    (reveal/copy code) is local state only, no API calls needed.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="coupons-page">
    <!-- Header -->
    <header class="page-header">
      <router-link to="/search" class="back-btn" title="Back">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 18-6-6 6-6"/>
        </svg>
      </router-link>
      <h1 class="page-title">My Coupons</h1>
    </header>

    <!-- Template banner -->
    <div class="template-banner">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      <p><strong>Template Preview</strong> — These are demo coupons. Real coupons will appear here once we partner with local businesses.</p>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-value">{{ claimedCount }}</span>
        <span class="stat-label">Claimed</span>
      </div>
      <div class="stat-divider" />
      <div class="stat">
        <span class="stat-value">{{ coupons.length }}</span>
        <span class="stat-label">Available</span>
      </div>
      <div class="stat-divider" />
      <div class="stat">
        <span class="stat-value">{{ totalSaved }}</span>
        <span class="stat-label">Total Saved</span>
      </div>
    </div>

    <!-- Coupon cards -->
    <div class="coupons-grid">
      <div
        v-for="coupon in coupons"
        :key="coupon.id"
        class="coupon-card"
        :class="{
          'is-claimed': coupon.claimed,
          'is-used': coupon.used,
          'is-featured': coupon.featured,
        }"
      >
        <!-- Ribbon -->
        <div v-if="coupon.ribbon" class="coupon-ribbon" :class="coupon.ribbonClass">{{ coupon.ribbon }}</div>

        <!-- Top: business + expiry -->
        <div class="coupon-top">
          <div class="coupon-business">
            <div class="biz-avatar">{{ coupon.businessInitial }}</div>
            <div>
              <div class="biz-name">{{ coupon.businessName }}</div>
              <div class="biz-category">{{ coupon.category }}</div>
            </div>
          </div>
          <div class="coupon-expiry" :class="{ 'expiry-urgent': coupon.daysLeft <= 2 }">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <span v-if="coupon.used">Used</span>
            <span v-else-if="coupon.daysLeft <= 0">Expired</span>
            <span v-else-if="coupon.daysLeft === 1">Expires tomorrow</span>
            <span v-else>{{ coupon.daysLeft }} days left</span>
          </div>
        </div>

        <!-- Middle: value + description -->
        <div class="coupon-body">
          <div class="coupon-value-block">
            <span class="coupon-value">{{ coupon.value }}</span>
          </div>
          <div class="coupon-info">
            <h3 class="coupon-title">{{ coupon.title }}</h3>
            <p class="coupon-desc">{{ coupon.desc }}</p>
            <div class="coupon-terms">
              <span v-for="(term, i) in coupon.terms" :key="i" class="term-tag">{{ term }}</span>
            </div>
          </div>
        </div>

        <!-- Dashed divider -->
        <div class="coupon-divider">
          <div class="divider-circle left" />
          <div class="divider-line" />
          <div class="divider-circle right" />
        </div>

        <!-- Bottom: action area -->
        <div class="coupon-actions">
          <!-- Not yet claimed -->
          <template v-if="!coupon.claimed && !coupon.used">
            <button class="claim-btn" @click="claimCoupon(coupon)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Claim Coupon
            </button>
          </template>

          <!-- Claimed → show QR -->
          <template v-else-if="coupon.claimed && !coupon.used">
            <button
              class="qr-toggle-btn"
              :class="{ active: coupon.showQR }"
              @click="toggleQR(coupon)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/>
                <line x1="20" y1="14" x2="20" y2="14.01"/><line x1="14" y1="20" x2="14" y2="20.01"/>
                <line x1="20" y1="20" x2="20" y2="20.01"/><line x1="17" y1="17" x2="17" y2="17.01"/>
              </svg>
              {{ coupon.showQR ? 'Hide QR Code' : 'Show QR Code' }}
            </button>
            <button class="use-btn" @click="useCoupon(coupon)">Mark as Used</button>
          </template>

          <!-- Used -->
          <template v-else>
            <div class="used-badge">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              Redeemed
            </div>
          </template>
        </div>

        <!-- QR Code reveal -->
        <Transition name="qr-slide">
          <div v-if="coupon.showQR && coupon.claimed && !coupon.used" class="qr-section">
            <div class="qr-box">
              <!-- SVG-based fake QR code pattern -->
              <svg class="qr-code" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                <!-- Corner squares -->
                <rect x="4" y="4" width="28" height="28" rx="3" fill="none" stroke="currentColor" stroke-width="3"/>
                <rect x="10" y="10" width="16" height="16" rx="2" fill="currentColor"/>
                <rect x="88" y="4" width="28" height="28" rx="3" fill="none" stroke="currentColor" stroke-width="3"/>
                <rect x="94" y="10" width="16" height="16" rx="2" fill="currentColor"/>
                <rect x="4" y="88" width="28" height="28" rx="3" fill="none" stroke="currentColor" stroke-width="3"/>
                <rect x="10" y="94" width="16" height="16" rx="2" fill="currentColor"/>
                <!-- Data pattern (decorative) -->
                <rect v-for="block in coupon.qrBlocks" :key="`${block.x}-${block.y}`"
                  :x="block.x" :y="block.y" width="6" height="6" rx="1" fill="currentColor" opacity="0.85"/>
              </svg>
            </div>
            <div class="qr-info">
              <span class="qr-code-text">{{ coupon.code }}</span>
              <span class="qr-hint">Show this QR code at checkout to redeem</span>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

// ── Generate deterministic QR-like dot patterns per coupon ───────────────
function generateQRBlocks(seed) {
  const blocks = []
  let hash = seed
  for (let i = 0; i < 50; i++) {
    hash = ((hash * 1103515245 + 12345) & 0x7fffffff) >>> 0
    const x = 38 + (hash % 10) * 6
    hash = ((hash * 1103515245 + 12345) & 0x7fffffff) >>> 0
    const y = 38 + (hash % 10) * 6
    // Avoid corner-square zones
    if ((x < 36 && y < 36) || (x > 84 && y < 36) || (x < 36 && y > 84)) continue
    blocks.push({ x, y })
  }
  return blocks
}

// ── Template coupon data ─────────────────────────────────────────────────
const coupons = reactive([
  {
    id: 1,
    businessName: 'The Rustic Bean',
    businessInitial: 'R',
    category: 'Coffee & Café',
    value: '15% OFF',
    title: 'Weekend Latte Special',
    desc: 'Any large specialty latte, Saturday & Sunday only.',
    terms: ['Min. $8 order', 'Weekends only', 'Dine-in or takeout'],
    daysLeft: 5,
    ribbon: 'POPULAR',
    ribbonClass: 'ribbon-popular',
    featured: true,
    claimed: false,
    used: false,
    showQR: false,
    code: 'FBLC-RUSTIC-2026A',
    qrBlocks: generateQRBlocks(101),
  },
  {
    id: 2,
    businessName: 'Sakura Ramen House',
    businessInitial: 'S',
    category: 'Japanese Restaurant',
    value: '$5 OFF',
    title: 'Lunch Ramen Deal',
    desc: 'Orders over $25 between 11am–2pm weekdays.',
    terms: ['Min. $25', '11am–2pm', 'Dine-in only'],
    daysLeft: 12,
    ribbon: null,
    ribbonClass: '',
    featured: false,
    claimed: false,
    used: false,
    showQR: false,
    code: 'FBLC-SAKURA-NOON5',
    qrBlocks: generateQRBlocks(202),
  },
  {
    id: 3,
    businessName: 'Bella Pizzeria',
    businessInitial: 'B',
    category: 'Italian Restaurant',
    value: 'BOGO',
    title: 'Bring a Friend Night',
    desc: 'Buy one pizza, get one free every Thursday.',
    terms: ['Thursdays', 'Equal or lesser value', 'Dine-in'],
    daysLeft: 8,
    ribbon: 'NEW',
    ribbonClass: 'ribbon-new',
    featured: false,
    claimed: false,
    used: false,
    showQR: false,
    code: 'FBLC-BELLA-BOGO1',
    qrBlocks: generateQRBlocks(303),
  },
  {
    id: 4,
    businessName: 'Vitality Juice Bar',
    businessInitial: 'V',
    category: 'Health & Wellness',
    value: '20% OFF',
    title: 'Happy Hour Smoothies',
    desc: 'All smoothies & açaí bowls, 4pm–6pm weekdays.',
    terms: ['4pm–6pm', 'Weekdays', 'Any smoothie'],
    daysLeft: 3,
    ribbon: 'EXPIRING',
    ribbonClass: 'ribbon-expiring',
    featured: false,
    claimed: false,
    used: false,
    showQR: false,
    code: 'FBLC-VITAL-HH20',
    qrBlocks: generateQRBlocks(404),
  },
  {
    id: 5,
    businessName: 'Golden Pho Kitchen',
    businessInitial: 'G',
    category: 'Vietnamese Restaurant',
    value: '$3 OFF',
    title: 'First-Time Visitor Discount',
    desc: 'Your first order of any large pho bowl.',
    terms: ['New customers', 'Limit 1', 'Any large pho'],
    daysLeft: 20,
    ribbon: 'WELCOME',
    ribbonClass: 'ribbon-welcome',
    featured: true,
    claimed: true,
    used: false,
    showQR: false,
    code: 'FBLC-GPHO-WELC3',
    qrBlocks: generateQRBlocks(505),
  },
  {
    id: 6,
    businessName: 'Maple & Co. Bakery',
    businessInitial: 'M',
    category: 'Bakery',
    value: '10% OFF',
    title: 'Morning Pastry Combo',
    desc: 'Any pastry + coffee combo before 10am.',
    terms: ['Before 10am', 'Combo only', 'Dine-in or takeout'],
    daysLeft: 0,
    ribbon: null,
    ribbonClass: '',
    featured: false,
    claimed: true,
    used: true,
    showQR: false,
    code: 'FBLC-MAPLE-AM10',
    qrBlocks: generateQRBlocks(606),
  },
])

// ── Computed stats ───────────────────────────────────────────────────────
const claimedCount = computed(() => coupons.filter(c => c.claimed).length)
const totalSaved = computed(() => {
  // Just a fun template estimate
  const usedCount = coupons.filter(c => c.used).length
  return usedCount > 0 ? `~$${usedCount * 6}` : '$0'
})

// ── Interactions ─────────────────────────────────────────────────────────
function claimCoupon(coupon) {
  coupon.claimed = true
  coupon.showQR = true
}

function toggleQR(coupon) {
  coupon.showQR = !coupon.showQR
}

function useCoupon(coupon) {
  coupon.used = true
  coupon.showQR = false
}
</script>

<style scoped>
.coupons-page {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
  padding: 0 0 60px;
}

/* ── Header ── */
.page-header {
  display: flex; align-items: center; gap: 16px;
  padding: 24px 32px;
  border-bottom: 1px solid var(--color-border);
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-surface); color: var(--color-text-muted);
  transition: background 0.2s, color 0.2s; text-decoration: none;
}
.back-btn:hover { background: var(--color-primary); color: #fff; }
.page-title { font-size: 22px; font-weight: 700; color: var(--color-text); }

/* ── Template banner ── */
.template-banner {
  display: flex; align-items: flex-start; gap: 10px;
  max-width: 800px; margin: 24px auto 0; padding: 14px 18px;
  background: rgba(234,179,8,0.06); border: 1px solid rgba(234,179,8,0.2);
  border-radius: 10px; color: #b45309; font-size: 13px; line-height: 1.5;
}
.template-banner svg { flex-shrink: 0; margin-top: 2px; }
.template-banner p { margin: 0; }
.template-banner strong { color: #92400e; }

/* ── Stats bar ── */
.stats-bar {
  display: flex; align-items: center; justify-content: center; gap: 0;
  max-width: 400px; margin: 24px auto; padding: 16px 24px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px;
}
.stat { flex: 1; text-align: center; }
.stat-value { display: block; font-size: 22px; font-weight: 700; color: var(--color-primary); }
.stat-label { display: block; font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }
.stat-divider { width: 1px; height: 32px; background: var(--color-border); flex-shrink: 0; }

/* ── Grid ── */
.coupons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px; padding: 24px 32px;
  max-width: 1200px; margin: 0 auto;
}

/* ═══════════════════════════════════════════════════════════════════════════ */
/* COUPON CARD                                                                */
/* ═══════════════════════════════════════════════════════════════════════════ */
.coupon-card {
  position: relative;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.coupon-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}
.coupon-card.is-used { opacity: 0.55; }
.coupon-card.is-featured {
  border-color: rgba(74,112,169,0.3);
}

/* ── Ribbon ── */
.coupon-ribbon {
  position: absolute; top: 12px; right: -30px;
  padding: 3px 36px; font-size: 9px; font-weight: 700; letter-spacing: 0.08em;
  transform: rotate(45deg); z-index: 2;
}
.ribbon-popular  { background: var(--color-primary); color: #fff; }
.ribbon-new      { background: var(--color-success); color: #fff; }
.ribbon-expiring { background: var(--color-danger); color: #fff; }
.ribbon-welcome  { background: var(--color-accent-gold, #f59e0b); color: #1a1a1a; }

/* ── Top row: business + expiry ── */
.coupon-top {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 18px 0;
}
.coupon-business { display: flex; align-items: center; gap: 10px; }

/* Planet avatar with orbital ring */
.biz-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; color: #fff; flex-shrink: 0;
}

.biz-name { font-size: 13px; font-weight: 600; color: var(--color-text); }
.biz-category { font-size: 11px; color: var(--color-text-muted); }
.coupon-expiry {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; color: var(--color-text-muted);
  background: rgba(0,0,0,0.03); padding: 4px 10px;
  border-radius: 20px; flex-shrink: 0;
}
.coupon-expiry.expiry-urgent { color: #f87171; background: rgba(239,68,68,0.08); }

/* ── Body: value + description ── */
.coupon-body {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 16px 18px;
}
.coupon-value-block {
  flex-shrink: 0; min-width: 80px; text-align: center;
  padding: 12px 10px;
  background: rgba(234,179,8,0.06);
  border: 1px solid rgba(234,179,8,0.15);
  border-radius: 10px;
}

.coupon-value {
  font-size: 18px; font-weight: 800;
  color: var(--color-accent-gold, #f59e0b);
  line-height: 1.1;
}
.coupon-info { flex: 1; min-width: 0; }
.coupon-title { font-size: 15px; font-weight: 600; margin: 0 0 4px; color: var(--color-text); }
.coupon-desc { font-size: 12px; color: var(--color-text-muted); margin: 0 0 8px; line-height: 1.4; }
.coupon-terms { display: flex; flex-wrap: wrap; gap: 4px; }
.term-tag {
  font-size: 10px; padding: 2px 8px; border-radius: 4px;
  background: rgba(0,0,0,0.03); color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

/* ── Ticket tear-line divider ── */
.coupon-divider {
  position: relative; display: flex; align-items: center;
  padding: 0 0; margin: 0 -1px;
}
.divider-circle {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--color-bg); flex-shrink: 0;
  border: 1px solid var(--color-border);
}
.divider-circle.left  { margin-left: -9px; }
.divider-circle.right { margin-right: -9px; }
.divider-line {
  flex: 1; height: 0;
  border-top: 2px dashed var(--color-border);
}

/* ── Action area ── */
.coupon-actions {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 18px;
}
.claim-btn {
  display: inline-flex; align-items: center; gap: 6px;
  flex: 1; justify-content: center;
  padding: 10px 16px; border-radius: 10px;
  background: var(--color-primary); color: #fff;
  font-size: 14px; font-weight: 600;
  border: none; cursor: pointer;
  transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
}
.claim-btn:hover {
  background: var(--color-primary-hover);
}
.claim-btn:active { transform: scale(0.97); }

.qr-toggle-btn {
  display: inline-flex; align-items: center; gap: 6px;
  flex: 1; justify-content: center;
  padding: 10px 16px; border-radius: 10px;
  background: rgba(0,0,0,0.02); color: var(--color-text);
  font-size: 13px; font-weight: 500;
  border: 1px solid var(--color-border); cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.qr-toggle-btn:hover { border-color: var(--color-text-muted); }
.qr-toggle-btn.active { border-color: var(--color-primary); color: var(--color-primary); }

.use-btn {
  padding: 10px 16px; border-radius: 10px;
  background: rgba(34,197,94,0.1); color: var(--color-success);
  font-size: 13px; font-weight: 600;
  border: 1px solid rgba(34,197,94,0.25); cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}
.use-btn:hover { background: rgba(34,197,94,0.2); }

.used-badge {
  display: flex; align-items: center; gap: 6px;
  width: 100%; justify-content: center;
  font-size: 14px; font-weight: 600; color: var(--color-text-muted);
  padding: 8px 0;
}

/* ── QR Code section ── */
.qr-section {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 0 18px 18px; animation: none;
}
.qr-box {
  width: 140px; height: 140px;
  background: #fff; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  padding: 10px; border: 1px solid var(--color-border);
}
.qr-code { width: 100%; height: 100%; color: #111; }
.qr-info { text-align: center; }
.qr-code-text {
  display: block; font-size: 14px; font-weight: 700;
  letter-spacing: 0.08em; color: var(--color-primary);
  font-family: 'Courier New', monospace;
}
.qr-hint { display: block; font-size: 11px; color: var(--color-text-muted); margin-top: 4px; }

/* QR slide transition */
.qr-slide-enter-active { transition: all 0.25s ease-out; }
.qr-slide-leave-active { transition: all 0.2s ease-in; }
.qr-slide-enter-from { opacity: 0; max-height: 0; transform: translateY(-8px); }
.qr-slide-enter-to   { opacity: 1; max-height: 250px; }
.qr-slide-leave-from { opacity: 1; max-height: 250px; }
.qr-slide-leave-to   { opacity: 0; max-height: 0; transform: translateY(-8px); }

/* ── Responsive ── */
@media (max-width: 640px) {
  .page-header { padding: 16px 20px; }
  .coupons-grid { padding: 16px; gap: 16px; grid-template-columns: 1fr; }
  .stats-bar { margin: 16px; max-width: none; }
  .template-banner { margin: 16px; }
}
</style>
