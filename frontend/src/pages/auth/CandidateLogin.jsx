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
        localStorage.setItem('recruitai.name', me.data.name || 'Candidate')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Welcome back to RecruitAI!')
      navigate('/candidate/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid email or password')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>

        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            margin: '0 auto 12px',
            width: 48,
            height: 48,
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, var(--color-primary), #4f46e5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: 'var(--shadow-md)'
          }}>
            <Brain size={24} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>
            Candidate Sign In
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            Access your AI resume analysis, job matching, and technical assessments.
          </p>
        </div>

        <div className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          {/* Quick Demo Fill Button */}
          <div style={{ marginBottom: 18 }}>
            <button
              type="button"
              onClick={fillDemo}
              className="btn btn-ghost btn-sm"
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                fontSize: '11px',
                border: '1px dashed var(--color-primary)',
                background: 'var(--color-primary-muted)',
                color: 'var(--color-primary)',
                fontWeight: 700
              }}
            >
              <Sparkles size={13} /> 1-Click: Fill Demo Candidate Account
            </button>
          </div>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Email Address</label>
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

            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Password</label>
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
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
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
              style={{ width: '100%', padding: '11px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700 }}
            >
              <User size={15} /> {busy ? 'Signing in...' : 'Sign In as Candidate'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Don't have a candidate account? </span>
            <Link to="/register/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>
              Create Account
            </Link>
          </div>

          <div style={{ textAlign: 'center', marginTop: 10, fontSize: 'var(--p-text-xs)' }}>
            <Link to="/login/company" style={{ color: 'var(--color-fg-muted)' }}>
              Are you an employer? Sign in here →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
