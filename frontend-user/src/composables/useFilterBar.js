/**
 * useFilterBar.js — Filter Dropdown Logic
 * ==========================================
 * PURPOSE:
 *   Manages the Sort / Rating / Tag dropdown state on the Search page.
 *   Handles which dropdown is open, tracks user selections, and
 *   triggers data re-fetches when filters change.
 *
 * MODULAR LOGIC:
 *   Extracts all filter UI logic from the FilterBar component so the
 *   component template stays clean. The component renders, this
 *   composable manages the behavior.
 *
 * KEY CONCEPTS:
 *   - Only one dropdown can be open at a time (toggling one closes others)
 *   - onFilterChange callback is called whenever a filter changes,
 *     letting the parent (SearchPage) know to re-fetch data
 */
import { ref } from 'vue'

export function useFilterBar(state, { onFilterChange }) {
  const openDropdown = ref(null) // 'sort' | 'rating' | null

  function toggleDropdown(name) {
    openDropdown.value = openDropdown.value === name ? null : name
  }

  function closeDropdowns() {
    openDropdown.value = null
  }

  function selectSort(value) {
    state.sortOrder.value = value
    openDropdown.value = null
    onFilterChange()
  }

  function onRatingChange(e) {
    state.minRating.value = parseFloat(e.target.value)
  }

  function toggleTag(tagId) {
    const ids = state.selectedTagIds.value
    const idx = ids.indexOf(tagId)
    idx >= 0 ? ids.splice(idx, 1) : ids.push(tagId)
    onFilterChange()
  }

  return {
    openDropdown,
    toggleDropdown,
    closeDropdowns,
    selectSort,
    onRatingChange,
    toggleTag,
  }
}
