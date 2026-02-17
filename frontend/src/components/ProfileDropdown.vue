<template>
  <div class="profile-wrapper" ref="targetRef">
    <div class="profile-icon" @click="isOpen = !isOpen">
      <img src="/shared/profile-icon.png" alt="Profile" />
    </div>
    <Transition name="dropdown">
      <div v-if="isOpen" class="profile-dropdown">
        <router-link to="/settings" class="dropdown-item" @click="isOpen = false">
          Account Settings
        </router-link>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useClickOutside } from '@/composables'

const isOpen = ref(false)
const { targetRef } = useClickOutside(() => { isOpen.value = false })
</script>

<style scoped>
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
  border-radius: 50%;
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

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
