import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, RefreshCw, TrendingUp, Briefcase, HelpCircle,
  Code, Building2, Sparkles, AlertCircle, CheckCircle2,
  ExternalLink, Layers, Lightbulb
} from 'lucide-react'
import { c0JobsAll, c4SkillGapAnalyze, c4SkillGapApplied, c4SkillGapSimulate, c4SkillGapRoles, c4ProgressSync } from '../api'

export default function SkillGap() {
  const navigate = useNavigate()
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [activeTab, setActiveTab] = useState('applied')
  const [appliedReports, setAppliedReports] = useState([])
  const [selectedJobId, setSelectedJobId] = useState(null)
  const [loadingApplied, setLoadingApplied] = useState(false)
  const [syncingProgress, setSyncingProgress] = useState(false)

  const [availableJobs, setAvailableJobs] = useState([])
  const [selectedOpeningId, setSelectedOpeningId] = useState('')
  const [roles, setRoles] = useState([])
  const [simulatedSkills, setSimulatedSkills] = useState([])
  const [customSimSkill, setCustomSimSkill] = useState('')
  const [simulationResult, setSimulationResult] = useState(null)
  const [simulating, setSimulating] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') { navigate('/login/candidate'); return }
    c4SkillGapRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => {})
    loadAppliedJobsAnalysis()
    loadAvailableJobs()
  }, [])

  const loadAppliedJobsAnalysis = async () => {
    setLoadingApplied(true)
    try {
      const r = await c4SkillGapApplied(candidateId)
      const data = r?.data?.data || r?.data || {}
      const reports = data.reports || []
      setAppliedReports(Array.isArray(reports) ? reports : [])
      setResult(data)
      if (!selectedJobId && reports.length > 0) setSelectedJobId(reports[0].job_id)
    } catch { toast.error('Failed to load applied jobs analysis') }
    finally { setLoadingApplied(false) }
  }

  const loadAvailableJobs = async () => {
    try {
      const r = await c0JobsAll()
      const jobs = r?.data?.jobs || r?.data || []
      setAvailableJobs(Array.isArray(jobs) ? jobs : [])
      if (jobs.length > 0) setSelectedOpeningId(jobs[0].id || jobs[0]._id)
    } catch { /* silent */ }
  }

  const syncToProgress = async () => {
    setSyncingProgress(true)
    try {
      await c4ProgressSync(candidateId)
      toast.success('Weaknesses synced to Progress Tracker')
    } catch { toast.error('Failed to sync to progress tracker') }
    finally { setSyncingProgress(false) }
  }

  const runSimulation = async () => {
    if (!currentOpening || simulatedSkills.length === 0) return
    setSimulating(true)
    try {
      const r = await c4SkillGapSimulate({
        candidate_id: candidateId,
        job_role: currentOpening.job_role || currentOpening.title,
        company: currentOpening.company_name,
        required_skills: openingRequiredSkills,
        skills: simulatedSkills,
        acquired_skills: simulatedSkills,
      })
      const data = r?.data?.data || r?.data || {}
      setSimulationResult({
        original_coverage: data.original_coverage || 0,
        simulated_coverage: data.simulated_coverage || 0,
        coverage_improvement: data.coverage_improvement || 0,
        simulated_matched: data.simulated_matched || [],
        remaining_missing: data.remaining_missing || [],
        resources: data.resources || [],
        learning_plan: data.learning_plan || [],
        improvement_suggestions: data.improvement_suggestions || [],
        job_title: currentOpening.title,
        company_name: currentOpening.company_name || 'Selected Employer'
      })
      toast.success(`Simulation Complete: +${data.coverage_improvement || 0}% improvement!`)
    } catch { toast.error('Simulation failed') }
    finally { setSimulating(false) }
  }

  const currentOpening = availableJobs.find(j => (j.id || j._id) === selectedOpeningId) || availableJobs[0]
  const openingRequiredSkills = currentOpening?.required_skills || []

  const addSimSkill = (skill) => {
    const s = skill?.trim()
    if (!s) return
    if (!simulatedSkills.some(x => x.toLowerCase() === s.toLowerCase())) {
      setSimulatedSkills([...simulatedSkills, s])
    }
    setCustomSimSkill('')
  }

  const removeSimSkill = (skill) => {
    setSimulatedSkills(simulatedSkills.filter(s => s.toLowerCase() !== skill.toLowerCase()))
  }

  const selectedReport = appliedReports.find(r => r.job_id === selectedJobId) || appliedReports[0]

  return (
    <div className="fade-in" style={{ padding: '24px 16px', maxWidth: 1050, margin: '0 auto' }}>
      {/* Header */}
      <div className="page-head" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1.2, marginBottom: 4 }}>
              Component 4 · Multi-Dimensional Evaluation Engine
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
              <Target size={28} style={{ color: 'var(--accent)' }} /> Skill Gap & Job Readiness Analyzer
            </h1>
            <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>
              Analyze your strengths & weaknesses across real applied jobs, or simulate skill acquisitions against available openings.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={loadAppliedJobsAnalysis} className="btn btn-ghost btn-sm" style={{ display: 'flex', alignItems: 'center', gap: 6 }} title="Refresh analysis">
              <RefreshCw size={14} className={loadingApplied ? 'spin' : ''} /> Refresh
            </button>
            <button onClick={syncToProgress} disabled={syncingProgress} className="btn btn-primary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <TrendingUp size={14} /> {syncingProgress ? 'Syncing...' : 'Sync Weaknesses to Progress'}
            </button>
          </div>
        </div>
      </div>

      {/* Tab Bar */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '2px solid var(--border)', paddingBottom: 0 }}>
        <button
          onClick={() => setActiveTab('applied')}
          style={{
            padding: '10px 20px', borderRadius: '8px 8px 0 0', border: 'none', cursor: 'pointer',
            fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6,
            background: activeTab === 'applied' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'applied' ? 'var(--color-on-primary)' : 'var(--text-muted)',
            transition: 'all 0.15s ease'
          }}
        >
          <Briefcase size={15} /> Applied Jobs
        </button>
        <button
          onClick={() => setActiveTab('explorer')}
          style={{
            padding: '10px 20px', borderRadius: '8px 8px 0 0', border: 'none', cursor: 'pointer',
            fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6,
            background: activeTab === 'explorer' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'explorer' ? 'var(--color-on-primary)' : 'var(--text-muted)',
            transition: 'all 0.15s ease'
          }}
        >
          <Sparkles size={15} /> Explorer (Simulation)
        </button>
      </div>

      {/* TAB 1: APPLIED JOBS & INTERVIEW REPORTS */}
      {activeTab === 'applied' && (
        <div>
          {loadingApplied ? (
            <div className="card" style={{ padding: 48, textAlign: 'center' }}>
              <RefreshCw size={28} className="spin" style={{ color: 'var(--accent)', marginBottom: 12 }} />
              <div style={{ fontSize: 15, fontWeight: 600 }}>Analyzing applied jobs and interview scores...</div>
              <div className="muted" style={{ fontSize: 13, marginTop: 4 }}>Connecting Component 1 (CV) & Component 2 (AI Interview) datasets</div>
            </div>
          ) : appliedReports.length === 0 ? (
            <div className="card" style={{ padding: 40, textAlign: 'center' }}>
              <Briefcase size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 6 }}>No Job Applications Yet</h3>
              <p className="muted" style={{ fontSize: 13, maxWidth: 500, margin: '0 auto 16px' }}>
                Apply for open positions on the Job Board and complete your AI Technical Interview to generate deep role-specific skill gap evaluations.
              </p>
              <Link to="/candidate/jobs" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={16} /> Browse Real Job Postings
              </Link>
            </div>
          ) : (
            <div>
              {/* Job Selector Pills */}
              <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 12, marginBottom: 16 }}>
                {appliedReports.map((rep) => {
                  const isSelected = rep.job_id === selectedReport?.job_id
                  return (
                    <button
                      key={rep.job_id}
                      onClick={() => setSelectedJobId(rep.job_id)}
                      style={{
                        padding: '10px 16px', borderRadius: 10, minWidth: 200, textAlign: 'left', cursor: 'pointer',
                        border: isSelected ? '2px solid var(--accent)' : '1px solid var(--border)',
                        background: isSelected ? 'rgba(59, 130, 246, 0.08)' : 'var(--bg-elevated)',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ fontSize: 13, fontWeight: 800, color: 'var(--text)' }}>{rep.job_title}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, display: 'flex', justifyContent: 'space-between' }}>
                        <span>{rep.company_name}</span>
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                          background: rep.interview_completed ? 'rgba(34, 197, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                          color: rep.interview_completed ? '#22c55e' : '#f59e0b'
                        }}>
                          {rep.interview_completed ? 'Interviewed' : 'Applied'}
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>

              {/* Selected Job Report */}
              {selectedReport && (
                <div className="card" style={{ padding: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
                  {/* Header & Scores */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, paddingBottom: 18, borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span className="chip" style={{ fontSize: 11, fontWeight: 700, background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent)' }}>
                          {selectedReport.company_name}
                        </span>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>• {selectedReport.location}</span>
                        {selectedReport.salary_range && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>• {selectedReport.salary_range}</span>}
                      </div>
                      <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text)', margin: 0 }}>{selectedReport.job_title}</h2>
                    </div>
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>CV Match (C1)</div>
                        <div style={{ fontSize: 18, fontWeight: 900, color: 'var(--text)' }}>{selectedReport.cv_score != null ? `${selectedReport.cv_score}%` : 'N/A'}</div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Interview Score (C2)</div>
                        <div style={{ fontSize: 18, fontWeight: 900, color: selectedReport.interview_completed ? 'var(--color-success)' : '#f59e0b' }}>
                          {selectedReport.interview_score != null ? `${selectedReport.interview_score}%` : 'Pending'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: 8, border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase' }}>Overall Fit Score</div>
                        <div style={{ fontSize: 20, fontWeight: 900, color: 'var(--accent)' }}>{selectedReport.composite_score}%</div>
                      </div>
                    </div>
                  </div>

                  {/* Interview alert */}
                  {!selectedReport.interview_completed && (
                    <div style={{ padding: 14, borderRadius: 8, background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <HelpCircle size={18} style={{ color: '#f59e0b' }} />
                        <span style={{ fontSize: 13, color: 'var(--text)' }}>
                          You have applied but haven&apos;t faced the technical interview yet. Take the interview to unlock complete insights!
                        </span>
                      </div>
                      <Link to="/candidate/interview" className="btn btn-sm" style={{ background: '#f59e0b', color: '#fff', fontWeight: 700, whiteSpace: 'nowrap' }}>
                        Start AI Interview
                      </Link>
                    </div>
                  )}

                  {/* Strengths */}
                  {selectedReport.strengths?.length > 0 && (
                    <div style={{ marginBottom: 20, padding: 16, background: 'rgba(34, 197, 94, 0.04)', borderRadius: 10, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#22c55e', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <CheckCircle2 size={18} /> Verified Strengths ({selectedReport.strengths.length})
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selectedReport.strengths.map((st, idx) => (
                          <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 6, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{st.skill}</span>
                              <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4, background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' }}>{st.source}</span>
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{st.details}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Weaknesses */}
                  {selectedReport.weaknesses?.length > 0 && (
                    <div style={{ marginBottom: 20, padding: 16, background: 'rgba(239, 68, 68, 0.04)', borderRadius: 10, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <AlertCircle size={18} /> Identified Weaknesses & Gaps ({selectedReport.weaknesses.length})
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selectedReport.weaknesses.map((wk, idx) => (
                          <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 6, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{wk.skill}</span>
                              <span style={{
                                fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                                background: wk.severity === 'Critical' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                color: wk.severity === 'Critical' ? '#ef4444' : '#f59e0b'
                              }}>{wk.source}</span>
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{wk.details}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Course Recommendations */}
                  {selectedReport.course_recommendations?.length > 0 && (
                    <div>
                      <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <Code size={18} style={{ color: 'var(--accent)' }} /> Targeted Courses ({selectedReport.course_recommendations.length})
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
                        {selectedReport.course_recommendations.map((c, idx) => (
                          <div key={idx} style={{ padding: 14, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--accent)', textTransform: 'uppercase' }}>{c.skill}</span>
                                <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4, background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>{c.priority} Priority</span>
                              </div>
                              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>{c.course}</div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 10 }}>{c.duration} • {c.level}</div>
                            </div>
                            <a href={c.url} target="_blank" rel="noopener noreferrer" className="btn btn-sm"
                              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, background: 'var(--color-primary)', color: '#fff', fontSize: 11, fontWeight: 700 }}>
                              Enroll Course <ExternalLink size={12} />
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: EXPLORER & WHAT-IF SIMULATOR */}
      {activeTab === 'explorer' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card" style={{ padding: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Building2 size={18} style={{ color: 'var(--accent)' }} /> Select Available Job Opening
                </h3>
                <p className="muted" style={{ fontSize: 12, margin: '2px 0 0' }}>Choose from active, verified job postings.</p>
              </div>
              <span className="chip" style={{ fontSize: 11, fontWeight: 700, background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent)' }}>
                {availableJobs.length} Live Openings
              </span>
            </div>
            <select
              value={selectedOpeningId}
              onChange={(e) => { setSelectedOpeningId(e.target.value); setSimulationResult(null); setSimulatedSkills([]) }}
              style={{ width: '100%', height: 46, padding: '0 14px', background: 'var(--input-bg)', border: '2px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, fontWeight: 600 }}
            >
              {availableJobs.map((j) => {
                const id = j.id || j._id
                return (
                  <option key={id} value={id}>
                    {j.title} @ {j.company_name || 'Tech Company'} ({j.location || 'Remote'})
                  </option>
                )
              })}
            </select>
          </div>

          {currentOpening && (
            <>
              {/* Missing Required Skills */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-danger)' }}>
                    <AlertCircle size={16} /> Job Required Skills ({openingRequiredSkills.length})
                  </h4>
                  <p className="muted" style={{ fontSize: 11, marginBottom: 8 }}>Click any required skill below to add it to your simulation:</p>
                  {openingRequiredSkills.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {openingRequiredSkills.map((s, i) => {
                        const isAdded = simulatedSkills.some(x => x.toLowerCase() === s.toLowerCase())
                        return (
                          <span
                            key={i}
                            className="chip"
                            onClick={() => addSimSkill(s)}
                            style={{
                              fontSize: 12, padding: '4px 10px',
                              background: isAdded ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.1)',
                              color: isAdded ? 'var(--color-success)' : 'var(--color-danger)',
                              border: `1px solid ${isAdded ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.3)'}`,
                              fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 4
                            }}
                            title={isAdded ? 'Already added to simulation' : 'Click to simulate acquiring this skill'}
                          >
                            {isAdded ? '✓' : '+'} {s}
                          </span>
                        )
                      })}
                    </div>
                  ) : <p className="muted" style={{ fontSize: 13 }}>No explicit required skills listed.</p>}
                </div>

                {/* Present Verified Skills + Add Input */}
                <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                    <CheckCircle2 size={16} /> Present Verified Skills ({simulatedSkills.length})
                  </h4>
                  {simulatedSkills.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {simulatedSkills.map((s, i) => (
                        <span key={i} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                          {s}
                          <button onClick={() => removeSimSkill(s)} style={{ border: 'none', background: 'transparent', color: 'inherit', cursor: 'pointer', padding: 0 }}>×</button>
                        </span>
                      ))}
                    </div>
                  ) : <p className="muted" style={{ fontSize: 13 }}>Add skills to simulate.</p>}
                  <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                    <input
                      value={customSimSkill}
                      onChange={(e) => setCustomSimSkill(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') addSimSkill(customSimSkill) }}
                      placeholder="Type a skill and press Enter..."
                      style={{ flex: 1, height: 38, padding: '0 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: 13 }}
                    />
                    <button onClick={() => addSimSkill(customSimSkill)} className="btn btn-ghost btn-sm">Add</button>
                  </div>
                </div>
              </div>

              {/* Simulation Button */}
              <button
                onClick={runSimulation}
                disabled={simulating || simulatedSkills.length === 0}
                className="btn btn-primary"
                style={{ width: '100%', height: 44, fontSize: 14, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Sparkles size={18} /> {simulating ? 'Calculating Impact...' : `Simulate Impact on ${currentOpening.title}`}
              </button>

              {/* Simulation Results */}
              {simulationResult && (
                <>
                  {/* Coverage Banner */}
                  <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Original Coverage</div>
                      <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--text)' }}>{simulationResult.original_coverage}%</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'rgba(34, 197, 94, 0.08)', borderRadius: 10, border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: '#22c55e', textTransform: 'uppercase' }}>Simulated Coverage</div>
                      <div style={{ fontSize: 24, fontWeight: 900, color: '#22c55e' }}>{simulationResult.simulated_coverage}%</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: 10, border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase' }}>Improvement</div>
                      <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--accent)' }}>+{simulationResult.coverage_improvement}%</div>
                    </div>
                  </div>

                  {/* Resources Grid */}
                  {simulationResult.resources?.length > 0 && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                      {simulationResult.resources.map((resItem, idx) => {
                        const pColor = resItem.priority === 'Critical' ? 'var(--color-danger)' : resItem.priority === 'High' ? 'var(--color-orange)' : 'var(--color-warning)'
                        return (
                          <div key={idx} style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: `${pColor}15`, color: pColor, border: `1px solid ${pColor}40`, fontWeight: 700 }}>{resItem.priority} Priority</span>
                                <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>{resItem.level || 'Beginner'} · {resItem.duration || '4 weeks'}</span>
                              </div>
                              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>
                                {resItem.skill}: <span style={{ color: 'var(--accent)' }}>{resItem.course}</span>
                              </div>
                            </div>
                            <a href={resItem.url || `https://www.coursera.org/search?query=${encodeURIComponent(resItem.skill)}`} target="_blank" rel="noreferrer"
                              className="btn btn-ghost btn-sm" style={{ marginTop: 12, fontSize: 12, border: '1px solid var(--border)', display: 'inline-flex', alignItems: 'center', gap: 6, alignSelf: 'flex-start' }}>
                              Enroll / Explore <ExternalLink size={13} />
                            </a>
                          </div>
                        )
                      })}
                    </div>
                  )}

                  {/* Learning Plan */}
                  {simulationResult.learning_plan?.length > 0 && (
                    <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                      <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Layers size={20} style={{ color: 'var(--color-primary)' }} /> Structured Learning Plan
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {simulationResult.learning_plan.map((planItem, i) => (
                          <div key={i} style={{ padding: 14, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 14 }}>
                            <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--accent)', color: 'var(--color-on-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14, flexShrink: 0 }}>
                              {planItem.phase || i + 1}
                            </div>
                            <div>
                              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{planItem.title || planItem.skill}</div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{planItem.description || planItem.duration}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Improvement Suggestions */}
                  {simulationResult.improvement_suggestions?.length > 0 && (
                    <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                      <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Lightbulb size={20} style={{ color: 'var(--color-warning)' }} /> Actionable AI Recommendations
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {simulationResult.improvement_suggestions.map((s, i) => (
                          <div key={i} style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                            <span style={{ color: 'var(--color-warning)' }}>•</span> {s}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
