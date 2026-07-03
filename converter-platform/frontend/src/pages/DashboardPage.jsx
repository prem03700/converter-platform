import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Files, CheckCircle2, HardDrive, TrendingUp, History, ArrowRight } from 'lucide-react'
import Navbar from '../components/Navbar'
import UploadCard from '../components/UploadCard'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import { historyApi, convertApi } from '../api/client'
import { useAuth } from '../context/AuthContext'

function fmt_bytes(b) {
  if (b < 1024) return `${b} B`
  if (b < 1024 ** 2) return `${(b / 1024).toFixed(1)} KB`
  if (b < 1024 ** 3) return `${(b / 1024 ** 2).toFixed(1)} MB`
  return `${(b / 1024 ** 3).toFixed(2)} GB`
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)

  const loadStats = useCallback(async () => {
    try {
      const { data } = await historyApi.stats()
      setStats(data)
    } catch {
      // Non-critical — dashboard still usable without stats
    } finally {
      setLoadingStats(false)
    }
  }, [])

  useEffect(() => { loadStats() }, [loadStats])

  const downloadUrl = (conv) =>
    `${import.meta.env.VITE_API_URL || '/api/v1'}/convert/${conv.id}/download`

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold dark:text-white text-slate-900">
            Good to see you, {user?.full_name?.split(' ')[0] || 'there'} 👋
          </h1>
          <p className="dark:text-slate-400 text-slate-500 text-sm mt-1">
            Upload a file below or view your conversion history.
          </p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={Files}
            label="Total files"
            value={loadingStats ? '–' : stats?.total_files ?? 0}
            color="text-brand-400"
          />
          <StatCard
            icon={CheckCircle2}
            label="Conversions done"
            value={loadingStats ? '–' : stats?.completed_conversions ?? 0}
            color="text-green-400"
          />
          <StatCard
            icon={HardDrive}
            label="Storage used"
            value={loadingStats ? '–' : fmt_bytes(stats?.total_storage_bytes ?? 0)}
            color="text-purple-400"
          />
          <StatCard
            icon={TrendingUp}
            label="Favourite format"
            value={loadingStats ? '–' : (stats?.favorite_formats?.[0]?.toUpperCase() ?? '—')}
            sub={stats?.favorite_formats?.slice(1).join(', ').toUpperCase()}
            color="text-orange-400"
          />
        </div>

        {/* Upload section */}
        <div>
          <h2 className="text-lg font-semibold dark:text-white text-slate-900 mb-4">
            New conversion
          </h2>
          <UploadCard onConversionComplete={loadStats} />
        </div>

        {/* Recent activity */}
        {stats?.recent_activity?.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold dark:text-white text-slate-900">
                Recent activity
              </h2>
              <Link to="/history" className="flex items-center gap-1 text-sm text-brand-400 hover:text-brand-300">
                View all <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="dark:glass-card glass-card-light divide-y dark:divide-white/10 divide-slate-100 overflow-hidden">
              {stats.recent_activity.map((c) => (
                <div key={c.id} className="flex items-center gap-4 px-5 py-4">
                  <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center shrink-0">
                    <History className="w-4 h-4 text-white" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium dark:text-white text-slate-900 truncate">
                      → .{c.target_format.toUpperCase()}
                    </p>
                    <p className="text-xs dark:text-slate-400 text-slate-500">
                      {new Date(c.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <StatusBadge status={c.status} />
                  {c.status === 'completed' && (
                    <a
                      href={downloadUrl(c)}
                      download
                      className="text-xs text-brand-400 hover:text-brand-300 font-medium"
                    >
                      Download
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
