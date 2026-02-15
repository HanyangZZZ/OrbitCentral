<template>
  <div class="app-shell">
    <main class="app-content">
      <RouterView v-slot="{ Component }">
        <component :is="Component" />
      </RouterView>
    </main>
  </div>
</template>

<script setup>
</script>
