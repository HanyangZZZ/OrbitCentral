<!--
  CategorySidebar.vue — Collapsible Category Navigation
  ─────────────────────────────────────────────────────────────────────────────
  Left sidebar on the SearchPage showing a parent → children category tree.

  HOW IT WORKS
  1. On mount, fetches all categories from the API (`getCategories`).
  2. Builds a tree: parents (parent === null) each get their children nested.
  3. Clicking a parent filters by that category (emits update:modelValue).
  4. The chevron button toggles children visibility with a slide animation.

  ICON SYSTEM
  The API returns Material Icon names like "restaurant" or "theater_comedy".
  This component maps those names to inline SVG strings via a local `iconMap`.
  The `iconFor()` function does exact match → partial match → default fallback.

  PROPS
  • modelValue — currently selected category ID (null = "All Businesses").

  MODULAR FLOW
    API categories → computed tree → template renders parent/child buttons
    → user click → emits modelValue → SearchPage reacts to the filter change
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <aside class="sidebar">
    <h2 class="sidebar-title">Categories</h2>

    <div v-if="loading" class="sidebar-loading">Loading...</div>

    <nav v-else class="category-nav">
      <!-- "All" option -->
      <button
        class="cat-item parent"
        :class="{ active: !modelValue }"
        @click="$emit('update:modelValue', null)"
      >
        <span class="cat-icon" v-html="iconFor('all')"></span>
        <span class="cat-name">All Businesses</span>
      </button>

      <!-- Parent categories with their children -->
      <div v-for="parent in tree" :key="parent.id" class="cat-group">
        <div class="cat-parent-row">
          <button
            class="cat-item parent"
            :class="{ active: modelValue === parent.id }"
            @click="$emit('update:modelValue', parent.id)"
          >
            <span class="cat-icon" v-html="iconFor(parent.icon_name)"></span>
            <span class="cat-name">{{ parent.name }}</span>
          </button>
          <button
            v-if="parent.children.length"
            class="expand-btn"
            :class="{ expanded: expandedIds.has(parent.id) }"
            @click.stop="toggleExpand(parent.id)"
            :title="expandedIds.has(parent.id) ? 'Collapse' : 'Expand'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
        </div>

        <Transition name="children-slide">
          <div v-if="expandedIds.has(parent.id)" class="cat-children">
            <button
              v-for="child in parent.children"
              :key="child.id"
              class="cat-item child"
              :class="{ active: modelValue === child.id }"
              @click="$emit('update:modelValue', child.id)"
            >
              <span class="cat-name">{{ child.name }}</span>
            </button>
          </div>
        </Transition>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getCategories } from '@/api/client'

defineProps({
  /** Currently selected category ID (null = all) */
  modelValue: { type: [Number, null], default: null }
})

defineEmits(['update:modelValue'])

const categories = ref([])
const loading = ref(true)
const expandedIds = reactive(new Set())

// Build parent → children tree from the flat API response
const tree = computed(() => {
  const parents = categories.value.filter(c => c.parent === null)
  return parents.map(p => ({
    ...p,
    children: categories.value.filter(c => c.parent === p.id)
  }))
})

function toggleExpand(parentId) {
  if (expandedIds.has(parentId)) {
    expandedIds.delete(parentId)
  } else {
    expandedIds.add(parentId)
  }
}

