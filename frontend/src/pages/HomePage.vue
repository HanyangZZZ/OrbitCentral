<template>
  <div class="portal">
    <header class="hero">
      <div>
        <h1>FBLC Data Portal</h1>
        <p>Manage your MySQL data through Django REST Framework APIs.</p>
      </div>
      <div class="hero-actions">
        <button type="button" class="btn ghost" @click="refreshAll">Refresh All</button>
        <span v-if="loading" class="status">Syncing...</span>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <section class="grid">
      <!-- ── Users ──────────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Users</h2>
        <form class="form" @submit.prevent="createUserRecord">
          <input v-model.trim="userForm.email" placeholder="Email" required />
          <input v-model.trim="userForm.password_hash" placeholder="Password" required />
          <select v-model="userForm.role">
            <option value="customer">Customer</option>
            <option value="merchant">Merchant</option>
            <option value="admin">Admin</option>
          </select>
          <label class="check">
            <input type="checkbox" v-model="userForm.is_verified_human" /> Verified human
          </label>
          <button class="btn" type="submit">Create user</button>
        </form>
        <ul class="list">
          <li v-for="user in users" :key="user.id">
            <strong>#{{ user.id }}</strong> {{ user.email }} · {{ user.role }}
          </li>
        </ul>
      </article>

      <!-- ── Profiles ───────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Profiles</h2>
        <form class="form" @submit.prevent="upsertProfileRecord">
          <input v-model.number="profileForm.user" type="number" min="1" placeholder="User ID" required />
          <input v-model.trim="profileForm.display_name" placeholder="Display name" />
          <input v-model.trim="profileForm.avatar_url" placeholder="Avatar URL" />
          <label class="check">
            <input type="checkbox" v-model="profileForm.high_contrast" /> High contrast
          </label>
          <label class="check">
            <input type="checkbox" v-model="profileForm.keyboard_only_nav" /> Keyboard only
          </label>
          <input v-model.number="profileForm.loyalty_points" type="number" min="0" placeholder="Loyalty points" />
          <button class="btn" type="submit">Upsert profile</button>
        </form>
        <ul class="list">
          <li v-for="profile in profiles" :key="profile.user">
            <strong>User #{{ profile.user }}</strong> {{ profile.display_name || 'No name' }}
          </li>
        </ul>
      </article>

      <!-- ── Categories ─────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Categories</h2>
        <form class="form" @submit.prevent="createCategoryRecord">
          <input v-model.trim="categoryForm.name" placeholder="Name" required />
          <input v-model.trim="categoryForm.slug" placeholder="Slug" required />
          <input v-model.trim="categoryForm.icon_name" placeholder="Icon" />
          <button class="btn" type="submit">Create category</button>
        </form>
        <ul class="list">
          <li v-for="category in categories" :key="category.id">
            <strong>#{{ category.id }}</strong> {{ category.name }} · {{ category.slug }}
          </li>
        </ul>
      </article>

      <!-- ── Businesses ─────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Businesses</h2>
        <form class="form" @submit.prevent="createBusinessRecord">
          <input v-model.trim="businessForm.name" placeholder="Name" required />
          <input v-model.number="businessForm.lat" type="number" step="0.000001" placeholder="Latitude" required />
          <input v-model.number="businessForm.lng" type="number" step="0.000001" placeholder="Longitude" required />
          <input v-model.number="businessForm.category" type="number" min="1" placeholder="Category ID" />
          <input v-model.trim="businessForm.contact_email" placeholder="Contact email" />
          <button class="btn" type="submit">Create business</button>
        </form>
        <ul class="list">
          <li v-for="business in businesses" :key="business.id">
            <strong>#{{ business.id }}</strong> {{ business.name }} · Rating {{ business.avg_rating }}
          </li>
        </ul>
      </article>

      <!-- ── Reviews ────────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Reviews</h2>
        <form class="form" @submit.prevent="createReviewRecord">
          <select v-model.number="reviewForm.business" required>
            <option disabled value="">Select business</option>
            <option v-for="business in businesses" :key="business.id" :value="business.id">
              #{{ business.id }} {{ business.name }}
            </option>
          </select>
          <input v-model.number="reviewForm.user" type="number" min="1" placeholder="User ID" />
          <input v-model.number="reviewForm.rating" type="number" min="1" max="5" placeholder="Rating" required />
          <input v-model.trim="reviewForm.content" placeholder="Content" />
          <button class="btn" type="submit">Add review</button>
        </form>
        <button class="btn ghost" type="button" @click="loadReviews">Load reviews</button>
        <ul class="list">
          <li v-for="review in reviews" :key="review.id">
            <strong>#{{ review.id }}</strong> Biz {{ review.business }} · {{ review.rating }}★
          </li>
        </ul>
      </article>

      <!-- ── Bookmarks ──────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Bookmarks</h2>
        <form class="form" @submit.prevent="createBookmarkRecord">
          <input v-model.number="bookmarkForm.user" type="number" min="1" placeholder="User ID" required />
          <input v-model.number="bookmarkForm.business" type="number" min="1" placeholder="Business ID" required />
          <button class="btn" type="submit">Create bookmark</button>
        </form>
        <ul class="list">
          <li v-for="bookmark in bookmarks" :key="bookmark.id">
            User {{ bookmark.user }} → Biz {{ bookmark.business }}
          </li>
        </ul>
      </article>

      <!-- ── Rewards ────────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Rewards</h2>
        <form class="form" @submit.prevent="createRewardRecord">
          <input v-model.number="rewardForm.provider_business" type="number" min="1" placeholder="Provider business ID" required />
          <input v-model.number="rewardForm.trigger_business" type="number" min="1" placeholder="Trigger business ID" />
          <input v-model.trim="rewardForm.title" placeholder="Title" required />
          <input v-model.trim="rewardForm.reward_type" placeholder="Type (dividend)" />
          <input v-model.number="rewardForm.discount_val" type="number" step="0.01" placeholder="Discount value" />
          <button class="btn" type="submit">Create reward</button>
        </form>
        <ul class="list">
          <li v-for="reward in rewards" :key="reward.id">
            <strong>#{{ reward.id }}</strong> {{ reward.title }} · {{ reward.reward_type || 'standard' }}
          </li>
        </ul>
      </article>

      <!-- ── Coupons ────────────────────────────────────────────────────── -->
      <article class="card">
        <h2>Coupons</h2>
        <form class="form" @submit.prevent="createCouponRecord">
          <input v-model.number="couponForm.user" type="number" min="1" placeholder="User ID" required />
          <input v-model.number="couponForm.reward" type="number" min="1" placeholder="Reward ID" required />
          <select v-model="couponForm.status">
            <option value="locked">Locked</option>
            <option value="unlocked">Unlocked</option>
            <option value="redeemed">Redeemed</option>
          </select>
          <button class="btn" type="submit">Create coupon</button>
        </form>
        <ul class="list">
          <li v-for="coupon in coupons" :key="coupon.id">
            <strong>#{{ coupon.id }}</strong> User {{ coupon.user }} · {{ coupon.status }}
          </li>
        </ul>
      </article>

      <!-- ── Automation Logs ────────────────────────────────────────────── -->
      <article class="card">
        <h2>Automation Logs</h2>
        <form class="form" @submit.prevent="createLogRecord">
          <input v-model.number="logForm.business" type="number" min="1" placeholder="Business ID" />
          <input v-model.trim="logForm.action_type" placeholder="Action type" />
          <input v-model.trim="logForm.status" placeholder="Status" />
          <button class="btn" type="submit">Create log</button>
        </form>
        <ul class="list">
          <li v-for="log in logs" :key="log.id">
            <strong>#{{ log.id }}</strong> {{ log.action_type || 'Action' }} · {{ log.status || 'Status' }}
          </li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import {
  createAutomationLog,
  createBookmark,
  createBusiness,
  createCategory,
  createCoupon,
  createReview,
  createReward,
  createUser,
  getAutomationLogs,
  getBookmarks,
  getBusinesses,
  getCategories,
  getCoupons,
  getProfiles,
  getReviews,
  getRewards,
  getUsers,
  upsertProfile
} from '../api/client'

