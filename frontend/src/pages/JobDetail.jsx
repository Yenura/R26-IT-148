import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  MapPin, Clock, ArrowLeft, FileSearch, MessagesSquare, Target, Users,
  Play, Settings, Building2, CheckCircle2, Briefcase, Award, Sparkles, AlertCircle
} from 'lucide-react'
import {
  uJobsPublic, uJobsGet, uJobsApply, uJobsWithdraw, uJobsApplicants,
  c2RunCode, c2Start, c2Submit, uResumeList, c0Applications, c0InterviewScores
} from '../api'
import PageHeader from '../components/PageHeader'
import ConfirmDialog from '../components/ConfirmDialog'
import SkeletonLoader from '../components/SkeletonLoader'

export default function JobDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const role = localStorage.getItem('recruitai.role')

  const [job, setJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [resumes, setResumes] = useState([])
  const [applied, setApplied] = useState(false)
  const [interviewStarted, setInterviewStarted] = useState(false)
  const [interviewSession, setInterviewSession] = useState(null)
  const [interviewDone, setInterviewDone] = useState(false)
  const [loading, setLoading] = useState(true)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) {
      navigate('/')
      return
    }
    loadJob()
  }, [id])

  const loadJob = async () => {
    setLoading(true)
    try {
      const r = role === 'company' ? await uJobsGet(id) : await uJobsPublic(id)
      setJob(r?.data)
      if (role === 'candidate') loadCandidateData(r?.data)
      if (role === 'company') loadApplicants()
    } catch {
      toast.error('Job not found')
    } finally {
      setLoading(false)
    }
  }

  const loadCandidateData = async (jobData) => {
    try {
      const candidateId = localStorage.getItem('recruitai.user_id')
      const [r1, r2, r3] = await Promise.all([
        uResumeList().catch(() => ({ data: [] })),
        c0Applications().catch(() => ({ data: [] })),
        candidateId ? c0InterviewScores(candidateId).catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
      ])
      const resumeList = Array.isArray(r1.data) ? r1.data : []
      setResumes(resumeList)
      const apps = Array.isArray(r2.data) ? r2.data : []
      setApplied(apps.some((a) => a.job_id === id && a.status !== 'withdrawn'))

      const scores = Array.isArray(r3.data) ? r3.data : []
      const targetRole = jobData?.job_role || jobData?.title || ''
      setInterviewDone(scores.some((s) => s.job_role === targetRole || s.job_id === id))
    } catch {
      // Non-critical: resume/app data failed to load, UI shows empty state
    }
  }

  const loadApplicants = async () => {
    try {
      const r = await uJobsApplicants(id)
      setApplicants(Array.isArray(r.data) ? r.data : r.data?.applicants || [])
    } catch {
      toast.error('Failed to load applicants')
    }
  }

  const handleApply = async () => {
    if (resumes.length === 0) {
      toast.error('Please upload a resume on the Dashboard before applying')
      return
    }
    if (job?.interview_required && !interviewDone) {
      toast.error('Please complete the AI Technical Interview before applying')
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
          await uJobsApply(id, {
            candidate_id: candidateId,
            candidate_name: candidateName,
            resume_id: resumes[0].id,
          })
          toast.success('Application submitted successfully!')
          setApplied(true)
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed to apply')
        }
      }
    })
  }

  const handleWithdraw = async () => {
    setConfirm({
      open: true,
      title: 'Withdraw application?',
      message: 'You can re-apply later if the position is still open.',
      danger: true,
      action: async () => {
        try {
          await uJobsWithdraw(id)
          toast.success('Application withdrawn')
          setApplied(false)
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed to withdraw')
        }
      }
    })
  }

  const startInterview = () => {
    const params = new URLSearchParams({
      role: job?.job_role || job?.title || '',
      skills: (job?.required_skills || []).join(','),
      level: job?.job_level || 'Mid-Level',
      count: String(job?.interview_question_count || 10),
      mcqTime: String(job?.interview_mcq_time || 60),
      descTime: String(job?.interview_desc_time || 300),
      codingTime: String(job?.interview_coding_time || 600),
      totalTime: String(job?.interview_total_time || 60),
    })
    navigate(`/candidate/interview?${params.toString()}`)
  }

  if (loading) {
    return (
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <SkeletonLoader type="card" count={2} />
      </div>
    )
  }

  if (!job) {
    return (
      <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center', padding: 60 }}>
        <h3>Job posting not found</h3>
        <button className="btn btn-ghost" onClick={() => navigate(-1)} style={{ marginTop: 12 }}>
          <ArrowLeft size={16} /> Back
        </button>
      </div>
    )
  }

  return (
    <div className="fade-in" style={{ maxWidth: 1040, margin: '0 auto' }}>
      {/* Back Button */}
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate(role === 'company' ? '/company/dashboard' : '/candidate/jobs')}
        style={{ marginBottom: 'var(--p-space-4)' }}
      >
        <ArrowLeft size={14} /> Back to {role === 'company' ? 'Dashboard' : 'Jobs'}
      </button>

      {/* 2-Column Responsive Layout */}
      <div className="dashboard-grid dashboard-grid-main" style={{ alignItems: 'start' }}>
        
        {/* Left Column: Job Description & Details */}
        <div>
          <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-6)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <span style={{
                fontSize: '11px',
                fontWeight: 700,
                textTransform: 'uppercase',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                background: 'var(--color-primary-muted)',
                color: 'var(--color-primary)'
              }}>
                {job.department || 'Engineering'}
              </span>
              <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>·</span>
              <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                {job.employment_type || 'Full-time'}
              </span>
            </div>

            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-fg)', margin: '0 0 12px 0' }}>
              {job.title}
            </h1>

            <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap', fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', paddingBottom: 16, borderBottom: '1px solid var(--color-border-subtle)', marginBottom: 20 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <Building2 size={15} style={{ color: 'var(--color-primary)' }} /> {job.company_name || 'Hiring Employer'}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <MapPin size={15} /> {job.location || 'Remote'}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <Clock size={15} /> {job.experience_required || 0}+ yrs experience
              </span>
            </div>

            {/* Description */}
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 8 }}>
                Role Description & Overview
              </h3>
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.6, whiteSpace: 'pre-line', margin: 0 }}>
                {job.description || 'Join our engineering team to architect and build high-scale, resilient applications.'}
              </p>
            </div>

            {/* Required Skills */}
            {job.required_skills?.length > 0 && (
              <div style={{ marginBottom: 24 }}>
                <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 10 }}>
                  Required Technical Competencies
                </h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {job.required_skills.map((skill) => (
                    <span
                      key={skill}
                      className="chip"
                      style={{
                        fontSize: '12px',
                        padding: '4px 10px',
                        background: 'var(--color-bg-elevated)',
                        borderColor: 'var(--color-border)',
                        color: 'var(--color-fg)'
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Candidate Qualification Requirements */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Education Requirement
                </div>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>
                  {job.education_required || 'Bachelor Degree in CS / IT / SE'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Minimum Experience
                </div>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>
                  {job.experience_required || 0} Years Relevant Experience
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Sticky Action & Screening Summary */}
        <div>
          <div className="card" style={{ padding: 'var(--p-space-5)', position: 'sticky', top: 76 }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
              {role === 'company' ? 'Job Management' : 'Application Summary'}
            </h3>

            {role === 'company' ? (
              /* Recruiter view */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ padding: 12, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>Total Applicants</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                    {applicants.length}
                  </div>
                </div>

                <Link to={`/company/pipeline/${job.id}`} className="btn btn-primary" style={{ width: '100%' }}>
                  <Users size={16} /> View Pipeline & Rankings
                </Link>
              </div>
            ) : (
              /* Candidate view */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {/* Tech Interview Requirement Badge */}
                {job.interview_required && (
                  <div style={{
                    padding: 12,
                    background: interviewDone ? 'var(--color-success-muted)' : 'var(--color-purple-muted)',
                    border: `1px solid ${interviewDone ? 'rgba(16, 185, 129, 0.3)' : 'rgba(139, 92, 246, 0.3)'}`,
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: interviewDone ? 'var(--color-success)' : 'var(--color-purple)', display: 'flex', alignItems: 'center', gap: 6 }}>
                      {interviewDone ? <CheckCircle2 size={14} /> : <MessagesSquare size={14} />}
                      {interviewDone ? 'AI Interview Completed' : 'AI Technical Interview Required'}
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--color-fg-secondary)', margin: '4px 0 0 0' }}>
                      {interviewDone
                        ? 'Your technical interview score is attached to this application.'
                        : `${job.interview_question_count || 10} questions · ${job.interview_total_time || 60} min total`}
                    </p>
                  </div>
                )}

                {/* Primary Action Button */}
                {applied ? (
                  <div>
                    <div style={{
                      padding: '10px 12px',
                      background: 'var(--color-success-muted)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--color-success)',
                      fontSize: 'var(--p-text-sm)',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      marginBottom: 10
                    }}>
                      <CheckCircle2 size={16} /> Application Submitted
                    </div>
                    <button
                      className="btn btn-ghost"
                      onClick={handleWithdraw}
                      style={{ width: '100%', color: 'var(--color-danger)' }}
                    >
                      Withdraw Application
                    </button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {job.interview_required && !interviewDone ? (
                      <button className="btn btn-primary" onClick={startInterview} style={{ width: '100%' }}>
                        <Play size={16} /> Start Technical Interview
                      </button>
                    ) : (
                      <button className="btn btn-primary" onClick={handleApply} style={{ width: '100%' }}>
                        <Briefcase size={16} /> Submit Application
                      </button>
                    )}
                  </div>
                )}

                {/* Direct link to CV Match */}
                <Link
                  to={`/pipeline/cv-match?job=${id}`}
                  className="btn btn-ghost btn-sm"
                  style={{ width: '100%', fontSize: 'var(--p-text-xs)', marginTop: 4 }}
                >
                  <Sparkles size={13} /> Check CV Match Fit
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

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
