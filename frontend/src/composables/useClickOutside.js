import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable for handling click outside detection
 * @param {Function} callback - Function to call when clicking outside
 * @returns {Object} - { targetRef: Ref }
 */
export function useClickOutside(callback) {
  const targetRef = ref(null)

  function handleClickOutside(e) {
    if (targetRef.value && !targetRef.value.contains(e.target)) {
      callback()
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleClickOutside)
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })

  return { targetRef }
}
