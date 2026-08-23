import React from 'react'
import { FileSearch, Plus, ArrowRight } from 'lucide-react'

export default function EmptyState({
  title = "No candidates analyzed yet",
  description = "Upload a candidate resume or select a target IT job role to begin AI screening.",
  actionLabel = "Upload Resume",
  onAction,
  icon: Icon = FileSearch
}) {
  return (
    <div style={{
      padding: 'var(--p-space-10) var(--p-space-6)',
      textAlign: 'center',
      background: 'var(--color-bg-elevated)',
      borderRadius: 'var(--radius-xl)',
      border: '1px dashed var(--color-border)',
      margin: 'var(--p-space-5) 0',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div style={{
        width: 60,
        height: 60,
        borderRadius: 'var(--radius-full)',
        background: 'var(--color-bg-soft)',
        color: 'var(--color-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto var(--p-space-4)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-xs)'
      }}>
        <Icon size={28} />
      </div>
      <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 8, letterSpacing: '-0.01em' }}>
        {title}
      </h3>
      <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', maxWidth: 480, margin: '0 auto var(--p-space-6)', lineHeight: 1.6 }}>
        {description}
      </p>
      {onAction && (
        <button
          className="btn btn-primary"
          onClick={onAction}
          style={{ padding: '10px 22px', fontSize: 'var(--p-text-sm)', fontWeight: 700, borderRadius: 'var(--radius-md)', display: 'inline-flex', alignItems: 'center', gap: 8 }}
        >
          <Plus size={15} /> {actionLabel} <ArrowRight size={14} />
        </button>
      )}
    </div>
  )
}
