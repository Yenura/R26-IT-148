import React, { useEffect, useState } from 'react'

function AnimatedNumber({ value }) {
  const [display, setDisplay] = useState(0)
  const num = typeof value === 'number' ? value : parseFloat(String(value).replace(/[^0-9.-]/g, ''))
  const isNumber = !isNaN(num) && typeof value === 'number'

  useEffect(() => {
    if (!isNumber) return
    let start = 0
    const duration = 900
    const startTime = performance.now()

    const step = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const ease = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      setDisplay(Math.round(start + (num - start) * ease))
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    requestAnimationFrame(step)
  }, [num, isNumber])

  if (!isNumber) return <span>{value}</span>
  return <span>{display}</span>
}

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
      border: 'rgba(99, 102, 241, 0.25)',
      glow: 'rgba(99, 102, 241, 0.15)',
      gradient: 'linear-gradient(90deg, #6366f1, #818cf8)'
    },
    success: {
      bg: 'var(--color-success-muted)',
      fg: 'var(--color-success)',
      border: 'rgba(16, 185, 129, 0.25)',
      glow: 'rgba(16, 185, 129, 0.15)',
      gradient: 'linear-gradient(90deg, #10b981, #34d399)'
    },
    warning: {
      bg: 'var(--color-warning-muted)',
      fg: 'var(--color-warning)',
      border: 'rgba(245, 158, 11, 0.25)',
      glow: 'rgba(245, 158, 11, 0.15)',
      gradient: 'linear-gradient(90deg, #f59e0b, #fbbf24)'
    },
    danger: {
      bg: 'var(--color-danger-muted)',
      fg: 'var(--color-danger)',
      border: 'rgba(244, 63, 94, 0.25)',
      glow: 'rgba(244, 63, 94, 0.15)',
      gradient: 'linear-gradient(90deg, #f43f5e, #fb7185)'
    },
    info: {
      bg: 'var(--color-info-muted)',
      fg: 'var(--color-info)',
      border: 'rgba(56, 189, 248, 0.25)',
      glow: 'rgba(56, 189, 248, 0.15)',
      gradient: 'linear-gradient(90deg, #38bdf8, #818cf8)'
    },
    purple: {
      bg: 'var(--color-purple-muted)',
      fg: 'var(--color-purple)',
      border: 'rgba(168, 85, 247, 0.25)',
      glow: 'rgba(168, 85, 247, 0.15)',
      gradient: 'linear-gradient(90deg, #a855f7, #c084fc)'
    }
  }

  const selectedColor = colorMap[color] || colorMap.primary

  return (
    <div
      className="card"
      onClick={onClick}
      style={{
        padding: 'var(--p-space-5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden',
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      {/* Top micro-gradient accent line */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 2,
        background: selectedColor.gradient
      }} />

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          color: 'var(--color-fg-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom: 4
        }}>
          {label}
        </div>
        <div style={{
          fontSize: '1.65rem',
          fontWeight: 800,
          color: 'var(--color-fg)',
          lineHeight: 1.15,
          fontFamily: 'var(--p-font-sans)',
          display: 'flex',
          alignItems: 'baseline',
          gap: 8,
          letterSpacing: '-0.02em'
        }}>
          <AnimatedNumber value={value} />
          {trend && (
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              color: trendPositive ? 'var(--color-success)' : 'var(--color-danger)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 2,
              padding: '1px 6px',
              borderRadius: 'var(--radius-full)',
              background: trendPositive ? 'var(--color-success-muted)' : 'var(--color-danger-muted)'
            }}>
              {trendPositive ? '↑' : '↓'} {trend}
            </span>
          )}
        </div>
        {helperText && (
          <div style={{ fontSize: '11px', color: 'var(--color-fg-secondary)', marginTop: 4, fontWeight: 500 }}>
            {helperText}
          </div>
        )}
      </div>

      {Icon && (
        <div style={{
          width: 44,
          height: 44,
          borderRadius: 'var(--radius-lg)',
          background: selectedColor.bg,
          color: selectedColor.fg,
          border: `1px solid ${selectedColor.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          marginLeft: 12,
          boxShadow: `0 4px 12px ${selectedColor.glow}`,
          transition: 'transform 0.2s ease'
        }}>
          <Icon size={20} />
        </div>
      )}
    </div>
  )
}
