<!--
  App.vue — Root Application Shell
  ─────────────────────────────────────────────────────────────────────────────
  This is the outermost component that wraps the entire Orbit app.

  LAYOUT
  ┌──────────────────────────────────────────┐
  │  AppHeader (sticky top bar)              │
  ├──────────────────────────────────────────┤
  │  <RouterView />  ← current page swaps   │
  │                     in here              │
  └──────────────────────────────────────────┘

  KEY DETAIL
  • The `hideSearch` prop tells the header NOT to show its built-in search bar
    on the Home page, because HomePage already renders its own HeroSearch.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <AppHeader :hide-search="isHome" />
  <RouterView />
</template>

<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'

const route = useRoute()

// HomePage already has its own centered HeroSearch, so hide the header search bar there
const isHome = computed(() => route.name === 'Home')
</script>
