import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Briefcase, MapPin, Clock, Building2, Search, CheckCircle, MessageSquare } from 'lucide-react'
import { c0JobsAll, uResumeList, c0Applications, c0InterviewScores, uJobsApply, uJobsWithdraw } from '../api'
import ConfirmDialog from '../components/ConfirmDialog'

const toArr = (r) => {
  const d = r?.data
  if (Array.isArray(d)) return d
  if (Array.isArray(d?.data)) return d.data
  if (Array.isArray(d?.applications)) return d.applications
  if (Array.isArray(d?.jobs)) return d.jobs
  return []
}

export default function JobBoard() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [resumes, setResumes] = useState([])
  const [appliedIds, setAppliedIds] = useState(new Set())
  const [interviewDone, setInterviewDone] = useState(new Set())
  const [search, setSearch] = useState('')
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') { navigate('/login/candidate'); return }
    loadData()
  }, [])

  // Re-observe .reveal elements after data loads
  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      document.querySelectorAll('.reveal:not(.visible)').forEach(el => el.classList.add('visible'))
      return
    }
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target) } }),
      { threshold: 0.15 }
    )
    document.querySelectorAll('.reveal:not(.visible)').forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [jobs, resumes])

  const loadData = async () => {
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
      setAppliedIds(new Set(apps.filter(a => a.status !== 'withdrawn').map(a => a.job_id)))
      const scores = toArr(r4)
      setInterviewDone(new Set(scores.map(s => s.job_id || s.job_role).filter(Boolean)))
    } catch {
      toast.error('Failed to load jobs')
    }
  }

  const apply = async (e, jobId) => {
    e.stopPropagation()
    if (resumes.length === 0) { toast.error('Upload a resume first on the Dashboard'); return }
    const job = jobs.find(j => j.id === jobId)
    if (job?.interview_required && !interviewDone.has(jobId) && !interviewDone.has(job.job_role || job.title)) {
      toast.error('Complete the interview first (open the job and click Start Interview)')
      return
    }
    setConfirm({
      open: true,
      title: 'Apply to this job?',
      message: 'Your resume will be submitted to the employer.',
      action: async () => {
        try {
          const candidateId = localStorage.getItem('recruitai.user_id') || ''
          const candidateName = localStorage.getItem('recruitai.name') || ''
          await uJobsApply(jobId, {
            candidate_id: candidateId,
            candidate_name: candidateName,
            resume_id: resumes[0].id,
          })
          setAppliedIds((prev) => new Set([...prev, jobId]))
          toast.success('Applied successfully!')
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
      message: 'You can re-apply later if the position is still open.',
      danger: true,
      action: async () => {
        try {
          await uJobsWithdraw(jobId)
          setAppliedIds((prev) => { const n = new Set(prev); n.delete(jobId); return n })
          toast.success('Application withdrawn')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed to withdraw')
        }
      }
    })
  }

  const filtered = jobs.filter((j) => {
    if (!search) return true
    const s = search.toLowerCase()
    return j.title?.toLowerCase().includes(s) || j.location?.toLowerCase().includes(s) || j.department?.toLowerCase().includes(s)
  })

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 900, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>Browse Jobs</h1>
      <p className="muted" style={{ fontSize: 13, marginBottom: 20 }}>Find open positions and apply with your resume</p>

      <div style={{ position: 'relative', marginBottom: 20 }}>
        <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text"
          placeholder="Search jobs by title, location, or department..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ paddingLeft: 36, width: '100%' }}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <Briefcase size={32} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
          <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>No jobs found</div>
          <div className="muted" style={{ fontSize: 13 }}>Check back later or ask a company to post positions.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map((job) => {
            const applied = appliedIds.has(job.id)
            return (
              <div
                key={job.id}
                className="card"
                style={{ padding: 20, cursor: 'pointer', transition: 'border-color 0.15s' }}
                onClick={() => navigate(`/candidate/jobs/${job.id}`)}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = ''}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <Briefcase size={16} style={{ color: 'var(--accent)' }} />
                      <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>{job.title}</h3>
                      {applied && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--color-success)', background: 'var(--color-success-bg, rgba(16,185,129,0.1))', padding: '2px 8px', borderRadius: 99 }}>
                          <CheckCircle size={11} /> Applied
                        </span>
                      )}
                      {job.interview_required && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: interviewDone.has(job.job_role || job.title) ? 'var(--color-success)' : 'var(--accent-2)', background: interviewDone.has(job.job_role || job.title) ? 'rgba(34,197,94,0.1)' : 'var(--color-accent2-bg, rgba(124,108,255,0.1))', padding: '2px 8px', borderRadius: 99 }}>
                          <MessageSquare size={11} /> {interviewDone.has(job.job_role || job.title) ? 'Interview Done' : 'Interview'}
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>
                      {job.location && <span><MapPin size={12} /> {job.location}</span>}
                      {job.employment_type && <span><Clock size={12} /> {job.employment_type}</span>}
                      {job.department && <span><Building2 size={12} /> {job.department}</span>}
                    </div>
                    {job.description && (
                      <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                        {job.description.slice(0, 150)}{job.description.length > 150 ? '...' : ''}
                      </p>
                    )}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 8 }}>
                        {job.required_skills.slice(0, 6).map((s) => (
                          <span key={s} className="chip" style={{ fontSize: 11 }}>{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div style={{ flexShrink: 0, marginLeft: 16 }} onClick={(e) => e.stopPropagation()}>
                    {applied ? (
                      <button className="btn btn-outline" onClick={(e) => withdraw(e, job.id)} style={{ fontSize: 13 }}>
                        Withdraw
                      </button>
                    ) : (
                      <button className="btn" onClick={(e) => apply(e, job.id)} style={{ fontSize: 13 }}>
                        Apply
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel={confirm.danger ? 'Withdraw' : 'Apply'}
        onConfirm={async () => { await confirm.action(); setConfirm({ ...confirm, open: false }) }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
