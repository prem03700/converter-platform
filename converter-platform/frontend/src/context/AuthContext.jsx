import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authApi, userApi } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem('theme')
    if (stored) return stored === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  // Apply / remove the 'dark' class on <html>
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const toggleDarkMode = useCallback(() => setDarkMode((d) => !d), [])

  // Hydrate current user on mount (silent fail = not logged in)
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { setLoading(false); return }
    userApi.me()
      .then(({ data }) => setUser(data))
      .catch(() => localStorage.clear())
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const { data: me } = await userApi.me()
    setUser(me)
    return me
  }, [])

  const register = useCallback(async (email, password, fullName) => {
    const { data } = await authApi.register(email, password, fullName)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const { data: me } = await userApi.me()
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    authApi.logout().catch(() => {})
    localStorage.clear()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, darkMode, toggleDarkMode, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
