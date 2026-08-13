import { useEffect, useState } from 'react'
import { Users, Activity, HardDrive, Server, CheckCircle2, XCircle } from 'lucide-react'
import Navbar from '../components/Navbar'
import StatCard from '../components/StatCard'
import { adminApi } from '../api/client'

export default function AdminPage() {
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([adminApi.stats(), adminApi.health(), adminApi.users()])
      .then(([{ data: s }, { data: h }, { data: u }]) => {
        setStats(s)
        setHealth(h)
        setUsers(u)
      })
      .finally(() => setLoading(false))
  }, [])

  const toggleUser = async (u) => {
    const fn = u.is_active ? adminApi.disableUser : adminApi.enableUser
    const { data } = await fn(u.id)
    setUsers((prev) => prev.map((x) => (x.id === u.id ? data : x)))
  }

  const fmt = (n) => (n ?? 0).toLocaleString()

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        <h1 className="text-2xl font-bold dark:text-white text-slate-900">Admin dashboard</h1>

        {loading ? (
          <div className="flex items-center gap-2 dark:text-slate-400 text-slate-500">
            <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            Loading…
          </div>
        ) : (
          <>
            {/* Platform stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard icon={Users}     label="Total users"       value={fmt(stats?.total_users)}       color="text-brand-400" />
              <StatCard icon={Activity}  label="Total conversions" value={fmt(stats?.total_conversions)} color="text-green-400" />
              <StatCard icon={HardDrive} label="Total storage"
                value={`${((stats?.total_storage_bytes || 0) / 1024 ** 3).toFixed(2)} GB`}
                color="text-purple-400"
              />
              <StatCard icon={Server}    label="Worker mode"
                value={health?.task_mode?.includes('eager') ? 'Eager' : 'Celery'}
                color="text-orange-400"
              />
            </div>

            {/* System health */}
            {health && (
              <div className="dark:glass-card glass-card-light p-6 space-y-4">
                <h2 className="text-base font-semibold dark:text-white text-slate-900">System health</h2>
                <div className="grid sm:grid-cols-2 gap-4 text-sm">
                  {[
                    ['Database', health.database],
                    ['Redis / Queue', health.redis],
                    ['Storage backend', health.storage_backend],
                    ['Disk free', `${health.disk_free_gb} GB of ${health.disk_total_gb} GB`],
                  ].map(([label, val]) => (
                    <div key={label} className="flex items-center justify-between dark:bg-white/5 bg-slate-100 rounded-xl px-4 py-3">
                      <span className="dark:text-slate-400 text-slate-500">{label}</span>
                      <span className={`flex items-center gap-1.5 font-medium ${
                        val === 'ok' ? 'text-green-400' : 'dark:text-slate-200 text-slate-800'
                      }`}>
                        {val === 'ok' && <CheckCircle2 className="w-3.5 h-3.5" />}
                        {val}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Users table */}
            <div className="dark:glass-card glass-card-light overflow-hidden">
              <div className="px-5 py-4 border-b dark:border-white/10 border-slate-100">
                <h2 className="text-base font-semibold dark:text-white text-slate-900">
                  Users ({users.length})
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b dark:border-white/10 border-slate-100">
                      {['Email', 'Name', 'Plan', 'Admin', 'Status', ''].map((h) => (
                        <th key={h} className="text-left px-5 py-3 text-xs font-semibold dark:text-slate-400 text-slate-500 uppercase tracking-wide">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y dark:divide-white/10 divide-slate-100">
                    {users.map((u) => (
                      <tr key={u.id} className="dark:hover:bg-white/5 hover:bg-slate-50 transition-colors">
                        <td className="px-5 py-3 dark:text-white text-slate-900">{u.email}</td>
                        <td className="px-5 py-3 dark:text-slate-300 text-slate-600">{u.full_name || '—'}</td>
                        <td className="px-5 py-3">
                          <span className="badge dark:bg-white/10 bg-slate-100 dark:text-slate-300 text-slate-600 capitalize">
                            {u.plan}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          {u.is_admin
                            ? <CheckCircle2 className="w-4 h-4 text-brand-400" />
                            : <XCircle className="w-4 h-4 dark:text-slate-600 text-slate-300" />}
                        </td>
                        <td className="px-5 py-3">
                          <span className={u.is_active ? 'badge-completed' : 'badge-failed'}>
                            {u.is_active ? 'Active' : 'Disabled'}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-right">
                          <button
                            onClick={() => toggleUser(u)}
                            className={`text-xs font-medium ${
                              u.is_active ? 'text-red-400 hover:text-red-300' : 'text-green-400 hover:text-green-300'
                            }`}
                          >
                            {u.is_active ? 'Disable' : 'Enable'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
