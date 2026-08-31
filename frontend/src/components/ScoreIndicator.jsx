import React from 'react'

/**
 * ScoreIndicator
 * Accessible, color-coded score visualizer.
 * Supports: 'badge', 'linear', 'circular', 'pill'
 */
export default function ScoreIndicator({
  score = 0,
  max = 100,
  label = '',
  size = 'md', // 'sm', 'md', 'lg'
  type = 'pill', // 'pill', 'badge', 'linear', 'circular'
  showStatus = true,
  className = '',
  style = {}
}) {
  const numScore = Math.min(max, Math.max(0, Number(score) || 0))
  const percent = Math.round((numScore / max) * 100)

  const isExcellent = percent >= 80
  const isGood = percent >= 60 && percent < 80
  const isModerate = percent >= 40 && percent < 60

  const statusText = isExcellent
    ? 'Strong Match'
    : isGood
    ? 'Good Match'
    : isModerate
    ? 'Moderate Match'
    : 'Needs Development'

  const color = isExcellent
    ? 'var(--color-success)'
    : isGood
    ? 'var(--color-primary)'
    : isModerate
    ? 'var(--color-warning)'
    : 'var(--color-danger)'

  const bg = isExcellent
    ? 'var(--color-success-muted)'
    : isGood
    ? 'var(--color-primary-muted)'
    : isModerate
    ? 'var(--color-warning-muted)'
    : 'var(--color-danger-muted)'

  const border = isExcellent
    ? 'rgba(5, 150, 105, 0.25)'
    : isGood
    ? 'rgba(37, 99, 235, 0.25)'
    : isModerate
    ? 'rgba(217, 119, 6, 0.25)'
    : 'rgba(225, 29, 72, 0.25)'

  if (type === 'linear') {
    return (
      <div style={{ width: '100%', ...style }} className={className}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
          {label && (
            <span style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--color-fg)' }}>
              {label}
            </span>
          )}
          <span style={{ fontSize: '12px', fontWeight: 800, color: color }}>
            {percent}% {showStatus && <span style={{ fontSize: '10.5px', fontWeight: 500, color: 'var(--color-fg-muted)' }}>({statusText})</span>}
          </span>
        </div>
        <div style={{
          width: '100%',
          height: size === 'sm' ? 5 : size === 'lg' ? 10 : 7,
          borderRadius: 'var(--radius-full)',
          background: 'var(--color-border-subtle)',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percent}%`,
            height: '100%',
            borderRadius: 'var(--radius-full)',
            background: color,
            transition: 'width 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
          }} />
        </div>
      </div>
    )
  }

  if (type === 'circular') {
    const dim = size === 'sm' ? 38 : size === 'lg' ? 68 : 52
    const stroke = size === 'sm' ? 3.5 : size === 'lg' ? 6 : 4.5
    const radius = (dim - stroke) / 2
    const circ = 2 * Math.PI * radius
    const offset = circ - (percent / 100) * circ

    return (
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, ...style }} className={className}>
        <div style={{ position: 'relative', width: dim, height: dim }}>
          <svg width={dim} height={dim} style={{ transform: 'rotate(-90deg)' }}>
            <circle
              cx={dim / 2}
              cy={dim / 2}
              r={radius}
              stroke="var(--color-border-subtle)"
              strokeWidth={stroke}
              fill="transparent"
            />
            <circle
              cx={dim / 2}
              cy={dim / 2}
              r={radius}
              stroke={color}
              strokeWidth={stroke}
              strokeDasharray={circ}
              strokeDashoffset={offset}
              strokeLinecap="round"
              fill="transparent"
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
          </svg>
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: size === 'sm' ? '10.5px' : size === 'lg' ? '17px' : '13px',
            fontWeight: 800,
            color: 'var(--color-fg)'
          }}>
            {percent}%
          </div>
        </div>
        {label && (
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-fg)' }}>{label}</div>
            {showStatus && <div style={{ fontSize: '10.5px', color: color, fontWeight: 600 }}>{statusText}</div>}
          </div>
        )}
      </div>
    )
  }

  // Default 'pill' / 'badge'
  return (
    <span
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: size === 'sm' ? '2px 8px' : size === 'lg' ? '6px 14px' : '3px 10px',
        borderRadius: 'var(--radius-full)',
        background: bg,
        border: `1px solid ${border}`,
        color: color,
        fontSize: size === 'sm' ? '11px' : size === 'lg' ? '14px' : '12px',
        fontWeight: 700,
        ...style
      }}
    >
      <span style={{ fontWeight: 800 }}>{percent}%</span>
      {label && <span style={{ color: 'var(--color-fg-muted)', fontWeight: 500 }}>• {label}</span>}
      {showStatus && <span>{statusText}</span>}
    </span>
  )
}
