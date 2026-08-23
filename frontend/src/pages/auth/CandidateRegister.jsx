import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft, Eye, EyeOff, Sparkles } from 'lucide-react'
import { C0 } from '../../api'

export default function CandidateRegister() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const register = async (e) => {
    e.preventDefault()
    if (!form.full_name.trim() || !form.email.trim() || !form.password) {
      return toast.error('Please fill in all required fields')
    }
    if (form.password.length < 6) {
      return toast.error('Password must be at least 6 characters')
    }
    setBusy(true)
    try {
      const r = await C0.post('/auth/register/candidate', form)
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'candidate')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || form.full_name)
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Candidate account created successfully!')
      navigate('/candidate/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

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
          <ArrowLeft size={14} /> Back to Home
        </Link>

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
            Candidate Registration
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Create your candidate profile to match CVs, take AI technical tests, and track your career roadmap.
          </p>
        </div>

        <form onSubmit={register} className="card" style={{
          padding: 'var(--p-space-7)',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-xl)'
        }}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)', marginBottom: 6, display: 'block' }}>
              Full Name *
            </label>
            <div style={{ position: 'relative' }}>
              <User size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="text"
                value={form.full_name}
                onChange={set('full_name')}
                placeholder="e.g. Alex Morgan"
                style={{ paddingLeft: 36 }}
                required
              />
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)', marginBottom: 6, display: 'block' }}>
              Email Address *
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                placeholder="alex@example.com"
                style={{ paddingLeft: 36 }}
                required
              />
            </div>
          </div>

          <div style={{ marginBottom: 22 }}>
            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)', marginBottom: 6, display: 'block' }}>
              Password *
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={set('password')}
                placeholder="Minimum 6 characters"
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
            <Sparkles size={15} /> {busy ? 'Creating Account...' : 'Create Candidate Account'}
          </button>

          <div style={{ textAlign: 'center', marginTop: 20, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Already have an account? </span>
            <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>
              Sign In Here
            </Link>
          </div>

          <div style={{ textAlign: 'center', marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)' }}>
            <Link to="/register/company" style={{ color: 'var(--color-fg-secondary)', textDecoration: 'none' }}>
              Hiring team? <span style={{ color: 'var(--color-purple)', fontWeight: 700 }}>Register Company →</span>
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
