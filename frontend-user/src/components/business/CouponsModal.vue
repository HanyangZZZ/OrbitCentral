<!--
  CouponsModal.vue — Business Coupons Overlay
  ─────────────────────────────────────────────────────────────────────────────
  Modal popup showing available coupons for a specific business.
  Uses BaseModal for the overlay/card shell.

  COUPON TYPES
  1. New Member coupon — always shown, auto-applied 10% welcome discount.
     Has a gold "NEW MEMBER" ribbon badge.
  2. Template coupons — loaded from TEMPLATE_COUPONS (config/businessDetail.js).
     Marked "Coming Soon" with a lock icon. Demo-only until partnerships.

  Each coupon card has: value badge | title + description | claim button.

  MODULAR FLOW
    BusinessDetailPage opens via v-model → renders coupon cards
    → Close button emits update:modelValue(false).
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <BaseModal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" title="Coupons" :subtitle="subtitle" wide>
    <div class="coupons-list">
      <!-- New Member Coupon -->
      <div class="coupon-card new-member">
        <div class="coupon-ribbon">NEW MEMBER</div>
        <div class="coupon-body">
          <div class="coupon-value">10% OFF</div>
          <div class="coupon-detail">
            <strong>Welcome Coupon</strong>
            <span>Valid for all new members on their first visit.</span>
          </div>
          <button class="coupon-claim-btn claimed" disabled>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            Auto-Applied
          </button>
        </div>
      </div>
      <!-- Template Coupons -->
      <div v-for="(coupon, i) in coupons" :key="i" class="coupon-card explore">
        <div class="coupon-body">
          <div class="coupon-value">{{ coupon.value }}</div>
          <div class="coupon-detail">
            <strong>{{ coupon.title }}</strong>
            <span>{{ coupon.desc }}</span>
          </div>
          <button class="coupon-claim-btn" disabled>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Coming Soon
          </button>
        </div>
      </div>
    </div>
    <TemplateNotice>Template only — real coupons will be available once we collaborate with this business.</TemplateNotice>
    <template #actions>
      <button class="action-btn secondary" @click="close">Close</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import TemplateNotice from '@/components/ui/TemplateNotice.vue'
import { TEMPLATE_COUPONS } from '@/config/businessDetail'

const props = defineProps({
  modelValue: Boolean,
  businessName: String
})

const emit = defineEmits(['update:modelValue'])

const coupons = TEMPLATE_COUPONS

const subtitle = computed(() => 
  `Exclusive deals for <strong>${props.businessName}</strong> — claim yours!`
)

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.coupons-list { display: flex; flex-direction: column; gap: 12px; max-height: 400px; overflow-y: auto; }
.coupon-card {
  position: relative; border-radius: 12px; overflow: hidden;
  border: 1px solid var(--color-border); background: var(--color-surface);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.coupon-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}
.coupon-card.new-member {
  border-color: rgba(234,179,8,0.3);
  background: linear-gradient(135deg, rgba(234,179,8,0.04), rgba(251,191,36,0.02));
}
.coupon-ribbon {
  position: absolute; top: 0; right: 0;
  padding: 3px 14px; font-size: 9px; font-weight: 700; letter-spacing: 0.06em;
  background: var(--color-accent-gold, #f59e0b); color: #1a1a1a;
  border-radius: 0 0 0 10px;
}
.coupon-body { display: flex; align-items: center; gap: 16px; padding: 16px 18px; }
.coupon-value {
  font-size: 18px; font-weight: 800; color: var(--color-accent-gold, #f59e0b);
  flex-shrink: 0; min-width: 64px;
  text-align: center; padding: 8px 4px;
  background: rgba(234,179,8,0.06); border: 1px solid rgba(234,179,8,0.15);
  border-radius: 8px;
}
.coupon-detail { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.coupon-detail strong { font-size: 14px; color: var(--color-text); }
.coupon-detail span { font-size: 12px; color: var(--color-text-muted); }
.coupon-claim-btn {
  padding: 6px 14px; font-size: 12px; font-weight: 600; border-radius: 8px;
  border: 1px solid var(--color-border); background: rgba(0,0,0,0.02);
  color: var(--color-text-muted); cursor: default; flex-shrink: 0;
  display: inline-flex; align-items: center; gap: 6px;
}
.coupon-claim-btn.claimed {
  border-color: rgba(234,179,8,0.3); color: var(--color-accent-gold, #f59e0b);
  background: rgba(234,179,8,0.06);
}
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 18px; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; border: none; transition: background 0.15s;
}
.action-btn.secondary { background: var(--color-surface); color: var(--color-text); border: 1px solid var(--color-border); }
.action-btn.secondary:hover { border-color: var(--color-primary); }
</style>
