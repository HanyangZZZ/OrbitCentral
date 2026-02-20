<!--
  ActivitiesModal.vue — "Vote for Activities" Modal
  ─────────────────────────────────────────────────────────────────────────────
  Lets users vote on activities they'd like a business to host.
  Uses BaseModal for the overlay/card shell.

  FEATURES
  • Activities are loaded from TEMPLATE_ACTIVITIES (config/businessDetail.js).
  • Each activity card is toggleable — clicking adds/removes it from `votes`.
  • Submit button shows the vote count and is disabled when none are selected.
  • TemplateNotice warns this is demo-only until business partnerships go live.

  ICON SYSTEM
  Activity icons (music, palette, chef, etc.) are inline SVG strings stored
  in a local ACTIVITY_ICONS map, rendered via v-html on a <span>.

  MODULAR FLOW
    BusinessDetailPage opens this modal via v-model → user toggles votes
    → close emits update:modelValue(false) → modal hides.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <BaseModal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" title="Vote for Activities" :subtitle="subtitle" wide>
    <div class="activities-list">
      <div
        v-for="(act, i) in activities"
        :key="i"
        class="activity-card"
        :class="{ voted: votes.includes(i) }"
        @click="toggleVote(i)"
      >
        <span class="activity-icon" v-html="ACTIVITY_ICONS[act.icon] || ACTIVITY_ICONS.default"></span>
        <div class="activity-info">
          <strong>{{ act.title }}</strong>
          <span class="activity-desc">{{ act.desc }}</span>
        </div>
        <span class="activity-vote-icon">
          <svg v-if="votes.includes(i)" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4338ca" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/></svg>
        </span>
      </div>
    </div>
    <TemplateNotice>Template only — voting will be activated once we partner with this business.</TemplateNotice>
    <template #actions>
      <button class="action-btn secondary" @click="close">Close</button>
      <button class="action-btn primary" :disabled="votes.length === 0" @click="close">
        Submit Votes ({{ votes.length }})
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import TemplateNotice from '@/components/ui/TemplateNotice.vue'
import { TEMPLATE_ACTIVITIES } from '@/config/businessDetail'

const ACTIVITY_ICONS = {
  music:    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  palette:  '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r="0.5" fill="currentColor"/><circle cx="17.5" cy="10.5" r="0.5" fill="currentColor"/><circle cx="8.5" cy="7.5" r="0.5" fill="currentColor"/><circle cx="6.5" cy="12.5" r="0.5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.93 0 1.5-.67 1.5-1.5 0-.39-.15-.74-.39-1.04-.23-.29-.38-.63-.38-1.01 0-.83.67-1.5 1.5-1.5H16c3.31 0 6-2.69 6-6 0-5.17-4.49-9-10-9z"/></svg>',
  chef:     '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 13.87A4 4 0 0 1 7.41 6a5.11 5.11 0 0 1 1.05-1.54 5 5 0 0 1 7.08 0A5.11 5.11 0 0 1 16.59 6 4 4 0 0 1 18 13.87V21H6z"/><line x1="6" y1="17" x2="18" y2="17"/></svg>',
  wellness: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
  mic:      '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
  game:     '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8h20"/><circle cx="8" cy="14" r="2"/><circle cx="16" cy="14" r="2"/></svg>',
  camera:   '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>',
  people:   '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  default:  '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/></svg>',
}

const props = defineProps({
  modelValue: Boolean,
  businessName: String
})

const emit = defineEmits(['update:modelValue'])

const activities = TEMPLATE_ACTIVITIES
const votes = ref([])

const subtitle = computed(() => 
  `Which activities would you love <strong>${props.businessName}</strong> to host? Vote for your favourites!`
)

function toggleVote(idx) {
  const pos = votes.value.indexOf(idx)
  if (pos >= 0) votes.value.splice(pos, 1)
  else votes.value.push(idx)
}

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.activities-list { display: flex; flex-direction: column; gap: 8px; max-height: 380px; overflow-y: auto; }
.activity-card {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px; border-radius: 10px;
  background: rgba(0,0,0,0.02); border: 1px solid var(--color-border);
  cursor: pointer; transition: all 0.15s; user-select: none;
}
.activity-card:hover { background: rgba(67,56,202,0.05); border-color: var(--color-border-light, #c7d2fe); }
.activity-card.voted { background: rgba(67,56,202,0.08); border-color: var(--color-accent, #4338ca); }
.activity-icon {
  width: 38px; height: 38px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; background: rgba(74,112,169,0.08); color: var(--color-primary, #4a70a9);
}
.activity-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.activity-info strong { font-size: 14px; color: var(--color-text); }
.activity-desc { font-size: 12px; color: var(--color-text-muted); }
.activity-vote-icon { flex-shrink: 0; display: flex; align-items: center; }
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 18px; border-radius: 8px; font-size: 13px; font-weight: 500;
  cursor: pointer; border: none; transition: background 0.15s;
}
.action-btn.primary { background: var(--color-primary); color: #fff; }
.action-btn.primary:hover { background: var(--color-primary-hover); }
.action-btn.primary:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.secondary { background: var(--color-surface); color: var(--color-text); border: 1px solid var(--color-border); }
.action-btn.secondary:hover { border-color: var(--color-primary); }
</style>
