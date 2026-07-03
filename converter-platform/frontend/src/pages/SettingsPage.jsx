import { useState } from 'react'
import { CheckCircle2 } from 'lucide-react'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../api/client'

export default function SettingsPage() {
  const { user, darkMode, toggleDarkMode } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    setError(null)
    try {
      await userApi.update({ full_name: fullName })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8 space-y-8">
        <h1 className="text-2xl font-bold dark:text-white text-slate-900">Settings</h1>

        {/* Profile */}
        <section className="dark:glass-card glass-card-light p-6 space-y-5">
          <h2 className="text-base font-semibold dark:text-white text-slate-900">Profile</h2>
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="block text-xs font-medium dark:text-slate-400 text-slate-600 mb-1.5">
                Full name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="dark:input input-light"
              />
            </div>
            <div>
              <label className="block text-xs font-medium dark:text-slate-400 text-slate-600 mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="dark:input input-light opacity-60 cursor-not-allowed"
              />
              <p className="text-xs dark:text-slate-500 text-slate-400 mt-1">
                Email changes are not supported yet.
              </p>
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <div className="flex items-center gap-3">
              <button type="submit" disabled={saving} className="btn-primary text-sm">
                {saving ? 'Saving…' : 'Save changes'}
              </button>
              {saved && (
                <span className="flex items-center gap-1.5 text-sm text-green-400">
                  <CheckCircle2 className="w-4 h-4" /> Saved
                </span>
              )}
            </div>
          </form>
        </section>

        {/* Appearance */}
        <section className="dark:glass-card glass-card-light p-6 space-y-4">
          <h2 className="text-base font-semibold dark:text-white text-slate-900">Appearance</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm dark:text-slate-300 text-slate-700">Dark mode</p>
              <p className="text-xs dark:text-slate-500 text-slate-400">Toggle between light and dark theme</p>
            </div>
            <button
              onClick={toggleDarkMode}
              className={`relative w-11 h-6 rounded-full transition-colors ${
                darkMode ? 'bg-brand-600' : 'bg-slate-300 dark:bg-slate-600'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                  darkMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </section>

        {/* Account info */}
        <section className="dark:glass-card glass-card-light p-6 space-y-3">
          <h2 className="text-base font-semibold dark:text-white text-slate-900">Account</h2>
          {[
            ['Plan', user?.plan?.charAt(0).toUpperCase() + user?.plan?.slice(1)],
            ['Member since', user ? new Date(user.created_at).toLocaleDateString() : '—'],
            ['User ID', user?.id],
          ].map(([label, val]) => (
            <div key={label} className="flex justify-between text-sm">
              <span className="dark:text-slate-400 text-slate-500">{label}</span>
              <span className="dark:text-slate-200 text-slate-800 font-mono text-xs">{val}</span>
            </div>
          ))}
        </section>
      </main>
    </div>
  )
}
