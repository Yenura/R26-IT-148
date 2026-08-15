import { AlertCircle, RotateCcw } from 'lucide-react'

export default function ErrorState({
  title = "Something went wrong",
  message = "Unable to complete the analysis at this moment.",
  onRetry
}) {
  return (
    <div style={{ padding: 40, textAlign: 'center', background: 'rgba(239, 68, 68, 0.05)', borderRadius: 14, border: '1px solid rgba(239, 68, 68, 0.2)', margin: '20px 0' }}>
      <div style={{ width: 52, height: 52, borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
        <AlertCircle size={26} />
      </div>
      <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text)', marginBottom: 6 }}>{title}</h3>
      <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 440, margin: '0 auto 20px', lineHeight: 1.5 }}>
        {message}
      </p>
      {onRetry && (
        <button className="btn btn-ghost" onClick={onRetry} style={{ padding: '8px 18px', fontSize: 13, border: '1px solid var(--border)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <RotateCcw size={14} /> Try Again
        </button>
      )}
    </div>
  )
}
