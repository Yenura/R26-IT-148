import React from 'react'

export default function PageHeader({
  badge,
  title,
  description,
  icon: Icon,
  actions,
  breadcrumbs
}) {
  return (
    <div className="page-head" style={{ marginBottom: 'var(--p-space-6)' }}>
      {breadcrumbs && (
        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginBottom: 'var(--p-space-2)', display: 'flex', alignItems: 'center', gap: 6 }}>
          {breadcrumbs}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--p-space-4)' }}>
        <div style={{ flex: '1 1 300px', minWidth: 0 }}>
          {badge && (
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'var(--color-primary)',
              background: 'var(--color-primary-muted)',
              padding: '2px 10px',
              borderRadius: 'var(--radius-full)',
              marginBottom: 'var(--p-space-2)'
            }}>
              {badge}
            </div>
          )}
          <h1 style={{
            fontSize: 'clamp(1.4rem, 2.8vw, 1.75rem)',
            fontWeight: 800,
            color: 'var(--color-fg)',
            letterSpacing: '-0.02em',
            lineHeight: 1.2,
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: 10
          }}>
            {Icon && <Icon size={24} style={{ color: 'var(--color-primary)', flexShrink: 0 }} />}
            <span>{title}</span>
          </h1>
          {description && (
            <p style={{
              fontSize: 'var(--p-text-base)',
              color: 'var(--color-fg-secondary)',
              marginTop: 'var(--p-space-2)',
              marginBottom: 0,
              lineHeight: 1.5,
              maxWidth: 720
            }}>
              {description}
            </p>
          )}
        </div>
        {actions && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--p-space-2)', flexWrap: 'wrap' }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}
