import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  User, Lock, Upload, Save, FileText, ShieldCheck, Mail, Calendar, Check
} from 'lucide-react'
import {
  authGetProfile, authUpdateProfile, authChangePassword,
  authUploadAvatar, uResumeList
} from '../api'
import PageHeader from '../components/PageHeader'

export default function Profile() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({ full_name: '', company_name: '', industry: '', website: '' })
  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [busy, setBusy] = useState(false)
  const [pwBusy, setPwBusy] = useState(false)
  const [resumeData, setResumeData] = useState(null)
  const fileRef = useRef()

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) {
      navigate('/')
      return
    }
    authGetProfile().then((r) => {
      setProfile(r.data)
      setForm({
        full_name: r.data.name || '',
        company_name: r.data.company_name || '',
        industry: r.data.industry || '',
        website: r.data.website || '',
      })
    }).catch(() => toast.error('Failed to load profile'))

    uResumeList().then((r) => {
      const list = Array.isArray(r.data) ? r.data : []
      if (list.length > 0) setResumeData(list[0])
    }).catch(() => {})
  }, [])

  const saveProfile = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const r = await authUpdateProfile(form)
      setProfile(r.data)
      localStorage.setItem('recruitai.name', r.data.name || '')
      toast.success('Profile updated successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    } finally {
      setBusy(false)
    }
  }

  const changePassword = async (e) => {
    e.preventDefault()
    if (pwForm.new_password.length < 6) return toast.error('New password must be at least 6 characters')
    if (pwForm.new_password !== pwForm.confirm_password) return toast.error('New passwords do not match')
    setPwBusy(true)
    try {
      await authChangePassword(pwForm)
      setPwForm({ current_password: '', new_password: '', confirm_password: '' })
      toast.success('Password changed successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Password change failed')
    } finally {
      setPwBusy(false)
    }
  }

  const uploadAvatar = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const MAX_SIZE = 5 * 1024 * 1024
    if (!file.type.startsWith('image/')) return toast.error('Please upload an image file')
    if (file.size > MAX_SIZE) return toast.error('Image must be under 5MB')
    const fd = new FormData()
    fd.append('file', file)
    try {
      const r = await authUploadAvatar(fd)
      setProfile((p) => ({ ...p, avatar_url: r.data.avatar_url }))
      localStorage.setItem('recruitai.avatar', r.data.avatar_url)
      toast.success('Avatar uploaded!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const setPw = (k) => (e) => setPwForm((f) => ({ ...f, [k]: e.target.value }))

  if (!profile) return <div className="card" style={{ padding: 40, textAlign: 'center' }}>
    <div className="shimmer" style={{ height: 20, width: 200, margin: '0 auto 12px', borderRadius: 6 }} />
    <div className="shimmer" style={{ height: 14, width: 140, margin: '0 auto', borderRadius: 6 }} />
  </div>

  return (
    <div className="fade-in" style={{ maxWidth: 720, margin: '0 auto' }}>
      <PageHeader
        badge="Candidate Settings"
        title="My Profile & Credentials"
        description="Manage your account identity, contact information, and security credentials."
        icon={User}
      />

      {/* Avatar & Header Card */}
      <div className="card" style={{ padding: 'var(--p-space-5)', display: 'flex', alignItems: 'center', gap: 20, marginBottom: 'var(--p-space-5)' }}>
        <div
          onClick={() => fileRef.current?.click()}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileRef.current?.click() } }}
          tabIndex={0}
          role="button"
          aria-label="Upload avatar"
          style={{ cursor: 'pointer', position: 'relative', flexShrink: 0 }}
          title="Click to update avatar"
        >
          {profile.avatar_url ? (
            <img
              src={profile.avatar_url}
              alt="Avatar"
              style={{ width: 68, height: 68, borderRadius: 'var(--radius-full)', objectFit: 'cover', border: '2px solid var(--color-border)' }}
            />
          ) : (
            <div className="avatar" style={{ width: 68, height: 68, fontSize: 24, borderRadius: 'var(--radius-full)' }}>
              {(profile.name || profile.email || 'U')[0].toUpperCase()}
            </div>
          )}
          <div style={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: 24,
            height: 24,
            background: 'var(--color-primary)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            border: '2px solid var(--card-bg)'
          }}>
            <Upload size={12} />
          </div>
        </div>
        <input ref={fileRef} type="file" accept="image/*" onChange={uploadAvatar} style={{ display: 'none' }} />

        <div>
          <div style={{ fontWeight: 800, fontSize: '1.25rem', color: 'var(--color-fg)' }}>
            {profile.name || 'Candidate'}
          </div>
          <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
            <Mail size={12} /> {profile.email}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            <Calendar size={11} /> Member since {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Active Member'}
          </div>
        </div>
      </div>

      {/* Profile Form */}
      <form onSubmit={saveProfile} className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <User size={16} style={{ color: 'var(--color-primary)' }} /> Account Details
        </h3>

        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>Full Name</label>
          <input
            type="text"
            value={form.full_name}
            onChange={set('full_name')}
            placeholder="Your full name"
            required
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>Email Address (Account Identifier)</label>
          <input type="email" value={profile.email} disabled />
        </div>

        <button className="btn btn-primary btn-sm" type="submit" disabled={busy}>
          <Save size={14} /> {busy ? 'Saving...' : 'Save Profile Changes'}
        </button>
      </form>

      {/* Resume Data Summary */}
      {resumeData && (
        <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileText size={16} style={{ color: 'var(--color-primary)' }} /> Active Resume Metadata
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 'var(--p-text-xs)' }}>
            <div>
              <div style={{ color: 'var(--color-fg-muted)', marginBottom: 2 }}>Current Active File:</div>
              <div style={{ fontWeight: 700, color: 'var(--color-fg)' }}>{resumeData.filename || 'Uploaded CV'}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-fg-muted)', marginBottom: 2 }}>Verified Experience:</div>
              <div style={{ fontWeight: 700, color: 'var(--color-fg)' }}>{resumeData.experience_years || 0} Years</div>
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <div style={{ color: 'var(--color-fg-muted)', marginBottom: 4 }}>Extracted Skills:</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {(resumeData.skills || []).slice(0, 8).map((s) => (
                  <span key={s} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>{s}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Password Change Card */}
      <form onSubmit={changePassword} className="card" style={{ padding: 'var(--p-space-5)' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Lock size={16} style={{ color: 'var(--color-primary)' }} /> Security & Password
        </h3>

        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>Current Password</label>
          <input
            type="password"
            value={pwForm.current_password}
            onChange={setPw('current_password')}
            placeholder="Enter existing password"
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>New Password</label>
          <input
            type="password"
            value={pwForm.new_password}
            onChange={setPw('new_password')}
            placeholder="Minimum 6 characters"
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>Confirm New Password</label>
          <input
            type="password"
            value={pwForm.confirm_password}
            onChange={setPw('confirm_password')}
            placeholder="Re-enter new password"
          />
        </div>

        <button className="btn btn-ghost btn-sm" type="submit" disabled={pwBusy}>
          <Lock size={14} /> {pwBusy ? 'Updating...' : 'Update Password'}
        </button>
      </form>
    </div>
  )
}
