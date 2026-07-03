import { useEffect, useState } from 'react'
import { Download, RefreshCw } from 'lucide-react'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import { historyApi } from '../api/client'

const PAGE_SIZE = 20

export default function HistoryPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  const load = async (p = 0) => {
    setLoading(true)
    try {
      const { data } = await historyApi.list(p * PAGE_SIZE, PAGE_SIZE)
      if (p === 0) setItems(data)
      else setItems((prev) => [...prev, ...data])
      setHasMore(data.length === PAGE_SIZE)
      setPage(p)
    } catch {
      /* non-critical */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(0) }, [])

  const downloadUrl = (conv) =>
    `${import.meta.env.VITE_API_URL || '/api/v1'}/convert/${conv.id}/download`

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold dark:text-white text-slate-900">Conversion history</h1>
          <button
            onClick={() => load(0)}
            className="flex items-center gap-2 btn-ghost text-sm dark:text-slate-300"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {items.length === 0 && !loading ? (
          <div className="text-center py-20 dark:text-slate-400 text-slate-500">
            No conversions yet. Upload a file from the dashboard to get started.
          </div>
        ) : (
          <div className="dark:glass-card glass-card-light overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="dark:border-b dark:border-white/10 border-b border-slate-100">
                  {['Format', 'Status', 'Size', 'Created', ''].map((h) => (
                    <th key={h} className="text-left px-5 py-3 text-xs font-semibold dark:text-slate-400 text-slate-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y dark:divide-white/10 divide-slate-100">
                {items.map((c) => (
                  <tr key={c.id} className="dark:hover:bg-white/5 hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3 font-mono dark:text-white text-slate-900 font-semibold">
                      .{c.target_format.toUpperCase()}
                    </td>
                    <td className="px-5 py-3">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-5 py-3 dark:text-slate-400 text-slate-500">
                      {c.output_size_bytes ? `${(c.output_size_bytes / 1024).toFixed(1)} KB` : '—'}
                    </td>
                    <td className="px-5 py-3 dark:text-slate-400 text-slate-500">
                      {new Date(c.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-3 text-right">
                      {c.status === 'completed' && (
                        <a
                          href={downloadUrl(c)}
                          download
                          className="inline-flex items-center gap-1.5 text-xs text-brand-400 hover:text-brand-300 font-medium"
                        >
                          <Download className="w-3.5 h-3.5" />
                          Download
                        </a>
                      )}
                      {c.status === 'failed' && c.error_message && (
                        <span
                          title={c.error_message}
                          className="text-xs text-red-400 cursor-help"
                        >
                          Error ⓘ
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {hasMore && (
          <div className="text-center">
            <button
              onClick={() => load(page + 1)}
              disabled={loading}
              className="btn-ghost text-sm dark:text-slate-300"
            >
              {loading ? 'Loading…' : 'Load more'}
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
