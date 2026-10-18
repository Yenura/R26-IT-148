import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Brain, Mail, ArrowLeft, KeyRound, CheckCircle2, Copy } from 'lucide-react'
import { C0 } from '../../api'
import { isValidEmail } from '../../utils'



const getErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.msg ? d.msg.replace(/^Value error,\s*/i, '') : JSON.stringify(d))).join(', ')
  }
  return err?.message || 'Something went wrong. Please try again.'
}

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e?.preventDefault()
    if (!email.trim()) { setError('Email is required'); return }
    if (!isValidEmail(email.trim())) { setError('Enter a valid email address'); return }
    setError('')
    setBusy(true)
    try {
      const r = await C0.post('/auth/forgot-password', { email: email.trim() })
      setResult(r.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const copyToken = async () => {
    try {
      await navigator.clipboard.writeText(result.dev_token)
      toast.success('Reset token copied')
    } catch {
      toast.error('Copy failed — select the token manually')
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
            Reset Password
          </h1>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 6, lineHeight: 1.5 }}>
            Enter your account email and we will generate a reset link.
          </p>
        </div>

        <div className="card" style={{
          padding: '28px 26px',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-lg)'
        }}>
          {!result ? (
            <form onSubmit={handleSubmit} noValidate>
              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: '12px', fontWeight: 600, marginTop: 0, color: 'var(--color-fg-secondary)' }}>Email Address</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                  <input
                    id="forgot-email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); setError('') }}
                    placeholder="you@example.com"
                    style={{
                      paddingLeft: 36,
                      fontSize: '13px',
                      borderColor: error ? 'var(--color-danger)' : undefined
                    }}
                    required
                  />
                </div>
                {error && <p style={{ color: 'var(--color-danger)', fontSize: 11, margin: '4px 0 0' }}>{error}</p>}
              </div>

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
                <Mail size={15} /> {busy ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          ) : (
            <div style={{ textAlign: 'center' }}>
              <CheckCircle2 size={40} style={{ color: 'var(--color-success)', margin: '0 auto 12px' }} />
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', lineHeight: 1.6, margin: '0 0 16px' }}>
                {result.message}
              </p>
              {result.dev_token && (
                <div style={{
                  textAlign: 'left',
                  background: 'var(--color-bg)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 14px',
                  marginBottom: 16
                }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
                    Dev reset token (valid 15 min)
                  </div>
                  <div className="mono" style={{ wordBreak: 'break-all', color: 'var(--color-fg)', marginBottom: 10 }}>
                    {result.dev_token}
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn btn-secondary btn-sm" type="button" onClick={copyToken} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <Copy size={13} /> Copy
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      type="button"
                      onClick={() => navigate(`/reset-password?token=${encodeURIComponent(result.dev_token)}`)}
                    >
                      Continue to Reset
                    </button>
                  </div>
                </div>
              )}
              <div style={{ display: 'flex', gap: 10, justifyContent: 'center', fontSize: 'var(--p-text-xs)' }}>
                <Link to="/login/candidate" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Candidate Sign In</Link>
                <span style={{ color: 'var(--color-fg-muted)' }}>·</span>
                <Link to="/login/company" style={{ color: 'var(--color-primary)', fontWeight: 700 }}>Employer Sign In</Link>
              </div>
            </div>
          )}
        </div>

        <div style={{ textAlign: 'center', marginTop: 16, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
          <Brain size={13} /> RecruitAI Ecosystem · Secure Account Recovery
        </div>
      </div>
    </div>
  )
}
