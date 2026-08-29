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
    let frameId

    const step = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const ease = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(start + (num - start) * ease))
      if (progress < 1) {
        frameId = requestAnimationFrame(step)
      }
    }
    frameId = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frameId)
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
    primary: { bg: 'var(--color-primary-muted)', fg: 'var(--color-primary)' },
    success: { bg: 'var(--color-success-muted)', fg: 'var(--color-success)' },
    warning: { bg: 'var(--color-warning-muted)', fg: 'var(--color-warning)' },
    danger: { bg: 'var(--color-danger-muted)', fg: 'var(--color-danger)' },
    info: { bg: 'var(--color-info-muted)', fg: 'var(--color-info)' },
    purple: { bg: 'var(--color-purple-muted)', fg: 'var(--color-purple)' }
  }

  const selectedColor = colorMap[color] || colorMap.primary

  return (
    <div
      className="stat"
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: onClick ? 'pointer' : 'default',
      }}
    >
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
              {trendPositive ? '\u2191' : '\u2193'} {trend}
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
          borderRadius: 'var(--radius-md)',
          background: selectedColor.bg,
          color: selectedColor.fg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          marginLeft: 12,
        }}>
          <Icon size={20} />
        </div>
      )}
    </div>
  )
}
