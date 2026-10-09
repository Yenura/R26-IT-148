import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FileText, ArrowLeft, Calendar, Tag, GraduationCap, Briefcase,
  Trash2, Edit3, CheckCircle, Clock
} from 'lucide-react'
import { uResumeGet, uResumeUpdate, uResumeDelete } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ConfirmDialog from '../components/ConfirmDialog'
import SkeletonLoader from '../components/SkeletonLoader'

export default function ResumeDetail() {
  const navigate = useNavigate()
  const { resumeId } = useParams()
  useAuth('candidate')

  const [resume, setResume] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editSkills, setEditSkills] = useState('')
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    if (resumeId) loadResume()
  }, [resumeId])

  const loadResume = async () => {
    setLoading(true)
    try {
      const res = await uResumeGet(resumeId)
      setResume(res.data)
      setEditSkills((res.data?.skills || []).join(', '))
    } catch (err) {
      toast.error('Failed to load resume')
      navigate('/candidate/dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    const skillsArray = editSkills.split(',').map((s) => s.trim()).filter(Boolean)
    setSaving(true)
    try {
      await uResumeUpdate(resumeId, { skills: skillsArray })
      toast.success('Resume updated successfully')
      setEditing(false)
      await loadResume()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update resume')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = () => {
    setConfirm({
      open: true,
      title: 'Delete this resume?',
      message: 'This will permanently remove the resume and all parsed data.',
      danger: true,
      action: async () => {
        try {
          await uResumeDelete(resumeId)
          toast.success('Resume deleted')
          navigate('/candidate/dashboard')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Delete failed')
        }
      }
    })
  }

  const skills = resume?.skills || []
  const education = resume?.education || 'Not specified'
  const experienceYears = resume?.experience_years ?? 'N/A'
  const fileType = resume?.file_type || resume?.filename?.split('.').pop()?.toUpperCase() || 'PDF'
  const uploadDate = resume?.created_at ? new Date(resume.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
  }) : 'Unknown'

  if (loading) {
    return (
      <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
        <PageHeader badge="Resume" title="Loading Resume..." icon={FileText} />
        <SkeletonLoader type="card" count={3} />
      </div>
    )
  }

  if (!resume) {
    return (
      <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
        <PageHeader badge="Resume" title="Resume Not Found" icon={FileText} />
        <div className="card" style={{ padding: 'var(--p-space-6)', textAlign: 'center' }}>
          <p style={{ color: 'var(--color-fg-muted)' }}>The requested resume could not be found.</p>
          <button className="btn btn-primary" onClick={() => navigate('/candidate/dashboard')} style={{ marginTop: 12 }}>
            <ArrowLeft size={15} /> Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <PageHeader
        badge="Resume Details"
        title={resume.filename || resume.candidate_name || 'Resume'}
        description={`Uploaded on ${uploadDate}`}
        icon={FileText}
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/dashboard')}>
              <ArrowLeft size={15} /> Dashboard
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => setEditing(!editing)}>
              <Edit3 size={15} /> {editing ? 'Cancel Edit' : 'Edit Resume'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={handleDelete} style={{ color: 'var(--color-danger)' }}>
              <Trash2 size={15} /> Delete
            </button>
          </div>
        }
      />

      {/* Stats Strip */}
      <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <StatCard label="Skills Extracted" value={skills.length} icon={CheckCircle} color="success" helperText="Parsed from resume" />
        <StatCard label="Experience" value={experienceYears} icon={Clock} color="info" helperText="Years of experience" />
        <StatCard label="File Type" value={fileType} icon={FileText} color="primary" helperText="Upload format" />
      </div>

      {/* Resume Content Card */}
      <div className="card" style={{ marginBottom: 'var(--p-space-4)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Tag size={18} style={{ color: 'var(--color-primary)' }} /> Extracted Skills
          </h3>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          {editing ? (
            <div>
              <label style={{ fontSize: '12px', marginBottom: 6, display: 'block' }}>Skills (comma-separated)</label>
              <textarea
                value={editSkills}
                onChange={(e) => setEditSkills(e.target.value)}
                rows={3}
                placeholder="e.g. Python, React, TypeScript, Docker"
                style={{ fontSize: 'var(--p-text-sm)' }}
              />
              <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                <button className="btn btn-primary btn-sm" onClick={handleUpdate} disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button className="btn btn-ghost btn-sm" onClick={() => { setEditing(false); setEditSkills(skills.join(', ')) }}>
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {skills.length > 0 ? skills.map((skill, i) => (
                <span key={`${skill}-${i}`} className="chip" style={{ fontSize: '12px', margin: 0 }}>
                  {skill}
                </span>
              )) : (
                <span style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>No skills extracted yet</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Education Card */}
      <div className="card" style={{ marginBottom: 'var(--p-space-4)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <GraduationCap size={18} style={{ color: 'var(--color-primary)' }} /> Education
          </h3>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
            {education}
          </p>
        </div>
      </div>

      {/* Experience Card */}
      <div className="card" style={{ marginBottom: 'var(--p-space-5)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={18} style={{ color: 'var(--color-primary)' }} /> Experience
          </h3>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
            {experienceYears} {experienceYears !== 'N/A' ? 'years' : ''} of professional experience
          </p>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
