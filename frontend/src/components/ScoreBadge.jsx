import React from 'react'
import { getScoreRating } from './ScoreMeter'

export default function ScoreBadge({
  score = 0,
  showLabel = true,
  suffix = '%'
}) {
  const num = typeof score === 'number' ? score : parseFloat(score) || 0
  const rating = getScoreRating(num)

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '3px 8px',
        borderRadius: 'var(--radius-full)',
        background: rating.bg,
        border: `1px solid ${rating.border}`,
        fontSize: 'var(--p-text-xs)',
        fontWeight: 700,
        color: rating.color,
        fontFamily: 'var(--p-font-sans)',
        whiteSpace: 'nowrap'
      }}
    >
      <span style={{ fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>
        {num.toFixed(0)}{suffix}
      </span>
      {showLabel && (
        <span style={{ opacity: 0.9, fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          · {rating.label}
        </span>
      )}
    </span>
  )
}
