<template>
  <div class="top-bar">
    <div class="top-bar-left">
      <router-link to="/" class="brand-name">Orbit</router-link>
      <slot name="left-extra"></slot>
    </div>
    
    <SearchBar 
      v-if="showSearch" 
      v-model:aiEnabled="localAiEnabled"
      class="top-bar-search"
    />
    
    <div class="top-bar-right">
      <router-link to="/leaderboard" class="nav-link">Leaderboard</router-link>
      <router-link to="/discover" class="nav-link">Discover</router-link>
      <router-link to="/settings/favorites" class="nav-link">Favorites</router-link>
      
      <div v-if="showLocation" class="location-chip">
        <span>Location</span>
        <svg class="location-pin-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" stroke="#000" stroke-width="1.8" fill="none"/>
        </svg>
      </div>
      
      <ProfileDropdown />
      <slot name="right-extra"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import SearchBar from './SearchBar.vue'
import ProfileDropdown from './ProfileDropdown.vue'

const props = defineProps({
  showSearch: {
    type: Boolean,
    default: false
  },
  showLocation: {
    type: Boolean,
    default: true
  },
  aiEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:aiEnabled'])

const localAiEnabled = ref(props.aiEnabled)

watch(localAiEnabled, (val) => {
  emit('update:aiEnabled', val)
})

watch(() => props.aiEnabled, (val) => {
  localAiEnabled.value = val
})
</script>

<style scoped>
.top-bar {
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
  gap: 0.75rem;
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

.location-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  line-height: 1;
  color: #000;
  white-space: nowrap;
}

.location-pin-icon {
  width: 0.875rem;
  height: 0.875rem;
  flex-shrink: 0;
}

.top-bar-search {
  flex: 1;
  min-width: 0;
}

@media (min-width: 768px) {
  .nav-link { display: inline; }
  .top-bar {
    padding: 1.25rem 2rem 0.75rem;
    gap: 1rem;
    flex-wrap: nowrap;
  }
  .brand-name { font-size: 1.25rem; }
}

@media (min-width: 1024px) {
  .top-bar {
    padding: 1.5rem 5.25rem 0.75rem;
    gap: 1.5rem;
  }
  .brand-name { font-size: 1.375rem; }
  .top-bar-left { gap: 1.25rem; }
  .top-bar-right { gap: 1.5rem; }
}
</style>
