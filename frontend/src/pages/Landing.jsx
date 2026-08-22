import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import { Brain, Briefcase, User, ArrowRight, FileSearch, BarChart3, Sparkles, Sun, Moon } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { HeroIllustration, ResumeScanIllustration, InterviewIllustration, RankingIllustration } from '../components/Illustrations'
import { CardTilt, FloatingParticles } from '../components/MicroInteractions'
import { AnimatedBackground } from '../components/AnimatedBackground'

function CountUp({ end, suffix = '', duration = 1500 }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true
        const start = performance.now()
        const animate = (now) => {
          const progress = Math.min((now - start) / duration, 1)
          setCount(Math.floor((1 - Math.pow(1 - progress, 3)) * end))
          if (progress < 1) requestAnimationFrame(animate)
        }
        requestAnimationFrame(animate)
      }
    }, { threshold: 0.5 })
    observer.observe(el)
    return () => observer.disconnect()
  }, [end, duration])

  return <span ref={ref}>{count}{suffix}</span>
}

const roles = [
  'Software Engineer', 'Data Scientist', 'ML Engineer', 'DevOps Engineer',
  'Cybersecurity Analyst', 'Cloud Architect', 'Frontend Developer',
  'Backend Developer', 'Full Stack Developer', 'QA Engineer',
  'Data Engineer', 'Mobile Developer', 'UI/UX Designer', 'SRE',
  'AI/NLP Engineer', 'Network Engineer', 'Blockchain Developer',
  'Systems Analyst', 'DBA', 'Embedded Systems Engineer',
]

