import React from 'react'
import { useLocation } from 'react-router-dom'

export default function GlobalBackground() {
  const location = useLocation()
  const path = location.pathname

  const isSkillGap = path.includes('skill-gap')
  const isProgress = path.includes('progress')
  const isRecruiter = path.includes('company') || path.includes('pipeline')

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: -1,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: 'radial-gradient(ellipse 90% 70% at 50% 25%, #0f0f1a 0%, #050508 100%)',
      }}
    >
      {/* Subtle Grid Dot Matrix Overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
          opacity: 0.65,
          maskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, #000 30%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, #000 30%, transparent 100%)',
        }}
      />

      {/* Subtle Tactile Noise Texture */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.025,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Floating Animated Gradient Orb 1: Indigo/Blue (Top-Left) */}
      <div
        className="floating-orb-1"
        style={{
          position: 'absolute',
          top: '-10%',
          left: '-5%',
          width: '550px',
          height: '550px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.16) 0%, rgba(79, 70, 229, 0.06) 50%, transparent 70%)',
          filter: 'blur(75px)',
          willChange: 'transform',
        }}
      />

      {/* Floating Animated Gradient Orb 2: Cyan/Emerald (Bottom-Right) */}
      <div
        className="floating-orb-2"
        style={{
          position: 'absolute',
          bottom: '-15%',
          right: '-5%',
          width: '500px',
          height: '500px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.13) 0%, rgba(6, 182, 212, 0.05) 50%, transparent 70%)',
          filter: 'blur(70px)',
          willChange: 'transform',
        }}
      />

      {/* Floating Animated Gradient Orb 3: Violet (Center/Mid) */}
      <div
        className="floating-orb-3"
        style={{
          position: 'absolute',
          top: '35%',
          left: '30%',
          width: '450px',
          height: '450px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.10) 0%, rgba(139, 92, 246, 0.03) 50%, transparent 70%)',
          filter: 'blur(65px)',
          willChange: 'transform',
        }}
      />

      {/* Page-Specific Atmospheric Tints */}
      {isSkillGap && (
        <div
          style={{
            position: 'absolute',
            top: '15%',
            right: '10%',
            width: '450px',
            height: '450px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(244, 63, 94, 0.12) 0%, rgba(245, 158, 11, 0.05) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.6s ease',
          }}
        />
      )}

      {isProgress && (
        <div
          style={{
            position: 'absolute',
            top: '20%',
            right: '15%',
            width: '450px',
            height: '450px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.14) 0%, rgba(99, 102, 241, 0.06) 50%, transparent 70%)',
            filter: 'blur(80px)',
            transition: 'opacity 0.6s ease',
          }}
        />
      )}

      {isRecruiter && (
        <div
          style={{
            position: 'absolute',
            top: '10%',
            right: '5%',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.13) 0%, rgba(99, 102, 241, 0.07) 50%, transparent 70%)',
            filter: 'blur(85px)',
            transition: 'opacity 0.6s ease',
          }}
        />
      )}
    </div>
  )
}
