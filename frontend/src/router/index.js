import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import DiscoverPage from '../pages/DiscoverPage.vue'
import AboutUsPage from '../pages/AboutUsPage.vue'
import UserSettingsPage from '../pages/UserSettingsPage.vue'
import FavoritesPage from '../pages/FavoritesPage.vue'
import BusinessDetailsPage from '../pages/BusinessDetailsPage.vue'
import LeaderboardPage from '../pages/LeaderboardPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/discover', name: 'discover', component: DiscoverPage },
  { path: '/about', name: 'about', component: AboutUsPage },
  { path: '/settings', name: 'settings', component: UserSettingsPage },
  { path: '/settings/favorites', name: 'favorites', component: FavoritesPage },
  { path: '/leaderboard', name: 'leaderboard', component: LeaderboardPage },
  { path: '/business/:slug', name: 'business', component: BusinessDetailsPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
