<!--
  BaseIcon.vue — Reusable SVG Icon Wrapper
  ─────────────────────────────────────────────────────────────────────────────
  Thin wrapper around an <svg> element with sensible defaults (Feather-style:
  stroke-based, 24×24 viewBox, round caps/joins).

  USAGE
    <BaseIcon :size="20" fill="red">
      <circle cx="12" cy="12" r="10" />
    </BaseIcon>

  Pass SVG child elements (paths, circles, etc.) via the default slot.
  Props control size, fill, stroke colour, and stroke width.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    :fill="fill"
    :stroke="stroke"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <slot />
  </svg>
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 16 },
  fill: { type: String, default: 'none' },
  stroke: { type: String, default: 'currentColor' },
  strokeWidth: { type: [Number, String], default: 2 }
})
</script>
