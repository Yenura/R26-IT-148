import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import {
  Brain, Briefcase, User, ArrowRight, FileSearch, BarChart3, Sun, Moon,
  CheckCircle2, ShieldCheck, Zap, Code, Award, Target, TrendingUp, Layers, ChevronRight,
  Terminal, Globe, Users, Play
} from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { HeroIllustration, ResumeScanIllustration, InterviewIllustration, RankingIllustration } from '../components/Illustrations'


function CountUp({ end, suffix = '', duration = 1500 }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    // Reduced motion: settle instantly instead of ticking.
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setCount(end)
      return
    }
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
  'Software Engineer', 'Data Scientist', 'Machine Learning Engineer', 'DevOps Engineer',
  'Cybersecurity Analyst', 'Cloud Solutions Architect', 'Frontend Developer',
  'Backend Developer', 'Full Stack Developer', 'QA/Test Automation Engineer',
  'Data Engineer', 'Mobile App Developer', 'UI/UX Designer', 'Site Reliability Engineer',
  'AI/NLP Engineer', 'Network Engineer', 'Blockchain Developer',
  'Business/Systems Analyst', 'Database Administrator', 'Embedded Systems Engineer',
]

export default function Landing() {
  const { theme, toggleTheme } = useTheme()
  const [activeTab, setActiveTab] = useState(0)

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'))
      return
    }
    let observer
    const timer = setTimeout(() => {
      observer = new IntersectionObserver(
        (entries) => entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add('visible')
            observer.unobserve(e.target)
          }
        }),
        { threshold: 0.05 }
      )
      document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
    }, 50)
    return () => {
      clearTimeout(timer)
      if (observer) observer.disconnect()
    }
  }, [])

  const features = [
    {
      id: 'screening',
      badge: 'Component 1 · SBERT Parser',
      title: 'Automated CV Screening & Role Classification',
      desc: 'Transforms raw PDF/DOCX resumes into verified competency embeddings. Computes education relevance, years of experience, and hard skill coverage.',
      color: 'var(--color-primary)',
      icon: FileSearch,
      stat: '98.4% Role Precision',
      demo: 'Extracts 40+ canonical tech skills, degrees, and calculates S_edu, S_exp, and S_skill.'
    },
    {
      id: 'interview',
      badge: 'Component 2 · Adaptive AI Exam',
      title: 'Interactive Multi-Modal Tech Interview Sandbox',
      desc: 'Conducts automated candidate technical interviews featuring timed MCQ concept probes, semantic descriptive evaluation, and an in-browser Python coding sandbox with live unit tests.',
      color: 'var(--color-purple)',
      icon: Code,
      stat: '100% Automated Scoring',
      demo: 'Instant test case validation, syntax evaluation, and weak-topic diagnostic extraction.'
    },
    {
      id: 'ranking',
      badge: 'Component 3 · LambdaMART LTR',
      title: 'Fair & Explainable Candidate Ranking Engine',
      desc: 'Combines Composite Screening Scores (CSS) with gradient-boosted LambdaMART Learning-to-Rank trees to rank top talent fairly without demographic bias.',
      color: 'var(--color-success)',
      icon: BarChart3,
      stat: '0.9414 NDCG@10',
      demo: 'Customizable recruiter weight sliders (w_cv / w_int) with PDF exportable ranking audit reports.'
    },
    {
      id: 'skillgap',
      badge: 'Component 4 · ML Career Roadmap',
      title: 'Actionable Skill Gap & Progress Tracking',
      desc: 'Trained on 20,000 engineering profiles to diagnose critical deficits and automatically generate targeted Coursera, Udemy, and Linux Foundation learning courses.',
      color: 'var(--color-orange)',
      icon: TrendingUp,
      stat: '0.9837 ROC-AUC',
      demo: 'What-If career simulation sandbox and automated sync from real interview weak spots.'
    }
  ]

  return (
    <main style={{ minHeight: '100dvh', background: 'var(--color-bg)' }}>
      {/* Fixed Frosted Top Bar */}
      <header style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '12px 24px',
        background: 'var(--navbar-bg, var(--material-bar))',
        backdropFilter: 'var(--navbar-blur, var(--material-blur))', WebkitBackdropFilter: 'var(--navbar-blur, var(--material-blur))',
        borderBottom: '1px solid var(--color-border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--p-white)'
          }}>
            <Brain size={16} color="var(--p-white)" strokeWidth={2.5} />
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
          <button
            onClick={toggleTheme} className="btn-ghost btn-sm" style={{ padding: '6px 8px' }}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}>
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        position: 'relative',
        padding: 'clamp(100px, 16vh, 170px) 24px 80px',
        maxWidth: 1200,
        margin: '0 auto',
        overflow: 'hidden'
      }}>
        <div className="landing-hero" style={{
          position: 'relative',
          zIndex: 1,
          maxWidth: 880,
          margin: '0 auto',
          textAlign: 'center'
        }}>
          {/* Hero copy — centered stack */}
          <div>
            <div className="hero-eyebrow" style={{
              fontSize: 'var(--p-text-xs)', fontWeight: 700,
              color: 'var(--color-fg-muted)', marginBottom: 'var(--p-space-4)',
              textTransform: 'uppercase', letterSpacing: '0.1em'
            }}>
              AI Recruitment Ecosystem
            </div>

            <h1 className="hero-title" style={{
              fontSize: 'clamp(2.75rem, 6vw, 5rem)',
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: '-0.03em',
              marginBottom: 'var(--p-space-5)',
              color: 'var(--color-fg)',
              textWrap: 'balance'
            }}>
              Screen Smarter.<br />
              <span style={{ color: 'var(--color-primary)' }}>Rank Fairer.</span><br />
              Hire Faster.
            </h1>

            <p className="hero-sub" style={{
              fontSize: 'var(--p-text-lg)',
              color: 'var(--color-fg-secondary)',
              maxWidth: 640,
              margin: '0 auto',
              lineHeight: 1.6,
              marginBottom: 'var(--p-space-7)'
            }}>
              Automate technical hiring from resume parsing and interactive coding interviews to LambdaMART candidate ranking and skill gap diagnosis.
            </p>

            {/* One filled pill plus one text link */}
            <div className="hero-cta" style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center' }}>
              <Link to="/register/candidate" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 'var(--p-text-base)', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <User size={16} /> Candidate Sign Up <ArrowRight size={15} />
              </Link>
              <Link to="/register/company" style={{ fontSize: 'var(--p-text-base)', fontWeight: 600, color: 'var(--color-primary)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Briefcase size={16} /> Post Jobs as Employer <ArrowRight size={15} />
              </Link>
            </div>

            {/* Key Value Badges */}
            <div style={{ display: 'flex', gap: 16, marginTop: 28, flexWrap: 'wrap', justifyContent: 'center', fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} /> 20 Specialized IT Roles
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} /> Automated Coding Sandbox
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} /> LambdaMART Fair Ranking
              </span>
            </div>
          </div>

          {/* Hero visual — product window below the copy */}
          <div className="landing-visual hero-visual" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: 'clamp(40px, 6vw, 64px)' }}>
            <div
              role="img"
              aria-label="Preview of the RecruitAI pipeline: CV match score 87, AI interview score 81, ranked number 1 of 24 candidates, shortlisted"
              style={{
              width: '100%', maxWidth: 680, textAlign: 'left',
              borderRadius: 14,
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border)',
              boxShadow: 'var(--shadow-xl)',
              overflow: 'hidden'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 14px', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f57' }} />
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#febc2e' }} />
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#28c840' }} />
                <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 600, color: 'var(--color-fg-muted)' }}>
                  RecruitAI — Pipeline
                </span>
                <span className="badge badge-green" style={{ marginLeft: 'auto' }}>Live</span>
              </div>

              {[
                { icon: FileSearch, title: 'CV Match', sub: 'S. Perera · Software Engineer', score: '87', bar: '87%' },
                { icon: Code, title: 'AI Interview', sub: 'SBERT semantic · 24 MCQs', score: '81', bar: '81%' },
              ].map((r) => (
                <div key={r.title} style={{ padding: '14px 16px 12px', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <r.icon size={16} style={{ color: 'var(--color-primary)', flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{r.title}</div>
                      <div style={{ fontSize: 11, color: 'var(--color-fg-muted)' }}>{r.sub}</div>
                    </div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--color-fg)', fontVariantNumeric: 'tabular-nums' }}>
                      {r.score}
                    </div>
                  </div>
                  <div className="progress-bar" style={{ marginTop: 10 }}>
                    <div style={{ width: r.bar }} />
                  </div>
                </div>
              ))}

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '14px 16px' }}>
                <BarChart3 size={16} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>LambdaMART Rank</div>
                  <div style={{ fontSize: 11, color: 'var(--color-fg-muted)' }}>#1 of 24 candidates</div>
                </div>
                <span className="badge badge-green">Shortlisted</span>
              </div>

              <Link to="/register/candidate" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, padding: '11px', borderTop: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-primary)' }}>
                Try the live demo <ArrowRight size={13} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Stats Strip */}
      <section className="reveal" style={{ padding: '0 24px', maxWidth: 1120, margin: '0 auto' }}>
        <div className="stats-grid" style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--p-space-4)',
          background: 'var(--color-surface)', border: '1px solid var(--color-border)',
          borderRadius: 'var(--p-radius-xl)', padding: 'var(--p-space-6) var(--p-space-8)',
          boxShadow: 'var(--shadow-md)'
        }}>
          {[
            { end: 20, suffix: '+', label: 'Canonical IT Roles', color: 'var(--color-primary)', helper: 'Multi-class SBERT embeddings' },
            { end: 94, suffix: '%', label: 'NDCG@10 Ranking Score', color: 'var(--color-success)', helper: 'LambdaMART LTR benchmark' },
            { end: 93, suffix: '%', label: 'Skill Gap ML Accuracy', color: 'var(--color-purple)', helper: 'Trained on 20,000 dataset' },
            { end: 100, suffix: '%', label: 'Instant Evaluation', color: 'var(--color-orange)', helper: 'Zero manual grading delays' },
          ].map((stat, i) => (
            <div key={stat.label} style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{
                fontSize: 'clamp(1.75rem, 3vw, 2.25rem)', fontWeight: 800,
                letterSpacing: '-0.03em', color: stat.color, fontVariantNumeric: 'tabular-nums',
                fontFamily: 'var(--p-font-sans)'
              }}>
                <CountUp end={stat.end} suffix={stat.suffix} duration={1500 + i * 200} />
              </div>
              <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 4 }}>
                {stat.label}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                {stat.helper}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Choose-your-path tiles — one idea per tile (§26) */}
      <section className="reveal" style={{ padding: 'clamp(32px, 6vw, 64px) 24px 0', maxWidth: 1120, margin: '0 auto' }}>
        <div className="path-tiles" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {[
            { icon: User, title: 'For Candidates', desc: 'Match your CV, practice interviews, close skill gaps.', cta: 'Find your fit', to: '/register/candidate' },
            { icon: Briefcase, title: 'For Employers', desc: 'Post roles, rank applicants fairly, shortlist faster.', cta: 'Hire smarter', to: '/register/company' },
          ].map((t) => (
            <div key={t.title} className="card glass-card" style={{
              padding: 'var(--p-space-6)', margin: 0,
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-xl)'
            }}>
              <t.icon size={22} style={{ color: 'var(--color-primary)', marginBottom: 12 }} />
              <h3 style={{ fontSize: 'var(--p-text-xl)', fontWeight: 800, letterSpacing: '-0.02em', margin: '0 0 6px', color: 'var(--color-fg)' }}>
                {t.title}
              </h3>
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', margin: '0 0 16px', lineHeight: 1.6 }}>
                {t.desc}
              </p>
              <Link to={t.to} style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-primary)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                {t.cta} <ArrowRight size={14} />
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Platform Architecture Showcase — alternating band */}
      <div style={{ background: 'var(--color-bg-soft)', borderTop: '1px solid var(--color-border-subtle)', borderBottom: '1px solid var(--color-border-subtle)' }}>
      <section className="reveal" style={{ padding: 'clamp(60px, 10vw, 100px) 24px', maxWidth: 1120, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 'var(--p-space-8)' }}>
          <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary)', letterSpacing: '0.1em', marginBottom: 8 }}>
            End-To-End Architecture
          </div>
          <h2 style={{ fontSize: 'clamp(2rem, 4vw, 3.5rem)', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--color-fg)', margin: 0, textWrap: 'balance' }}>
            Four Intelligent Microservice Engines
          </h2>
          <p style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg-secondary)', maxWidth: 640, margin: '12px auto 0', lineHeight: 1.6 }}>
            Each component addresses a distinct phase of modern tech recruiting with specialized AI models and explainable scoring.
          </p>
        </div>

        {/* Feature Tabs Bar */}
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 'var(--p-space-6)' }}>
          {features.map((f, idx) => (
            <button
              key={f.id}
              onClick={() => setActiveTab(idx)}
              className={`btn btn-sm ${activeTab === idx ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '8px 16px', fontSize: 'var(--p-text-xs)', fontWeight: 700, borderRadius: 'var(--radius-full)' }}
            >
              <f.icon size={14} /> {f.badge.split('·')[0].trim()}
            </button>
          ))}
        </div>

        {/* Active Feature Showcase Card */}
        <div className="card glass-card" style={{
          padding: 'var(--p-space-8)',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-xl)',
          display: 'grid',
          gridTemplateColumns: '1.1fr 0.9fr',
          gap: 40,
          alignItems: 'center',
          overflow: 'hidden'
        }}>
          <div key={activeTab} style={{ animation: 'tab-fade-in 0.35s cubic-bezier(0.16, 1, 0.3, 1)' }}>
            <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: features[activeTab].color, letterSpacing: '0.08em', marginBottom: 6 }}>
              {features[activeTab].badge}
            </div>
            <h3 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--color-fg)', margin: '0 0 12px 0', letterSpacing: '-0.02em' }}>
              {features[activeTab].title}
            </h3>
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.65, marginBottom: 20 }}>
              {features[activeTab].desc}
            </p>

            <div style={{
              padding: 16,
              background: 'var(--color-bg)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border-subtle)',
              marginBottom: 24
            }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                Diagnostic Capability:
              </div>
              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg)', fontWeight: 500 }}>
                {features[activeTab].demo}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ padding: '8px 14px', background: 'var(--color-primary-muted)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(10, 132, 255, 0.25)' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-primary)' }}>
                  {features[activeTab].stat}
                </span>
              </div>
              <Link to="/register/candidate" style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                Explore Sandbox <ArrowRight size={13} />
              </Link>
            </div>
          </div>

          <div style={{
            height: 280,
            background: 'var(--color-bg)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24
          }}>
            {activeTab === 0 && <ResumeScanIllustration />}
            {activeTab === 1 && <InterviewIllustration />}
            {activeTab === 2 && <RankingIllustration />}
            {activeTab === 3 && <HeroIllustration />}
          </div>
        </div>
      </section>
      </div>

      {/* 20 IT Roles Supported Carousel */}
      <section className="reveal" style={{ padding: 'clamp(32px, 6vw, 64px) 24px', maxWidth: 1120, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <h2 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 800, color: 'var(--color-fg)', letterSpacing: '-0.02em', margin: 0 }}>
            20 Enterprise IT Domains & Role Taxonomies
          </h2>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            Tailored skill lexicons, benchmark weights, and adaptive interview question banks.
          </p>
        </div>

        <div style={{
          display: 'flex', gap: 8, overflowX: 'auto',
          scrollSnapType: 'x mandatory', paddingBottom: 8,
          WebkitOverflowScrolling: 'touch', scrollbarWidth: 'none'
        }}
          tabIndex={0}
          role="region"
          aria-label="Supported IT roles — scroll horizontally to browse all 20"
        >
          {roles.map((r) => (
            <span
              key={r}
              style={{
                flexShrink: 0, scrollSnapAlign: 'start', display: 'inline-flex', alignItems: 'center',
                background: 'var(--color-surface)', border: '1px solid var(--color-border)',
                borderRadius: 'var(--p-radius-md)', padding: '8px 16px',
                fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', whiteSpace: 'nowrap',
                fontWeight: 600, transition: 'border-color 0.2s ease, color 0.2s ease, background-color 0.2s ease', cursor: 'default'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--color-primary)';
                e.currentTarget.style.color = 'var(--color-primary)';
                e.currentTarget.style.background = 'var(--color-primary-muted)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--color-border)';
                e.currentTarget.style.color = 'var(--color-fg-secondary)';
                e.currentTarget.style.background = 'var(--color-surface)';
              }}
            >
              {r}
            </span>
          ))}
        </div>
      </section>

      {/* CTA Conversion Box */}
      <section className="reveal" style={{ padding: 'clamp(60px, 8vw, 100px) 24px', textAlign: 'center', maxWidth: 720, margin: '0 auto' }}>
        <div className="card glass-card" style={{
          padding: 'var(--p-space-8)',
          background: 'linear-gradient(180deg, var(--color-bg-elevated) 0%, var(--color-surface) 100%)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-xl)'
        }}>
          <h2 style={{ fontSize: 'clamp(1.75rem, 3vw, 2.35rem)', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 12, color: 'var(--color-fg)', textWrap: 'balance' }}>
            Transform Your Hiring Pipeline Today
          </h2>
          <p style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg-secondary)', marginBottom: 28, lineHeight: 1.6, maxWidth: 520, margin: '0 auto 28px' }}>
            Join forward-thinking hiring teams and candidates leveraging transparent, explainable machine learning recruitment.
          </p>

          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register/company" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: 'var(--p-text-base)' }}>
              Start as Employer <ArrowRight size={15} />
            </Link>
            <Link to="/register/candidate" className="btn btn-ghost" style={{ padding: '14px 32px', fontSize: 'var(--p-text-base)' }}>
              Candidate Sign Up
            </Link>
          </div>

          <div style={{ marginTop: 24, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            Already registered?{' '}
            <Link to="/login/company" style={{ color: 'var(--color-purple)', fontWeight: 700 }}>Employer Sign In</Link> ·{' '}
            <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Candidate Sign In</Link>
          </div>
        </div>
      </section>

    </main>
  )
}
