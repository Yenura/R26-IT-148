import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Briefcase, MapPin, Clock, Building2, Search, CheckCircle,
  MessageSquare, ChevronRight, Filter, Sparkles, UserCheck
} from 'lucide-react'
import {
  c0JobsAll, uResumeList, c0Applications, c0InterviewScores,
  uJobsApply, uJobsWithdraw
} from '../api'
import { useAuth } from '../hooks/useAuth'
import { toArr } from '../utils'
import PageHeader from '../components/PageHeader'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function JobBoard() {
  const navigate = useNavigate()
  useAuth('candidate')
  const [jobs, setJobs] = useState([])
  const [resumes, setResumes] = useState([])
  const [appliedIds, setAppliedIds] = useState(new Set())
  const [interviewDone, setInterviewDone] = useState(new Set())
  const [search, setSearch] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [loading, setLoading] = useState(true)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [resumeSelectOpen, setResumeSelectOpen] = useState(false)
  const [pendingJobId, setPendingJobId] = useState(null)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    if (jobs.length === 0) setLoading(true)
    try {
      const candidateId = localStorage.getItem('recruitai.user_id')
      const [r1, r2, r3, r4] = await Promise.all([
        c0JobsAll().catch(() => ({ data: [] })),
        uResumeList().catch(() => ({ data: [] })),
        c0Applications().catch(() => ({ data: [] })),
        candidateId ? c0InterviewScores(candidateId).catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
      ])
      setJobs(toArr(r1))
      setResumes(toArr(r2))
      const apps = toArr(r3)
      setAppliedIds(new Set(apps.filter((a) => a.status !== 'withdrawn').map((a) => a.job_id)))
      const scores = toArr(r4)
      setInterviewDone(new Set(scores.map((s) => s.job_id).filter(Boolean)))
    } catch {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const apply = async (e, jobId) => {
    e.stopPropagation()
    if (resumes.length === 0) {
      toast.error('Upload a resume first on the Dashboard')
      return
    }
    const job = jobs.find((j) => j.id === jobId)
    if (job?.interview_required && !interviewDone.has(jobId)) {
      toast.error('Please complete the AI Technical Interview first (open the job and click Start Interview)')
      return
    }
    if (resumes.length === 1) {
      doApply(jobId, resumes[0].id)
      return
    }
    setPendingJobId(jobId)
    setSelectedResumeId(resumes[0]?.id || '')
    setResumeSelectOpen(true)
  }

  const doApply = async (jobId, resumeId) => {
    setConfirm({
      open: true,
      title: 'Apply to this job?',
      message: 'Your resume will be submitted to the employer pipeline.',
      action: async () => {
        try {
          const candidateId = localStorage.getItem('recruitai.user_id') || ''
          const candidateName = localStorage.getItem('recruitai.name') || ''
          await uJobsApply(jobId, {
            candidate_id: candidateId,
            candidate_name: candidateName,
            resume_id: resumeId,
          })
          setAppliedIds((prev) => new Set([...prev, jobId]))
          toast.success('Application submitted successfully!')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed to apply')
        }
      }
    })
  }

  const withdraw = async (e, jobId) => {
    e.stopPropagation()
    setConfirm({
      open: true,
      title: 'Withdraw application?',
      message: 'You can re-apply later if the position remains open.',
      danger: true,
      action: async () => {
        try {
          await uJobsWithdraw(jobId)
          setAppliedIds((prev) => {
            const n = new Set(prev)
            n.delete(jobId)
            return n
          })
          toast.success('Application withdrawn')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed to withdraw')
        }
      }
    })
  }

  const filtered = jobs.filter((j) => {
    const s = search.toLowerCase()
    const matchesSearch = !search ||
      j.title?.toLowerCase().includes(s) ||
      j.location?.toLowerCase().includes(s) ||
      j.department?.toLowerCase().includes(s) ||
      (j.required_skills || []).some((sk) => sk.toLowerCase().includes(s))

    const matchesType = selectedType === 'all' || (j.employment_type || 'Full-time').toLowerCase() === selectedType.toLowerCase()

    return matchesSearch && matchesType
  })

  return (
    <div className="fade-in" style={{ maxWidth: 1040, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Opportunity Discovery"
        title="Explore Open Positions"
        description="Discover engineering and technology openings matching your skills, qualifications, and experience level."
        icon={Briefcase}
      />

      {/* Search & Filter Bar */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: '1 1 280px' }}>
            <Search
              size={16}
              style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }}
            />
            <input
              type="text"
              placeholder="Search by role title, required skill, or location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: 36 }}
            />
          </div>

          {/* Type Filter Pills */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            {['all', 'Full-time', 'Contract', 'Part-time', 'Internship'].map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`btn btn-sm ${selectedType === type ? 'btn-primary' : 'btn-ghost'}`}
                style={{ fontSize: 'var(--p-text-xs)', padding: '6px 12px', textTransform: 'capitalize' }}
              >
                {type === 'all' ? 'All Roles' : type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Job Postings List */}
      {loading ? (
        <SkeletonLoader type="card" count={4} />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No matching job postings found"
          description={search ? "Try adjusting your search criteria or filters." : "There are currently no active job postings available."}
          actionLabel={search ? "Clear Search" : undefined}
          onAction={search ? () => { setSearch(''); setSelectedType('all'); } : undefined}
          icon={Briefcase}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-3)' }}>
          {filtered.map((job) => {
            const isApplied = appliedIds.has(job.id)
            const hasInterview = job.interview_required

            return (
              <div
                key={job.id}
                onClick={() => navigate(`/candidate/jobs/${job.id}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/candidate/jobs/${job.id}`)}
                className="card card-interactive"
                style={{
                  padding: 'var(--p-space-5)',
                  margin: 0,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 16,
                  flexWrap: 'wrap'
                }}
              >
                <div style={{ flex: '1 1 400px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, color: 'var(--color-fg)' }}>
                      {job.title}
                    </h3>
                    {isApplied && (
                      <span style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-full)',
                        background: 'var(--color-success-muted)',
                        color: 'var(--color-success)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 3
                      }}>
                        <CheckCircle size={11} /> Applied
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginBottom: 8 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--color-fg-secondary)', fontWeight: 600 }}>
                      <Building2 size={13} /> {job.company_name || 'Employer'}
                    </span>
                    <span>·</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <MapPin size={13} /> {job.location || 'Remote'}
                    </span>
                    <span>·</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Clock size={13} /> {job.employment_type || 'Full-time'}
                    </span>
                    <span>·</span>
                    <span>{job.job_level || 'Mid-Level'}</span>
                    <span>·</span>
                    <span>{job.experience_required || 0}+ yrs exp</span>
                  </div>

                  {job.required_skills?.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {[...new Set(job.required_skills)].slice(0, 5).map((s, i) => (
                        <span key={`${s}-${i}`} className="chip" style={{ fontSize: '11px', margin: 0, padding: '2px 8px' }}>
                          {s}
                        </span>
                      ))}
                      {job.required_skills.length > 5 && (
                        <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', alignSelf: 'center' }}>
                          +{job.required_skills.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }} onClick={(e) => e.stopPropagation()}>
                  {hasInterview && (
                    <span style={{
                      fontSize: '11px',
                      color: 'var(--color-purple)',
                      background: 'var(--color-purple-muted)',
                      padding: '3px 8px',
                      borderRadius: 'var(--radius-full)',
                      border: '1px solid rgba(139, 92, 246, 0.25)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }}>
                      <MessageSquare size={12} /> Tech Interview
                    </span>
                  )}

                  {isApplied ? (
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={(e) => withdraw(e, job.id)}
                      style={{ color: 'var(--color-danger)' }}
                    >
                      Withdraw
                    </button>
                  ) : (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={(e) => apply(e, job.id)}
                    >
                      Apply Now
                    </button>
                  )}

                  <button
                    className="btn-ghost btn-sm"
                    onClick={() => navigate(`/candidate/jobs/${job.id}`)}
                    aria-label="View full job posting"
                    style={{ padding: 6 }}
                    title="View full job posting"
                  >
                    <ChevronRight size={18} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Resume Selection Modal */}
      {resumeSelectOpen && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--modal-overlay, rgba(0,0,0,0.5))', backdropFilter: 'blur(8px)', padding: 'var(--p-space-4)' }}
          onClick={() => setResumeSelectOpen(false)}
        >
          <div
            style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border-strong)', borderRadius: 'var(--radius-xl)', padding: 'var(--p-space-5)', maxWidth: 420, width: '100%', boxShadow: 'var(--shadow-xl)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: '0 0 12px', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>Select Resume to Submit</h3>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '0 0 16px' }}>
              Choose which resume to attach to this application.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
              {resumes.map((r) => (
                <label
                  key={r.id}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    border: `1.5px solid ${selectedResumeId === r.id ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    background: selectedResumeId === r.id ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)',
                    cursor: 'pointer'
                  }}
                >
                  <input
                    type="radio"
                    name="resume-select"
                    value={r.id}
                    checked={selectedResumeId === r.id}
                    onChange={() => setSelectedResumeId(r.id)}
                    style={{ accentColor: 'var(--color-primary)' }}
                  />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 'var(--p-text-sm)' }}>{r.filename || 'Resume'}</div>
                    {r.candidate_name && <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>{r.candidate_name}</div>}
                  </div>
                </label>
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setResumeSelectOpen(false)}>Cancel</button>
              <button
                className="btn btn-primary btn-sm"
                disabled={!selectedResumeId}
                onClick={() => { setResumeSelectOpen(false); doApply(pendingJobId, selectedResumeId) }}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel={confirm.danger ? 'Withdraw' : 'Apply'}
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
