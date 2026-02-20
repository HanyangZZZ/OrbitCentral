<!--
  BaseModal.vue — Reusable Modal Dialog
  ─────────────────────────────────────────────────────────────────────────────
  A generic overlay + centred card that any feature can use via v-model.

  USAGE
    <BaseModal v-model="showModal" title="My Title" subtitle="Some extra info">
      <p>Body content goes here</p>
      <template #actions>
        <button @click="showModal = false">Cancel</button>
      </template>
    </BaseModal>

  FEATURES
  • Teleported to <body> so it always sits above everything (z-index 1000).
  • Clicking the dark overlay closes the modal (via @click.self).
  • Optional `wide` prop bumps max-width from 480 → 560px.
  • Named slots: `header` (override title), default (body), `actions` (footer).

  MODULAR FLOW
    Parent v-model ↔ modelValue prop → overlay renders when true
    → close() emits update:modelValue(false) → parent hides the modal.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal" :class="{ 'modal-wide': wide }">
        <div v-if="title || $slots.header" class="modal-header-row">
          <h2 class="modal-title">
            <slot name="header">{{ title }}</slot>
          </h2>
          <button class="modal-close" @click="close">✕</button>
        </div>
        <p v-if="subtitle" class="modal-subtitle" v-html="subtitle" />
        <slot />
        <div v-if="$slots.actions" class="modal-actions">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  title: String,
  subtitle: String,
  wide: Boolean
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(15,23,42,0.4); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 14px; padding: 28px; width: 90%; max-width: 480px;
  box-shadow: var(--shadow-lg);
}
.modal-wide { max-width: 560px; }
.modal-header-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;
}
.modal-title { font-size: 18px; font-weight: 600; margin: 0; color: var(--color-text); }
.modal-close {
  width: 32px; height: 32px; border-radius: 8px; border: none;
  background: rgba(0,0,0,0.04); color: var(--color-text-muted);
  font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.modal-close:hover { background: rgba(0,0,0,0.08); color: var(--color-text); }
.modal-subtitle {
  font-size: 13px; color: var(--color-text-muted); margin: 0 0 18px; line-height: 1.5;
}
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
</style>