// Simple SVG icons mapping for icon_name values
// API returns Material Icon names like "theater_comedy", "storefront", "favorite", "home_repair_service", "restaurant"
const iconMap = {
  all: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  // API icon_name values
  restaurant: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
  theater_comedy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8h20"/><path d="M8 4v4"/><path d="M16 4v4"/><polygon points="10,11 10,18 16,14.5"/></svg>',
  storefront: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  favorite: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v4"/><path d="M12 19v4"/><path d="M4.22 4.22l2.83 2.83"/><path d="M16.95 16.95l2.83 2.83"/><path d="M1 12h4"/><path d="M19 12h4"/><path d="M4.22 19.78l2.83-2.83"/><path d="M16.95 7.05l2.83-2.83"/></svg>',
  home_repair_service: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
  // Slug-based fallbacks
  entertainment: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8h20"/><path d="M8 4v4"/><path d="M16 4v4"/><polygon points="10,11 10,18 16,14.5"/></svg>',
  retail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  services: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v4"/><path d="M12 19v4"/><path d="M4.22 4.22l2.83 2.83"/><path d="M16.95 16.95l2.83 2.83"/><path d="M1 12h4"/><path d="M19 12h4"/><path d="M4.22 19.78l2.83-2.83"/><path d="M16.95 7.05l2.83-2.83"/></svg>',
  coffee: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8z"/><path d="M6 2v3"/><path d="M10 2v3"/><path d="M14 2v3"/></svg>',
  shopping: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  health: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  fitness: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6.5 6.5a3.5 3.5 0 1 0 7 0 3.5 3.5 0 0 0-7 0z"/><path d="M2 21c0-3.9 3.1-7 7-7h2a7 7 0 0 1 7 7"/><path d="M17.5 3.5l-1.5 1.5"/><path d="M20.5 6.5l-1.5 1.5"/><path d="M17.5 9.5l3-3"/></svg>',
  beauty: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2a7 7 0 0 0-7 7c0 3.9 3.1 7 7 7s7-3.1 7-7a7 7 0 0 0-7-7z"/><path d="M12 16v6"/><path d="M9 22h6"/></svg>',
  education: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  nightlife: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  bar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 22h8"/><path d="M12 11v11"/><path d="M19 3l-7 8-7-8z"/></svg>',
  grocery: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>',
  automotive: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 17h14v-5H5v5z"/><path d="M5 12l2-5h10l2 5"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/></svg>',
  pets: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="4" r="2"/><circle cx="4" cy="8" r="2"/><circle cx="18" cy="8" r="2"/><circle cx="6" cy="15" r="2"/><circle cx="16" cy="15" r="2"/><path d="M8.5 17.5c1.5 2.5 5.5 2.5 7 0 1.5-2.5-1-5-3.5-5s-5 2.5-3.5 5z"/></svg>',
  default: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
}

function iconFor(name) {
  if (!name) return iconMap.default
  const lower = name.toLowerCase()
  // Exact match
  if (iconMap[lower]) return iconMap[lower]
  // Partial match: check if key is in icon_name OR icon_name is in key
  const key = Object.keys(iconMap).find(k =>
    lower.includes(k) || k.includes(lower)
  )
  return key ? iconMap[key] : iconMap.default
}

onMounted(async () => {
  try {
    const { data } = await getCategories()
    categories.value = data.results ?? []
  } catch (err) {
    console.error('Failed to load categories:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  padding: 20px 0;
  border-right: 1px solid var(--color-border);
  height: calc(100vh - 65px);
  overflow-y: auto;
  position: sticky;
  top: 65px;
  background: var(--color-surface);
}

.sidebar-title {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', system-ui, sans-serif;
  font-size: 13px;
  font-weight: 300;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  padding: 0 20px 12px;
}

.sidebar-loading {
  padding: 20px;
  color: var(--color-text-muted);
  font-size: 13px;
}

.category-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cat-group {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.cat-parent-row {
  display: flex;
  align-items: center;
}

.cat-parent-row .cat-item {
  flex: 1;
}

.expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-right: 10px;
  background: none;
  border: none;
  border-radius: 6px;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: transform 0.2s ease, background 0.15s, color 0.15s;
  flex-shrink: 0;
}

.expand-btn:hover {
  background: rgba(74, 112, 169, 0.08);
  color: var(--color-primary);
}

.expand-btn.expanded {
  transform: rotate(180deg);
}

.cat-children {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

/* Children slide transition */
.children-slide-enter-active {
  transition: all 0.25s ease-out;
  max-height: 500px;
}
.children-slide-leave-active {
  transition: all 0.2s ease-in;
  max-height: 500px;
}
.children-slide-enter-from {
  opacity: 0;
  max-height: 0;
}
.children-slide-enter-to {
  opacity: 1;
  max-height: 500px;
}
.children-slide-leave-from {
  opacity: 1;
  max-height: 500px;
}
.children-slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.cat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 20px;
  background: none;
  border: none;
  color: var(--color-text-light, #475569);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', system-ui, sans-serif;
  font-size: 14px;
  font-weight: 300;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  border-radius: 0;
}

.cat-item:hover {
  background: rgba(74, 112, 169, 0.06);
  color: var(--color-text);
}

.cat-item.active {
  background: rgba(74, 112, 169, 0.1);
  color: var(--color-primary);
  font-weight: 400;
}

.cat-item.parent {
  font-weight: 300;
}

.cat-item.child {
  padding-left: 50px;
  font-size: 13px;
}

.cat-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: currentColor;
}

.cat-icon :deep(svg) {
  width: 100%;
  height: 100%;
}
</style>
