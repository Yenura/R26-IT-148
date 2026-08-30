import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Upload, Briefcase, MapPin, Clock, ChevronRight, Trash2, Edit3, X, Check,
  Sparkles, FileText, Target, TrendingUp, CheckCircle2, ArrowRight, UserCheck, Eye, MessagesSquare
} from 'lucide-react'
import {
  uResumeList, uResumeUpload, uResumeDelete, uResumeUpdate,
  c0JobsAll, c0Predictions, c0Applications
} from '../api'
import { useAuth } from '../hooks/useAuth'
import { toArr } from '../utils'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import UploadZone from '../components/UploadZone'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function CandidateDashboard() {
  const navigate = useNavigate()
  useAuth('candidate')
  const candidateName = localStorage.getItem('recruitai.name') || 'Candidate'

  const [resumes, setResumes] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.cand.resumes')
      return cached ? JSON.parse(cached) : []
    } catch { return [] }
  })
  const [jobs, setJobs] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.jobs.cached')
      return cached ? JSON.parse(cached) : []
    } catch { return [] }
  })
  const [applications, setApplications] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.cand.apps')
      return cached ? JSON.parse(cached) : []
    } catch { return [] }
  })
  const [predictions, setPredictions] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.cand.preds')
      return cached ? JSON.parse(cached) : []
    } catch { return [] }
  })
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        uResumeList().catch(() => ({ data: [] })),
        c0JobsAll().catch(() => ({ data: [] })),
        c0Predictions().catch(() => ({ data: [] })),
        c0Applications().catch(() => ({ data: [] })),
      ])
      const resArr = toArr(r1)
      const jobArr = toArr(r2)
      const predArr = toArr(r3)
      const appArr = toArr(r4)
      setResumes(resArr)
      setJobs(jobArr)
      setPredictions(predArr)
      setApplications(appArr)
      try {
        sessionStorage.setItem('recruitai.cand.resumes', JSON.stringify(resArr))
        sessionStorage.setItem('recruitai.jobs.cached', JSON.stringify(jobArr))
        sessionStorage.setItem('recruitai.cand.preds', JSON.stringify(predArr))
        sessionStorage.setItem('recruitai.cand.apps', JSON.stringify(appArr))
      } catch {}
    } catch {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file) => {
    if (!file) return
    setSelectedFile(file)
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      await uResumeUpload(formData)
      toast.success('Resume parsed and skills extracted successfully!')
      setSelectedFile(null)
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
      setSelectedFile(null)
    } finally {
      setUploading(false)
    }
  }

  const deleteResume = async (id) => {
    setConfirm({
      open: true,
      title: 'Delete resume?',
      message: 'This will permanently remove this CV and its associated match predictions.',
      danger: true,
      action: async () => {
        try {
          await uResumeDelete(id)
          toast.success('Resume removed')
          loadData()
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Delete failed')
        }
      }
    })
  }

  const startEdit = (resume) => {
    setEditingId(resume.id)
    setEditForm({
      candidate_name: resume.candidate_name || '',
      email: resume.email || '',
      phone: resume.phone || '',
      education: resume.education || '',
      experience_years: resume.experience_years || 0,
      skills: (resume.skills || []).join(', '),
    })
  }

  const saveEdit = async () => {
    try {
      await uResumeUpdate(editingId, {
        candidate_name: editForm.candidate_name,
        email: editForm.email,
        phone: editForm.phone,
        education: editForm.education,
        experience_years: parseFloat(editForm.experience_years) || 0,
        skills: editForm.skills.split(',').map((s) => s.trim()).filter(Boolean),
      })
      toast.success('Profile updated')
      setEditingId(null)
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    }
  }

  const appliedJobIds = new Set(
    applications.filter((a) => a.status !== 'withdrawn').map((a) => a.job_id)
  )

  const bestPrediction = predictions.length > 0
    ? Math.max(...predictions.map((p) => p.overall_score || 0))
    : 0

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto' }}>
      {/* Header & Primary CTAs */}
      <PageHeader
        badge="Candidate Portal"
        title={`Welcome back, ${candidateName}`}
        description="Your unified AI recruitment cockpit: manage resumes, explore matching roles, and level up technical readiness."
        actions={
          <>
            <Link to="/pipeline/cv-match" className="btn btn-primary btn-sm">
              <Sparkles size={15} /> Run AI CV Match
            </Link>
            <Link to="/candidate/interview" className="btn btn-ghost btn-sm">
              <MessagesSquare size={15} /> Practice Interview
            </Link>
            <Link to="/candidate/jobs" className="btn btn-ghost btn-sm">
              <Briefcase size={15} /> Explore Jobs
            </Link>
          </>
        }
      />

      {/* KPI Metric Strip */}
      {loading ? (
        <SkeletonLoader type="stat" count={4} />
      ) : (
        <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
          <StatCard
            label="Active CVs"
            value={resumes.length}
            icon={FileText}
            color="primary"
            helperText={resumes.length > 0 ? 'Ready for auto-matching' : 'Upload your first CV'}
          />
          <StatCard
            label="Applied Roles"
            value={applications.filter((a) => a.status !== 'withdrawn').length}
            icon={UserCheck}
            color="info"
            helperText="Tracked in pipeline"
          />
          <StatCard
            label="Open Positions"
            value={jobs.length}
            icon={Briefcase}
            color="success"
            helperText="Active recruiter postings"
          />
          <StatCard
            label="Top Fit Match"
            value={bestPrediction > 0 ? `${bestPrediction.toFixed(0)}%` : '—'}
            icon={Target}
            color={bestPrediction >= 80 ? 'success' : 'purple'}
            helperText={bestPrediction > 0 ? 'Highest AI match' : 'Run CV Match'}
          />
        </div>
      )}

      {/* Main 2-Column Cockpit */}
            <div className="dashboard-grid dashboard-grid-main" style={{ alignItems: 'start' }}>
        
        {/* Left Column: Resumes & Application Status */}
        <div>
          {/* Resume Upload & Management */}
          <div className="card" style={{ marginBottom: 'var(--p-space-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-4)' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Upload size={18} style={{ color: 'var(--color-primary)' }} /> My Resumes & Extracted Profiles
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '3px 0 0 0' }}>
                  Upload your CV to automatically extract technical skills, experience, and education.
                </p>
              </div>
            </div>

            {/* Upload Zone */}
            <div style={{ marginBottom: 'var(--p-space-4)' }}>
              <UploadZone
                onFileSelect={handleFileUpload}
                uploading={uploading}
                selectedFile={selectedFile}
                onRemoveFile={() => setSelectedFile(null)}
              />
            </div>

            {/* Resumes List */}
            {resumes.length === 0 ? (
              <EmptyState
                title="No resumes uploaded yet"
                description="Upload your CV (PDF, DOCX, TXT) to unlock automatic role matching, interview prep, and skill gap roadmaps."
                actionLabel="Choose File"
                icon={FileText}
                onAction={() => document.getElementById('resume-file-input')?.click()}
              />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-3)' }}>
                {resumes.map((r) => (
                  <div
                    key={r.id}
                    style={{
                      padding: 'var(--p-space-4)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--color-border-subtle)',
                      background: 'var(--color-bg-elevated)',
                      transition: 'all var(--duration-normal) var(--ease)'
                    }}
                  >
                    {editingId === r.id ? (
                      /* Inline Edit Mode */
                      <div>
                        <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 12, color: 'var(--color-primary)' }}>
                          Edit Extracted Profile Information
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
                          <div>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Candidate Name</label>
                            <input
                              type="text"
                              value={editForm.candidate_name}
                              onChange={(e) => setEditForm((f) => ({ ...f, candidate_name: e.target.value }))}
                            />
                          </div>
                          <div>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Email</label>
                            <input
                              type="email"
                              value={editForm.email}
                              onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))}
                            />
                          </div>
                          <div>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Phone</label>
                            <input
                              type="text"
                              value={editForm.phone}
                              onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))}
                            />
                          </div>
                          <div>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Experience (Years)</label>
                            <input
                              type="number"
                              min={0}
                              max={50}
                              step={0.5}
                              value={editForm.experience_years}
                              onChange={(e) => setEditForm((f) => ({ ...f, experience_years: e.target.value }))}
                            />
                          </div>
                          <div style={{ gridColumn: 'span 2' }}>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Education</label>
                            <input
                              type="text"
                              value={editForm.education}
                              onChange={(e) => setEditForm((f) => ({ ...f, education: e.target.value }))}
                            />
                          </div>
                          <div style={{ gridColumn: 'span 2' }}>
                            <label style={{ fontSize: 11, marginTop: 0 }}>Skills (Comma Separated)</label>
                            <input
                              type="text"
                              value={editForm.skills}
                              onChange={(e) => setEditForm((f) => ({ ...f, skills: e.target.value }))}
                            />
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <button className="btn btn-sm" onClick={saveEdit}>
                            <Check size={13} /> Save Changes
                          </button>
                          <button className="btn btn-ghost btn-sm" onClick={() => setEditingId(null)}>
                            <X size={13} /> Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      /* Standard View Mode */
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                            <div style={{
                              width: 38,
                              height: 38,
                              borderRadius: 'var(--radius-md)',
                              background: 'var(--color-primary-muted)',
                              color: 'var(--color-primary)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexShrink: 0
                            }}>
                              <FileText size={18} />
                            </div>
                            <div>
                              <div style={{ fontWeight: 700, fontSize: 'var(--p-text-base)', color: 'var(--color-fg)' }}>
                                {r.filename}
                              </div>
                              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                                {r.candidate_name && <span><strong>{r.candidate_name}</strong> · </span>}
                                {r.education && <span>{r.education} · </span>}
                                <span>{r.experience_years || 0} yrs experience</span>
                              </div>
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                            <button
                              className="btn-ghost btn-sm"
                              onClick={() => startEdit(r)}
                              aria-label="Edit parsed details"
                              title="Edit parsed details"
                              style={{ padding: 8, minWidth: 44, minHeight: 44 }}
                            >
                              <Edit3 size={14} />
                            </button>
                            <button
                              className="btn-ghost btn-sm"
                              onClick={() => deleteResume(r.id)}
                              aria-label="Delete resume"
                              title="Delete resume"
                              style={{ padding: 8, minWidth: 44, minHeight: 44, color: 'var(--color-danger)' }}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </div>

                        {/* Extracted Skills Cloud */}
                        {r.skills?.length > 0 && (
                          <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
                            <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginRight: 4 }}>
                              Extracted Skills:
                            </span>
                            {[...new Set(r.skills)].slice(0, 8).map((s, i) => (
                               <span key={`${s}-${i}`} className="chip" style={{ fontSize: '11px', margin: 0, padding: '2px 8px' }}>
                                {s}
                              </span>
                            ))}
                            {r.skills.length > 8 && (
                              <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                                +{r.skills.length - 8} more
                              </span>
                            )}
                          </div>
                        )}

                        {/* Direct action CTA */}
                        <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                          <Link
                            to={`/pipeline/cv-match`}
                            className="btn btn-ghost btn-sm"
                            style={{ fontSize: 'var(--p-text-xs)' }}
                          >
                            <Sparkles size={13} /> Run Detailed CV Match
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Applications Status */}
          {applications.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-3)' }}>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <UserCheck size={16} style={{ color: 'var(--color-success)' }} /> My Active Applications ({applications.length})
                </h3>
                <Link to="/candidate/jobs" className="btn-ghost btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
                  View All Jobs
                </Link>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {applications.map((app) => {
                  const job = jobs.find((j) => j.id === app.job_id) || {}
                  return (
                    <div
                      key={app.id || app.job_id}
                      style={{
                        padding: '12px 14px',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border-subtle)',
                        background: 'var(--color-bg-elevated)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 12
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                          {job.title || app.job_title || 'Applied Position'}
                        </div>
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2, display: 'flex', gap: 8 }}>
                          <span>{job.company_name || 'Hiring Company'}</span>
                          <span>·</span>
                          <span>{job.location || 'Remote'}</span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                        <span style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-full)',
                          background: app.status === 'withdrawn' ? 'var(--color-danger-muted)' : 'var(--color-success-muted)',
                          color: app.status === 'withdrawn' ? 'var(--color-danger)' : 'var(--color-success)',
                          border: `1px solid ${app.status === 'withdrawn' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`,
                          textTransform: 'capitalize'
                        }}>
                          {app.status || 'Under Review'}
                        </span>

                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => navigate(`/candidate/interview?role=${job.job_role || job.title || ''}&jobId=${app.job_id}`)}
                          style={{ fontSize: '11px', padding: '4px 8px' }}
                          title="Take or retake technical interview"
                        >
                          <MessagesSquare size={12} /> Interview
                        </button>

                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => navigate(`/candidate/skill-gap`)}
                          style={{ fontSize: '11px', padding: '4px 8px', color: 'var(--color-primary)' }}
                          title="View Skill Gap and composite evaluation"
                        >
                          <Sparkles size={12} /> Skill Gap
                        </button>

                        <button
                          className="btn-ghost btn-sm"
                          onClick={() => navigate(`/candidate/jobs/${app.job_id}`)}
                          aria-label="View job posting"
                          style={{ padding: 6 }}
                          title="View job posting"
                        >
                          <Eye size={14} />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Open Jobs & Career Fast Track */}
        <div>
          {/* Top Job Matches */}
          <div className="card" style={{ marginBottom: 'var(--p-space-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-3)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Open Job Opportunities
              </h3>
              <Link to="/candidate/jobs" className="btn-ghost btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
                Browse ({jobs.length})
              </Link>
            </div>

            {jobs.length === 0 ? (
              <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--color-fg-muted)', fontSize: 'var(--p-text-sm)' }}>
                No active job postings yet.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {jobs.slice(0, 5).map((job) => {
                  const applied = appliedJobIds.has(job.id)
                  return (
                    <div
                      key={job.id}
                      onClick={() => navigate(`/candidate/jobs/${job.id}`)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => e.key === 'Enter' && navigate(`/candidate/jobs/${job.id}`)}
                      style={{
                        padding: '12px 14px',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border-subtle)',
                        background: 'var(--color-bg-elevated)',
                        cursor: 'pointer',
                        transition: 'all var(--duration-normal) var(--ease)'
                      }}
                      className="card-interactive"
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                        <div style={{ fontWeight: 700, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                          {job.title}
                        </div>
                        {applied && (
                          <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 6px', borderRadius: 'var(--radius-full)' }}>
                            Applied
                          </span>
                        )}
                      </div>

                      <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', gap: 10, alignItems: 'center' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                          <MapPin size={11} /> {job.location || 'Remote'}
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                          <Clock size={11} /> {job.employment_type || 'Full-time'}
                        </span>
                      </div>

                      {job.required_skills?.length > 0 && (
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 8 }}>
                          {[...new Set(job.required_skills)].slice(0, 3).map((s, i) => (
                            <span key={`${s}-${i}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                              {s}
                            </span>
                          ))}
                          {job.required_skills.length > 3 && (
                            <span style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>
                              +{job.required_skills.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Quick AI Skill Development Box */}
          <div
            className="card"
            style={{
              background: 'linear-gradient(135deg, var(--color-primary-muted), var(--color-purple-muted))',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              padding: 'var(--p-space-5)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <TrendingUp size={18} style={{ color: 'var(--color-primary)' }} />
              <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>
                Career Roadmap & Skill Matrix
              </div>
            </div>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', lineHeight: 1.5, margin: '0 0 14px 0' }}>
              Analyze technical gaps against industry benchmarks and simulate hiring readiness with automated learning pathways.
            </p>
            <div style={{ display: 'flex', gap: 8 }}>
              <Link to="/pipeline/progress" className="btn btn-ghost btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
                Progress Tracker
              </Link>
            </div>
          </div>
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
