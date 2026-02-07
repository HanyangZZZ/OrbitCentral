import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api'
})

export const getItems = () => api.get('/items/')
export const createItem = (payload) => api.post('/items/', payload)

export default api
