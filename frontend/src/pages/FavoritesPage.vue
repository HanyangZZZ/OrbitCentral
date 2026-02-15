<template>
  <section class="favorites-page-figma">
    <div class="favorites-top-bar">
      <div class="top-bar-left">
        <router-link to="/" class="brand-name">Orbit</router-link>
      </div>
      <div class="discover-search" :class="{ 'ai-on': aiEnabled }">
        <span class="search-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="6.5" stroke="#0f172a" stroke-width="2" />
            <path d="M16.5 16.5L21 21" stroke="#0f172a" stroke-width="2" stroke-linecap="round" />
          </svg>
        </span>
        <input class="search-input" type="text" placeholder="Search" aria-label="Search" />
        <div class="ai-toggle" aria-label="Ask AI">
          <span>Ask AI</span>
          <button
            class="toggle-switch"
            type="button"
            role="switch"
            :aria-checked="aiEnabled"
            @click="aiEnabled = !aiEnabled"
          >
            <span class="toggle-knob" aria-hidden="true"></span>
          </button>
        </div>
      </div>
      <div class="top-bar-right">
        <router-link to="/leaderboard" class="nav-link">Leaderboard</router-link>
        <router-link to="/discover" class="nav-link">Discover</router-link>
        <router-link to="/settings/favorites" class="nav-link">Favorites</router-link>
        <div class="location-chip">
          <span>Location</span>
          <svg class="location-pin-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" stroke="#000" stroke-width="1.8" fill="none"/>
          </svg>
        </div>
        <div class="profile-wrapper" ref="profileWrapper">
          <div class="profile-icon" @click="profileOpen = !profileOpen">
            <img src="/figma-discovery-page/image_12_53x54.png" alt="" />
          </div>
          <div v-if="profileOpen" class="profile-dropdown">
            <router-link to="/settings" class="dropdown-item" @click="profileOpen = false">Account Settings</router-link>
          </div>
        </div>
      </div>
    </div>
    <div
      class="figma-frame-wrap"
      :style="{ height: (900 * figmaScale) + 'px' }"
    >
      <iframe
        class="figma-frame"
        src="/figma-favorites-page/index.html"
        title="Favorites page design"
        :style="{ transform: 'scale(' + figmaScale + ')' }"
      ></iframe>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const aiEnabled = ref(false)
const profileOpen = ref(false)
const profileWrapper = ref(null)

// ── Responsive iframe scaling ──
const figmaScale = ref(1)

function updateScale() {
  const vw = window.innerWidth
  figmaScale.value = vw < 1280 ? vw / 1280 : 1
}

function handleClickOutside(e) {
  if (profileWrapper.value && !profileWrapper.value.contains(e.target)) {
    profileOpen.value = false
  }
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  window.removeEventListener('resize', updateScale)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.favorites-page-figma {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 0;
  background: white;
  overflow-x: hidden;
}

.favorites-top-bar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  gap: 0.75rem;
  position: relative;
  z-index: 2;
  flex-wrap: wrap;
  box-sizing: border-box;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-name {
  font-family: 'Barlow', 'SF Pro', 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #000;
  text-decoration: none;
  transition: font-weight 0.15s ease, text-shadow 0.15s ease;
}

.brand-name:hover {
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(74, 112, 169, 0.3);
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-link {
  display: none;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #000;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  transition: font-weight 0.15s ease, color 0.15s ease;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}

.nav-link:hover {
  font-weight: 600;
  color: #4a70a9;
  border-bottom-color: #4a70a9;
}

.discover-search {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  background: #f8f8f8;
  border-radius: 0.75rem;
  padding: 0.625rem 1rem;
}

.discover-search.ai-on {
  background: #efece3;
}

.search-icon {
  display: inline-flex;
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #0f172a;
  outline: none;
}

.search-input::placeholder {
  color: #0f172a;
  opacity: 0.5;
}

.ai-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.75rem;
  font-weight: 400;
  color: #1f2937;
  white-space: nowrap;
}

.toggle-switch {
  width: 2.125rem;
  height: 1.125rem;
  border-radius: 999px;
  border: none;
  background: #d7d2c8;
  padding: 0.125rem;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.discover-search.ai-on .toggle-switch {
  background: #4a70a9;
}

.toggle-knob {
  width: 0.875rem;
  height: 0.875rem;
  border-radius: 50%;
  background: #ffffff;
  transform: translateX(0);
  transition: transform 0.2s ease;
}

.discover-search.ai-on .toggle-knob {
  transform: translateX(1rem);
}

.location-chip {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #000;
  white-space: nowrap;
}

.location-pin-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.profile-wrapper {
  position: relative;
}

.profile-icon {
  cursor: pointer;
}

.profile-icon img {
  width: 2.25rem;
  height: 2.25rem;
  max-width: 100%;
  height: auto;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.625rem);
  right: 0;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.10);
  padding: 0.75rem 1.25rem;
  z-index: 100;
  white-space: nowrap;
  min-width: 10rem;
}

.dropdown-item {
  display: block;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.8125rem;
  font-weight: 200;
  color: #000;
  text-decoration: none;
  cursor: pointer;
  transition: font-weight 0.15s ease, color 0.15s ease;
}

.dropdown-item:hover {
  font-weight: 500;
  color: #4a70a9;
}

.figma-frame-wrap {
  position: relative;
  width: 100%;
  max-width: 1280px;
  overflow: hidden;
  margin: 0 auto;
}

.figma-frame {
  width: 1280px;
  height: 900px;
  border: none;
  background: white;
  box-shadow: none;
  position: relative;
  z-index: 1;
  transform-origin: top left;
}

img {
  max-width: 100%;
  height: auto;
}

@media (min-width: 768px) {
  .nav-link { display: inline; }
  .favorites-top-bar {
    padding: 1.25rem 2rem 0.75rem;
    gap: 1rem;
    flex-wrap: nowrap;
  }
  .brand-name { font-size: 1.25rem; }
}

@media (min-width: 1024px) {
  .favorites-top-bar {
    padding: 1.5rem 5.25rem 0.75rem;
    gap: 1.5rem;
  }
  .brand-name { font-size: 1.375rem; }
}
</style>
