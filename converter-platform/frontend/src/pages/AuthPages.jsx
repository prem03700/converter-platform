import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileInput, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

function AuthForm({ mode }) {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const isLogin = mode === 'login'

  const [form, setForm] = useState({ email: '', password: '', fullName: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (isLogin) {
        await login(form.email, form.password)
      } else {
        await register(form.email, form.password, form.fullName)
      }
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50 flex items-center justify-center px-4">
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md space-y-8">
        {/* Logo */}
        <div className="text-center">
          <div className="w-12 h-12 rounded-2xl bg-brand-gradient flex items-center justify-center mx-auto mb-4">
            <FileInput className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold dark:text-white text-slate-900">
            {isLogin ? 'Welcome back' : 'Create your account'}
          </h1>
          <p className="text-sm dark:text-slate-400 text-slate-500 mt-1">
            {isLogin ? 'Sign in to your account to continue' : 'Free to get started, no credit card needed'}
          </p>
        </div>

        {/* Card */}
        <div className="dark:glass-card glass-card-light p-8 space-y-5">
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-xs font-medium dark:text-slate-400 text-slate-600 mb-1.5">
                  Full name
                </label>
                <input
                  type="text"
                  placeholder="Jane Smith"
                  value={form.fullName}
                  onChange={set('fullName')}
                  className="dark:input input-light"
                  autoComplete="name"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium dark:text-slate-400 text-slate-600 mb-1.5">
                Email address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={set('email')}
                required
                className="dark:input input-light"
                autoComplete="email"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium dark:text-slate-400 text-slate-600">
                  Password
                </label>
                {isLogin && (
                  <Link to="/forgot-password" className="text-xs text-brand-400 hover:text-brand-300">
                    Forgot password?
                  </Link>
                )}
              </div>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  placeholder={isLogin ? '••••••••' : 'At least 8 characters'}
                  value={form.password}
                  onChange={set('password')}
                  required
                  minLength={8}
                  className="dark:input input-light pr-10"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 dark:text-slate-500 text-slate-400"
                >
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading
                ? (isLogin ? 'Signing in…' : 'Creating account…')
                : (isLogin ? 'Sign in' : 'Create account')}
            </button>
          </form>

          <p className="text-center text-sm dark:text-slate-400 text-slate-500">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <Link
              to={isLogin ? '/register' : '/login'}
              className="text-brand-400 hover:text-brand-300 font-medium"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export function LoginPage() { return <AuthForm mode="login" /> }
export function RegisterPage() { return <AuthForm mode="register" /> }
