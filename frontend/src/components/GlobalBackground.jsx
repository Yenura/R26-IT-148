import React, { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

export default function GlobalBackground() {
  const location = useLocation()
  const path = location.pathname
  const { theme } = useTheme()
  const isLight = theme === 'light'
  const spotlightRef = useRef(null)

  const isSkillGap = path.includes('skill-gap')
  const isProgress = path.includes('progress')
  const isRecruiter = path.includes('company') || path.includes('pipeline')
  const isInterview = path.includes('interview')

  useEffect(() => {
    let frameId = null
    let lastUpdate = 0
    const THROTTLE_MS = 16 // ~60fps

    const handlePointerMove = (e) => {
      const now = Date.now()
      if (now - lastUpdate < THROTTLE_MS) return
      lastUpdate = now

      if (frameId) cancelAnimationFrame(frameId)
      frameId = requestAnimationFrame(() => {
        if (spotlightRef.current) {
          spotlightRef.current.style.setProperty('--mouse-x', `${e.clientX}px`)
          spotlightRef.current.style.setProperty('--mouse-y', `${e.clientY}px`)
        }
        document.documentElement.style.setProperty('--cursor-x', `${e.clientX}px`)
        document.documentElement.style.setProperty('--cursor-y', `${e.clientY}px`)
      })
    }

    // 3. Viewport Scroll Progress Bar Handler
    const scrollBar = document.getElementById('global-scroll-progress-bar')
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight
      if (totalHeight > 0 && scrollBar) {
        const progress = (window.scrollY / totalHeight) * 100
        scrollBar.style.width = `${progress}%`
      }
    }

    window.addEventListener('pointermove', handlePointerMove, { passive: true })
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('scroll', handleScroll)
      if (frameId) cancelAnimationFrame(frameId)
    }
  }, [])

  return (
    <>
      {/* 0. Viewport Top Reading Scroll Progress Bar */}
      <div
        id="global-scroll-progress-bar"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          height: '3px',
          width: '0%',
          background: 'linear-gradient(90deg, #6366f1, #a855f7, #06b6d4)',
          boxShadow: '0 0 12px rgba(99, 102, 241, 0.75)',
          zIndex: 9999,
          pointerEvents: 'none',
          transition: 'width 0.1s ease-out',
        }}
      />

      <div
        aria-hidden="true"
        className="global-aurora-canvas"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: -1,
          pointerEvents: 'none',
          overflow: 'hidden',
          background: isLight ? '#f8fafc' : '#070814',
        }}
      >
      {/* 1. Interactive Cursor Spotlight Ambient Glow */}
      <div
        ref={spotlightRef}
        className="global-cursor-spotlight"
        style={{
          position: 'fixed',
          inset: 0,
          background: isLight
            ? 'radial-gradient(700px circle at var(--mouse-x, 50vw) var(--mouse-y, 50vh), rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.05) 50%, transparent 80%)'
            : 'radial-gradient(700px circle at var(--mouse-x, 50vw) var(--mouse-y, 50vh), rgba(99, 102, 241, 0.24), rgba(6, 182, 212, 0.12) 45%, transparent 75%)',
          pointerEvents: 'none',
          zIndex: 1,
          transition: 'opacity 0.3s ease',
        }}
      />

      {/* 2. Luminous Top Aurora Sunburst Header Beam */}
      <div
        className="aurora-top-beam"
        style={{
          position: 'absolute',
          top: '-15%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '120vw',
          height: '600px',
          background: isLight
            ? 'radial-gradient(ellipse 70% 60% at 50% 0%, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0.12) 40%, rgba(6, 182, 212, 0.08) 70%, transparent 100%)'
            : 'radial-gradient(ellipse 70% 60% at 50% 0%, rgba(99, 102, 241, 0.38) 0%, rgba(168, 85, 247, 0.26) 40%, rgba(6, 182, 212, 0.16) 75%, transparent 100%)',
          filter: 'blur(60px)',
          opacity: 0.95,
          willChange: 'transform',
        }}
      />

      {/* 3. Floating Luminous Aurora Nebula Orbs */}
      {/* Orb 1: Electric Indigo & Fuchsia Nebula (Top Left) */}
      <div
        className="aurora-orb-indigo"
        style={{
          position: 'absolute',
          top: '-100px',
          left: '-80px',
          width: '650px',
          height: '650px',
          borderRadius: '50%',
          background: isLight
            ? 'radial-gradient(circle, rgba(99, 102, 241, 0.20) 0%, rgba(236, 72, 153, 0.12) 45%, transparent 70%)'
            : 'radial-gradient(circle, rgba(99, 102, 241, 0.38) 0%, rgba(236, 72, 153, 0.22) 45%, rgba(79, 70, 229, 0.1) 65%, transparent 75%)',
          filter: 'blur(75px)',
          willChange: 'transform',
        }}
      />

      {/* Orb 2: Neon Cyan & Emerald Flare (Bottom Right) */}
      <div
        className="aurora-orb-cyan"
        style={{
          position: 'absolute',
          bottom: '-120px',
          right: '-80px',
          width: '600px',
          height: '600px',
          borderRadius: '50%',
          background: isLight
            ? 'radial-gradient(circle, rgba(6, 182, 212, 0.16) 0%, rgba(16, 185, 129, 0.10) 50%, transparent 70%)'
            : 'radial-gradient(circle, rgba(6, 182, 212, 0.32) 0%, rgba(16, 185, 129, 0.20) 50%, rgba(14, 165, 233, 0.08) 65%, transparent 75%)',
          filter: 'blur(75px)',
          willChange: 'transform',
        }}
      />

      {/* Orb 3: Royal Violet Core (Center / Mid Screen) */}
      <div
        className="aurora-orb-violet"
        style={{
          position: 'absolute',
          top: '38%',
          left: '45%',
          transform: 'translate(-50%, -50%)',
          width: '750px',
          height: '750px',
          borderRadius: '50%',
          background: isLight
            ? 'radial-gradient(circle, rgba(168, 85, 247, 0.14) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 70%)'
            : 'radial-gradient(circle, rgba(168, 85, 247, 0.28) 0%, rgba(139, 92, 246, 0.16) 45%, rgba(99, 102, 241, 0.08) 65%, transparent 75%)',
          filter: 'blur(85px)',
          willChange: 'transform',
        }}
      />

      {/* 4. Page-Specific Contextual Aurora Glows */}
      {isSkillGap && (
        <div
          className="aurora-accent-pulse"
          style={{
            position: 'absolute',
            top: '20%',
            right: '8%',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(244, 63, 94, 0.28) 0%, rgba(245, 158, 11, 0.18) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.8s ease',
          }}
        />
      )}

      {isProgress && (
        <div
          className="aurora-accent-pulse"
          style={{
            position: 'absolute',
            top: '25%',
            right: '12%',
            width: '520px',
            height: '520px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.28) 0%, rgba(6, 182, 212, 0.16) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.8s ease',
          }}
        />
      )}

      {isRecruiter && (
        <div
          className="aurora-accent-pulse"
          style={{
            position: 'absolute',
            top: '12%',
            right: '6%',
            width: '550px',
            height: '550px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.30) 0%, rgba(99, 102, 241, 0.20) 50%, transparent 70%)',
            filter: 'blur(85px)',
            transition: 'opacity 0.8s ease',
          }}
        />
      )}

      {isInterview && (
        <div
          className="aurora-accent-pulse"
          style={{
            position: 'absolute',
            top: '30%',
            left: '10%',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(56, 189, 248, 0.28) 0%, rgba(99, 102, 241, 0.18) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.8s ease',
          }}
        />
      )}

      {/* 5. Crisp High-Tech Dot Matrix & Intersection Grid */}
      <div
        className="aurora-grid-pattern"
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: isLight
            ? 'radial-gradient(rgba(99, 102, 241, 0.12) 1.2px, transparent 1.2px), linear-gradient(rgba(0,0,0,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.025) 1px, transparent 1px)'
            : 'radial-gradient(rgba(165, 180, 252, 0.16) 1.2px, transparent 1.2px), linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)',
          backgroundSize: '48px 48px, 48px 48px, 48px 48px',
          opacity: 0.75,
          maskImage: 'radial-gradient(ellipse 90% 85% at 50% 40%, #000 40%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 90% 85% at 50% 40%, #000 40%, transparent 100%)',
        }}
      />

      {/* 6. Tactile Micro-Noise Texture */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: isLight ? 0.018 : 0.035,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
    </>
  )
}
