import { useEffect, useRef, useCallback } from 'react'

export function useRipple() {
  const ref = useRef(null)

  const createRipple = useCallback((e) => {
    const button = ref.current
    if (!button) return

    const rect = button.getBoundingClientRect()
    const ripple = document.createElement('span')
    const size = Math.max(rect.width, rect.height)

    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${e.clientX - rect.left - size / 2}px;
      top: ${e.clientY - rect.top - size / 2}px;
      background: rgba(255,255,255,0.2);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple-expand 0.6s ease-out forwards;
      pointer-events: none;
    `

    button.appendChild(ripple)
    setTimeout(() => ripple.remove(), 600)
  }, [])

  useEffect(() => {
    const button = ref.current
    if (!button) return
    button.addEventListener('click', createRipple)
    return () => button.removeEventListener('click', createRipple)
  }, [createRipple])

  return ref
}

export function RippleButton({ children, style, ...props }) {
  const rippleRef = useRipple()

  return (
    <>
      <style>{`
        @keyframes ripple-expand {
          to { transform: scale(2.5); opacity: 0; }
        }
      `}</style>
      <button
        ref={rippleRef}
        style={{ position: 'relative', overflow: 'hidden', ...style }}
        {...props}
      >
        {children}
      </button>
    </>
  )
}

export function CardTilt({ children, style, intensity = 8 }) {
  const cardRef = useRef(null)

  useEffect(() => {
    const card = cardRef.current
    if (!card) return

    const handleMove = (e) => {
      const rect = card.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      card.style.transform = `
        perspective(600px)
        rotateY(${x * intensity}deg)
        rotateX(${-y * intensity}deg)
        translateY(-3px)
        scale(1.01)
      `
    }

    const handleLeave = () => {
      card.style.transform = ''
      card.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.1, 0.25, 1)'
    }

    const handleEnter = () => {
      card.style.transition = 'transform 0.15s ease-out'
    }

    card.addEventListener('mousemove', handleMove)
    card.addEventListener('mouseleave', handleLeave)
    card.addEventListener('mouseenter', handleEnter)

    return () => {
      card.removeEventListener('mousemove', handleMove)
      card.removeEventListener('mouseleave', handleLeave)
      card.removeEventListener('mouseenter', handleEnter)
    }
  }, [intensity])

  return (
    <div ref={cardRef} style={{ transition: 'transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1)', ...style }}>
      {children}
    </div>
  )
}

export function FloatingParticles({ count = 30, color = 'rgba(59,130,246,0.25)' }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()

    const w = canvas.offsetWidth
    const h = canvas.offsetHeight

    const particles = Array.from({ length: count }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 3 + 1.5,
      opacity: Math.random() * 0.6 + 0.2,
    }))

    const animate = () => {
      ctx.clearRect(0, 0, w, h)

      particles.forEach(p => {
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0 || p.x > w) p.vx *= -1
        if (p.y < 0 || p.y > h) p.vy *= -1

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = color.replace(/[\d.]+\)$/, `${p.opacity})`)
        ctx.fill()
      })

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 120) {
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.strokeStyle = color.replace(/[\d.]+\)$/, `${0.15 * (1 - dist / 120)})`)
            ctx.lineWidth = 0.8
            ctx.stroke()
          }
        }
      }

      animId = requestAnimationFrame(animate)
    }
    animate()

    return () => cancelAnimationFrame(animId)
  }, [count, color])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  )
}
