<template>
  <div class="search-bar" :class="{ 'ai-on': aiEnabled }">
    <span class="search-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="11" cy="11" r="6.5" stroke="#0f172a" stroke-width="2" />
        <path d="M16.5 16.5L21 21" stroke="#0f172a" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>
    <input 
      class="search-input" 
      type="text" 
      :placeholder="placeholder"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      aria-label="Search" 
    />
    <div class="ai-toggle" aria-label="Ask AI">
      <span>Ask AI</span>
      <button
        class="toggle-switch"
        type="button"
        role="switch"
        :aria-checked="aiEnabled"
        @click="$emit('update:aiEnabled', !aiEnabled)"
      >
        <span class="toggle-knob" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  aiEnabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Search'
  }
})

defineEmits(['update:modelValue', 'update:aiEnabled'])
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  background: #f8f8f8;
  border-radius: 0.75rem;
  padding: 0.625rem 1rem;
}

.search-bar.ai-on {
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

.search-bar.ai-on .toggle-switch {
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

.search-bar.ai-on .toggle-knob {
  transform: translateX(1rem);
}
</style>
