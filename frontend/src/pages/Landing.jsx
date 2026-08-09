import { Link } from 'react-router-dom'
import { Brain, Briefcase, User, ArrowRight, CheckCircle, BarChart3, FileSearch, Target } from 'lucide-react'

export default function Landing() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      {/* Hero */}
      <div style={{ padding: '80px 24px 60px', textAlign: 'center', maxWidth: 800, margin: '0 auto' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 999, padding: '6px 16px', fontSize: 13, color: 'var(--text-muted)', marginBottom: 24 }}>
          <Brain size={16} style={{ color: 'var(--accent)' }} /> AI-Powered Recruitment
        </div>
        <h1 style={{ fontSize: 48, fontWeight: 900, lineHeight: 1.1, marginBottom: 16 }}>
          Hire Smarter.<br /><span style={{ color: 'var(--accent)' }}>Grow Faster.</span>
        </h1>
        <p style={{ fontSize: 18, color: 'var(--text-muted)', maxWidth: 560, margin: '0 auto 40px', lineHeight: 1.6 }}>
          Match resumes to jobs with AI, run interviews, rank candidates, and track skill gaps — all in one platform.
        </p>

        {/* CTAs */}
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/register/company" className="btn" style={{ padding: '14px 28px', fontSize: 15 }}>
            <Briefcase size={18} /> I'm Hiring <ArrowRight size={16} />
          </Link>
          <Link to="/register/candidate" className="btn btn-accent2" style={{ padding: '14px 28px', fontSize: 15 }}>
            <User size={18} /> I'm Looking for Work <ArrowRight size={16} />
          </Link>
        </div>

        <div style={{ marginTop: 24, fontSize: 13, color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login/company">Company Login</Link> or <Link to="/login/candidate">Candidate Login</Link>
        </div>
      </div>

      {/* Features */}
      <div style={{ padding: '60px 24px', maxWidth: 1000, margin: '0 auto' }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, textAlign: 'center', marginBottom: 40 }}>How It Works</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20 }}>
          {[
            { icon: FileSearch, title: 'Upload Resume', desc: 'Upload PDF, DOCX, or paste text. AI extracts skills, experience, and education.', color: 'var(--accent)' },
            { icon: Brain, title: 'AI Matching', desc: 'Semantic matching scores your fit against job requirements with weighted formulas.', color: 'var(--accent-2)' },
            { icon: BarChart3, title: 'Rank Candidates', desc: 'Companies rank applicants by CV match, interview score, and skill gaps.', color: 'var(--accent)' },
            { icon: Target, title: 'Skill Gap Analysis', desc: 'Identify missing skills and get a personalized learning roadmap.', color: 'var(--accent-2)' },
          ].map((f) => (
            <div key={f.title} className="card" style={{ padding: 24, textAlign: 'center' }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: `${f.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                <f.icon size={24} style={{ color: f.color }} />
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Roles */}
      <div style={{ padding: '40px 24px 80px', maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, marginBottom: 16 }}>20 Roles Supported</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
          {['Software Engineer','Data Scientist','ML Engineer','DevOps Engineer','Cybersecurity Analyst','Cloud Architect','DBA','Frontend Developer','Backend Developer','Mobile Developer','Full Stack Developer','QA Engineer','Data Engineer','SRE','UI/UX Designer','Network Engineer','Systems Analyst','AI/NLP Engineer','Blockchain Developer','Embedded Systems Engineer'].map((r) => (
            <span key={r} className="chip" style={{ fontSize: 12 }}>{r}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
