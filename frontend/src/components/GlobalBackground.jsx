import React from 'react'

export default function GlobalBackground() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: -1,
        pointerEvents: 'none',
        background: 'var(--color-bg)',
      }}
    />
  )
}
