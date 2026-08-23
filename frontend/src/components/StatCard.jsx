import React from 'react'

export default function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  trendPositive,
  color = 'primary',
  helperText,
  onClick
}) {
  const colorMap = {
    primary: {
      bg: 'var(--color-primary-muted)',
      fg: 'var(--color-primary)',
      border: 'rgba(59, 130, 246, 0.2)',
    },
    success: {
      bg: 'var(--color-success-muted)',
      fg: 'var(--color-success)',
      border: 'rgba(16, 185, 129, 0.2)',
    },
    warning: {
      bg: 'var(--color-warning-muted)',
      fg: 'var(--color-warning)',
      border: 'rgba(245, 158, 11, 0.2)',
    },
    danger: {
      bg: 'var(--color-danger-muted)',
      fg: 'var(--color-danger)',
      border: 'rgba(244, 63, 94, 0.2)',
    },
    info: {
      bg: 'var(--color-info-muted)',
      fg: 'var(--color-info)',
      border: 'rgba(99, 102, 241, 0.2)',
    },
    purple: {
      bg: 'var(--color-purple-muted)',
      fg: 'var(--color-purple)',
      border: 'rgba(139, 92, 246, 0.2)',
    }
  }

  const selectedColor = colorMap[color] || colorMap.primary

  return (
    <div
      className="card"
      onClick={onClick}
      style={{
        padding: 'var(--p-space-4) var(--p-space-5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all var(--duration-normal) var(--ease)',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 'var(--p-text-xs)',
          fontWeight: 600,
          color: 'var(--color-fg-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: 4
        }}>
          {label}
        </div>
        <div style={{
          fontSize: '1.625rem',
          fontWeight: 800,
          color: 'var(--color-fg)',
          lineHeight: 1.15,
          fontFamily: 'var(--p-font-sans)',
          display: 'flex',
          alignItems: 'baseline',
          gap: 8
        }}>
          <span>{value}</span>
          {trend && (
            <span style={{
              fontSize: 'var(--p-text-xs)',
              fontWeight: 700,
              color: trendPositive ? 'var(--color-success)' : 'var(--color-danger)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 2
            }}>
              {trendPositive ? '↑' : '↓'} {trend}
            </span>
          )}
        </div>
        {helperText && (
          <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            {helperText}
          </div>
        )}
      </div>

      {Icon && (
        <div style={{
          width: 44,
          height: 44,
          borderRadius: 'var(--radius-md)',
          background: selectedColor.bg,
          color: selectedColor.fg,
          border: `1px solid ${selectedColor.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          marginLeft: 12
        }}>
          <Icon size={20} />
        </div>
      )}
    </div>
  )
}
