<!--
  FilterBar.vue — Sort, Rating & Tag Filter Controls
  ─────────────────────────────────────────────────────────────────────────────
  Horizontal bar below the search results header on SearchPage.

  SECTIONS (left → right)
  1. Sort dropdown    — relevance, rating, newest, distance
  2. Rating slider    — 0–5 range slider to filter by minimum rating
  3. Tag pills        — suggested tags based on the current search
     (fetched by useSearchApi, passed as suggestedTags prop)

  DESIGN NOTE
  This is a "dumb" presentational component — it doesn't hold any filter
  state itself. Everything is driven by props from the parent (SearchPage),
  and user actions emit events back up:
    toggle-dropdown, select-sort, rating-change, clear-rating, toggle-tag

  INLINE SVG ICONS
  Sort/Star/Chevron/Check icons are tiny render-function components created
  with Vue's `h()` helper, keeping them lightweight and avoiding imports.

  MODULAR FLOW
    SearchPage (useFilterBar composable) ↔ FilterBar props/emits
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="filter-bar">
    <!-- Sort dropdown -->
    <div class="filter-group">
      <button class="filter-btn" @click="$emit('toggle-dropdown', 'sort')">
        <SortIcon /> Sort <ChevronIcon />
      </button>
      <div v-if="openDropdown === 'sort'" class="dropdown-panel sort-dropdown">
        <button
          v-for="opt in sortOptions" :key="opt.value"
          class="dropdown-item" :class="{ active: sortOrder === opt.value }"
          @click="$emit('select-sort', opt.value)"
        >
          {{ opt.label }}
          <CheckIcon v-if="sortOrder === opt.value" />
        </button>
      </div>
    </div>

    <!-- Rating dropdown -->
    <div class="filter-group">
      <button
        class="filter-btn" :class="{ 'has-value': minRating > 0 }"
        @click="$emit('toggle-dropdown', 'rating')"
      >
        <StarIcon /> Rating{{ minRating > 0 ? `: ${minRating}+` : '' }} <ChevronIcon />
      </button>
      <div v-if="openDropdown === 'rating'" class="dropdown-panel rating-dropdown">
        <div class="rating-header">
          <span class="rating-label">Rating</span>
          <span class="rating-value">{{ minRating > 0 ? `over ${minRating}` : 'Any' }}</span>
        </div>
        <input
          type="range" class="rating-slider"
          min="0" max="5" step="0.5" :value="minRating"
          @input="$emit('rating-change', $event)"
        />
        <div class="rating-ticks">
          <span>Any</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
        </div>
        <button v-if="minRating > 0" class="rating-clear" @click="$emit('clear-rating')">Clear</button>
      </div>
    </div>

    <div class="filter-divider" />

    <!-- Smart Tags -->
    <div v-if="suggestedTags.length" class="tag-filters">
      <button
        v-for="tag in suggestedTags" :key="tag.id"
        class="tag-toggle" :class="{ active: selectedTagIds.includes(tag.id) }"
        @click="$emit('toggle-tag', tag.id)"
      >
        {{ tag.name }}
        <span v-if="tag.usage_count" class="tag-count">{{ tag.usage_count }}</span>
      </button>
    </div>
    <span v-else-if="showNoTagsHint" class="no-tags-hint">No suggested filters</span>
  </div>
</template>

<script setup>
import { h } from 'vue'

defineProps({
  openDropdown:   { type: String,  default: null },
  sortOrder:      { type: String,  default: '' },
  sortOptions:    { type: Array,   required: true },
  minRating:      { type: Number,  default: 0 },
  suggestedTags:  { type: Array,   default: () => [] },
  selectedTagIds: { type: Array,   default: () => [] },
  showNoTagsHint: { type: Boolean, default: false },
})

defineEmits([
  'toggle-dropdown', 'select-sort',
  'rating-change', 'clear-rating', 'toggle-tag',
])

