<template>
  <section class="about-us-page">
    <div class="about-top-bar">
      <div class="top-bar-left">
        <router-link to="/" class="brand-name">Orbit</router-link>
      </div>
      <div class="top-bar-right">
        <router-link to="/leaderboard" class="nav-link">Leaderboard</router-link>
        <router-link to="/discover" class="nav-link">Discover</router-link>
        <router-link to="/settings/favorites" class="nav-link">Favorites</router-link>
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
    <div class="about-content">
      <h1>About Us</h1>
      <p>Welcome to Orbit — Your City, Personalized.</p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const profileOpen = ref(false)
const profileWrapper = ref(null)

function handleClickOutside(e) {
  if (profileWrapper.value && !profileWrapper.value.contains(e.target)) {
    profileOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.about-us-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  background: white;
}

.about-top-bar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 84px 12px;
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

@media (min-width: 768px) {
  .nav-link { display: inline; }
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

.brand-name {
  font-family: 'Barlow', 'SF Pro', 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 500;
  color: #000;
  text-decoration: none;
  transition: font-weight 0.15s ease, text-shadow 0.15s ease;
}

.brand-name:hover {
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(74, 112, 169, 0.3);
}

.about-content {
  padding: 60px 40px;
  text-align: center;
}

.about-content h1 {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 36px;
  font-weight: 510;
  margin-bottom: 16px;
}

.about-content p {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 18px;
  font-weight: 300;
  color: #333;
}
</style>
