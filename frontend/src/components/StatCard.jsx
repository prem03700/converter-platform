export default function StatCard({ icon: Icon, label, value, sub, color = 'text-brand-400' }) {
  return (
    <div className="dark:glass-card glass-card-light p-5 space-y-3">
      <div className={`w-9 h-9 rounded-lg bg-current/10 flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold dark:text-white text-slate-900">{value}</p>
        <p className="text-sm dark:text-slate-400 text-slate-500">{label}</p>
        {sub && <p className="text-xs dark:text-slate-500 text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}
