import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Lock, ArrowLeft, KeyRound, CheckCircle2, Eye, EyeOff } from 'lucide-react'
import { C0 } from '../../api'

const getErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.msg ? d.msg.replace(/^Value error,\s*/i, '') : JSON.stringify(d))).join(', ')
  }
  return err?.message || 'Something went wrong. Please try again.'
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState(searchParams.get('token') || '')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e?.preventDefault()
    if (!token.trim()) { setError('Reset token is required'); return }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return }
    if (password !== confirm) { setError('Passwords do not match'); return }
    setError('')
    setBusy(true)
    try {
      const r = await C0.post('/auth/reset-password', { token: token.trim(), new_password: password })
      setDone(true)
      toast.success(r.data.message || 'Password updated')
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--color-bg)',
      padding: '24px 16px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ width: '100%', maxWidth: 440, display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1 }}>
        <Link to="/" className="btn btn-ghost btn-sm" style={{ marginBottom: 16, alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 6, borderRadius: 'var(--radius-full)' }}>
          <ArrowLeft size={14} /> Back to Home
        </Link>

        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{
            margin: '0 auto 12px',
            width: 52,
            height: 52,
            borderRadius: 'var(--radius-lg)',
            background: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: 'var(--shadow-glow)'
          }}>
            <KeyRound size={26} color="#ffffff" strokeWidth={2.5} />
          </div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0, letterSpacing: '-0.02em' }}>
            Choose New Password
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Paste your reset token and set a new password. Tokens expire after 15 minutes.
          </p>
        </div>

        <div className="card" style={{
          padding: '28px 26px',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-lg)'
        }}>
          {!done ? (
            <form onSubmit={handleSubmit} noValidate>
              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: '12px', fontWeight: 600, marginTop: 0, color: 'var(--color-fg-secondary)' }}>Reset Token</label>
                <input
                  id="reset-token"
                  type="text"
                  autoComplete="off"
                  value={token}
                  onChange={(e) => { setToken(e.target.value); setError('') }}
                  placeholder="Paste the token from the previous step"
                  className="mono"
                  style={{ fontSize: '13px' }}
                  required
                />
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: '12px', fontWeight: 600, marginTop: 0, color: 'var(--color-fg-secondary)' }}>New Password</label>
                <div style={{ position: 'relative' }}>
                  <input
                    id="reset-password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); setError('') }}
                    placeholder="Minimum 6 characters"
                    style={{ paddingRight: 36, fontSize: '13px' }}
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
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: '12px', fontWeight: 600, marginTop: 0, color: 'var(--color-fg-secondary)' }}>Confirm New Password</label>
                <input
                  id="reset-confirm"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={confirm}
                  onChange={(e) => { setConfirm(e.target.value); setError('') }}
                  placeholder="Re-enter new password"
                  style={{ fontSize: '13px' }}
                  required
                />
              </div>

              {error && <p style={{ color: 'var(--color-danger)', fontSize: 11, margin: '0 0 12px' }}>{error}</p>}

              <button
                className="btn btn-primary"
                type="submit"
                disabled={busy}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  fontSize: '13.5px',
                  fontWeight: 800,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8
                }}
              >
                <Lock size={15} /> {busy ? 'Updating...' : 'Update Password'}
              </button>
            </form>
          ) : (
            <div style={{ textAlign: 'center' }}>
              <CheckCircle2 size={40} style={{ color: 'var(--color-success)', margin: '0 auto 12px' }} />
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', lineHeight: 1.6, margin: '0 0 16px' }}>
                Your password has been updated. Please sign in with your new password.
              </p>
              <div style={{ display: 'flex', gap: 10, justifyContent: 'center', fontSize: 'var(--p-text-xs)' }}>
                <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Candidate Sign In</Link>
                <span style={{ color: 'var(--color-fg-muted)' }}>·</span>
                <Link to="/login/company" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Employer Sign In</Link>
              </div>
              <button className="btn btn-ghost btn-sm" type="button" onClick={() => navigate('/')} style={{ marginTop: 16 }}>
                Back to Home
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
