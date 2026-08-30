export function AnimatedBackground() {
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      overflow: 'hidden',
      pointerEvents: 'none',
      zIndex: 0,
    }}>
      <div style={{
        position: 'absolute',
        top: '-10%',
        left: '-5%',
        width: 'clamp(300px, 40vw, 600px)',
        height: 'clamp(300px, 40vw, 600px)',
        borderRadius: '50%',
        background: 'radial-gradient(circle, var(--color-primary-muted) 0%, transparent 70%)',
        filter: 'blur(80px)',
        opacity: 0.5,
      }} />
      <div style={{
        position: 'absolute',
        top: '5%',
        right: '-8%',
        width: 'clamp(250px, 35vw, 500px)',
        height: 'clamp(250px, 35vw, 500px)',
        borderRadius: '50%',
        background: 'radial-gradient(circle, var(--color-success-muted) 0%, transparent 70%)',
        filter: 'blur(80px)',
        opacity: 0.4,
      }} />
    </div>
  )
}
