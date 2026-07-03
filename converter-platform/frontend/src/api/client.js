import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000, // 60 s — file uploads + conversions can be slow
})

// ── Attach access token to every outgoing request ─────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Auto-refresh on 401 then retry the original request once ─────────────
let isRefreshing = false
let refreshQueue = [] // callbacks waiting for the new token

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      // No refresh token — force logout
      localStorage.clear()
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({ resolve, reject })
      }).then((token) => {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
      const newAccess = data.access_token
      localStorage.setItem('access_token', newAccess)
      localStorage.setItem('refresh_token', data.refresh_token)
      api.defaults.headers.common.Authorization = `Bearer ${newAccess}`
      refreshQueue.forEach(({ resolve }) => resolve(newAccess))
      refreshQueue = []
      original.headers.Authorization = `Bearer ${newAccess}`
      return api(original)
    } catch {
      refreshQueue.forEach(({ reject }) => reject(error))
      refreshQueue = []
      localStorage.clear()
      window.location.href = '/login'
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  }
)

export default api

// ── Typed helpers ─────────────────────────────────────────────────────────
export const authApi = {
  register: (email, password, fullName) =>
    api.post('/auth/register', { email, password, full_name: fullName }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  refresh: (refreshToken) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: () => api.post('/auth/logout'),
}

export const userApi = {
  me: () => api.get('/users/me'),
  update: (data) => api.patch('/users/me', data),
}

export const filesApi = {
  upload: (file, onProgress) =>
    api.post('/files/upload', (() => { const f = new FormData(); f.append('file', file); return f })(), {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / e.total)),
    }),
  list: (skip = 0, limit = 50) => api.get(`/files?skip=${skip}&limit=${limit}`),
  delete: (id) => api.delete(`/files/${id}`),
  downloadUrl: (id) => `${BASE_URL}/files/${id}/download`,
  previewUrl: (id) => `${BASE_URL}/files/${id}/preview`,
}

export const convertApi = {
  supportedTargets: (fileId) => api.get(`/convert/supported-targets/${fileId}`),
  convert: (fileId, targetFormat, aiOptions = null) =>
    api.post('/convert', { file_id: fileId, target_format: targetFormat, ai_options: aiOptions }),
  status: (id) => api.get(`/convert/${id}/status`),
  cancel: (id) => api.post(`/convert/${id}/cancel`),
  downloadUrl: (id) => `${BASE_URL}/convert/${id}/download`,
}

export const historyApi = {
  list: (skip = 0, limit = 50) => api.get(`/history?skip=${skip}&limit=${limit}`),
  stats: () => api.get('/history/stats'),
}

export const adminApi = {
  users: () => api.get('/admin/users'),
  stats: () => api.get('/admin/statistics'),
  health: () => api.get('/admin/system-health'),
  disableUser: (id) => api.patch(`/admin/users/${id}/disable`),
  enableUser: (id) => api.patch(`/admin/users/${id}/enable`),
}
