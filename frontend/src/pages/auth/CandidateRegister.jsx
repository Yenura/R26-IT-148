import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft } from 'lucide-react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function CandidateRegister() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const register = async (e) => {
    e.preventDefault()
    if (!form.full_name || !form.email || !form.password) return toast.error('Fill required fields')
    if (form.password.length < 6) return toast.error('Password must be 6+ characters')
    setBusy(true)
    try {
      const r = await axios.post(`${API}/api/v1/auth/register/candidate`, form)
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'candidate')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await axios.get(`${API}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${r.data.access_token}` }
        })
        localStorage.setItem('recruitai.name', me.data.name || '')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Account created!')
      navigate('/candidate/dashboard')
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
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>Candidate Registration</h1>
          <p className="muted" style={{ fontSize: 13 }}>Create your candidate account</p>
        </div>
        <form onSubmit={register} className="card" style={{ padding: 28 }}>
          <label>Full Name *</label>
          <input type="text" value={form.full_name} onChange={set('full_name')} placeholder="John Doe" />
          <label>Email *</label>
          <input type="email" value={form.email} onChange={set('email')} placeholder="john@example.com" />
          <label>Password *</label>
          <input type="password" value={form.password} onChange={set('password')} placeholder="Min 6 characters" />
          <button className="btn btn-success" type="submit" disabled={busy} style={{ width: '100%', marginTop: 16 }}>
            <User size={16} /> {busy ? 'Creating…' : 'Create Candidate Account'}
          </button>
          <div style={{ textAlign: 'center', marginTop: 16, fontSize: 13 }}>
            <span className="muted">Have an account? </span>
            <Link to="/login/candidate">Login</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
