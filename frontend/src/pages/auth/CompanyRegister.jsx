import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, Building2, ArrowLeft } from 'lucide-react'
import { C0 } from '../../api'

export default function CompanyRegister() {
  const [form, setForm] = useState({ company_name: '', email: '', password: '', industry: '', website: '' })
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const register = async (e) => {
    e.preventDefault()
    if (!form.company_name || !form.email || !form.password) return toast.error('Fill required fields')
    if (form.password.length < 6) return toast.error('Password must be 6+ characters')
    setBusy(true)
    try {
      const r = await C0.post('/auth/register/company', form)
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'company')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || '')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Company registered!')
      navigate('/company/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
      <div style={{ width: 440, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 16, alignSelf: 'flex-start' }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div className="sidebar-logo" style={{ margin: '0 auto 12px', width: 48, height: 48 }}><Brain size={24} /></div>
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>Company Registration</h1>
          <p className="muted" style={{ fontSize: 13 }}>Create your company account</p>
        </div>
        <form onSubmit={register} className="card" style={{ padding: 28 }}>
          <label>Company Name *</label>
          <input type="text" value={form.company_name} onChange={set('company_name')} placeholder="Acme Corp" />
          <label>Email *</label>
          <input type="email" value={form.email} onChange={set('email')} placeholder="hr@acme.com" />
          <label>Password *</label>
          <input type="password" value={form.password} onChange={set('password')} placeholder="Min 6 characters" />
          <label>Industry</label>
          <input type="text" value={form.industry} onChange={set('industry')} placeholder="Technology" />
          <label>Website</label>
          <input type="text" value={form.website} onChange={set('website')} placeholder="https://acme.com" />
          <button className="btn btn-success" type="submit" disabled={busy} style={{ width: '100%', marginTop: 16 }}>
            <Building2 size={16} /> {busy ? 'Creating…' : 'Create Company Account'}
          </button>
          <div style={{ textAlign: 'center', marginTop: 16, fontSize: 13 }}>
            <span className="muted">Have an account? </span>
            <Link to="/login/company">Login</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