export default function Landing() {
  const { theme, toggleTheme } = useTheme()

  // Self-contained reveal observer (App.jsx observer runs before lazy page renders)
  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'))
      return
    }
    const timer = setTimeout(() => {
      const observer = new IntersectionObserver(
        (entries) => entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add('visible')
            observer.unobserve(e.target)
          }
        }),
        { threshold: 0.05 }
      )
      document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
      return () => observer.disconnect()
    }, 50)
    return () => clearTimeout(timer)
  }, [])

  return (
    <main style={{ minHeight: '100dvh', background: 'var(--color-bg)' }}>
      {/* Fixed top bar */}
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '12px 24px',
        background: 'color-mix(in srgb, var(--color-bg) 80%, transparent)',
        backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--color-border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'linear-gradient(135deg, var(--color-primary), #4f46e5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
          }}>
            <Brain size={16} />
          </div>
          <div style={{ fontWeight: 800, fontSize: 'var(--p-text-lg)', letterSpacing: '-0.3px', color: 'var(--color-fg)' }}>
            RecruitAI
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Link to="/login/candidate" className="btn btn-ghost btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
            Candidate Sign In
          </Link>
          <Link to="/login/company" className="btn btn-ghost btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
            Employer Sign In
          </Link>
          <button onClick={toggleTheme} className="btn-ghost btn-sm" style={{ padding: '6px 8px' }}
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}>
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </div>

      {/* Hero */}
      <section style={{ position: 'relative', padding: 'clamp(80px, 14vh, 160px) 24px 80px', maxWidth: 1100, margin: '0 auto', overflow: 'hidden' }}>
        <AnimatedBackground />
        <FloatingParticles count={30} color="rgba(59,130,246,0.3)" />

        <div className="landing-hero" style={{ position: 'relative', zIndex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'clamp(40px, 6vw, 80px)', alignItems: 'center' }}>
          {/* Left */}
          <div>
            <div className="hero-eyebrow" style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'var(--color-primary-muted)', border: '1px solid rgba(59,130,246,0.15)',
              borderRadius: 999, padding: '6px 16px', fontSize: 'var(--p-text-sm)',
              color: 'var(--color-primary)', marginBottom: 'var(--p-space-6)', fontWeight: 'var(--p-weight-semibold)',
            }}>
              <Sparkles size={14} /> AI-Powered Recruitment
            </div>

            <h1 className="hero-title" style={{
              fontSize: 'clamp(2.5rem, 5.5vw, 4rem)', fontWeight: 800, lineHeight: 1.08,
              letterSpacing: '-0.04em', marginBottom: 'var(--p-space-5)', color: 'var(--color-fg)', textWrap: 'balance',
            }}>
              Hire smarter.<br />
              <span className="gradient-text-shimmer">Grow faster.</span>
            </h1>

            <p className="hero-sub" style={{
              fontSize: 'var(--p-text-lg)', color: 'var(--color-fg-secondary)',
              maxWidth: 440, lineHeight: 1.6, marginBottom: 'var(--p-space-8)',
            }}>
              Match resumes to jobs with AI, run interviews, and track skill gaps — all in one platform.
            </p>

            <div className="hero-cta" style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <Link to="/register/company" className="btn btn-pulse" style={{ padding: '14px 28px', fontSize: 'var(--p-text-base)' }}>
                <Briefcase size={16} /> Post a Job <ArrowRight size={14} />
              </Link>
              <Link to="/register/candidate" className="btn btn-ghost" style={{ padding: '14px 28px', fontSize: 'var(--p-text-base)' }}>
                <User size={16} /> Find Work
              </Link>
            </div>
          </div>

          {/* Right — illustration */}
          <div className="landing-visual hero-visual" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div className="hero-illustration" style={{
              width: 'clamp(320px, 38vw, 460px)', height: 'clamp(320px, 38vw, 460px)',
              borderRadius: 'var(--p-radius-xl)', background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border)', boxShadow: 'var(--shadow-xl), var(--shadow-glow)',
              overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <HeroIllustration />
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="reveal" style={{ padding: '0 24px', maxWidth: 1000, margin: '0 auto' }}>
        <div className="stats-grid" style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--p-space-4)',
          background: 'var(--color-surface)', border: '1px solid var(--color-border)',
          borderRadius: 'var(--p-radius-xl)', padding: 'var(--p-space-6) var(--p-space-8)',
        }}>
          {[
            { end: 20, suffix: '+', label: 'IT Roles', color: 'var(--color-primary)' },
            { end: 92, suffix: '%', label: 'Match Accuracy', color: 'var(--color-success)' },
            { end: 3, suffix: 'x', label: 'Faster Hiring', color: 'var(--color-purple)' },
            { end: 24, suffix: '/7', label: 'AI Interviews', color: 'var(--color-orange)' },
          ].map((stat, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{
                fontSize: 'clamp(1.5rem, 3vw, 2rem)', fontWeight: 800,
                letterSpacing: '-0.03em', color: stat.color, fontVariantNumeric: 'tabular-nums',
              }}>
                <CountUp end={stat.end} suffix={stat.suffix} duration={1500 + i * 200} />
              </div>
              <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', marginTop: 'var(--p-space-1)' }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bento features */}
      <section className="reveal" style={{ padding: 'clamp(40px, 8vw, 80px) 24px', maxWidth: 1000, margin: '0 auto' }}>
        <h2 style={{ fontSize: 'clamp(1.75rem, 3.5vw, 2.25rem)', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 'var(--p-space-10)', textAlign: 'center', textWrap: 'balance' }}>
          How it works
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gridAutoFlow: 'dense', gap: 'var(--p-space-4)' }}>
          <CardTilt intensity={6} style={{ gridColumn: 'span 7' }} className="bento-large">
            <div className="reveal reveal-delay-1" style={{
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              borderRadius: 'var(--p-radius-xl)', padding: 'var(--p-space-7)',
              display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              minHeight: 260, overflow: 'hidden', position: 'relative', height: '100%',
            }}>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ width: 48, height: 48, borderRadius: 'var(--p-radius-lg)', background: 'var(--color-primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--p-space-5)' }}>
                  <FileSearch size={24} style={{ color: 'var(--color-primary)' }} />
                </div>
                <h3 style={{ fontSize: 'var(--p-text-2xl)', fontWeight: 700, marginBottom: 'var(--p-space-3)', letterSpacing: '-0.02em' }}>AI Resume Matching</h3>
                <p style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg-secondary)', lineHeight: 1.6, maxWidth: 360 }}>
                  Upload your CV. Our model extracts skills, education, and experience, then scores your fit against open roles using weighted formulas.
                </p>
              </div>
              <div style={{ position: 'absolute', right: -10, bottom: -10, width: 180, opacity: 0.7 }}><ResumeScanIllustration /></div>
            </div>
          </CardTilt>

          <CardTilt intensity={6} style={{ gridColumn: 'span 5' }} className="bento-small">
            <div className="reveal reveal-delay-2" style={{
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              borderRadius: 'var(--p-radius-xl)', padding: 'var(--p-space-6)',
              minHeight: 120, overflow: 'hidden', position: 'relative', height: '100%',
            }}>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ width: 40, height: 40, borderRadius: 'var(--p-radius-md)', background: 'var(--color-success-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--p-space-4)' }}>
                  <Brain size={20} style={{ color: 'var(--color-success)' }} />
                </div>
                <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, marginBottom: 'var(--p-space-2)', letterSpacing: '-0.01em' }}>Automated Interviews</h3>
                <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>MCQ, descriptive, and coding questions generated from job requirements.</p>
              </div>
              <div style={{ position: 'absolute', right: -5, bottom: -5, width: 120, opacity: 0.6 }}><InterviewIllustration /></div>
            </div>
          </CardTilt>

          <CardTilt intensity={6} style={{ gridColumn: 'span 5' }} className="bento-small">
            <div className="reveal reveal-delay-3" style={{
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              borderRadius: 'var(--p-radius-xl)', padding: 'var(--p-space-6)',
              minHeight: 120, overflow: 'hidden', position: 'relative', height: '100%',
            }}>
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ width: 40, height: 40, borderRadius: 'var(--p-radius-md)', background: 'var(--color-primary-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--p-space-4)' }}>
                  <BarChart3 size={20} style={{ color: 'var(--color-primary)' }} />
                </div>
                <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, marginBottom: 'var(--p-space-2)', letterSpacing: '-0.01em' }}>Candidate Ranking</h3>
                <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>Compare applicants by CV match, interview score, and skill gap.</p>
              </div>
              <div style={{ position: 'absolute', right: -5, bottom: -5, width: 120, opacity: 0.6 }}><RankingIllustration /></div>
            </div>
          </CardTilt>
        </div>
      </section>

      {/* Steps */}
      <section className="reveal" style={{ padding: 'clamp(48px, 8vw, 96px) 24px', maxWidth: 1000, margin: '0 auto' }}>
        <h2 style={{ fontSize: 'clamp(1.75rem, 3.5vw, 2.25rem)', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 'var(--p-space-10)', textAlign: 'center', textWrap: 'balance' }}>
          From application to hire in three steps
        </h2>
        <div className="steps-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--p-space-6)', position: 'relative' }}>
          <div style={{ position: 'absolute', top: 32, left: '16%', right: '16%', height: 2, background: 'linear-gradient(90deg, var(--color-primary), var(--color-success), var(--color-purple))', opacity: 0.3, zIndex: 0 }} />
          {[
            { num: '01', title: 'Upload Resume', desc: 'Candidate uploads CV. AI extracts skills, experience, and education in seconds.', icon: FileSearch, color: 'var(--color-primary)' },
            { num: '02', title: 'AI Interview', desc: 'Automated technical interview with MCQ, descriptive, and coding questions.', icon: Brain, color: 'var(--color-success)' },
            { num: '03', title: 'Get Ranked', desc: 'Compare candidates by CV match, interview score, and skill gap analysis.', icon: BarChart3, color: 'var(--color-purple)' },
          ].map((step, i) => (
            <div key={i} className={`reveal reveal-delay-${i + 1}`} style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
              <div style={{
                width: 64, height: 64, borderRadius: 'var(--p-radius-xl)',
                background: `color-mix(in srgb, ${step.color} 15%, transparent)`,
                border: `1px solid color-mix(in srgb, ${step.color} 30%, transparent)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto var(--p-space-5)',
                transition: 'all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1)', cursor: 'default',
              }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.1) translateY(-4px)'; e.currentTarget.style.boxShadow = `0 8px 24px color-mix(in srgb, ${step.color} 30%, transparent)`; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
              >
                <step.icon size={28} style={{ color: step.color }} />
              </div>
              <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: step.color, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 'var(--p-space-2)' }}>
                Step {step.num}
              </div>
              <h3 style={{ fontSize: 'var(--p-text-xl)', fontWeight: 700, marginBottom: 'var(--p-space-3)', letterSpacing: '-0.02em' }}>{step.title}</h3>
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.6, maxWidth: 280, margin: '0 auto' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Roles */}
      <section className="reveal" style={{ padding: 'clamp(32px, 6vw, 64px) 24px', maxWidth: 1000, margin: '0 auto' }}>
        <h2 style={{ fontSize: 'var(--p-text-xl)', fontWeight: 700, textAlign: 'center', marginBottom: 'var(--p-space-6)', letterSpacing: '-0.02em' }}>
          20 IT roles supported
        </h2>
        <div style={{ display: 'flex', gap: 'var(--p-space-2)', overflowX: 'auto', scrollSnapType: 'x mandatory', paddingBottom: 'var(--p-space-2)', WebkitOverflowScrolling: 'touch', scrollbarWidth: 'none' }}>
          {roles.map((r) => (
            <span key={r} style={{
              flexShrink: 0, scrollSnapAlign: 'start', display: 'inline-flex', alignItems: 'center',
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              borderRadius: 'var(--p-radius-md)', padding: '8px 16px',
              fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', whiteSpace: 'nowrap',
              transition: 'all 0.2s ease', cursor: 'default',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.color = 'var(--color-primary)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = ''; e.currentTarget.style.color = ''; }}
            >{r}</span>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="reveal" style={{ padding: 'clamp(48px, 8vw, 96px) 24px', textAlign: 'center', maxWidth: 600, margin: '0 auto' }}>
        <h2 style={{ fontSize: 'clamp(1.5rem, 3vw, 2.25rem)', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 'var(--p-space-4)', textWrap: 'balance' }}>
          Start hiring today
        </h2>
        <p style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg-secondary)', marginBottom: 'var(--p-space-7)', lineHeight: 1.6 }}>
          Create a free account. Post your first job in minutes.
        </p>
        <Link to="/register/company" className="btn btn-pulse" style={{ padding: '14px 32px', fontSize: 'var(--p-text-base)' }}>
          Get Started <ArrowRight size={14} />
        </Link>
        <div style={{ marginTop: 'var(--p-space-5)', fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>
          Already have an account?{' '}
          <Link to="/login/company">Company Login</Link> or{' '}
          <Link to="/login/candidate">Candidate Login</Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: 'var(--p-space-8) 24px', borderTop: '1px solid var(--color-border)', maxWidth: 1000, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--p-space-4)' }}>
          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>RecruitAI — AI-powered recruitment platform</div>
          <div style={{ display: 'flex', gap: 'var(--p-space-6)', fontSize: 'var(--p-text-sm)' }}>
            <Link to="/login/company" style={{ color: 'var(--color-fg-muted)' }}>Company Login</Link>
            <Link to="/login/candidate" style={{ color: 'var(--color-fg-muted)' }}>Candidate Login</Link>
            <Link to="/register/company" style={{ color: 'var(--color-fg-muted)' }}>Get Started</Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
