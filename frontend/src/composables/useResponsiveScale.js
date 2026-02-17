import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable for responsive iframe scaling
 * @param {number} designWidth - The original design width (default: 1280)
 * @returns {Object} - { scale: Ref<number>, updateScale: Function }
 */
export function useResponsiveScale(designWidth = 1280) {
  const scale = ref(1)

  function updateScale() {
    const vw = window.innerWidth
    scale.value = vw < designWidth ? vw / designWidth : 1
  }

  onMounted(() => {
    updateScale()
    window.addEventListener('resize', updateScale)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateScale)
  })

  return { scale, updateScale }
}