const loading = ref(false)
const error = ref('')

const users = ref([])
const profiles = ref([])
const categories = ref([])
const businesses = ref([])
const reviews = ref([])
const bookmarks = ref([])
const rewards = ref([])
const coupons = ref([])
const logs = ref([])

const userForm = ref({
  email: '',
  password_hash: '',
  role: 'customer',
  is_verified_human: false
})

const profileForm = ref({
  user: '',
  display_name: '',
  avatar_url: '',
  high_contrast: false,
  keyboard_only_nav: false,
  loyalty_points: 0
})

const categoryForm = ref({
  name: '',
  slug: '',
  icon_name: ''
})

const businessForm = ref({
  name: '',
  lat: 37.7749,
  lng: -122.4194,
  category: '',
  contact_email: ''
})

const reviewForm = ref({
  business: '',
  user: '',
  rating: 5,
  content: ''
})

const bookmarkForm = ref({
  user: '',
  business: ''
})

const rewardForm = ref({
  provider_business: '',
  trigger_business: '',
  title: '',
  reward_type: 'dividend',
  discount_val: ''
})

const couponForm = ref({
  user: '',
  reward: '',
  status: 'locked'
})

const logForm = ref({
  business: '',
  action_type: '',
  status: ''
})

// ── Data fetching ─────────────────────────────────────────────────────────────
// DRF paginated responses: { count, next, previous, results }
const extractResults = (response) => response.data.results ?? []

const refreshAll = async () => {
  loading.value = true
  error.value = ''
  try {
    const [
      usersRes,
      profilesRes,
      categoriesRes,
      businessesRes,
      bookmarksRes,
      rewardsRes,
      couponsRes,
      logsRes
    ] = await Promise.all([
      getUsers(),
      getProfiles(),
      getCategories(),
      getBusinesses(),
      getBookmarks(),
      getRewards(),
      getCoupons(),
      getAutomationLogs()
    ])

    users.value = extractResults(usersRes)
    profiles.value = extractResults(profilesRes)
    categories.value = extractResults(categoriesRes)
    businesses.value = extractResults(businessesRes)
    bookmarks.value = extractResults(bookmarksRes)
    rewards.value = extractResults(rewardsRes)
    coupons.value = extractResults(couponsRes)
    logs.value = extractResults(logsRes)
  } catch (err) {
    error.value = 'Unable to reach the backend. Is Django running?'
  } finally {
    loading.value = false
  }
}

