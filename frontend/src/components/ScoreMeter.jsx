import React from 'react'

export function getScoreRating(score) {
  const num = typeof score === 'number' ? score : parseFloat(score) || 0
  if (num >= 85) return { label: 'Exceptional Match', color: 'var(--color-success)', bg: 'var(--color-success-muted)', border: 'rgba(16, 185, 129, 0.3)' }
  if (num >= 70) return { label: 'Strong Fit', color: 'var(--color-primary)', bg: 'var(--color-primary-muted)', border: 'rgba(59, 130, 246, 0.3)' }
  if (num >= 50) return { label: 'Moderate Fit', color: 'var(--color-warning)', bg: 'var(--color-warning-muted)', border: 'rgba(245, 158, 11, 0.3)' }
  return { label: 'Needs Development', color: 'var(--color-danger)', bg: 'var(--color-danger-muted)', border: 'rgba(244, 63, 94, 0.3)' }
}

export default function ScoreMeter({
  score = 0,
  max = 100,
  label,
  showRating = true,
  size = 'md', // 'sm', 'md', 'lg'
  suffix = '%'
}) {
  const num = typeof score === 'number' ? score : parseFloat(score) || 0
  const normalized = Math.min(100, Math.max(0, (num / max) * 100))
  const rating = getScoreRating(normalized)

  const heightMap = {
    sm: 6,
    md: 8,
    lg: 12
  }

  const barHeight = heightMap[size] || 8

  return (
    <div style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        {label && (
          <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 600, color: 'var(--color-fg-muted)' }}>
            {label}
          </span>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginLeft: 'auto' }}>
          <span style={{
            fontSize: size === 'lg' ? '1.125rem' : 'var(--p-text-sm)',
            fontWeight: 800,
            color: 'var(--color-fg)',
            fontFamily: 'var(--p-font-mono)'
          }}>
            {num.toFixed(0)}{suffix}
          </span>
          {showRating && (
            <span style={{
              fontSize: '10px',
              fontWeight: 700,
              color: rating.color,
              background: rating.bg,
              padding: '1px 6px',
              borderRadius: 'var(--radius-full)',
              border: `1px solid ${rating.border}`
            }}>
              {rating.label}
            </span>
          )}
        </div>
      </div>

      <div style={{
        width: '100%',
        height: barHeight,
        background: 'var(--color-border-subtle)',
        borderRadius: 'var(--radius-full)',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <div
          style={{
            width: `${normalized}%`,
            height: '100%',
            background: rating.color,
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        />
      </div>
    </div>
  )
}
