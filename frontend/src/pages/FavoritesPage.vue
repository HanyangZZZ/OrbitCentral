<template>
  <section class="favorites-page">
    <TopBar :show-search="true" v-model:ai-enabled="aiEnabled" />

    <div
      class="figma-frame-wrap"
      :style="{ height: (900 * scale) + 'px' }"
    >
      <iframe
        class="figma-frame"
        src="/figma-favorites-page/index.html"
        title="Favorites page design"
        :style="{ transform: 'scale(' + scale + ')' }"
      ></iframe>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { TopBar } from '@/components'
import { useResponsiveScale } from '@/composables'

const aiEnabled = ref(false)
const { scale } = useResponsiveScale(1280)
</script>

<style scoped>
.favorites-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 0;
  background: white;
  overflow-x: hidden;
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
  transform-origin: top left;
}
</style>
