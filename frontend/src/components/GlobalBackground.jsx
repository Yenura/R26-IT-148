import React from 'react'
import { useTheme } from '../context/ThemeContext'

/**
 * Calm, static ambient background (Apple restraint: no cursor
 * spotlights, no animation loops — content carries the page).
 */
export default function GlobalBackground() {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        // Decorative back layer: must sit behind ALL content. A fixed
        // z-index:0 layer paints above non-positioned text and swallows it.
        zIndex: -1,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: 'var(--color-bg)',
      }}
    >
      {/* Single faint static wash for depth */}
      <div
        style={{
          position: 'absolute',
          top: '-15%',
          left: '20%',
          width: '500px',
          height: '500px',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(10, 132, 255, 0.05) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(0, 113, 227, 0.04) 0%, transparent 70%)',
          filter: 'blur(90px)',
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}
