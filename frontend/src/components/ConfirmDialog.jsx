import { AlertTriangle, Trash2, X } from 'lucide-react'

export default function ConfirmDialog({
  open,
  title = 'Are you sure?',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}) {
  if (!open) return null

  return (
    <div
      onClick={onCancel}
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--p-radius-lg)',
          padding: 'var(--p-space-6)',
          maxWidth: 400, width: '100%',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: 'var(--p-space-4)' }}>
          <div style={{
            width: 40, height: 40, borderRadius: 'var(--p-radius-md)', flexShrink: 0,
            background: danger ? 'var(--color-error-muted)' : 'var(--color-primary-muted)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {danger
              ? <Trash2 size={18} style={{ color: 'var(--color-error)' }} />
              : <AlertTriangle size={18} style={{ color: 'var(--color-primary)' }} />}
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>{title}</h3>
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>{message}</p>
          </div>
          <button onClick={onCancel} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-fg-muted)', padding: 4 }}>
            <X size={16} />
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="btn btn-ghost btn-sm" onClick={onCancel}>{cancelLabel}</button>
          <button
            className={`btn btn-sm ${danger ? 'btn-danger' : ''}`}
            onClick={onConfirm}
            style={danger ? { background: 'var(--color-danger)', color: 'var(--color-on-danger)', border: 'none' } : {}}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
