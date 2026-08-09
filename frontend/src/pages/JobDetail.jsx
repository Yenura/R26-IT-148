import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Briefcase, MapPin, Clock, ArrowLeft, FileSearch, MessagesSquare, Target, Users, Play, Settings } from 'lucide-react'
import { uJobsPublic, uJobsGet, uJobsApply, uJobsWithdraw, uJobsApplicants } from '../api'

const C2 = import.meta.env.VITE_C2_URL || 'http://127.0.0.1:8002'

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

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadJob()
  }, [id])

  const loadJob = async () => {
    try {
      // Candidates use public endpoint, companies use owned endpoint
      const r = role === 'company' ? await uJobsGet(id) : await uJobsPublic(id)
      setJob(r.data)
      if (role === 'candidate') loadCandidateData()
      if (role === 'company') loadApplicants()
    } catch {
      toast.error('Job not found')
    }
  }

  const loadCandidateData = async () => {
    try {
      const { default: api } = await import('../api')
      const [r1, r2] = await Promise.all([
        api.C0.get('/resume/'),
        api.C0.get('/jobs'),
      ])
      setResumes(r1.data)
      const apps = Array.isArray(r2.data) ? r2.data : r2.data.applications || []
      setApplied(apps.some(a => a.job_id === id && a.status !== 'withdrawn'))
    } catch {}
  }

  const loadApplicants = async () => {
    try {
      const r = await uJobsApplicants(id)
      setApplicants(Array.isArray(r.data) ? r.data : r.data.applicants || [])
    } catch {}
  }

  const apply = async () => {
    if (resumes.length === 0) { toast.error('Upload a resume first'); return }
    try {
      const candidateId = localStorage.getItem('recruitai.user_id') || ''
      const candidateName = localStorage.getItem('recruitai.name') || ''
      await uJobsApply(id, {
        candidate_id: candidateId,
        candidate_name: candidateName,
        resume_id: resumes[0].id,
      })
      toast.success('Applied!')
      setApplied(true)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to apply')
    }
  }

  const withdraw = async () => {
    if (!confirm('Withdraw your application?')) return
    try {
      await uJobsWithdraw(id)
      toast.success('Application withdrawn')
      setApplied(false)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to withdraw')
    }
  }

  const startInterview = async () => {
    if (!job) return
    try {
      const skills = job.required_skills?.length > 0 ? job.required_skills : [job.title]
      const r = await fetch(`${C2}/api/v1/interview/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: localStorage.getItem('recruitai.user_id') || 'guest',
          job_role: job.title,
          required_skills: skills,
          num_questions: job.interview_question_count || 10,
        }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Failed to start interview')
      setInterviewSession(data)
      setInterviewStarted(true)
    } catch (err) {
      toast.error(err.message || 'Failed to start interview')
    }
  }

  if (!job) return <div className="empty">Loading job...</div>

  const skills = job.required_skills?.length > 0 ? job.required_skills : []

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        <ArrowLeft size={14} /> Back
      </button>

      {/* Job Header */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 4 }}>{job.title}</h1>
            <div className="muted" style={{ fontSize: 13, display: 'flex', gap: 16 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><MapPin size={14} /> {job.location || 'Remote'}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={14} /> {job.employment_type || 'Full-time'}</span>
              {job.experience_required > 0 && <span>{job.experience_required}+ years exp</span>}
            </div>
          </div>
          {role === 'candidate' && (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {applied ? (
                <>
                  <span style={{ fontSize: 13, color: 'var(--color-success)', fontWeight: 600 }}>Applied</span>
                  <button className="btn btn-ghost btn-sm" onClick={withdraw} style={{ fontSize: 13 }}>Withdraw</button>
                </>
              ) : (
                <button className="btn btn-success" onClick={apply}>Apply Now</button>
              )}
            </div>
          )}
        </div>

        {job.description && <p style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 12 }}>{job.description}</p>}

        {skills.length > 0 && (
          <div style={{ marginBottom: 8 }}>
            <span className="muted" style={{ fontSize: 12 }}>Required Skills: </span>
            {skills.map(s => <span key={s} className="chip" style={{ fontSize: 11 }}>{s}</span>)}
          </div>
        )}
        {job.preferred_skills?.length > 0 && (
          <div>
            <span className="muted" style={{ fontSize: 12 }}>Preferred: </span>
            {job.preferred_skills.map(s => <span key={s} className="chip" style={{ fontSize: 11, borderColor: 'var(--color-info)', color: 'var(--color-info)' }}>{s}</span>)}
          </div>
        )}

        {/* Interview Config Badge */}
        {job.interview_required && (
          <div style={{ marginTop: 12, padding: '8px 12px', borderRadius: 6, background: 'var(--color-warning-bg, rgba(251,191,36,0.1))', border: '1px solid var(--color-warning, #f59e0b)', fontSize: 13 }}>
            <Settings size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
            Interview required ({job.interview_question_count || 10} questions)
          </div>
        )}
      </div>

      {/* Candidate Actions */}
      {role === 'candidate' && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 12 }}>Quick Actions</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <Link to="/pipeline/cv-match" style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
              padding: 20, borderRadius: 8, border: '1px solid var(--color-border)',
              background: 'var(--color-bg-elevated)', textDecoration: 'none', color: 'var(--color-fg)',
            }}>
              <FileSearch size={24} style={{ color: 'var(--color-primary)' }} />
              <span style={{ fontWeight: 600, fontSize: 13 }}>CV Match</span>
            </Link>
            <button onClick={startInterview} disabled={interviewStarted} style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
              padding: 20, borderRadius: 8, border: '1px solid var(--color-border)',
              background: 'var(--color-bg-elevated)', color: 'var(--color-fg)',
              cursor: interviewStarted ? 'default' : 'pointer', opacity: interviewStarted ? 0.6 : 1,
            }}>
              <MessagesSquare size={24} style={{ color: 'var(--color-success)' }} />
              <span style={{ fontWeight: 600, fontSize: 13 }}>
                {interviewStarted ? 'In Progress...' : 'Start Interview'}
              </span>
              {job.interview_required && (
                <span style={{ fontSize: 11, color: 'var(--color-warning)' }}>Required</span>
              )}
            </button>
            <Link to="/pipeline/skill-gap" style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
              padding: 20, borderRadius: 8, border: '1px solid var(--color-border)',
              background: 'var(--color-bg-elevated)', textDecoration: 'none', color: 'var(--color-fg)',
            }}>
              <Target size={24} style={{ color: 'var(--color-warning)' }} />
              <span style={{ fontWeight: 600, fontSize: 13 }}>Skill Gap</span>
            </Link>
          </div>
        </div>
      )}

      {/* Practice Interview Link (candidates only) */}
      {role === 'candidate' && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ marginBottom: 4 }}>Practice Interview</h3>
              <p className="muted" style={{ fontSize: 13 }}>Practice with questions for this role. Adjustable question count.</p>
            </div>
            <Link to={`/candidate/interview?role=${encodeURIComponent(job.title)}&skills=${encodeURIComponent(skills.join(','))}`} className="btn btn-ghost btn-sm">
              <Play size={14} /> Practice
            </Link>
          </div>
        </div>
      )}

      {/* Inline Interview (if started) */}
      {interviewStarted && interviewSession && (
        <InlineInterview session={interviewSession} job={job} onDone={() => { setInterviewStarted(false); setInterviewSession(null) }} />
      )}

      {/* Company Applicants View */}
      {role === 'company' && (
        <div className="card">
          <h3 style={{ marginBottom: 12 }}><Users size={16} /> Applicants ({applicants.length})</h3>
          {applicants.length === 0 ? (
            <div className="empty" style={{ padding: 24 }}>
              <p>No applicants yet</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {applicants.map((a) => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 500 }}>{a.candidate_name || '—'}</td>
                    <td><span className={`badge ${a.status === 'applied' ? 'badge-blue' : 'badge-green'}`}>{a.status}</span></td>
                    <td className="muted" style={{ fontSize: 13 }}>{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

/* ── Inline Interview Component ─────────────────────────────── */
function InlineInterview({ session, job, onDone }) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)

  const questions = session.questions || []
  const q = questions[step]

  const setAnswer = (val) => setAnswers(prev => ({ ...prev, [step]: val }))

  const submit = async () => {
    setSubmitting(true)
    try {
      const formattedAnswers = questions.map((qq, i) => {
        const a = answers[i]
        if (qq.question_type === 'MCQ') {
          return { question_id: qq.id, selected_option: a != null ? Number(a) : null }
        }
        return { question_id: qq.id, answer_text: a || '' }
      })
      const r = await fetch(`${C2}/api/v1/interview/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.session_id,
          answers: formattedAnswers,
        }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Submit failed')
      setResult(data)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (result) {
    const eval_ = result.evaluation || result
    const score = eval_.overall_score ?? eval_.score ?? 0
    return (
      <div className="card fade-in">
        <h3>Interview Complete</h3>
        <div style={{ fontSize: 48, fontWeight: 800, color: score >= 70 ? 'var(--color-success)' : 'var(--color-danger)', margin: '16px 0' }}>
          {Math.round(score)}%
        </div>
        <p className="muted" style={{ marginBottom: 16 }}>{eval_.grade || (score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs improvement')}</p>
        <button className="btn btn-primary" onClick={onDone}>Done</button>
      </div>
    )
  }

  if (!q) return null

  return (
    <div className="card fade-in" style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <span className="muted" style={{ fontSize: 13 }}>
          Question {step + 1} of {questions.length}
        </span>
        <span className="chip" style={{ fontSize: 11 }}>{q.question_type}</span>
      </div>

      <p style={{ fontSize: 15, lineHeight: 1.6, marginBottom: 20, fontWeight: 500 }}>{q.question_text}</p>

      {q.question_type === 'MCQ' && q.options && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
          {q.options.map((opt, idx) => (
            <label key={idx} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px',
              borderRadius: 6, border: '1px solid var(--color-border)',
              background: answers[step] === String(idx) ? 'var(--color-primary-bg)' : 'var(--color-bg-elevated)',
              cursor: 'pointer',
            }}>
              <input type="radio" name={`q-${step}`} value={idx}
                checked={answers[step] === String(idx)}
                onChange={() => setAnswer(String(idx))} />
              <span style={{ fontSize: 14 }}>{typeof opt === 'object' ? opt.text : opt}</span>
            </label>
          ))}
        </div>
      )}

      {q.question_type === 'Descriptive' && (
        <textarea
          className="input"
          rows={5}
          placeholder="Type your answer..."
          value={answers[step] || ''}
          onChange={e => setAnswer(e.target.value)}
          style={{ marginBottom: 20 }}
        />
      )}

      {q.question_type === 'Coding' && (
        <textarea
          className="input"
          rows={8}
          placeholder="Write your code..."
          value={answers[step] || ''}
          onChange={e => setAnswer(e.target.value)}
          style={{ marginBottom: 20, fontFamily: 'monospace', fontSize: 13 }}
        />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => setStep(s => Math.max(0, s - 1))} disabled={step === 0}>Previous</button>
        {step < questions.length - 1 ? (
          <button className="btn btn-primary btn-sm" onClick={() => setStep(s => s + 1)}>Next</button>
        ) : (
          <button className="btn btn-success btn-sm" onClick={submit} disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Interview'}
          </button>
        )}
      </div>
    </div>
  )
}
