import { Link } from 'react-router-dom'
import { Brain, Briefcase, User, ArrowRight, FileSearch, BarChart3 } from 'lucide-react'

const features = [
  {
    icon: FileSearch,
    title: 'AI Resume Matching',
    desc: 'Upload your CV. Our model extracts skills, education, and experience, then scores your fit against open roles.',
  },
  {
    icon: Brain,
    title: 'Automated Interviews',
    desc: 'MCQ, descriptive, and coding questions generated from job requirements. Evaluated by semantic scoring.',
  },
  {
    icon: BarChart3,
    title: 'Candidate Ranking',
    desc: 'Companies compare applicants by CV match, interview performance, and skill gap analysis in one view.',
  },
]

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
      {/* Hero — stacked center, ambient gradient background */}
      <section style={{
        position: 'relative',
        padding: 'clamp(80px, 12vh, 140px) 24px 60px',
        textAlign: 'center',
        maxWidth: 720,
        margin: '0 auto',
        overflow: 'hidden',
      }}>
        {/* Ambient radial gradient behind hero */}
        <div style={{
          position: 'absolute',
          top: '-40%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '140%',
          height: '120%',
          background: 'radial-gradient(ellipse at center, var(--color-primary-muted) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 0,
        }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Eyebrow — 1 max on entire page (design-taste-frontend eyebrow restraint) */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 999,
            padding: '6px 16px',
            fontSize: 'var(--p-text-sm)',
            color: 'var(--color-fg-muted)',
            marginBottom: 'var(--p-space-6)',
          }}>
            <Brain size={15} style={{ color: 'var(--color-primary)' }} />
            AI-Powered Recruitment
          </div>

          {/* Headline — max 2 lines (gpt-taste 2-line iron rule) */}
          <h1 style={{
            fontSize: 'clamp(2.25rem, 5vw, 3.5rem)',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            marginBottom: 'var(--p-space-4)',
            color: 'var(--color-fg)',
          }}>
            Hire smarter.<br />
            <span style={{ color: 'var(--color-primary)' }}>Grow faster.</span>
          </h1>

          {/* Subtext — max 20 words (design-taste-frontend 4.7) */}
          <p style={{
            fontSize: 'var(--p-text-lg)',
            color: 'var(--color-fg-secondary)',
            maxWidth: 520,
            margin: '0 auto',
            lineHeight: 1.6,
            marginBottom: 'var(--p-space-8)',
          }}>
            Match resumes to jobs with AI, run interviews, and track skill gaps in one platform.
          </p>

          {/* CTAs — one primary, one secondary (design-taste-frontend 4.5) */}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register/company" className="btn" style={{ padding: '12px 24px', fontSize: 'var(--p-text-base)' }}>
              <Briefcase size={16} /> Post a Job <ArrowRight size={14} />
            </Link>
            <Link to="/register/candidate" className="btn btn-ghost" style={{ padding: '12px 24px', fontSize: 'var(--p-text-base)' }}>
              <User size={16} /> Find Work
            </Link>
          </div>
        </div>
      </section>

      {/* Features — asymmetric bento grid (gpt-taste 4, design-taste-frontend 4.3) */}
      <section className="reveal" style={{ padding: 'clamp(40px, 8vw, 80px) 24px', maxWidth: 960, margin: '0 auto' }}>
        <h2 style={{
          fontSize: 'var(--p-text-2xl)',
          fontWeight: 800,
          letterSpacing: '-0.02em',
          marginBottom: 'var(--p-space-8)',
          textAlign: 'center',
        }}>
          How it works
        </h2>
        {/* Bento: 1 large + 2 stacked (asymmetric, not 3 equal cards) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gridAutoFlow: 'dense',
          gap: 'var(--p-space-4)',
        }}>
          {/* Large feature card — spans 7 cols */}
          <div style={{
            gridColumn: 'span 7',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--p-radius-lg)',
            padding: 'var(--p-space-6)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            minHeight: 220,
          }}>
            <div>
              <div style={{
                width: 40, height: 40,
                borderRadius: 'var(--p-radius-md)',
                background: 'var(--color-primary-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 'var(--p-space-4)',
              }}>
                <FileSearch size={20} style={{ color: 'var(--color-primary)' }} />
              </div>
              <h3 style={{ fontSize: 'var(--p-text-xl)', fontWeight: 700, marginBottom: 'var(--p-space-2)' }}>
                AI Resume Matching
              </h3>
              <p style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>
                Upload your CV. Our model extracts skills, education, and experience, then scores your fit against open roles using weighted formulas.
              </p>
            </div>
          </div>

          {/* Two smaller cards — stacked in remaining 5 cols */}
          <div style={{
            gridColumn: 'span 5',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--p-radius-lg)',
            padding: 'var(--p-space-5)',
            minHeight: 100,
          }}>
            <div style={{
              width: 36, height: 36,
              borderRadius: 'var(--p-radius-md)',
              background: 'var(--color-success-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 'var(--p-space-3)',
            }}>
              <Brain size={18} style={{ color: 'var(--color-success)' }} />
            </div>
            <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, marginBottom: 'var(--p-space-1)' }}>
              Automated Interviews
            </h3>
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>
              MCQ, descriptive, and coding questions generated from job requirements.
            </p>
          </div>

          <div style={{
            gridColumn: 'span 5',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--p-radius-lg)',
            padding: 'var(--p-space-5)',
            minHeight: 100,
          }}>
            <div style={{
              width: 36, height: 36,
              borderRadius: 'var(--p-radius-md)',
              background: 'var(--color-primary-muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 'var(--p-space-3)',
            }}>
              <BarChart3 size={18} style={{ color: 'var(--color-primary)' }} />
            </div>
            <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, marginBottom: 'var(--p-space-1)' }}>
              Candidate Ranking
            </h3>
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>
              Compare applicants by CV match, interview score, and skill gap.
            </p>
          </div>
        </div>
      </section>

      {/* Roles — horizontal scroll-snap (design-taste-frontend 4.9: long lists need different UI) */}
      <section className="reveal" style={{ padding: 'clamp(32px, 6vw, 64px) 24px', maxWidth: 960, margin: '0 auto' }}>
        <h2 style={{
          fontSize: 'var(--p-text-xl)',
          fontWeight: 700,
          textAlign: 'center',
          marginBottom: 'var(--p-space-5)',
        }}>
          20 IT roles supported
        </h2>
        <div style={{
          display: 'flex',
          gap: 'var(--p-space-2)',
          overflowX: 'auto',
          scrollSnapType: 'x mandatory',
          paddingBottom: 'var(--p-space-2)',
          WebkitOverflowScrolling: 'touch',
        }}>
          {roles.map((r) => (
            <span key={r} style={{
              flexShrink: 0,
              scrollSnapAlign: 'start',
              display: 'inline-flex',
              alignItems: 'center',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--p-radius-sm)',
              padding: 'var(--p-space-1) var(--p-space-3)',
              fontSize: 'var(--p-text-sm)',
              color: 'var(--color-fg-secondary)',
              whiteSpace: 'nowrap',
            }}>
              {r}
            </span>
          ))}
        </div>
      </section>

      {/* CTA — single strong action (gpt-taste AIDA) */}
      <section className="reveal" style={{
        padding: 'clamp(48px, 8vw, 96px) 24px',
        textAlign: 'center',
        maxWidth: 600,
        margin: '0 auto',
      }}>
        <h2 style={{
          fontSize: 'clamp(1.5rem, 3vw, 2rem)',
          fontWeight: 800,
          letterSpacing: '-0.02em',
          marginBottom: 'var(--p-space-3)',
        }}>
          Start hiring today
        </h2>
        <p style={{
          fontSize: 'var(--p-text-base)',
          color: 'var(--color-fg-secondary)',
          marginBottom: 'var(--p-space-6)',
        }}>
          Create a free account. Post your first job in minutes.
        </p>
        <Link to="/register/company" className="btn" style={{ padding: '12px 28px', fontSize: 'var(--p-text-base)' }}>
          Get Started <ArrowRight size={14} />
        </Link>
        <div style={{ marginTop: 'var(--p-space-4)', fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>
          Already have an account?{' '}
          <Link to="/login/company">Company Login</Link> or{' '}
          <Link to="/login/candidate">Candidate Login</Link>
        </div>
      </section>
    </main>
  )
}
