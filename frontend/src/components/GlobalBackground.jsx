import React from 'react'
import { useLocation } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

export default function GlobalBackground() {
  const location = useLocation()
  const path = location.pathname
  const { theme } = useTheme()

  const isSkillGap = path.includes('skill-gap')
  const isProgress = path.includes('progress')
  const isRecruiter = path.includes('company') || path.includes('pipeline')

  return (
    <div
      aria-hidden="true"
      className="global-bg-container"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: -1,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      {/* 1. Grid Pattern Overlay */}
      <div className="grid-overlay" />

      {/* 2. Tactile Noise Texture Overlay */}
      <div className="noise-overlay" />

      {/* 3. Floating Animated Gradient Orbs */}
      <div className="orb-1" />
      <div className="orb-2" />
      <div className="orb-3" />

      {/* 4. Page-Specific Ambient Tints */}
      {isSkillGap && (
        <div
          className="page-tint-orb skillgap"
          style={{
            position: 'fixed',
            top: '15%',
            right: '10%',
            width: '450px',
            height: '450px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(239, 68, 68, 0.12) 0%, rgba(245, 158, 11, 0.05) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.6s ease',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
      )}

      {isProgress && (
        <div
          className="page-tint-orb progress"
          style={{
            position: 'fixed',
            top: '20%',
            right: '15%',
            width: '450px',
            height: '450px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.14) 0%, rgba(99, 102, 241, 0.06) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.6s ease',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
      )}

      {isRecruiter && (
        <div
          className="page-tint-orb recruiter"
          style={{
            position: 'fixed',
            top: '10%',
            right: '5%',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(139, 92, 246, 0.13) 0%, rgba(99, 102, 241, 0.07) 50%, transparent 70%)',
            filter: 'blur(85px)',
            transition: 'opacity 0.6s ease',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />
      )}
    </div>
  )
}
