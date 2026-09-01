import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, ArrowLeft, KeyRound } from 'lucide-react'
import { C0 } from '../../api'

export default function ForgotPassword({ role = 'candidate' }) {
  const [params] = useSearchParams()
  const r = params.get('role') || role
  const isCompany = r === 'company'
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [token, setToken] = useState('')
  const navigate = useNavigate()
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  const submit = async (e) => {
    e.preventDefault()
    if (!email.trim() || !EMAIL_RE.test(email.trim())) return toast.error('Enter a valid email')
    setBusy(true)
    try {
      const res = await C0.post('/auth/forgot-password', { email: email.trim() })
      if (res.data?.reset_token) {
        setToken(res.data.reset_token)
        toast.success('Reset token generated (demo) — copy it below')
      } else {
        toast.success('If an account exists, a reset link has been generated.')
        setToken('')
      }
    } catch (err) {
      const detail = err?.response?.data?.detail
      const msg = Array.isArray(detail) ? detail[0]?.msg : detail
      toast.error(msg || 'Failed to generate reset link')
    } finally { setBusy(false) }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)', padding: 20 }}>
      <div style={{ width: '100%', maxWidth: 420, display: 'flex', flexDirection: 'column' }}>
        <Link to={isCompany ? '/login/company' : '/login/candidate'} className="btn btn-ghost btn-sm" style={{ marginBottom: 20, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6 }}><ArrowLeft size={14} /> Back to Sign In</Link>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ margin: '0 auto 12px', width: 48, height: 48, borderRadius: 'var(--radius-md)', background: isCompany ? 'linear-gradient(135deg, var(--color-purple), #6366f1)' : 'linear-gradient(135deg, var(--color-primary), #4f46e5)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}><KeyRound size={22} /></div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0 }}>Forgot Password</h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>{isCompany ? 'Employer' : 'Candidate'} — enter your email to generate a reset link.</p>
        </div>
        <div className="card" style={{ padding: 'var(--p-space-6)', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-xl)' }}>
          <form onSubmit={submit}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={isCompany ? 'recruiter@techcorp.com' : 'candidate@example.com'} style={{ paddingLeft: 36 }} required />
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: '100%', padding: '11px 16px', fontWeight: 700, background: isCompany ? 'var(--color-purple)' : undefined, borderColor: isCompany ? 'var(--color-purple)' : undefined }}>
              {busy ? 'Generating...' : 'Generate Reset Link'}
            </button>
          </form>
          {token && (
            <div style={{ marginTop: 16, padding: 12, background: 'var(--color-primary-muted)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', wordBreak: 'break-all' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>Demo Reset Token (15 min):</div>
              <div style={{ fontSize: 11, fontFamily: 'var(--p-font-mono)', color: 'var(--color-primary)', marginBottom: 8 }}>{token}</div>
              <Link to={`/reset-password?token=${encodeURIComponent(token)}`} className="btn btn-primary btn-sm" style={{ width: '100%', justifyContent: 'center' }}>Go to Reset Password →</Link>
            </div>
          )}
          <div style={{ textAlign: 'center', marginTop: 16, fontSize: 'var(--p-text-xs)' }}>
            <Link to={isCompany ? '/login/company' : '/login/candidate'} style={{ color: isCompany ? 'var(--color-purple)' : 'var(--color-primary)', fontWeight: 700 }}>Back to Sign In</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
