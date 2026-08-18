import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ListOrdered, Trophy, Users, Briefcase, AlertCircle, Award } from 'lucide-react'
import { c0JobsAll, c3Pipeline } from '../api'

export default function Ranking() {
  const navigate = useNavigate()
  const userRole = localStorage.getItem('recruitai.role')
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [loadingJobs, setLoadingJobs] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') { navigate('/login/company'); return }
    loadJobs()
  }, [])

  const loadCompanyJobs = async () => {
    setLoadingJobs(true)
    try {
      // Fetch ONLY jobs belonging to the currently logged-in company
      const r = await C0.get('/jobs')
      const companyJobs = Array.isArray(r.data) ? r.data : []
      setJobs(companyJobs)

      if (companyJobs.length > 0) {
        const firstJobId = companyJobs[0].id || companyJobs[0]._id
        setSelectedJob(firstJobId)
        computePipeline(firstJobId)
      }
    } catch { toast.error('Failed to load jobs') }
  }

  const computePipeline = async (targetJobId) => {
    const jobIdToUse = targetJobId || selectedJob
    if (!jobIdToUse) return toast.error('Please select a job')
    
    setBusy(true)
    try {
      const r = await c3Pipeline(jobIdToUse)
      setResult(r.data)
      toast.success('Candidate Ranking & LTR Evaluation Complete!')
    } catch (err) {
      toast.error('Failed to compute candidate ranking')
    } finally {
      setBusy(false)
    }
  }

  const selectedJobObj = jobs.find(j => (j.id || j._id) === selectedJob)

  return (
    <div className="fade-in" style={{ padding: '24px 16px', maxWidth: 1050, margin: '0 auto' }}>
      {/* Header */}
      <div className="page-head" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1.2, marginBottom: 4 }}>
              Company Recruitment Portal · Component 3 Engine
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
              <Award size={30} style={{ color: 'var(--accent)' }} /> Multi-Criteria Candidate Ranking & LTR Pipeline
            </h1>
            <p className="muted" style={{ fontSize: 13, marginTop: 6, margin: 0 }}>
              Evaluates and ranks all applicants for your company's posted jobs using the <strong>Weighted Average & LambdaMART LTR model</strong>. Combines 3 CV criteria from Component 1 ($S_{'{skill}'}, S_{'{exp}'}, S_{'{edu}'}$) and 3 Interview sections from Component 2 ($P_{'{mcq}'}, P_{'{desc}'}, P_{'{code}'}$).
            </p>
          </div>

          <button
            className="btn btn-ghost btn-sm"
            onClick={() => computePipeline()}
            disabled={busy || jobs.length === 0}
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <RefreshCw size={14} className={busy ? 'spin' : ''} /> Recalculate Ranking
          </button>
        </div>
      </div>

      {/* Control Setup Card */}
      <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={18} style={{ color: 'var(--accent)' }} /> Select Target Job Requirement
          </h3>
          <span className="chip" style={{ fontSize: 12, padding: '4px 12px', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--color-info)', border: '1px solid rgba(59, 130, 246, 0.3)', fontWeight: 700 }}>
            LambdaMART LTR Optimized
          </span>
        </div>
      ) : (
        /* Control Setup Card for Company's Jobs */
        <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Briefcase size={18} style={{ color: 'var(--accent)' }} /> Select from Your Company's Posted Job Openings
            </h3>
            <span className="chip" style={{ fontSize: 11, padding: '4px 12px', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.3)', fontWeight: 700 }}>
              {jobs.length} Active Positions
            </span>
          </div>

          {/* Company-Only Job Selector */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              Your Posted Roles ({jobs.length})
            </label>
            <select
              value={selectedJob}
              onChange={(e) => {
                const val = e.target.value
                setSelectedJob(val)
                if (val) computePipeline(val)
              }}
              style={{ width: '100%', padding: '12px 14px', background: 'var(--input-bg)', border: '2px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, fontWeight: 700 }}
            >
              {jobs.map((j) => {
                const id = j.id || j._id
                return (
                  <option key={id} value={id}>
                    {j.title} • {j.department || 'Engineering'} ({j.location || 'Remote'}) — {j.employment_type || 'Full-time'}
                  </option>
                )
              })}
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
                  <span key={s} style={{ fontSize: 11, padding: '1px 6px', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--color-info)', borderRadius: 4 }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

        <button
          className="btn"
          onClick={() => computePipeline()}
          disabled={busy}
          style={{ width: '100%', padding: '14px', fontSize: 15, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, background: 'var(--color-primary)', color: 'var(--color-on-primary)' }}
        >
          <ListOrdered size={18} /> {busy ? 'Running Multi-Criteria LTR Ranking...' : 'Run Candidate Ranking & Blended Score Evaluation'}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="fade-in card" style={{ padding: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 16, marginBottom: 20, borderBottom: '1px solid var(--border)', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h3 style={{ fontSize: 18, fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text)' }}>
                <Trophy size={20} style={{ color: 'var(--accent)' }} />
                Ranked Applicants for {selectedJobObj?.title || 'Selected Position'}
              </h3>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
                Ranked from Best Candidate (#1) to Worst Candidate using 6-dimensional weighted scoring ($w_{`{CV}`} = 40\\%$, $w_{`{Interview}`} = 60\\%$) & LambdaMART LTR.
              </p>
            </div>
            <span className="chip" style={{ fontSize: 12, padding: '6px 14px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)', fontWeight: 700 }}>
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
                      background: !c.passed_hard_filter ? 'var(--border)' : i === 0 ? 'var(--accent)' : i === 1 ? 'var(--color-info)' : 'var(--border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 900, fontSize: 16, color: c.passed_hard_filter && i < 2 ? 'var(--color-on-primary)' : 'var(--text)'
                    }}>
                      {c.passed_hard_filter ? `#${c.rank}` : '✗'}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontWeight: 800, fontSize: 16, color: 'var(--text)' }}>{c.candidate_name}</span>
                        {c.passed_hard_filter ? (
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)', fontWeight: 700 }}>
                            ✓ Qualified
                          </span>
                        ) : (
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-danger)', border: '1px solid rgba(239, 68, 68, 0.3)', fontWeight: 700 }}>
                            {c.filter_fail_reason || 'Disqualified'}
                          </span>
                        )}
                      </div>

                      {/* Final Composite CSS Score */}
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 26, fontWeight: 900, color: passed ? 'var(--accent)' : 'var(--text-muted)', lineHeight: 1 }}>
                          {((c.CSS || 0) * 100).toFixed(1)}%
                        </div>
                        <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginTop: 4 }}>
                          Composite CSS Fit
                        </div>
                      </div>
                    </div>

                    {/* AI REASONING / WHY THIS CANDIDATE IS GOOD OR BAD */}
                    <div style={{
                      padding: 14,
                      background: 'var(--bg-elevated)',
                      borderRadius: 8,
                      border: '1px solid var(--border)',
                      marginBottom: 16
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>
                        <Brain size={15} /> AI Hiring Assessment & Evaluation:
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.4, marginBottom: 10 }}>
                        {c.reasoning || 'Candidate evaluated across CV credentials and technical interview performance.'}
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        {/* Strengths */}
                        <div>
                          <div style={{ fontSize: 11, fontWeight: 700, color: '#22c55e', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <CheckCircle2 size={13} /> Key Strengths:
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                            {(c.strengths || []).map((st, sIdx) => (
                              <span key={sIdx} className="chip" style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                                {st}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Weaknesses */}
                        <div>
                          <div style={{ fontSize: 11, fontWeight: 700, color: '#ef4444', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                            <AlertCircle size={13} /> Areas of Concern / Gaps:
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                            {(c.weaknesses || []).map((wk, wIdx) => (
                              <span key={wIdx} className="chip" style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                                {wk}
                              </span>
                            ))}
                          </div>
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
                    <strong style={{ color: 'var(--color-success)', fontSize: 13 }}>{((c.S_skill || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: MCQ SCORE</span>
                    <strong style={{ color: 'var(--color-info)', fontSize: 13 }}>{((c.P_mcq || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: DESCRIPTIVE</span>
                    <strong style={{ color: 'var(--color-purple)', fontSize: 13 }}>{((c.P_desc || 0) * 100).toFixed(0)}%</strong>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)' }}>C2: CODING</span>
                    <strong style={{ color: 'var(--color-warning)', fontSize: 13 }}>{((c.P_code || 0) * 100).toFixed(0)}%</strong>
                  </div>
                </div>
              </div>
            ))}

                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2 }}>
                              <span style={{ color: 'var(--text-muted)' }}>2. Experience ($S_{'{exp}'}$)</span>
                              <strong style={{ color: 'var(--text)' }}>{((c.S_exp || 0) * 100).toFixed(0)}%</strong>
                            </div>
                            <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{ width: `${(c.S_exp || 0) * 100}%`, height: '100%', background: '#3b82f6', borderRadius: 2 }} />
                            </div>
                          </div>

                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2 }}>
                              <span style={{ color: 'var(--text-muted)' }}>3. Education ($S_{'{edu}'}$)</span>
                              <strong style={{ color: 'var(--text)' }}>{((c.S_edu || 0) * 100).toFixed(0)}%</strong>
                            </div>
                            <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{ width: `${(c.S_edu || 0) * 100}%`, height: '100%', background: '#3b82f6', borderRadius: 2 }} />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* COMPONENT 2: INTERVIEW SECTIONS (60%) */}
                      <div style={{ padding: 12, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                          <Cpu size={13} style={{ color: '#22c55e' }} /> Component 2: AI Interview Sections (60%)
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2 }}>
                              <span style={{ color: 'var(--text-muted)' }}>1. Conceptual MCQs ($P_{'{mcq}'}$)</span>
                              <strong style={{ color: 'var(--text)' }}>{((c.P_mcq || 0) * 100).toFixed(0)}%</strong>
                            </div>
                            <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{ width: `${(c.P_mcq || 0) * 100}%`, height: '100%', background: '#22c55e', borderRadius: 2 }} />
                            </div>
                          </div>

                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2 }}>
                              <span style={{ color: 'var(--text-muted)' }}>2. Descriptive Theory ($P_{'{desc}'}$)</span>
                              <strong style={{ color: 'var(--text)' }}>{((c.P_desc || 0) * 100).toFixed(0)}%</strong>
                            </div>
                            <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{ width: `${(c.P_desc || 0) * 100}%`, height: '100%', background: '#22c55e', borderRadius: 2 }} />
                            </div>
                          </div>

                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2 }}>
                              <span style={{ color: 'var(--text-muted)' }}>3. Live Coding ($P_{'{code}'}$)</span>
                              <strong style={{ color: 'var(--text)' }}>{((c.P_code || 0) * 100).toFixed(0)}%</strong>
                            </div>
                            <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{ width: `${(c.P_code || 0) * 100}%`, height: '100%', background: '#22c55e', borderRadius: 2 }} />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
