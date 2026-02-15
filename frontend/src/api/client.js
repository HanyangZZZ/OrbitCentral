import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})

export const getItems = () => api.get('/items/')
export const createItem = (payload) => api.post('/items/', payload)
export const searchVibe = (query) => api.post('/search/vibe/', { query })
export const sortHighestRated = (payload = {}) => api.post('/businesses/sort/', { sort: 'highest_rated', ...payload })
export const getBookmarkStatus = (payload = {}) => api.post('/bookmarks/status/', payload)
export const toggleBookmark = (payload = {}) => api.post('/bookmarks/toggle/', payload)
export const getGroupedBookmarks = (payload = {}) => api.post('/bookmarks/grouped/', payload)

export default api
