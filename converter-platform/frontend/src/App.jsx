import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute, AdminRoute, GuestRoute } from './components/RouteGuards'
import HomePage from './pages/HomePage'
import { LoginPage, RegisterPage } from './pages/AuthPages'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'
import SettingsPage from './pages/SettingsPage'
import AdminPage from './pages/AdminPage'
import PricingPage from './pages/PricingPage'
import DocsPage from './pages/DocsPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/"        element={<HomePage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/docs"    element={<DocsPage />} />

        {/* Guest only (redirect to dashboard if logged in) */}
        <Route element={<GuestRoute />}>
          <Route path="/login"    element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected — must be logged in */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/history"   element={<HistoryPage />} />
          <Route path="/settings"  element={<SettingsPage />} />
        </Route>

        {/* Admin only */}
        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<AdminPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  )
}
