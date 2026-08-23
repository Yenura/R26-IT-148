import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, RefreshCw, TrendingUp, Briefcase, HelpCircle,
  Code, Building2, Sparkles, AlertCircle, CheckCircle2,
  ExternalLink, Layers, Lightbulb, ArrowRight
} from 'lucide-react'
import { c0JobsAll, c4SkillGapAnalyze, c4SkillGapApplied, c4SkillGapSimulate, c4SkillGapRoles, c4ProgressSync } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'

export default function SkillGap() {
  const navigate = useNavigate()
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [activeTab, setActiveTab] = useState('applied')
  const [appliedReports, setAppliedReports] = useState(() => {
    try {
      const cached = sessionStorage.getItem(`recruitai.skillgap.${candidateId}`)
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
  const [selectedJobId, setSelectedJobId] = useState(() => {
    try {
      const cached = sessionStorage.getItem(`recruitai.skillgap.${candidateId}`)
      const parsed = cached ? JSON.parse(cached) : []
      return parsed.length > 0 ? parsed[0].job_id : null
    } catch {
      return null
    }
  })
  const [loadingApplied, setLoadingApplied] = useState(false)
  const [syncingProgress, setSyncingProgress] = useState(false)

  const [availableJobs, setAvailableJobs] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.jobs.cached')
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
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
    
    // Concurrent parallel background revalidation
    Promise.all([
      c4SkillGapRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => {}),
      loadAppliedJobsAnalysis(),
      loadAvailableJobs(),
    ])
  }, [])

  const loadAppliedJobsAnalysis = async () => {
    if (appliedReports.length === 0) setLoadingApplied(true)
    try {
      const r = await c4SkillGapApplied(candidateId)
      const data = r?.data?.data || r?.data || {}
      const reports = data.reports || []
      setAppliedReports(Array.isArray(reports) ? reports : [])
      setResult(data)
      try {
        sessionStorage.setItem(`recruitai.skillgap.${candidateId}`, JSON.stringify(reports))
      } catch {}
      if (!selectedJobId && reports.length > 0) setSelectedJobId(reports[0].job_id)
    } catch {
      if (appliedReports.length === 0) toast.error('Failed to load applied jobs analysis')
    }
    finally { setLoadingApplied(false) }
  }

  const loadAvailableJobs = async () => {
    try {
      const r = await c0JobsAll()
      const jobs = r?.data?.jobs || r?.data || []
      const arr = Array.isArray(jobs) ? jobs : []
      setAvailableJobs(arr)
      try {
        sessionStorage.setItem('recruitai.jobs.cached', JSON.stringify(arr))
      } catch {}
      if (arr.length > 0 && !selectedOpeningId) setSelectedOpeningId(arr[0].id || arr[0]._id)
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
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Skill Analysis & Roadmaps"
        title="Skill Gap & Job Readiness Analyzer"
        description="Diagnose your strengths & weaknesses across real applied positions, or simulate targeted skill acquisitions against live job openings."
        icon={Target}
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={loadAppliedJobsAnalysis} className="btn btn-ghost btn-sm" title="Refresh analysis">
              <RefreshCw size={14} className={loadingApplied ? 'spin' : ''} /> Refresh
            </button>
            <button onClick={syncToProgress} disabled={syncingProgress} className="btn btn-primary btn-sm">
              <TrendingUp size={14} /> {syncingProgress ? 'Syncing...' : 'Sync Weaknesses to Progress'}
            </button>
          </div>
        }
      />

      {/* Tab Bar */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border)', paddingBottom: 0 }}>
        <button
          onClick={() => setActiveTab('applied')}
          className={`btn btn-sm ${activeTab === 'applied' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', borderBottom: 'none' }}
        >
          <Briefcase size={15} /> Applied Positions ({appliedReports.length})
        </button>
        <button
          onClick={() => setActiveTab('explorer')}
          className={`btn btn-sm ${activeTab === 'explorer' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', borderBottom: 'none' }}
        >
          <Sparkles size={15} /> What-If Simulator & Explorer
        </button>
      </div>

      {/* TAB 1: APPLIED JOBS & INTERVIEW REPORTS */}
      {activeTab === 'applied' && (
        <div>
          {loadingApplied ? (
            <div className="card" style={{ padding: 48, textAlign: 'center' }}>
              <RefreshCw size={28} className="spin" style={{ color: 'var(--color-primary)', margin: '0 auto 12px' }} />
              <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 600, color: 'var(--color-fg)' }}>Analyzing applied jobs and interview scores...</div>
              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>Connecting resume qualifications with technical interview evaluations</div>
            </div>
          ) : appliedReports.length === 0 ? (
            <EmptyState
              title="No Job Applications Yet"
              description="Apply for open positions on the Job Board and complete your technical assessments to generate deep role-specific skill gap evaluations."
              actionLabel="Browse Real Job Postings"
              onAction={() => navigate('/candidate/jobs')}
              icon={Briefcase}
            />
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
                        padding: '12px 16px', borderRadius: 'var(--radius-lg)', minWidth: 220, textAlign: 'left', cursor: 'pointer',
                        border: isSelected ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                        background: isSelected ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)',
                        boxShadow: isSelected ? 'var(--shadow-md)' : 'var(--shadow-xs)',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{rep.job_title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>{rep.company_name}</span>
                        <span style={{
                          fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: 'var(--radius-full)',
                          background: rep.interview_completed ? 'var(--color-success-muted)' : 'var(--color-warning-muted)',
                          color: rep.interview_completed ? 'var(--color-success)' : 'var(--color-warning)',
                          border: `1px solid ${rep.interview_completed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
                        }}>
                          {rep.interview_completed ? '✓ Interviewed' : 'Applied'}
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>

              {/* Selected Job Report */}
              {selectedReport && (
                <div className="card" style={{ padding: 'var(--p-space-6)', borderRadius: 'var(--radius-xl)' }}>
                  {/* Header & Scores */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, paddingBottom: 18, borderBottom: '1px solid var(--color-border-subtle)', marginBottom: 20 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>
                          {selectedReport.company_name}
                        </span>
                        <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>• {selectedReport.location}</span>
                        {selectedReport.salary_range && <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>• {selectedReport.salary_range}</span>}
                      </div>
                      <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-fg)', margin: 0, letterSpacing: '-0.02em' }}>
                        {selectedReport.job_title}
                      </h2>
                    </div>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>CV Match</div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.cv_score != null ? `${selectedReport.cv_score}%` : 'N/A'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Interview Score</div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: selectedReport.interview_completed ? 'var(--color-success)' : 'var(--color-warning)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.interview_score != null ? `${selectedReport.interview_score}%` : 'Pending'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-primary-muted)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-primary)', textTransform: 'uppercase' }}>Overall Fit</div>
                        <div style={{ fontSize: '1.3rem', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.composite_score}%
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Interview alert with animated subtle glow */}
                  {!selectedReport.interview_completed && (
                    <div style={{
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-warning-muted)',
                      border: '1px solid rgba(245, 158, 11, 0.4)',
                      boxShadow: '0 0 20px -4px rgba(245, 158, 11, 0.25)',
                      marginBottom: 20,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: 12
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <HelpCircle size={20} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
                        <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg)' }}>
                          You have applied but haven&apos;t taken the technical assessment yet. Complete the interview to unlock complete gap diagnostics!
                        </span>
                      </div>
                      <Link to="/candidate/interview" className="btn btn-sm" style={{ background: 'var(--color-warning)', color: '#fff', fontWeight: 700, whiteSpace: 'nowrap' }}>
                        Start Technical Assessment
                      </Link>
                    </div>
                  )}

                  {/* Strengths */}
                  {selectedReport.strengths?.length > 0 && (
                    <div style={{ marginBottom: 20, padding: 16, background: 'var(--color-success-muted)', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                      <h3 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <CheckCircle2 size={16} /> Verified Strengths ({selectedReport.strengths.length})
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selectedReport.strengths.map((st, idx) => (
                          <div key={idx} style={{
                            padding: '10px 14px',
                            background: 'var(--color-bg-elevated)',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid rgba(16, 185, 129, 0.2)',
                            borderLeft: '4px solid var(--color-success)'
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{st.skill}</span>
                              <span style={{ fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: 'var(--radius-full)', background: 'var(--color-success-muted)', color: 'var(--color-success)' }}>{st.source}</span>
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 3 }}>{st.details}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Weaknesses with Left Colored Border */}
                  {selectedReport.weaknesses?.length > 0 && (
                    <div style={{ marginBottom: 20, padding: 16, background: 'var(--color-danger-muted)', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(244, 63, 94, 0.25)' }}>
                      <h3 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-danger)', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <AlertCircle size={16} /> Identified Skill Deficits ({selectedReport.weaknesses.length})
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selectedReport.weaknesses.map((wk, idx) => {
                          const isCrit = wk.severity === 'Critical'
                          return (
                            <div key={idx} style={{
                              padding: '10px 14px',
                              background: 'var(--color-bg-elevated)',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid rgba(244, 63, 94, 0.2)',
                              borderLeft: `4px solid ${isCrit ? 'var(--color-danger)' : 'var(--color-warning)'}`
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{wk.skill}</span>
                                <span style={{
                                  fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: 'var(--radius-full)',
                                  background: isCrit ? 'var(--color-danger-muted)' : 'var(--color-warning-muted)',
                                  color: isCrit ? 'var(--color-danger)' : 'var(--color-warning)'
                                }}>{wk.source}</span>
                              </div>
                              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 3 }}>{wk.details}</div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* Course Recommendations */}
                  {selectedReport.course_recommendations?.length > 0 && (
                    <div>
                      <h3 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <Code size={16} style={{ color: 'var(--color-primary)' }} /> Targeted Learning Modules ({selectedReport.course_recommendations.length})
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
                        {selectedReport.course_recommendations.map((c, idx) => (
                          <div key={idx} style={{ padding: 14, background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--color-primary)', textTransform: 'uppercase' }}>{c.skill}</span>
                                <span style={{ fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: 'var(--radius-full)', background: 'var(--color-danger-muted)', color: 'var(--color-danger)' }}>{c.priority} Priority</span>
                              </div>
                              <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>{c.course}</div>
                              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginBottom: 10 }}>{c.duration} • {c.level}</div>
                            </div>
                            <a href={c.url} target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-sm"
                              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: '11px', fontWeight: 700 }}>
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
          <div className="card" style={{ padding: 'var(--p-space-6)', borderRadius: 'var(--radius-xl)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
              <div>
                <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Building2 size={18} style={{ color: 'var(--color-primary)' }} /> Select Target Job Opening
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0' }}>Choose from active, verified job postings to simulate acquisitions.</p>
              </div>
              <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>
                {availableJobs.length} Live Openings
              </span>
            </div>
            <select
              value={selectedOpeningId}
              onChange={(e) => { setSelectedOpeningId(e.target.value); setSimulationResult(null); setSimulatedSkills([]) }}
              style={{ width: '100%', height: 44, padding: '0 14px', background: 'var(--input-bg)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)', fontWeight: 600 }}
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
                <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                  <h4 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-danger)' }}>
                    <AlertCircle size={15} /> Job Required Skills ({openingRequiredSkills.length})
                  </h4>
                  <p style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginBottom: 8 }}>Click any required skill below to add it to your simulation:</p>
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
                              fontSize: '11px', padding: '4px 10px',
                              background: isAdded ? 'var(--color-success-muted)' : 'var(--color-danger-muted)',
                              color: isAdded ? 'var(--color-success)' : 'var(--color-danger)',
                              border: `1px solid ${isAdded ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.3)'}`,
                              fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 4
                            }}
                            title={isAdded ? 'Already added to simulation' : 'Click to simulate acquiring this skill'}
                          >
                            {isAdded ? '✓' : '+'} {s}
                          </span>
                        )
                      })}
                    </div>
                  ) : <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>No explicit required skills listed.</p>}
                </div>

                {/* Present Verified Skills + Add Input */}
                <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                  <h4 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                    <CheckCircle2 size={15} /> Simulated Acquired Skills ({simulatedSkills.length})
                  </h4>
                  {simulatedSkills.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {simulatedSkills.map((s, i) => (
                        <span key={i} className="chip" style={{ fontSize: '11px', padding: '4px 10px', background: 'var(--color-success-muted)', color: 'var(--color-success)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                          {s}
                          <button onClick={() => removeSimSkill(s)} style={{ border: 'none', background: 'transparent', color: 'inherit', cursor: 'pointer', padding: '0 0 0 4px', fontWeight: 800 }}>×</button>
                        </span>
                      ))}
                    </div>
                  ) : <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>Click missing skills on the left or type below.</p>}
                  <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                    <input
                      value={customSimSkill}
                      onChange={(e) => setCustomSimSkill(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') addSimSkill(customSimSkill) }}
                      placeholder="Type a skill and press Enter..."
                      style={{ flex: 1, height: 36, padding: '0 12px', background: 'var(--input-bg)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', color: 'var(--color-fg)', fontSize: '12px' }}
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
                style={{ width: '100%', padding: '12px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Sparkles size={16} /> {simulating ? 'Calculating Impact...' : `Simulate Impact on ${currentOpening.title}`}
              </button>

              {/* Simulation Results */}
              {simulationResult && (
                <>
                  {/* Coverage Banner */}
                  <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Original Fit</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{simulationResult.original_coverage}%</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'var(--color-success-muted)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-success)', textTransform: 'uppercase' }}>Simulated Fit</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-success)', fontFamily: 'var(--p-font-mono)' }}>{simulationResult.simulated_coverage}%</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '12px 20px', background: 'var(--color-primary-muted)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                      <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-primary)', textTransform: 'uppercase' }}>Net Gain</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>+{simulationResult.coverage_improvement}%</div>
                    </div>
                  </div>

                  {/* Resources Grid */}
                  {simulationResult.resources?.length > 0 && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                      {simulationResult.resources.map((resItem, idx) => {
                        const pColor = resItem.priority === 'Critical' ? 'var(--color-danger)' : resItem.priority === 'High' ? 'var(--color-orange)' : 'var(--color-warning)'
                        return (
                          <div key={idx} style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span className="chip" style={{ fontSize: '10px', padding: '2px 8px', background: `${pColor}15`, color: pColor, border: `1px solid ${pColor}40`, fontWeight: 700 }}>{resItem.priority} Priority</span>
                                <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>{resItem.level || 'Beginner'} · {resItem.duration || '4 weeks'}</span>
                              </div>
                              <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>
                                {resItem.skill}: <span style={{ color: 'var(--color-primary)' }}>{resItem.course}</span>
                              </div>
                            </div>
                            <a href={resItem.url || `https://www.coursera.org/search?query=${encodeURIComponent(resItem.skill)}`} target="_blank" rel="noreferrer"
                              className="btn btn-ghost btn-sm" style={{ marginTop: 12, fontSize: '11px', border: '1px solid var(--color-border)', display: 'inline-flex', alignItems: 'center', gap: 6, alignSelf: 'flex-start' }}>
                              Enroll / Explore <ExternalLink size={13} />
                            </a>
                          </div>
                        )
                      })}
                    </div>
                  )}

                  {/* Learning Plan */}
                  {simulationResult.learning_plan?.length > 0 && (
                    <div style={{ padding: 20, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                      <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-fg)' }}>
                        <Layers size={18} style={{ color: 'var(--color-primary)' }} /> Structured Learning Roadmap
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {simulationResult.learning_plan.map((planItem, i) => (
                          <div key={i} style={{ padding: 12, background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', display: 'flex', alignItems: 'center', gap: 14 }}>
                            <div style={{ width: 32, height: 32, borderRadius: 'var(--radius-full)', background: 'var(--color-primary)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '12px', flexShrink: 0 }}>
                              {planItem.phase || i + 1}
                            </div>
                            <div>
                              <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)' }}>{planItem.title || planItem.skill}</div>
                              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>{planItem.description || planItem.duration}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Improvement Suggestions */}
                  {simulationResult.improvement_suggestions?.length > 0 && (
                    <div style={{ padding: 20, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                      <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-fg)' }}>
                        <Lightbulb size={18} style={{ color: 'var(--color-warning)' }} /> Actionable Next Steps
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {simulationResult.improvement_suggestions.map((s, i) => (
                          <div key={i} style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
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
