<template>
  <VerifyEmailPage   v-if="page === 'verify-email'" />
  <ResetPasswordPage v-else-if="page === 'reset-password'" />
  <HomePage          v-else />
</template>

<script setup>
import { computed } from 'vue'
import HomePage          from './pages/HomePage.vue'
import VerifyEmailPage   from './pages/VerifyEmailPage.vue'
import ResetPasswordPage from './pages/ResetPasswordPage.vue'

const page = computed(() => {
  const path = window.location.pathname.replace(/^\/+|\/+$/g, '')
  if (path === 'verify-email')   return 'verify-email'
  if (path === 'reset-password') return 'reset-password'
  return 'home'
})
</script>
