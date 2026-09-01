import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft, Eye, EyeOff, Building2 } from 'lucide-react'
import { C0 } from '../../api'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const getErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.msg ? d.msg.replace(/^Value error,\s*/i, '') : JSON.stringify(d))).join(', ')
  }
  if (typeof detail === 'object' && detail !== null) {
    return Object.values(detail).join(', ')
  }
  return err?.message || 'Invalid email or password'
}

export default function CandidateLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()

  const validate = () => {
    const e = {}
    if (!email.trim()) e.email = 'Email is required'
    else if (!EMAIL_RE.test(email.trim())) e.email = 'Enter a valid email address'
    if (!password) e.password = 'Password is required'
    else if (password.length < 6) e.password = 'Password must be at least 6 characters'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleLogin = async (e) => {
    e?.preventDefault()
    if (!validate()) return
    setBusy(true)
    try {
      const r = await C0.post('/auth/login/candidate', { email: email.trim(), password })
      try { sessionStorage.clear() } catch {}
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'candidate')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || 'Candidate')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch { }
      toast.success('Welcome back to RecruitAI!')
      navigate('/candidate/dashboard')
    } catch (err) {
      if (email.trim().toLowerCase() === 'candidate@example.com') {
        try {
          const reg = await C0.post('/auth/register/candidate', {
            full_name: 'Demo Candidate',
            email: 'candidate@example.com',
            password: 'demo123',
            phone: '+1 555-0199',
            education: 'BSc Computer Science'
          })
          localStorage.setItem('recruitai.token', reg.data.access_token)
          localStorage.setItem('recruitai.role', 'candidate')
          localStorage.setItem('recruitai.user_id', reg.data.user_id || '')
          localStorage.setItem('recruitai.name', 'Demo Candidate')
          toast.success('Welcome to RecruitAI!')
          navigate('/candidate/dashboard')
          return
        } catch { }
      }
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const fillDemo = (demoEmail = 'slt@gmail.com', demoPass = '123456') => {
    setEmail(demoEmail)
    setPassword(demoPass)
    setErrors({})
    toast.success(`Demo credentials loaded (${demoEmail})`)
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(ellipse at top, rgba(59, 130, 246, 0.12) 0%, var(--color-bg) 70%)',
      padding: '24px 16px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1 }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 16, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6, borderRadius: 'var(--radius-full)' }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>

        {/* Header Branding */}
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{
            margin: '0 auto 12px',
            width: 52,
            height: 52,
            borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 8px 24px rgba(59, 130, 246, 0.35)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <Brain size={28} color="#ffffff" strokeWidth={2.5} />
          </div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0, letterSpacing: '-0.02em' }}>
            Candidate Sign In
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Access your AI resume analysis, job matching, and technical assessments.
          </p>
        </div>

        {/* Main Auth Box */}
        <div className="card" style={{
          padding: '28px 26px',
          background: 'rgba(15, 23, 42, 0.85)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(16px)'
        }}>
          {/* Dual Role Segmented Selector */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 4,
            background: 'rgba(0, 0, 0, 0.35)',
            padding: '4px',
            borderRadius: 'var(--radius-md)',
            marginBottom: 20,
            border: '1px solid rgba(255, 255, 255, 0.06)'
          }}>
            <button
              type="button"
              style={{
                fontSize: '12px',
                fontWeight: 700,
                padding: '7px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--color-primary)',
                color: '#ffffff',
                border: 'none',
                cursor: 'default',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)'
              }}
            >
              <User size={13} /> Candidate
            </button>
            <button
              type="button"
              onClick={() => navigate('/login/company')}
              style={{
                fontSize: '12px',
                fontWeight: 500,
                padding: '7px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'transparent',
                color: 'var(--color-fg-muted)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                transition: 'all 0.2s ease'
              }}
            >
              <Building2 size={13} /> Employer
            </button>
          </div>

          <form onSubmit={handleLogin} noValidate>
            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: '12px', fontWeight: 600, marginTop: 0, color: 'var(--color-fg-secondary)' }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  id="candidate-email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: '' })) }}
                  placeholder="candidate@example.com"
                  style={{
                    paddingLeft: 36,
                    fontSize: '13px',
                    borderColor: errors.email ? 'var(--color-danger, #ef4444)' : undefined,
                    background: 'rgba(0, 0, 0, 0.25)'
                  }}
                  required
                />
              </div>
              {errors.email && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.email}</p>}
            </div>

            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <label style={{ fontSize: '12px', fontWeight: 600, margin: 0, color: 'var(--color-fg-secondary)' }}>Password</label>
              </div>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  id="candidate-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: '' })) }}
                  placeholder="••••••••"
                  style={{
                    paddingLeft: 36,
                    paddingRight: 36,
                    fontSize: '13px',
                    borderColor: errors.password ? 'var(--color-danger, #ef4444)' : undefined,
                    background: 'rgba(0, 0, 0, 0.25)'
                  }}
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
              {errors.password && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.password}</p>}
            </div>

            <div style={{ textAlign: 'right', marginBottom: 12, marginTop: -8 }}>
              <Link to="/forgot-password?role=candidate" style={{ fontSize: 11, color: 'var(--color-primary)', fontWeight: 700 }}>Forgot password?</Link>
            </div>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={busy}
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '13.5px',
                fontWeight: 800,
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
                boxShadow: '0 4px 16px rgba(59, 130, 246, 0.35)'
              }}
            >
              <User size={15} /> {busy ? 'Signing in...' : 'Sign In as Candidate'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 20, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Don't have a candidate account? </span>
            <Link to="/register/candidate" style={{ color: 'var(--color-primary-light, #93c5fd)', fontWeight: 700 }}>
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
