import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, Lock, User, ArrowLeft } from 'lucide-react'
import { C0 } from '../../api'

export default function CandidateLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e?.preventDefault()
    if (!email || !password) return toast.error('Fill in all fields')
    setBusy(true)
    try {
      const r = await C0.post('/auth/login/candidate', { email: email, password: password })
      localStorage.setItem('recruitai.token', r.data.access_token)
      localStorage.setItem('recruitai.role', 'candidate')
      localStorage.setItem('recruitai.user_id', r.data.user_id || '')
      try {
        const me = await C0.get('/auth/me')
        localStorage.setItem('recruitai.name', me.data.name || '')
        localStorage.setItem('recruitai.avatar', me.data.avatar_url || '')
      } catch {}
      toast.success('Welcome back!')
      navigate('/candidate/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start', border: '1px solid var(--border)' }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>
        
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div className="sidebar-logo" style={{ margin: '0 auto 14px', width: 52, height: 52, borderRadius: 14 }}>
            <Brain size={28} />
          </div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: 'var(--text)' }}>Candidate Sign In</h1>
          <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>Access your AI recruitment dashboard & tools</p>
        </div>

        <div className="card" style={{ padding: 32, borderRadius: 16, border: '1px solid var(--border)', background: 'var(--bg-elevated)', boxShadow: '0 8px 30px rgba(0,0,0,0.12)' }}>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  id="candidate-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  maxLength={100}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="candidate@example.com"
                  style={{ paddingLeft: 40, height: 44, fontSize: 14, borderRadius: 8 }}
                />
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  id="candidate-password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  maxLength={100}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{ paddingLeft: 40, height: 44, fontSize: 14, borderRadius: 8 }}
                />
              </div>
            </div>

            <button className="btn" type="submit" disabled={busy} style={{ width: '100%', height: 44, fontSize: 14, fontWeight: 700, borderRadius: 8, background: 'var(--color-primary)', color: '#fff' }}>
              <User size={16} /> {busy ? 'Signing in...' : 'Sign In as Candidate'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 20, fontSize: 13 }}>
            <span className="muted">Don't have a candidate account? </span>
            <Link to="/register/candidate" style={{ color: 'var(--accent)', fontWeight: 600 }}>Register Candidate</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
