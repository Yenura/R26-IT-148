import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, Building2, ArrowLeft, Sparkles, Eye, EyeOff } from 'lucide-react'
import { C0 } from '../../api'

export default function CompanyLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e?.preventDefault()
    if (!email || !password) return toast.error('Please enter work email and password')
    setBusy(true)
    try {
      const r = await C0.post('/auth/login/company', { email: email.trim(), password })
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'company')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || me.data.company_name || 'Tech Recruiter')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Welcome back, Recruiter!')
      navigate('/company/dashboard')
    } catch (err) {
      if (email.trim().toLowerCase() === 'company@example.com') {
        try {
          const reg = await C0.post('/auth/register/company', {
            company_name: 'Tech Corp Global',
            email: 'company@example.com',
            password: 'demo123',
            industry: 'Technology',
            website: 'https://techcorp.example.com'
          })
          localStorage.setItem('recruitai.token', reg.data.access_token)
          localStorage.setItem('recruitai.role', 'company')
          localStorage.setItem('recruitai.user_id', reg.data.user_id || '')
          localStorage.setItem('recruitai.name', 'Tech Corp Global')
          toast.success('Welcome to RecruitAI Recruiter Suite!')
          navigate('/company/dashboard')
          return
        } catch {}
      }
      toast.error(err?.response?.data?.detail || 'Invalid company credentials')
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
            background: 'linear-gradient(135deg, var(--color-purple), #6366f1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: 'var(--shadow-md)'
          }}>
            <Building2 size={24} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>
            Employer Sign In
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Post engineering roles, monitor applicant pipelines, and evaluate candidates with automated multi-criteria ranking.
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
                border: '1px dashed var(--color-purple)',
                background: 'rgba(147, 51, 234, 0.08)',
                color: 'var(--color-purple)',
                fontWeight: 700
              }}
            >
              <Sparkles size={13} /> 1-Click: Fill Demo Employer Account
            </button>
          </div>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Work Email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  id="company-email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="recruiter@techcorp.com"
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
                  id="company-password"
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
              style={{ width: '100%', padding: '11px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, background: 'var(--color-purple)', borderColor: 'var(--color-purple)' }}
            >
              <Building2 size={15} /> {busy ? 'Signing in...' : 'Sign In as Employer'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Don't have an employer account? </span>
            <Link to="/register/company" style={{ color: 'var(--color-purple)', fontWeight: 700 }}>
              Register Company
            </Link>
          </div>

          <div style={{ textAlign: 'center', marginTop: 10, fontSize: 'var(--p-text-xs)' }}>
            <Link to="/login/candidate" style={{ color: 'var(--color-fg-muted)' }}>
              Looking for a job? Candidate sign in →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
