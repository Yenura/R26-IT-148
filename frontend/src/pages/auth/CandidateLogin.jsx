import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft, Sparkles, Eye, EyeOff } from 'lucide-react'
import { C0 } from '../../api'

export default function CandidateLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e?.preventDefault()
    if (!email || !password) return toast.error('Please enter your email and password')
    setBusy(true)
    try {
      const r = await C0.post('/auth/login/candidate', { email: email.trim(), password })
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'candidate')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || '')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Welcome back to RecruitAI!')
      navigate('/candidate/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid candidate credentials')
    } finally {
      setBusy(false)
    }
  }

  const fillDemo = () => {
    setEmail('candidate@example.com')
    setPassword('candidate123')
    toast.success('Demo candidate credentials loaded')
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(ellipse 80% 80% at 50% -20%, rgba(59, 130, 246, 0.15), rgba(9, 9, 11, 0))',
      backgroundColor: 'var(--color-bg)',
      padding: 24,
      position: 'relative'
    }}>
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column', zIndex: 1 }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <ArrowLeft size={14} /> Back to Platform Overview
        </Link>

        {/* Brand Badge */}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            margin: '0 auto 14px',
            width: 52,
            height: 52,
            borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, var(--color-primary), #6366f1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 8px 24px rgba(59, 130, 246, 0.35)'
          }}>
            <Brain size={28} />
          </div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0, letterSpacing: '-0.02em' }}>
            Candidate Portal
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Sign in to access AI resume screening, technical interviews, and skill gap roadmaps.
          </p>
        </div>

        {/* Glassmorphic Form Card */}
        <div className="card" style={{
          padding: 'var(--p-space-7)',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-xl)'
        }}>
          {/* Quick Demo Fill Bar */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            background: 'var(--color-primary-muted)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 20
          }}>
            <div style={{ fontSize: '11px', color: 'var(--color-primary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={13} /> Quick Evaluation Mode
            </div>
            <button
              type="button"
              onClick={fillDemo}
              className="btn btn-primary btn-sm"
              style={{ fontSize: '10px', padding: '3px 8px', height: 'auto', fontWeight: 700 }}
            >
              Fill Demo
            </button>
          </div>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)', marginBottom: 6, display: 'block' }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  id="candidate-email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="candidate@example.com"
                  style={{ paddingLeft: 36 }}
                  required
                />
              </div>
            </div>

            <div style={{ marginBottom: 22 }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)', marginBottom: 6, display: 'block' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  id="candidate-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{ paddingLeft: 36, paddingRight: 36 }}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: 12,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--color-fg-muted)',
                    padding: 0
                  }}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={busy}
              style={{ width: '100%', padding: '12px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, borderRadius: 'var(--radius-md)' }}
            >
              <User size={15} /> {busy ? 'Signing In...' : 'Sign In as Candidate'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 20, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Don't have a candidate account? </span>
            <Link to="/register/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>
              Create Candidate Account
            </Link>
          </div>

          <div style={{ textAlign: 'center', marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)' }}>
            <Link to="/login/company" style={{ color: 'var(--color-fg-secondary)', textDecoration: 'none', fontWeight: 500 }}>
              Are you an employer / recruiter? <span style={{ color: 'var(--color-purple)', fontWeight: 700 }}>Sign in here →</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
