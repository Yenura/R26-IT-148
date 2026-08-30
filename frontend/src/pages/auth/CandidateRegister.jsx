import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft, Eye, EyeOff, Sparkles } from 'lucide-react'
import { C0 } from '../../api'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function CandidateRegister() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()

  const validate = () => {
    const e = {}
    if (!form.full_name.trim()) e.full_name = 'Full name is required'
    else if (form.full_name.trim().length < 2) e.full_name = 'Name must be at least 2 characters'
    if (!form.email.trim()) e.email = 'Email is required'
    else if (!EMAIL_RE.test(form.email.trim())) e.email = 'Enter a valid email address'
    if (!form.password) e.password = 'Password is required'
    else if (form.password.length < 6) e.password = 'Password must be at least 6 characters'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const register = async (e) => {
    e.preventDefault()
    if (!validate()) return
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
      toast.success('Candidate account created!')
      navigate('/candidate/dashboard')
    } catch (err) {
      const detail = err?.response?.data?.detail
      const msg = Array.isArray(detail) ? (detail[0]?.msg?.replace('Value error, ','') || detail[0]?.msg || detail[0]) : detail
      toast.error(msg || 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  const set = (k) => (e) => {
    setForm((f) => ({ ...f, [k]: e.target.value }))
    setErrors((p) => ({ ...p, [k]: '' }))
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start' }}>
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
            color: '#fff'
          }}>
            <Brain size={26} color="#ffffff" strokeWidth={2.5} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>
            Create Candidate Account
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            Join RecruitAI to analyze your CV and discover matching roles.
          </p>
        </div>

        <form onSubmit={register} noValidate className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Full Name *</label>
            <input
              type="text"
              value={form.full_name}
              onChange={set('full_name')}
              placeholder="e.g. Alex Morgan"
              style={{ borderColor: errors.full_name ? 'var(--color-danger, #ef4444)' : undefined }}
              required
            />
            {errors.full_name && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.full_name}</p>}
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Email Address *</label>
            <input
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="alex@example.com"
              style={{ borderColor: errors.email ? 'var(--color-danger, #ef4444)' : undefined }}
              required
            />
            {errors.email && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.email}</p>}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Password *</label>
            <input
              type="password"
              value={form.password}
              onChange={set('password')}
              placeholder="Minimum 6 characters"
              style={{ borderColor: errors.password ? 'var(--color-danger, #ef4444)' : undefined }}
              required
            />
            {errors.password && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.password}</p>}
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={busy}
            style={{ width: '100%', padding: '11px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700 }}
          >
            <User size={15} /> {busy ? 'Creating Account...' : 'Create Candidate Account'}
          </button>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Already have an account? </span>
            <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>
              Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
