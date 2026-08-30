import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, Building2, ArrowLeft, Globe, Eye, EyeOff, Briefcase } from 'lucide-react'
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
  return err?.message || 'Registration failed. Please try again.'
}

export default function CompanyRegister() {
  const [form, setForm] = useState({
    company_name: '',
    email: '',
    password: '',
    industry: '',
    website: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()

  const validate = () => {
    const e = {}
    if (!form.company_name.trim()) e.company_name = 'Company name is required'
    else if (form.company_name.trim().length < 2) e.company_name = 'Name must be at least 2 characters'
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
      const payload = {
        company_name: form.company_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        industry: form.industry.trim(),
        website: form.website.trim()
      }
      const r = await C0.post('/auth/register/company', payload)
      try { sessionStorage.clear() } catch {}
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'company')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || me.data.company_name || form.company_name.trim())
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Company account created successfully!')
      navigate('/company/dashboard')
    } catch (err) {
      toast.error(getErrorMessage(err))
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
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column' }}>
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
            Register Organization
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            Create an employer account to publish jobs, review candidates, and manage hiring pipelines.
          </p>
        </div>

        <form onSubmit={register} noValidate className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Company Name *</label>
            <div style={{ position: 'relative' }}>
              <Building2 size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="text"
                autoComplete="organization"
                value={form.company_name}
                onChange={set('company_name')}
                placeholder="e.g. Acme Tech Inc."
                style={{ paddingLeft: 36, borderColor: errors.company_name ? 'var(--color-danger, #ef4444)' : undefined }}
                required
              />
            </div>
            {errors.company_name && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.company_name}</p>}
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Work Email *</label>
            <div style={{ position: 'relative' }}>
              <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="email"
                autoComplete="email"
                value={form.email}
                onChange={set('email')}
                placeholder="recruiter@acme.com"
                style={{ paddingLeft: 36, borderColor: errors.email ? 'var(--color-danger, #ef4444)' : undefined }}
                required
              />
            </div>
            {errors.email && <p style={{ color: 'var(--color-danger, #ef4444)', fontSize: 11, margin: '4px 0 0' }}>{errors.email}</p>}
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Password *</label>
            <div style={{ position: 'relative' }}>
              <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                value={form.password}
                onChange={set('password')}
                placeholder="Minimum 6 characters"
                style={{ paddingLeft: 36, paddingRight: 36, borderColor: errors.password ? 'var(--color-danger, #ef4444)' : undefined }}
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

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Industry</label>
              <div style={{ position: 'relative' }}>
                <Briefcase size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  type="text"
                  value={form.industry}
                  onChange={set('industry')}
                  placeholder="e.g. SaaS"
                  style={{ paddingLeft: 30 }}
                />
              </div>
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Website</label>
              <div style={{ position: 'relative' }}>
                <Globe size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input
                  type="text"
                  value={form.website}
                  onChange={set('website')}
                  placeholder="https://..."
                  style={{ paddingLeft: 30 }}
                />
              </div>
            </div>
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={busy}
            style={{ width: '100%', padding: '11px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, background: 'var(--color-purple)', borderColor: 'var(--color-purple)' }}
          >
            <Building2 size={15} /> {busy ? 'Creating Account...' : 'Create Employer Account'}
          </button>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            <span>Already have an employer account? </span>
            <Link to="/login/company" style={{ color: 'var(--color-purple)', fontWeight: 700 }}>
              Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
