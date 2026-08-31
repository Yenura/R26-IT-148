import React, { useEffect, useState, useRef } from 'react'
import { useTheme } from '../context/ThemeContext'

export default function GlobalBackground() {
  const { theme } = useTheme()
  const [pos, setPos] = useState({ x: -1000, y: -1000 })
  const [opacity, setOpacity] = useState(0)
  const animFrame = useRef(null)
  const targetPos = useRef({ x: -1000, y: -1000 })

  useEffect(() => {
    // Disable spotlight on touch/coarse pointer devices to save battery
    if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) return

    const handleMouseMove = (e) => {
      targetPos.current = { x: e.clientX, y: e.clientY }
      setOpacity(1)
    }

    const handleMouseLeave = () => {
      setOpacity(0)
    }

    const handleMouseEnter = () => {
      setOpacity(1)
    }

    let currentX = -1000
    let currentY = -1000

    const render = () => {
      // Smooth fluid interpolation for the glowing mouse trail
      currentX += (targetPos.current.x - currentX) * 0.14
      currentY += (targetPos.current.y - currentY) * 0.14
      setPos({ x: Math.round(currentX), y: Math.round(currentY) })
      animFrame.current = requestAnimationFrame(render)
    }

    window.addEventListener('mousemove', handleMouseMove, { passive: true })
    document.addEventListener('mouseleave', handleMouseLeave)
    document.addEventListener('mouseenter', handleMouseEnter)
    animFrame.current = requestAnimationFrame(render)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseleave', handleMouseLeave)
      document.removeEventListener('mouseenter', handleMouseEnter)
      if (animFrame.current) cancelAnimationFrame(animFrame.current)
    }
  }, [])

  const isDark = theme === 'dark'

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: 'var(--color-bg)',
      }}
    >
      {/* Interactive Cursor Spotlight Aura */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: isDark
            ? `radial-gradient(650px circle at ${pos.x}px ${pos.y}px, rgba(99, 102, 241, 0.14), rgba(139, 92, 246, 0.07) 35%, rgba(59, 130, 246, 0.02) 65%, transparent 80%)`
            : `radial-gradient(600px circle at ${pos.x}px ${pos.y}px, rgba(37, 99, 235, 0.08), rgba(99, 102, 241, 0.04) 40%, transparent 75%)`,
          opacity: opacity,
          transition: 'opacity 0.4s ease',
          willChange: 'background',
          pointerEvents: 'none',
        }}
      />

      {/* Subtle Ambient Atmospheric Glows */}
      <div
        style={{
          position: 'absolute',
          top: '-15%',
          left: '20%',
          width: '500px',
          height: '500px',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(37, 99, 235, 0.03) 0%, transparent 70%)',
          filter: 'blur(90px)',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '-10%',
          right: '15%',
          width: '550px',
          height: '550px',
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(139, 92, 246, 0.05) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(147, 51, 234, 0.03) 0%, transparent 70%)',
          filter: 'blur(100px)',
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}
