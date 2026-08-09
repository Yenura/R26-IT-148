import { useState, useEffect, useRef } from 'react'
import toast from 'react-hot-toast'
import { Building2, Mail, Lock, Upload, Save } from 'lucide-react'
import { authGetProfile, authUpdateProfile, authChangePassword, authUploadAvatar } from '../api'

export default function CompanyProfile() {
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({ full_name: '', company_name: '', industry: '', website: '' })
  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '' })
  const [busy, setBusy] = useState(false)
  const [pwBusy, setPwBusy] = useState(false)
  const fileRef = useRef()

  useEffect(() => {
    authGetProfile().then(r => {
      setProfile(r.data)
      setForm({
        full_name: r.data.name || '',
        company_name: r.data.company_name || '',
        industry: r.data.industry || '',
        website: r.data.website || '',
      })
    }).catch(() => {})
  }, [])

  const saveProfile = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const r = await authUpdateProfile(form)
      setProfile(r.data)
      localStorage.setItem('recruitai.name', r.data.name || '')
      toast.success('Profile updated')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    } finally {
      setBusy(false)
    }
  }

  const changePassword = async (e) => {
    e.preventDefault()
    if (pwForm.new_password.length < 6) return toast.error('New password must be 6+ characters')
    setPwBusy(true)
    try {
      await authChangePassword(pwForm)
      setPwForm({ current_password: '', new_password: '' })
      toast.success('Password changed')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Password change failed')
    } finally {
      setPwBusy(false)
    }
  }

  const uploadAvatar = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      const r = await authUploadAvatar(fd)
      setProfile(p => ({ ...p, avatar_url: r.data.avatar_url }))
      localStorage.setItem('recruitai.avatar', r.data.avatar_url)
      toast.success('Logo uploaded')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    }
  }

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))
  const setPw = (k) => (e) => setPwForm(f => ({ ...f, [k]: e.target.value }))

  if (!profile) return <div className="empty">Loading profile...</div>

  return (
    <div className="fade-in" style={{ maxWidth: 640 }}>
      <div className="page-head">
        <h1>Company Profile</h1>
        <p>Manage your company information</p>
      </div>

      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
        <div
          onClick={() => fileRef.current?.click()}
          style={{ cursor: 'pointer', position: 'relative' }}
          title="Change logo"
        >
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt="Logo"
              style={{ width: 72, height: 72, borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--color-border)' }}
            />
          ) : (
            <div className="avatar" style={{ width: 72, height: 72, fontSize: 28 }}>
              {(profile.name || profile.email || '?')[0].toUpperCase()}
            </div>
          )}
          <div style={{
            position: 'absolute', bottom: 0, right: 0, width: 24, height: 24,
            background: 'var(--color-primary)', borderRadius: '50%', display: 'flex',
            alignItems: 'center', justifyContent: 'center', border: '2px solid var(--card-bg)'
          }}>
            <Upload size={12} color="white" />
          </div>
        </div>
        <input ref={fileRef} type="file" accept="image/*" onChange={uploadAvatar} style={{ display: 'none' }} />
        <div>
          <div style={{ fontWeight: 700, fontSize: 18 }}>{profile.company_name || profile.name || 'Unnamed'}</div>
          <div className="muted" style={{ fontSize: 13 }}>{profile.email}</div>
          <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Member since {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : '—'}
          </div>
        </div>
      </div>

      <form onSubmit={saveProfile} className="card">
        <h3><Building2 size={18} /> Company Information</h3>
        <label>Company Name</label>
        <input type="text" value={form.company_name} onChange={set('company_name')} placeholder="Company name" />
        <label>Industry</label>
        <input type="text" value={form.industry} onChange={set('industry')} placeholder="e.g. Technology, Finance" />
        <label>Website</label>
        <input type="text" value={form.website} onChange={set('website')} placeholder="https://..." />
        <label>Email</label>
        <input type="email" value={profile.email} disabled />
        <button className="btn btn-success" type="submit" disabled={busy} style={{ marginTop: 12 }}>
          <Save size={16} /> {busy ? 'Saving...' : 'Save Changes'}
        </button>
      </form>

      <form onSubmit={changePassword} className="card">
        <h3><Lock size={18} /> Change Password</h3>
        <label>Current Password</label>
        <input type="password" value={pwForm.current_password} onChange={setPw('current_password')} placeholder="Enter current password" />
        <label>New Password</label>
        <input type="password" value={pwForm.new_password} onChange={setPw('new_password')} placeholder="Min 6 characters" />
        <button className="btn btn-ghost" type="submit" disabled={pwBusy} style={{ marginTop: 12 }}>
          <Lock size={16} /> {pwBusy ? 'Changing...' : 'Change Password'}
        </button>
      </form>
    </div>
  )
}
