import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, Building2, ArrowLeft } from 'lucide-react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export default function CompanyLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const login = async (e) => {
    e.preventDefault()
    if (!email || !password) return toast.error('Fill in all fields')
    setBusy(true)
    try {
      const r = await axios.post(`${API}/api/v1/auth/login/company`, { email, password })
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'company')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await axios.get(`${API}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${r.data.access_token}` }
        })
        localStorage.setItem('recruitai.name', me.data.name || '')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Logged in')
      navigate('/company/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
      <div style={{ width: 420, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 16, alignSelf: 'flex-start' }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div className="sidebar-logo" style={{ margin: '0 auto 12px', width: 48, height: 48 }}><Brain size={24} /></div>
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>Company Login</h1>
          <p className="muted" style={{ fontSize: 13 }}>Sign in to your company account</p>
        </div>
        <form onSubmit={login} className="card" style={{ padding: 28 }}>
          <label>Email</label>
          <div style={{ position: 'relative' }}>
            <Mail size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="company@example.com" style={{ paddingLeft: 36 }} />
          </div>
          <label>Password</label>
          <div style={{ position: 'relative' }}>
            <Lock size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Your password" style={{ paddingLeft: 36 }} />
          </div>
          <button className="btn" type="submit" disabled={busy} style={{ width: '100%', marginTop: 16 }}>
            <Building2 size={16} /> {busy ? 'Signing in…' : 'Company Login'}
          </button>
          <div style={{ textAlign: 'center', marginTop: 16, fontSize: 13 }}>
            <span className="muted">No account? </span>
            <Link to="/register/company">Register as Company</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