const loadReviews = async () => {
  const businessId = Number(reviewForm.value.business)
  if (!businessId) {
    error.value = 'Select a business to load reviews.'
    return
  }
  try {
    const response = await getReviews({ business: businessId })
    reviews.value = extractResults(response)
  } catch (err) {
    error.value = 'Failed to load reviews.'
  }
}

// ── Create helpers ────────────────────────────────────────────────────────────
const createUserRecord = async () => {
  try {
    await createUser({ ...userForm.value })
    userForm.value = { email: '', password_hash: '', role: 'customer', is_verified_human: false }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create user.'
  }
}

const upsertProfileRecord = async () => {
  try {
    await upsertProfile({
      ...profileForm.value,
      user: Number(profileForm.value.user)
    })
    profileForm.value = {
      user: '',
      display_name: '',
      avatar_url: '',
      high_contrast: false,
      keyboard_only_nav: false,
      loyalty_points: 0
    }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to upsert profile.'
  }
}

const createCategoryRecord = async () => {
  try {
    await createCategory({ ...categoryForm.value })
    categoryForm.value = { name: '', slug: '', icon_name: '' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create category.'
  }
}

const createBusinessRecord = async () => {
  try {
    await createBusiness({
      ...businessForm.value,
      category: businessForm.value.category ? Number(businessForm.value.category) : null
    })
    businessForm.value = { name: '', lat: 37.7749, lng: -122.4194, category: '', contact_email: '' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create business.'
  }
}

const createReviewRecord = async () => {
  const businessId = Number(reviewForm.value.business)
  if (!businessId) {
    error.value = 'Select a business to add a review.'
    return
  }
  try {
    await createReview({
      business: businessId,
      user: reviewForm.value.user ? Number(reviewForm.value.user) : null,
      rating: Number(reviewForm.value.rating),
      content: reviewForm.value.content
    })
    reviewForm.value = { business: businessId, user: '', rating: 5, content: '' }
    await loadReviews()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create review.'
  }
}

const createBookmarkRecord = async () => {
  try {
    await createBookmark({
      user: Number(bookmarkForm.value.user),
      business: Number(bookmarkForm.value.business)
    })
    bookmarkForm.value = { user: '', business: '' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create bookmark.'
  }
}

const createRewardRecord = async () => {
  try {
    await createReward({
      ...rewardForm.value,
      provider_business: Number(rewardForm.value.provider_business),
      trigger_business: rewardForm.value.trigger_business ? Number(rewardForm.value.trigger_business) : null
    })
    rewardForm.value = { provider_business: '', trigger_business: '', title: '', reward_type: 'dividend', discount_val: '' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create reward.'
  }
}

const createCouponRecord = async () => {
  try {
    await createCoupon({
      ...couponForm.value,
      user: Number(couponForm.value.user),
      reward: Number(couponForm.value.reward)
    })
    couponForm.value = { user: '', reward: '', status: 'locked' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create coupon.'
  }
}

const createLogRecord = async () => {
  try {
    await createAutomationLog({
      business: logForm.value.business ? Number(logForm.value.business) : null,
      action_type: logForm.value.action_type,
      status: logForm.value.status
    })
    logForm.value = { business: '', action_type: '', status: '' }
    await refreshAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create log.'
  }
}

onMounted(() => {
  refreshAll()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
</style>

<style scoped>
.portal {
  min-height: 100vh;
  padding: 40px clamp(20px, 4vw, 48px) 64px;
  background: radial-gradient(circle at 10% 10%, #0f1c2e 0%, #0a1220 40%, #060b14 100%);
  color: #e2e8f0;
  font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 28px;
}

.hero h1 {
  margin: 0 0 6px;
  font-size: 30px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero p {
  margin: 0;
  color: #94a3b8;
}

.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status {
  font-size: 12px;
  color: #fbbf24;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.card {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 18px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 12px 30px rgba(2, 6, 23, 0.4);
}

.card h2 {
  margin: 0;
  font-size: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #e2e8f0;
}

.form {
  display: grid;
  gap: 8px;
}

.form input,
.form select {
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  padding: 10px 12px;
  color: #e2e8f0;
  font-size: 13px;
}

.form input::placeholder {
  color: #64748b;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #38bdf8, #6366f1);
  color: #0b1120;
  font-weight: 600;
  cursor: pointer;
}

.btn.ghost {
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
}

.check {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: #cbd5f5;
}

.error {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  padding: 12px 16px;
  border-radius: 12px;
  color: #fecaca;
  margin-bottom: 18px;
}

@media (max-width: 720px) {
  .hero h1 {
    font-size: 22px;
  }
}
</style>
