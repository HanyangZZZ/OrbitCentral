<template>
  <div class="app-shell">
    <nav class="top-nav">
      <div class="brand">FBLC</div>
      <div class="links">
        <RouterLink to="/">Dashboard</RouterLink>
      </div>
    </nav>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  background: #0f172a;
  color: #e2e8f0;
}

.brand {
  font-weight: 700;
  letter-spacing: 0.08em;
}

.links {
  display: flex;
  gap: 16px;
}

.links a {
  color: #cbd5f5;
  text-decoration: none;
  font-size: 14px;
  padding: 6px 10px;
  border-radius: 999px;
}

.links a.router-link-active {
  background: rgba(148, 163, 184, 0.2);
  color: #ffffff;
}

main {
  flex: 1;
}
</style>
