<template>
  <div class="container">
    <header>
      <h1>Dynamic Sorting</h1>
      <p>Sort by rating or category and the UI updates instantly.</p>
    </header>

    <section class="controls">
      <label>
        Sort by
        <select v-model="sortKey">
          <option value="rating">Rating</option>
          <option value="category">Category</option>
        </select>
      </label>

      <button class="order" type="button" @click="toggleSortOrder">
        Order: {{ sortOrderLabel }}
      </button>

      <button class="refresh" type="button" @click="fetchItems">
        Refresh
      </button>
    </section>

    <form class="form" @submit.prevent="handleCreate">
      <input
        v-model.trim="form.name"
        class="input"
        type="text"
        placeholder="Name"
        required
      />
      <input
        v-model.number="form.rating"
        class="input"
        type="number"
        min="0"
        max="5"
        step="0.1"
        placeholder="Rating"
        required
      />
      <input
        v-model.trim="form.category"
        class="input"
        type="text"
        placeholder="Category"
        required
      />
      <button class="create" type="submit">Add item</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <ul class="items">
      <li v-for="item in sortedItems" :key="item.id">
        <div class="title">{{ item.name }}</div>
        <div class="meta">
          Rating: {{ item.rating }} · Category: {{ item.category }}
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { createItem, getItems } from './api/client'

const items = ref([])
const sortKey = ref('rating')
const sortOrder = ref('desc')
const error = ref('')
const form = ref({
  name: '',
  rating: 4.0,
  category: 'A'
})

const sortOrderLabel = computed(() =>
  sortOrder.value === 'asc' ? 'Ascending' : 'Descending'
)

const sortedItems = computed(() => {
  const sorted = [...items.value].sort((a, b) => {
    const aValue = a[sortKey.value]
    const bValue = b[sortKey.value]

    if (aValue === bValue) return 0

    if (sortKey.value === 'rating') {
      return aValue - bValue
    }

    return String(aValue).localeCompare(String(bValue))
  })

  return sortOrder.value === 'asc' ? sorted : sorted.reverse()
})

const fetchItems = async () => {
  try {
    const response = await getItems()
    items.value = response.data.items ?? []
    error.value = ''
  } catch (error) {
    items.value = []
    error.value = 'Unable to reach the backend. Is Django running on port 8000?'
  }
}

const handleCreate = async () => {
  try {
    await createItem({
      name: form.value.name,
      rating: form.value.rating,
      category: form.value.category
    })
    form.value = { name: '', rating: 4.0, category: 'A' }
    await fetchItems()
  } catch (error) {
    error.value = 'Failed to create item on the backend.'
  }
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

fetchItems()
</script>
