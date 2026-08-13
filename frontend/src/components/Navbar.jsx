import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  FileInput, Moon, Sun, Menu, X, User, LogOut,
  LayoutDashboard, History, Settings, ChevronDown
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, darkMode, toggleDarkMode } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  const navLinks = [
    { to: '/', label: 'Home' },
    { to: '/pricing', label: 'Pricing' },
    { to: '/docs', label: 'API Docs' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 dark:bg-surface-dark/80 bg-white/80 backdrop-blur-glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center">
              <FileInput className="w-4 h-4 text-white" />
            </div>
            <span className="hidden sm:block dark:text-white text-slate-900">
              Universal<span className="text-brand-500"> Converter</span>
            </span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className={`text-sm font-medium transition-colors ${
                  location.pathname === to
                    ? 'text-brand-500'
                    : 'dark:text-slate-400 text-slate-600 hover:text-brand-500'
                }`}
              >
                {label}
              </Link>
            ))}
          </div>

          {/* Right cluster */}
          <div className="flex items-center gap-3">
            {/* Dark mode toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg dark:text-slate-400 text-slate-500 hover:text-brand-500 hover:bg-white/10 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setProfileOpen((o) => !o)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl
                    dark:bg-white/10 bg-slate-100 hover:bg-slate-200 dark:hover:bg-white/20
                    dark:text-slate-200 text-slate-700 text-sm font-medium transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-brand-gradient flex items-center justify-center text-white text-xs">
                    {user.email[0].toUpperCase()}
                  </div>
                  <span className="hidden sm:block max-w-[100px] truncate">{user.full_name || user.email}</span>
                  <ChevronDown className="w-3 h-3" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-52 dark:bg-surface-card bg-white border dark:border-white/10 border-slate-200 rounded-xl shadow-lg overflow-hidden z-50">
                    <div className="px-4 py-3 border-b dark:border-white/10 border-slate-100">
                      <p className="text-xs dark:text-slate-400 text-slate-500">Signed in as</p>
                      <p className="text-sm font-medium dark:text-white text-slate-900 truncate">{user.email}</p>
                    </div>
                    {[
                      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
                      { to: '/history', icon: History, label: 'History' },
                      { to: '/settings', icon: Settings, label: 'Settings' },
                    ].map(({ to, icon: Icon, label }) => (
                      <Link
                        key={to}
                        to={to}
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm
                          dark:text-slate-300 text-slate-700
                          dark:hover:bg-white/10 hover:bg-slate-50 transition-colors"
                      >
                        <Icon className="w-4 h-4" />
                        {label}
                      </Link>
                    ))}
                    {user.is_admin && (
                      <Link
                        to="/admin"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm text-brand-400 dark:hover:bg-white/10 hover:bg-slate-50"
                      >
                        <User className="w-4 h-4" />
                        Admin Panel
                      </Link>
                    )}
                    <div className="border-t dark:border-white/10 border-slate-100">
                      <button
                        onClick={() => { setProfileOpen(false); handleLogout() }}
                        className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-400 dark:hover:bg-white/10 hover:bg-slate-50 transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Sign out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="btn-ghost text-sm hidden sm:block dark:text-slate-300 text-slate-600 hover:text-brand-500">
                  Sign in
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Get started
                </Link>
              </div>
            )}

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileOpen((o) => !o)}
              className="md:hidden p-2 rounded-lg dark:text-slate-400 text-slate-500"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t dark:border-white/10 border-slate-200 px-4 py-4 space-y-2">
          {navLinks.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className="block py-2 text-sm dark:text-slate-300 text-slate-700"
            >
              {label}
            </Link>
          ))}
          {!user && (
            <Link to="/login" onClick={() => setMobileOpen(false)} className="block py-2 text-sm dark:text-slate-300 text-slate-700">
              Sign in
            </Link>
          )}
        </div>
      )}
    </nav>
  )
}
