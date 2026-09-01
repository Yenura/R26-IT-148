import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Lock, ArrowLeft, KeyRound, Eye, EyeOff } from 'lucide-react'
import { C0 } from '../../api'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [token, setToken] = useState(params.get('token') || '')
  const [pwd, setPwd] = useState('')
  const [confirm, setConfirm] = useState('')
  const [show, setShow] = useState(false)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!token.trim()) return toast.error('Reset token is required')
    if (pwd.length < 6) return toast.error('Password must be at least 6 characters')
    if (pwd !== confirm) return toast.error('Passwords do not match')
    setBusy(true)
    try {
      await C0.post('/auth/reset-password', { token: token.trim(), new_password: pwd })
      toast.success('Password reset! Please sign in.')
      navigate('/login/candidate')
    } catch (err) {
      const d = err?.response?.data?.detail
      const msg = Array.isArray(d) ? d[0]?.msg : d
      toast.error(msg || 'Reset failed')
    } finally { setBusy(false) }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column' }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6 }}><ArrowLeft size={14} /> Back to Home</Link>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ margin: '0 auto 12px', width: 48, height: 48, borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, var(--color-primary), #4f46e5)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}><KeyRound size={22} /></div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>Reset Password</h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>Paste the token from Forgot Password and choose a new password.</p>
        </div>
        <div className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          <form onSubmit={submit}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Reset Token</label>
              <input type="text" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste token here" required />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>New Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input type={show ? 'text' : 'password'} value={pwd} onChange={(e) => setPwd(e.target.value)} placeholder="Minimum 6 characters" style={{ paddingLeft: 36, paddingRight: 36 }} required />
                <button type="button" onClick={() => setShow(!show)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-fg-muted)', padding: 0 }}>{show ? <EyeOff size={15} /> : <Eye size={15} />}</button>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Confirm Password</label>
              <input type={show ? 'text' : 'password'} value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Repeat new password" required />
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: '100%', padding: '11px 16px', fontWeight: 700 }}>{busy ? 'Resetting...' : 'Reset Password'}</button>
          </form>
          <div style={{ textAlign: 'center', marginTop: 16, fontSize: 'var(--p-text-xs)' }}>
            <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Back to Sign In</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
