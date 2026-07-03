import { Clock, Loader2, CheckCircle2, XCircle, Ban } from 'lucide-react'

const BADGE = {
  pending:    { cls: 'badge-pending',    icon: Clock,         label: 'Pending' },
  processing: { cls: 'badge-processing', icon: Loader2,       label: 'Processing' },
  completed:  { cls: 'badge-completed',  icon: CheckCircle2,  label: 'Done' },
  failed:     { cls: 'badge-failed',     icon: XCircle,       label: 'Failed' },
  cancelled:  { cls: 'badge-cancelled',  icon: Ban,           label: 'Cancelled' },
}

export default function StatusBadge({ status }) {
  const def = BADGE[status] || BADGE.pending
  const Icon = def.icon
  return (
    <span className={def.cls}>
      <Icon className={`w-3 h-3 ${status === 'processing' ? 'animate-spin' : ''}`} />
      {def.label}
    </span>
  )
}
