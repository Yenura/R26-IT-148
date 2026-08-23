import React from 'react'

export function CardSkeleton({ count = 1 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-4)' }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card" style={{ padding: 'var(--p-space-5)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <div className="skeleton" style={{ height: 20, width: '40%', borderRadius: 4 }} />
            <div className="skeleton" style={{ height: 20, width: '15%', borderRadius: 4 }} />
          </div>
          <div className="skeleton" style={{ height: 14, width: '70%', borderRadius: 4, marginBottom: 8 }} />
          <div className="skeleton" style={{ height: 14, width: '50%', borderRadius: 4, marginBottom: 16 }} />
          <div style={{ display: 'flex', gap: 6 }}>
            <div className="skeleton" style={{ height: 24, width: 60, borderRadius: 12 }} />
            <div className="skeleton" style={{ height: 24, width: 80, borderRadius: 12 }} />
            <div className="skeleton" style={{ height: 24, width: 70, borderRadius: 12 }} />
          </div>
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 4 }) {
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--color-border)', display: 'flex', gap: 16 }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 14, flex: 1, borderRadius: 4 }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ padding: '14px 18px', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', gap: 16, alignItems: 'center' }}>
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="skeleton" style={{ height: j === 0 ? 18 : 14, flex: j === 0 ? 1.5 : 1, borderRadius: 4 }} />
          ))}
        </div>
      ))}
    </div>
  )
}

export function StatStripSkeleton({ count = 4 }) {
  return (
    <div className="grid" style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))`, gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card" style={{ padding: 'var(--p-space-4)' }}>
          <div className="skeleton" style={{ height: 12, width: '50%', marginBottom: 10, borderRadius: 4 }} />
          <div className="skeleton" style={{ height: 28, width: '35%', borderRadius: 4 }} />
        </div>
      ))}
    </div>
  )
}

export default function SkeletonLoader({ type = 'card', count = 3, rows = 5, cols = 4 }) {
  if (type === 'table') return <TableSkeleton rows={rows} cols={cols} />
  if (type === 'stat') return <StatStripSkeleton count={count} />
  return <CardSkeleton count={count} />
}
