/**
 * router/index.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Application Router — single source of truth for every navigable page.
 *
 * HOW IT WORKS
 * 1. Each route is lazy-loaded with `() => import(…)` so the browser only
 *    downloads a page's code when the user actually visits it.
 * 2. Routes that need a logged-in user carry `meta: { requiresAuth: true }`.
 * 3. A global navigation guard (`beforeEach`) runs before every route change:
 *    – If the target route requires auth AND there's no saved JWT token,
 *      the user is redirected to /login with a `?redirect=` query so they
 *      land back on the intended page after logging in.
 *
 * MODULAR FLOW
 *   App boots → createRouter() builds the route table → beforeEach guard
 *   protects private pages → lazy-loaded page components render inside
 *   <RouterView /> (see App.vue).
 * ─────────────────────────────────────────────────────────────────────────────
 */
import { createRouter, createWebHistory } from 'vue-router'
import { getSavedToken } from '@/api/core'

/* ── Route Definitions ────────────────────────────────────────────────────── */
const routes = [
  // ── Public pages (no auth needed) ───────────────────────────────────────
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/HomePage.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/RegisterPage.vue')
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('@/pages/VerifyEmailPage.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/pages/ResetPasswordPage.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/pages/SearchPage.vue')
  },
  {
    path: '/business/:id',           // Dynamic segment — id passed as a prop
    name: 'BusinessDetail',
    component: () => import('@/pages/BusinessDetailPage.vue'),
    props: true                      // Vue auto-injects :id as a component prop
  },

  // ── Auth-required pages ────────────────────────────────────────────────
  {
    path: '/bookmarks',
    name: 'Bookmarks',
    component: () => import('@/pages/BookmarksPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/coupons',
    name: 'Coupons',
    component: () => import('@/pages/CouponsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/missions',
    name: 'Missions',
    component: () => import('@/pages/MissionsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/ProfilePage.vue'),
    meta: { requiresAuth: true }
  },

  // ── Info / utility pages ───────────────────────────────────────────────
  {
    path: '/about',
    name: 'About',
    component: () => import('@/pages/AboutPage.vue')
  },
  {
    path: '/icons',
    name: 'IconLibrary',
    component: () => import('@/pages/IconLibraryPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ── Navigation guard — redirect unauthenticated users to Login ───────────
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !getSavedToken()) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
})

export default router