// Tiny inline SVG components to keep the template clean
const icon = (d, size = 14) => ({
  render: () => h('svg', {
    xmlns: 'http://www.w3.org/2000/svg', width: size, height: size,
    viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor',
    'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round',
  }, d.map(p => h('path', { d: p })))
})
const SortIcon    = icon(['m3 16 4 4 4-4', 'M7 20V4', 'm21 8-4-4-4 4', 'M17 4v16'])
const StarIcon    = icon(['M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 21 12 17.77 5.82 21 7 14.14l-5-4.87 6.91-1.01L12 2'])
const ChevronIcon = icon(['m6 9 6 6 6-6'], 12)
const CheckIcon   = icon(['M20 6 9 17l-5-5'])
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

/* ── Filter button ── */
.filter-group { position: relative; }
.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  white-space: nowrap;
}
.filter-btn:hover  { border-color: var(--color-primary); background: rgba(74,112,169,0.04); }
.filter-btn.has-value {
  border-color: var(--color-primary);
  background: rgba(74,112,169,0.08);
  color: var(--color-primary);
}

/* ── Dropdown ── */
.dropdown-panel {
  position: absolute; top: calc(100% + 6px); left: 0; z-index: 200;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--shadow-lg, 0 8px 28px rgba(15,23,42,0.12));
  overflow: hidden;
}
.sort-dropdown { min-width: 180px; }
.dropdown-item {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; padding: 10px 16px;
  background: none; border: none;
  color: var(--color-text-light, #475569); font-size: 13px;
  cursor: pointer; text-align: left;
  transition: background 0.1s, color 0.1s;
}
.dropdown-item:hover { background: rgba(74,112,169,0.06); color: var(--color-text); }
.dropdown-item.active { color: var(--color-primary); font-weight: 500; }

/* ── Rating panel ── */
.rating-dropdown { min-width: 260px; padding: 16px; }
.rating-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
.rating-label  { font-size: 14px; font-weight: 600; color: var(--color-text); }
.rating-value  { font-size: 13px; color: var(--color-text-muted); }
.rating-slider {
  -webkit-appearance: none; appearance: none;
  width: 100%; height: 6px; border-radius: 3px;
  background: var(--color-border); outline: none; cursor: pointer;
}
.rating-slider::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 20px; height: 20px; border-radius: 50%;
  background: #fff;
  border: 3px solid var(--color-primary);
  cursor: grab; transition: transform 0.1s;
  box-shadow: var(--shadow-sm);
}
.rating-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.rating-slider::-moz-range-thumb {
  width: 20px; height: 20px; border-radius: 50%;
  background: #fff;
  border: 3px solid var(--color-primary); cursor: grab;
}
.rating-ticks {
  display: flex; justify-content: space-between;
  margin-top: 6px; font-size: 11px; color: var(--color-text-muted);
}
.rating-clear {
  margin-top: 12px; width: 100%; padding: 6px;
  background: none; border: 1px solid var(--color-border);
  border-radius: 6px; color: var(--color-text-muted);
  font-size: 12px; cursor: pointer;
}
.rating-clear:hover { color: var(--color-text); border-color: var(--color-primary); }

/* ── Misc ── */
.filter-divider { width: 1px; height: 24px; background: var(--color-border); margin: 0 4px; }
.tag-filters { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.tag-toggle {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; font-size: 12px; white-space: nowrap; cursor: pointer;
  background: rgba(67,56,202,0.05); border: 1px solid var(--color-border-light, #c7d2fe);
  border-radius: 999px; color: var(--color-accent, #4338ca); transition: all 0.15s;
}
.tag-toggle:hover  { background: rgba(67,56,202,0.1); border-color: var(--color-accent); }
.tag-toggle.active { background: rgba(67,56,202,0.15); border-color: var(--color-accent); color: var(--color-accent); font-weight: 500; }
.tag-count   { font-size: 10px; opacity: 0.6; }
.no-tags-hint { font-size: 12px; color: var(--color-text-muted); }
</style>
