<template>
  <section class="about-us-page">
    <TopBar :show-search="false" :show-location="false" />

    <div class="about-content">
      <h1>About Us</h1>
      <p>Welcome to Orbit — Your City, Personalized.</p>
    </div>
  </section>
</template>

<script setup>
import { TopBar } from '@/components'
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
