export function AnimatedBackground() {
  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      overflow: 'hidden',
      pointerEvents: 'none',
      zIndex: 0,
    }}>
      {/* Animated gradient blob — top left */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        left: '-5%',
        width: 'clamp(300px, 40vw, 600px)',
        height: 'clamp(300px, 40vw, 600px)',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)',
        filter: 'blur(60px)',
        animation: 'blob-drift-1 12s ease-in-out infinite',
      }} />

      {/* Animated gradient blob — right side */}
      <div style={{
        position: 'absolute',
        top: '5%',
        right: '-8%',
        width: 'clamp(250px, 35vw, 500px)',
        height: 'clamp(250px, 35vw, 500px)',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 70%)',
        filter: 'blur(50px)',
        animation: 'blob-drift-2 15s ease-in-out infinite',
      }} />

      {/* Animated gradient blob — bottom center */}
      <div style={{
        position: 'absolute',
        bottom: '-15%',
        left: '30%',
        width: 'clamp(200px, 30vw, 450px)',
        height: 'clamp(200px, 30vw, 450px)',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)',
        filter: 'blur(40px)',
        animation: 'blob-drift-3 18s ease-in-out infinite',
      }} />

      {/* Grid pattern */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `
          linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '60px 60px',
        maskImage: 'radial-gradient(ellipse 80% 60% at 50% 50%, black 30%, transparent 80%)',
        WebkitMaskImage: 'radial-gradient(ellipse 80% 60% at 50% 50%, black 30%, transparent 80%)',
      }} />

      {/* Subtle scan line */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(59,130,246,0.15), transparent)',
        animation: 'scan-line 6s linear infinite',
        willChange: 'transform',
      }} />

      <style>{`
        @keyframes blob-drift-1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, 20px) scale(1.05); }
          66% { transform: translate(-20px, 30px) scale(0.95); }
        }
        @keyframes blob-drift-2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(-25px, 15px) scale(1.08); }
          66% { transform: translate(15px, -25px) scale(0.92); }
        }
        @keyframes blob-drift-3 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(20px, -20px) scale(1.1); }
        }
        @keyframes scan-line {
          0% { transform: translateY(0); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
          .animated-bg-scan { animation: none !important; }
        }
      `}</style>
    </div>
  )
}
