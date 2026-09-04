import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Upload, Briefcase, MapPin, Clock, ChevronRight, Trash2, Edit3, X, Check,
  Sparkles, FileText, Target, TrendingUp, CheckCircle2, ArrowRight, UserCheck, Eye, MessagesSquare,
  Search, GraduationCap, Building2
} from 'lucide-react'
import {
  uResumeList, uResumeUpload, uResumeDelete, uResumeUpdate,
  c0JobsAll, c0Predictions, c0Applications
} from '../api'
import { useAuth } from '../hooks/useAuth'
import { toArr, cleanCandidateName, cleanCompanyName } from '../utils'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import UploadZone from '../components/UploadZone'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const cleanEducationText = (rawEdu) => {
  if (!rawEdu) return 'BSc Degree in Computing / IT'
  let edu = String(rawEdu).trim()
  if (edu.includes('|')) {
    edu = edu.split('|')[0].trim()
  }
  return edu.length > 55 ? `${edu.slice(0, 52)}...` : edu
}

export default function CandidateDashboard() {
  const navigate = useNavigate()
  useAuth('candidate')
  const rawCandidateName = localStorage.getItem('recruitai.name') || 'Candidate'
  const candidateName = rawCandidateName
    .split(' ')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ')

  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [applications, setApplications] = useState([])
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })
const [jobSearch, setJobSearch] = useState('')

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

  const filteredJobs = jobs.filter((j) => {
    if (!jobSearch.trim()) return true
    const q = jobSearch.toLowerCase()
    return (
      (j.title && j.title.toLowerCase().includes(q)) ||
      (j.company_name && j.company_name.toLowerCase().includes(q)) ||
      (j.location && j.location.toLowerCase().includes(q)) ||
      (j.required_skills && j.required_skills.some((s) => String(s).toLowerCase().includes(q)))
    )
  })

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto' }}>
      {/* Header & Primary CTAs */}
      <PageHeader
        badge="Candidate AI Cockpit"
        title={`Welcome back, ${candidateName}`}
        description="Your unified AI recruitment cockpit: manage resumes, explore matching roles, and level up technical readiness."
        actions={
          <>
            <Link to="/pipeline/cv-match" className="btn btn-primary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700 }}>
              <Sparkles size={15} /> Run AI CV Match
            </Link>
            <Link to="/candidate/interview" className="btn btn-ghost btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <MessagesSquare size={15} /> Practice Interview
            </Link>
            <Link to="/candidate/jobs" className="btn btn-ghost btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
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
            helperText={resumes.length > 0 ? `${resumes.length} verified profile${resumes.length > 1 ? 's' : ''}` : 'Upload your first CV'}
          />
          <StatCard
            label="Applied Roles"
            value={applications.filter((a) => a.status !== 'withdrawn').length}
            icon={UserCheck}
            color="info"
            helperText="Active in recruitment pipeline"
          />
          <StatCard
            label="Open Positions"
            value={jobs.length}
            icon={Briefcase}
            color="success"
            helperText="Live recruiter postings"
          />
          <StatCard
            label="Top Fit Match"
            value={bestPrediction > 0 ? `${bestPrediction.toFixed(0)}%` : '—'}
            icon={Target}
            color={bestPrediction >= 80 ? 'success' : 'purple'}
            helperText={bestPrediction > 0 ? 'Peak AI match score' : 'Run CV Match'}
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
                        {(() => {
                          const candDisplayName = cleanCandidateName(r.candidate_name, r.filename)
                          const initials = candDisplayName.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase() || 'CV'
                          return (
                            <>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                                  <div style={{
                                    width: 42,
                                    height: 42,
                                    borderRadius: 'var(--radius-md)',
                                    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                                    color: '#ffffff',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontWeight: 800,
                                    fontSize: '14px',
                                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
                                    flexShrink: 0
                                  }}>
                                    {initials}
                                  </div>
                                  <div>
                                    <div style={{ fontWeight: 800, fontSize: '15px', color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                                      <span>{candDisplayName}</span>
                                      <span style={{ fontSize: '10.5px', fontWeight: 600, padding: '2px 8px', borderRadius: 'var(--radius-full)', background: 'rgba(255, 255, 255, 0.06)', color: 'var(--color-fg-muted)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                                        📄 {r.filename}
                                      </span>
                                    </div>
                                    <div style={{ fontSize: '11.5px', color: 'var(--color-fg-muted)', marginTop: 4, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                                        <GraduationCap size={13} style={{ color: 'var(--color-primary-light, #93c5fd)' }} />
                                        {cleanEducationText(r.education)}
                                      </span>
                                      <span>•</span>
                                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                                        <Clock size={13} style={{ color: 'var(--color-success)' }} />
                                        {r.experience_years || 0} yrs experience
                                      </span>
                                    </div>
                                  </div>
                                </div>

                                <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                                  <button
                                    className="btn-ghost btn-sm"
                                    onClick={() => startEdit(r)}
                                    aria-label="Edit parsed details"
                                    title="Edit parsed details"
                                    style={{ padding: 6, minWidth: 32, minHeight: 32, borderRadius: 'var(--radius-md)', border: '1px solid rgba(255, 255, 255, 0.06)' }}
                                  >
                                    <Edit3 size={13} />
                                  </button>
                                  <button
                                    className="btn-ghost btn-sm"
                                    onClick={() => deleteResume(r.id)}
                                    aria-label="Delete resume"
                                    title="Delete resume"
                                    style={{ padding: 6, minWidth: 32, minHeight: 32, color: 'var(--color-danger)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(244, 63, 94, 0.15)' }}
                                  >
                                    <Trash2 size={13} />
                                  </button>
                                </div>
                              </div>

                              {/* Extracted Skills Cloud */}
                              {r.skills?.length > 0 && (
                                <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
                                  <span style={{ fontSize: '10px', fontWeight: 800, color: 'var(--color-fg-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginRight: 4 }}>
                                    Skills:
                                  </span>
                                  {[...new Set(r.skills)].slice(0, 8).map((s, i) => (
                                    <span key={`${s}-${i}`} className="chip" style={{ fontSize: '10.5px', margin: 0, padding: '2px 8px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                                      {s}
                                    </span>
                                  ))}
                                  {r.skills.length > 8 && (
                                    <span style={{ fontSize: '10.5px', color: 'var(--color-fg-muted)', alignSelf: 'center' }}>
                                      +{r.skills.length - 8} more
                                    </span>
                                  )}
                                </div>
                              )}

                              {/* Action CTAs */}
                              <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', justifyContent: 'flex-end', gap: 8, flexWrap: 'wrap' }}>
                                <Link
                                  to={`/candidate/resume/${r.id}`}
                                  className="btn btn-ghost btn-sm"
                                  style={{ fontSize: '11px', padding: '4px 10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}
                                >
                                  <Eye size={12} /> Full Details
                                </Link>
                                <Link
                                  to={`/candidate/interview?role=${encodeURIComponent(r.predicted_role || 'Software Engineer')}`}
                                  className="btn btn-ghost btn-sm"
                                  style={{ fontSize: '11px', padding: '4px 10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}
                                >
                                  <MessagesSquare size={12} style={{ color: 'var(--color-purple)' }} /> Practice Mock Interview
                                </Link>
                                <Link
                                  to={`/pipeline/cv-match?resumeId=${r.id}`}
                                  className="btn btn-primary btn-sm"
                                  style={{ fontSize: '11px', padding: '4px 12px', fontWeight: 700 }}
                                >
                                  <Sparkles size={12} /> Run Detailed CV Match
                                </Link>
                              </div>
                            </>
                          )
                        })()}
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
                          <span>{cleanCompanyName(job.company_name) || 'Hiring Company'}</span>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Open Job Opportunities
                </h3>
                <p style={{ fontSize: '11px', color: 'var(--color-fg-muted)', margin: '2px 0 0 0' }}>
                  Explore active job postings and evaluate your semantic CV fit.
                </p>
              </div>
              <Link to="/candidate/jobs" className="btn btn-ghost btn-sm" style={{ fontSize: '11.5px', padding: '4px 8px' }}>
                Browse All ({jobs.length})
              </Link>
            </div>

            {/* Quick Filter / Search */}
            <div style={{ marginBottom: 12, position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="text"
                value={jobSearch}
                onChange={(e) => setJobSearch(e.target.value)}
                placeholder="Search jobs by title, tech stack, or company..."
                style={{
                  width: '100%',
                  fontSize: '12px',
                  padding: '9px 12px 9px 34px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--color-border-subtle)',
                  color: 'var(--color-fg)'
                }}
              />
            </div>

            {filteredJobs.length === 0 ? (
              <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--color-fg-muted)', fontSize: 'var(--p-text-sm)' }}>
                No active job postings matched "{jobSearch}".
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {filteredJobs.slice(0, 5).map((job) => {
                  const applied = appliedJobIds.has(job.id)
                  const compName = cleanCompanyName(job.company_name)
                  const compInitials = compName.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()
                  return (
                    <div
                      key={job.id}
                      style={{
                        padding: '14px 16px',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--color-border-subtle)',
                        background: 'var(--color-bg-elevated)',
                        transition: 'all var(--duration-normal) var(--ease)'
                      }}
                      className="card-interactive"
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div style={{
                            width: 32,
                            height: 32,
                            borderRadius: 'var(--radius-sm)',
                            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2))',
                            color: 'var(--color-primary-light, #93c5fd)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '11px',
                            fontWeight: 800,
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            flexShrink: 0
                          }}>
                            {compInitials}
                          </div>
                          <div>
                            <div style={{ fontWeight: 800, fontSize: '13.5px', color: 'var(--color-fg)' }}>
                              {job.title}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-primary-light, #93c5fd)', fontWeight: 600, marginTop: 1 }}>
                              {compName}
                            </div>
                          </div>
                        </div>

                        {applied ? (
                          <span style={{ fontSize: '10.5px', fontWeight: 800, color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                            ✓ Applied
                          </span>
                        ) : (
                          <button
                            type="button"
                            onClick={() => navigate(`/pipeline/cv-match?jobId=${job.id}&role=${encodeURIComponent(job.job_role || job.title)}`)}
                            className="btn btn-ghost btn-sm"
                            style={{ fontSize: '11px', padding: '4px 9px', color: 'var(--color-primary)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 'var(--radius-md)', fontWeight: 600 }}
                            title="Evaluate your CV fit score for this position"
                          >
                            <Sparkles size={11} /> Evaluate Fit
                          </button>
                        )}
                      </div>

                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', display: 'flex', gap: 12, alignItems: 'center', marginBottom: 8, marginTop: 4 }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          <MapPin size={12} /> {job.location || 'Remote'}
                        </span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Clock size={12} /> {job.employment_type || 'Full-time'}
                        </span>
                        {job.experience_required && (
                          <span>{job.experience_required}+ yrs req</span>
                        )}
                      </div>

                      {job.required_skills?.length > 0 && (
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {[...new Set(job.required_skills)].slice(0, 4).map((s, i) => (
                            <span key={`${s}-${i}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '2px 7px', background: 'rgba(255, 255, 255, 0.04)' }}>
                              {s}
                            </span>
                          ))}
                          {job.required_skills.length > 4 && (
                            <span style={{ fontSize: '10px', color: 'var(--color-fg-muted)', alignSelf: 'center' }}>
                              +{job.required_skills.length - 4} more
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

          {/* AI Career Acceleration Suite Hub */}
          <div
            className="card panel-dark"
            style={{
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--p-space-5)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <TrendingUp size={18} style={{ color: 'var(--color-primary)' }} />
              <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)' }}>
                RecruitAI Technical Acceleration Suite
              </div>
            </div>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', lineHeight: 1.5, margin: '0 0 14px 0' }}>
              Maximize candidate hiring velocity with integrated AI screening tools:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <Link
                to="/pipeline/cv-match"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '11px', padding: '8px 10px', display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-start', border: '1px solid rgba(255, 255, 255, 0.08)' }}
              >
                <Sparkles size={13} style={{ color: 'var(--color-primary)' }} /> 3-Pillar CV Match
              </Link>
              <Link
                to="/candidate/interview"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '11px', padding: '8px 10px', display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-start', border: '1px solid rgba(255, 255, 255, 0.08)' }}
              >
                <MessagesSquare size={13} style={{ color: 'var(--color-purple)' }} /> Mock Interview
              </Link>
              <Link
                to="/candidate/skill-gap"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '11px', padding: '8px 10px', display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-start', border: '1px solid rgba(255, 255, 255, 0.08)' }}
              >
                <Target size={13} style={{ color: 'var(--color-success)' }} /> Skill Gap Sandbox
              </Link>
              <Link
                to="/pipeline/progress"
                className="btn btn-ghost btn-sm"
                style={{ fontSize: '11px', padding: '8px 10px', display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-start', border: '1px solid rgba(255, 255, 255, 0.08)' }}
              >
                <ArrowRight size={13} style={{ color: 'var(--color-warning)' }} /> Roadmap Tracker
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

