import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ListOrdered, Trophy, Users, Briefcase, Sparkles, Filter, CheckCircle2, AlertCircle, TrendingUp, Cpu, Award } from 'lucide-react'
import { c3Roles, c0JobsAll, c3Pipeline } from '../api'

export default function Ranking() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const r = await c0JobsAll()
      const jobList = r.data || []
      setJobs(jobList)
      if (jobList.length > 0) {
        setSelectedJob(jobList[0].id)
      }
    } catch {}
  }

  const computePipeline = async (targetJobId) => {
    const jobIdToUse = targetJobId || selectedJob
    if (!jobIdToUse && !selectedRole) return toast.error('Please select a job or role')
    
    setBusy(true)
    try {
      const r = await c3Pipeline(jobIdToUse || selectedRole)
      setResult(r.data)
      toast.success('Multi-Criteria Candidate Ranking Complete!')
    } catch (err) {
      toast.error('Failed to compute pipeline ranking')
    } finally {
      setBusy(false)
    }
  }

  const selectedJobObj = jobs.find(j => j.id === selectedJob)

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 1000, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="page-head" style={{ marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1, marginBottom: 4 }}>
            Component 3 Engine
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
            <Award size={30} style={{ color: 'var(--accent)' }} /> Multi-Criteria Candidate Ranking & LTR Engine
          </h1>
          <p className="muted" style={{ fontSize: 13, marginTop: 6, margin: 0 }}>
            Evaluates Candidate Scoring System (CSS) & LambdaMART Learning-to-Rank (LTR) model across Component 1 features ($S_{`{skill}`}, S_{`{exp}`}, S_{`{edu}`}$) and Component 2 interview metrics ($P_{`{mcq}`}, P_{`{desc}`}, P_{`{code}`}$).
          </p>
        </div>
      </div>

      {/* Control Setup Card */}
      <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={18} style={{ color: 'var(--accent)' }} /> Select Target Job Requirement
          </h3>
          <span className="chip" style={{ fontSize: 12, padding: '4px 12px', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.3)', fontWeight: 700 }}>
            LambdaMART LTR Optimized
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 20 }}>
          {/* Posted Job Selector */}
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              Posted Job Positions ({jobs.length})
            </label>
            <select
              value={selectedJob}
              onChange={(e) => {
                setSelectedJob(e.target.value)
                if (e.target.value) computePipeline(e.target.value)
              }}
              style={{ width: '100%', padding: '12px 14px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, fontWeight: 600 }}
            >
              <option value="">Choose a job position...</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} {j.company_name ? `— ${j.company_name}` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Canonical Role Fallback */}
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              Or Target IT Role
            </label>
            <select
              value={selectedRole}
              onChange={(e) => {
                setSelectedRole(e.target.value)
                if (e.target.value) {
                  setSelectedJob('')
                  computePipeline(e.target.value)
                }
              }}
              style={{ width: '100%', padding: '12px 14px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14 }}
            >
              <option value="">All IT Roles...</option>
              {Object.keys(roles).sort().map((r) => (
                <option key={r} value={r}>
                  {r.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Job Spec Overview */}
        {selectedJobObj && (
          <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)', marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>
                {selectedJobObj.title} {selectedJobObj.location ? `· ${selectedJobObj.location}` : ''}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <strong>Required Skills:</strong>
                {selectedJobObj.required_skills?.map((s) => (
                  <span key={s} style={{ fontSize: 11, padding: '1px 6px', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', borderRadius: 4 }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <div style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-muted)' }}>
              <div>Min Experience: <strong>{selectedJobObj.experience_required || 0} years</strong></div>
              <div>Applications: <strong>{selectedJobObj.applicant_count || 0} candidates</strong></div>
            </div>
          </div>
        )}

        <button
          className="btn"
          onClick={() => computePipeline()}
          disabled={busy}
          style={{ width: '100%', padding: '14px', fontSize: 15, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, background: 'var(--color-primary)', color: '#fff' }}
        >
          <ListOrdered size={18} /> {busy ? 'Running Multi-Criteria LTR Ranking...' : 'Run Candidate Ranking & Blended Score Evaluation'}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="fade-in card" style={{ padding: 28, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 16, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text)' }}>
                <Trophy size={20} style={{ color: 'var(--accent)' }} />
                Ranked Candidate Leaderboard {result.job_role && `— ${result.job_role.replace(/_/g, ' ')}`}
              </h3>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
                Sorted by CSS (Candidate Scoring System) & LambdaMART LTR scores.
              </p>
            </div>
            <span className="chip" style={{ fontSize: 12, padding: '6px 14px', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.3)', fontWeight: 700 }}>
              {(result.data || []).length} Candidates Evaluated
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {(result.data || []).map((c, i) => (
              <div
                key={c.candidate_id || i}
                style={{
                  padding: 20,
                  borderRadius: 10,
                  background: 'var(--bg)',
                  border: i === 0 && c.passed_hard_filter ? '1px solid var(--accent)' : '1px solid var(--border)',
                  opacity: c.passed_hard_filter ? 1 : 0.7,
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, marginBottom: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    {/* Rank Pill */}
                    <div style={{
                      width: 40, height: 40, borderRadius: 10,
                      background: !c.passed_hard_filter ? 'var(--border)' : i === 0 ? 'var(--accent)' : i === 1 ? '#3b82f6' : 'var(--border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 900, fontSize: 16, color: c.passed_hard_filter && i < 2 ? '#fff' : 'var(--text)'
                    }}>
                      {c.passed_hard_filter ? `#${c.rank}` : '✗'}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontWeight: 800, fontSize: 16, color: 'var(--text)' }}>{c.candidate_name}</span>
                        {c.passed_hard_filter ? (
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.3)', fontWeight: 700 }}>
                            ✓ Qualified
                          </span>
                        ) : (
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)', fontWeight: 700 }}>
                            {c.filter_fail_reason || 'Disqualified'}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                        Candidate ID: <strong style={{ color: 'var(--text)' }}>{c.candidate_id}</strong>
                        {c.ltr_score != null && (
                          <span style={{ marginLeft: 12, color: 'var(--accent)' }}>
                            LTR Model Score: <strong>{(c.ltr_score * 100).toFixed(1)}%</strong>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Final CSS Score Badge */}
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 24, fontWeight: 900, color: c.passed_hard_filter ? 'var(--accent)' : 'var(--text-muted)', lineHeight: 1 }}>
                      {((c.CSS || 0) * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginTop: 4 }}>
                      CSS Score
                    </div>
                  </div>
                </div>

                {/* 6 Feature Components Grid (C1 & C2 Vector Inputs) */}
                <div style={{
                  display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)',
                  gap: 8, padding: '12px 14px', background: 'var(--bg-elevated)', borderRadius: 8, fontSize: 12, border: '1px solid var(--border)'
                }}>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C1: EDUCATION</span>
                    <strong style={{ color: 'var(--text)', fontSize: 13 }}>{((c.S_edu || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C1: EXPERIENCE</span>
                    <strong style={{ color: 'var(--text)', fontSize: 13 }}>{((c.S_exp || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C1: SKILL MATCH</span>
                    <strong style={{ color: '#22c55e', fontSize: 13 }}>{((c.S_skill || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: MCQ SCORE</span>
                    <strong style={{ color: '#3b82f6', fontSize: 13 }}>{((c.P_mcq || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: DESCRIPTIVE</span>
                    <strong style={{ color: '#8b5cf6', fontSize: 13 }}>{((c.P_desc || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: CODING</span>
                    <strong style={{ color: '#f59e0b', fontSize: 13 }}>{((c.P_code || 0) * 100).toFixed(0)}%</strong>
                  </div>
                </div>
              </div>
            ))}

            {(!result.data || result.data.length === 0) && (
              <div style={{ padding: 24, textAlign: 'center', background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                <AlertCircle size={24} style={{ marginBottom: 8, color: 'var(--text-muted)' }} />
                <div style={{ fontSize: 14, fontWeight: 600 }}>No applicants found for this position</div>
                <div style={{ fontSize: 12, marginTop: 4 }}>Select another job position or post a new job to start ranking candidates.</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

