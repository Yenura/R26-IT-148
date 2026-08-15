import { FileSearch, Plus, ArrowRight } from 'lucide-react'

export default function EmptyState({
  title = "No candidates analyzed yet",
  description = "Upload a candidate resume or select a target IT job role to begin AI screening.",
  actionLabel = "Upload Resume",
  onAction,
  icon: Icon = FileSearch
}) {
  return (
    <div style={{ padding: 48, textAlign: 'center', background: 'var(--bg-elevated)', borderRadius: 14, border: '1px dashed var(--border)', margin: '20px 0' }}>
      <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--bg)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', border: '1px solid var(--border)' }}>
        <Icon size={26} />
      </div>
      <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text)', marginBottom: 6 }}>{title}</h3>
      <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 460, margin: '0 auto 20px', lineHeight: 1.5 }}>
        {description}
      </p>
      {onAction && (
        <button className="btn" onClick={onAction} style={{ padding: '10px 20px', fontSize: 13, fontWeight: 700, borderRadius: 8, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <Plus size={15} /> {actionLabel} <ArrowRight size={14} />
        </button>
      )}
    </div>
  )
}
