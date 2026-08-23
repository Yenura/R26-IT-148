import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, Building2, ArrowLeft, Globe } from 'lucide-react'
import { C0 } from '../../api'

export default function CompanyRegister() {
  const [form, setForm] = useState({ company_name: '', email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const register = async (e) => {
    e.preventDefault()
    if (!form.company_name.trim() || !form.email.trim() || !form.password) {
      return toast.error('Please fill in required fields')
    }
    if (form.password.length < 6) {
      return toast.error('Password must be at least 6 characters')
    }
    setBusy(true)
    try {
      const r = await C0.post('/auth/register/company', form)
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'company')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || form.company_name)
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Company account created!')
      navigate('/company/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start' }}>
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
            color: '#fff'
          }}>
            <Building2 size={24} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>
            Register Organization
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
            Create an employer account to publish jobs and screen applicants.
          </p>
        </div>

        <form onSubmit={register} className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Company Name *</label>
            <input
              type="text"
              value={form.company_name}
              onChange={set('company_name')}
              placeholder="e.g. Acme Tech Inc."
              required
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Work Email *</label>
            <input
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="recruiter@acme.com"
              required
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Password *</label>
            <input
              type="password"
              value={form.password}
              onChange={set('password')}
              placeholder="Minimum 6 characters"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 20 }}>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Industry</label>
              <input
                type="text"
                value={form.industry}
                onChange={set('industry')}
                placeholder="e.g. SaaS"
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Website</label>
              <input
                type="text"
                value={form.website}
                onChange={set('website')}
                placeholder="https://..."
              />
            </div>
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={busy}
            style={{ width: '100%', padding: '11px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, background: 'var(--color-purple)', borderColor: 'var(--color-purple)' }}
          >
            <Building2 size={15} /> {busy ? 'Registering...' : 'Create Employer Account'}
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
