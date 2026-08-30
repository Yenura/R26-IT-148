import { useEffect, useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, RefreshCw, TrendingUp, Briefcase, HelpCircle,
  Code, Building2, Sparkles, AlertCircle, CheckCircle2,
  ExternalLink, Layers, Lightbulb, ArrowRight, Network,
  Search, Clock, BookOpen
} from 'lucide-react'
import { c0JobsAll, c4SkillGapAnalyze, c4SkillGapApplied, c4SkillGapSimulate, c4SkillGapRoles, c4ProgressSync, c4SkillGapGraph, authGetProfile } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'

export default function SkillGap() {
  const navigate = useNavigate()
  useAuth()
  const [searchParams] = useSearchParams()
  const paramJobId = searchParams.get('jobId') || ''
  const paramRole = searchParams.get('role') || ''

  const userRole = localStorage.getItem('recruitai.role') || 'candidate'
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [activeTab, setActiveTab] = useState(userRole === 'company' ? 'explorer' : 'applied')
  const [appliedReports, setAppliedReports] = useState([])
  const [selectedJobId, setSelectedJobId] = useState(paramJobId || null)
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
  const [graphNodes, setGraphNodes] = useState(() => [
    { id: 'Python', label: 'Python' },
    { id: 'SQL', label: 'SQL' },
    { id: 'Git', label: 'Git' },
    { id: 'Linux', label: 'Linux' },
    { id: 'Java', label: 'Java' },
    { id: 'JavaScript', label: 'JavaScript' },
    { id: 'Pandas', label: 'Pandas' },
    { id: 'NumPy', label: 'NumPy' },
    { id: 'Statistics', label: 'Statistics' },
    { id: 'FastAPI', label: 'FastAPI' },
    { id: 'Django', label: 'Django' },
    { id: 'Machine Learning', label: 'Machine Learning' },
    { id: 'Scikit-Learn', label: 'Scikit-Learn' },
    { id: 'Deep Learning', label: 'Deep Learning' },
    { id: 'PyTorch', label: 'PyTorch' },
    { id: 'TensorFlow', label: 'TensorFlow' },
    { id: 'MLOps', label: 'MLOps' },
    { id: 'Docker', label: 'Docker' },
    { id: 'Kubernetes', label: 'Kubernetes' },
    { id: 'CI/CD', label: 'CI/CD' },
    { id: 'AWS', label: 'AWS' },
    { id: 'Azure', label: 'Azure' },
    { id: 'React', label: 'React' },
    { id: 'Node.js', label: 'Node.js' },
    { id: 'PostgreSQL', label: 'PostgreSQL' },
    { id: 'MongoDB', label: 'MongoDB' },
    { id: 'System Design', label: 'System Design' }
  ])
  const [graphEdges, setGraphEdges] = useState(() => [
    { source: 'Python', target: 'Pandas' },
    { source: 'Python', target: 'NumPy' },
    { source: 'Python', target: 'Statistics' },
    { source: 'Python', target: 'FastAPI' },
    { source: 'Python', target: 'Django' },
    { source: 'Python', target: 'Machine Learning' },
    { source: 'Pandas', target: 'Machine Learning' },
    { source: 'Statistics', target: 'Machine Learning' },
    { source: 'Machine Learning', target: 'Scikit-Learn' },
    { source: 'Machine Learning', target: 'Deep Learning' },
    { source: 'Deep Learning', target: 'PyTorch' },
    { source: 'Deep Learning', target: 'TensorFlow' },
    { source: 'Machine Learning', target: 'MLOps' },
    { source: 'Docker', target: 'MLOps' },
    { source: 'Linux', target: 'Docker' },
    { source: 'Docker', target: 'Kubernetes' },
    { source: 'Git', target: 'CI/CD' },
    { source: 'Docker', target: 'CI/CD' },
    { source: 'Linux', target: 'AWS' },
    { source: 'Linux', target: 'Azure' },
    { source: 'JavaScript', target: 'React' },
    { source: 'JavaScript', target: 'Node.js' },
    { source: 'SQL', target: 'PostgreSQL' },
    { source: 'SQL', target: 'MongoDB' }
  ])
  const [graphLoading, setGraphLoading] = useState(false)
  const [graphSelectedNode, setGraphSelectedNode] = useState(null)
  const [graphCategoryFilter, setGraphCategoryFilter] = useState('all')
  const [graphSearchTerm, setGraphSearchTerm] = useState('')

  useEffect(() => {
    // Concurrent parallel background revalidation & pre-fetching
    Promise.all([
      c4SkillGapRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => {}),
      loadAppliedJobsAnalysis(),
      loadAvailableJobs(),
      loadGraph(),
    ])
  }, [])

  const loadGraph = async () => {
    try {
      const r = await c4SkillGapGraph()
      if (r?.data?.nodes?.length > 0) setGraphNodes(r.data.nodes)
      if (r?.data?.edges?.length > 0) setGraphEdges(r.data.edges)
    } catch {
      // Keep canonical fallback
    }
  }

  const loadAppliedJobsAnalysis = async (overrideId) => {
    if (userRole === 'company') return
    const currentId = overrideId || localStorage.getItem('recruitai.user_id') || candidateId
    if (appliedReports.length === 0) setLoadingApplied(true)
    try {
      let r = await c4SkillGapApplied(currentId)
      let raw = r?.data || {}
      let reports = Array.isArray(raw) ? raw : (raw.reports || raw.data || (Array.isArray(raw.data) ? raw.data : []))
      let arr = Array.isArray(reports) ? reports : []

      // If no reports found and ID might be default/stale, resolve authentic user ID
      if (arr.length === 0) {
        try {
          const me = await authGetProfile()
          const resolvedId = me?.data?.id || me?.data?._id || me?.data?.user_id
          if (resolvedId && resolvedId !== currentId) {
            localStorage.setItem('recruitai.user_id', resolvedId)
            const r2 = await c4SkillGapApplied(resolvedId)
            const raw2 = r2?.data || {}
            const reports2 = Array.isArray(raw2) ? raw2 : (raw2.reports || raw2.data || [])
            if (Array.isArray(reports2) && reports2.length > 0) {
              arr = reports2
              raw = raw2
            }
          }
        } catch {}
      }

      setAppliedReports(arr)
      setResult(raw)
      try {
        sessionStorage.setItem(`recruitai.skillgap.${currentId}`, JSON.stringify(arr))
      } catch {}
      if (arr.length === 0) {
        setSelectedJobId(null)
      } else if (paramJobId && arr.some((a) => a.job_id === paramJobId)) {
        setSelectedJobId(paramJobId)
      } else if (!selectedJobId || !arr.some((a) => a.job_id === selectedJobId)) {
        setSelectedJobId(arr[0].job_id)
      }
    } catch {
      // Graceful fallback for empty or initial states
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
        <button
          onClick={() => { setActiveTab('graph'); if (graphNodes.length === 0) loadGraph() }}
          className={`btn btn-sm ${activeTab === 'graph' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ borderRadius: 'var(--radius-md) var(--radius-md) 0 0', borderBottom: 'none' }}
        >
          <Network size={15} /> Skill Dependency Graph
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
                        <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>CV Overall Mark</div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.cv_score != null ? `${selectedReport.cv_score}%` : 'N/A'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Interview Mark</div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: selectedReport.interview_completed ? 'var(--color-purple)' : 'var(--color-warning)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.interview_score != null ? `${selectedReport.interview_score}%` : 'Pending'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: selectedReport.interview_completed ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: `1px solid ${selectedReport.interview_completed ? 'rgba(99, 102, 241, 0.4)' : 'var(--color-border)'}` }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, color: selectedReport.interview_completed ? 'var(--color-primary)' : 'var(--color-fg-muted)', textTransform: 'uppercase' }}>
                          {selectedReport.interview_completed ? 'Final Total Mark (CSS)' : 'Current Total (CV Mark)'}
                        </div>
                        <div style={{ fontSize: '1.3rem', fontWeight: 900, color: selectedReport.interview_completed ? 'var(--color-primary)' : 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                          {selectedReport.composite_score != null ? `${Number(selectedReport.composite_score).toFixed(1)}%` : (selectedReport.hire_probability != null ? `${Number(selectedReport.hire_probability).toFixed(1)}%` : 'N/A')}
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
                          Your CV Match score is recorded! Complete the AI Technical Interview to unlock your full combined score and top ranking.
                        </span>
                      </div>
                      <Link to={`/candidate/interview?role=${selectedReport.job_title}&jobId=${selectedReport.job_id}`} className="btn btn-sm" style={{ background: 'var(--color-warning)', color: '#fff', fontWeight: 700, whiteSpace: 'nowrap' }}>
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
{selectedReport.strengths.map((st) => (
                          <div key={st.skill} style={{
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
{selectedReport.weaknesses.map((wk) => {
                          const isCrit = wk.severity === 'Critical'
                          return (
                            <div key={wk.skill} style={{
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
{selectedReport.course_recommendations.map((c) => (
                          <div key={c.skill} style={{ padding: 14, background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
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
<div className="dashboard-grid dashboard-grid-equal" style={{ gap: 16 }}>
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
                          <button
                            key={i}
                            className="chip"
                            onClick={() => addSimSkill(s)}
                            aria-pressed={isAdded}
                            style={{
                              fontSize: '11px', padding: '4px 10px',
                              background: isAdded ? 'var(--color-success-muted)' : 'var(--color-danger-muted)',
                              color: isAdded ? 'var(--color-success)' : 'var(--color-danger)',
                              border: `1px solid ${isAdded ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.3)'}`,
fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 4,
                              transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                            }}
                            onMouseDown={(e) => { e.currentTarget.style.transform = 'scale(0.95)' }}
                            onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
                            onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
                            title={isAdded ? 'Already added to simulation' : 'Click to simulate acquiring this skill'}
                          >
                            {isAdded ? '✓' : '+'} {s}
                          </button>
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
 {[...new Set(simulatedSkills)].map((s, i) => (
                         <span key={`${s}-${i}`} className="chip" style={{ fontSize: '11px', padding: '4px 10px', background: 'var(--color-success-muted)', color: 'var(--color-success)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                          {s}
                          <button onClick={() => removeSimSkill(s)} aria-label={`Remove ${s}`} style={{ border: 'none', background: 'transparent', color: 'inherit', cursor: 'pointer', padding: '0 0 0 4px', fontWeight: 800 }}>×</button>
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
{simulationResult.resources.map((resItem) => {
                        const pColor = resItem.priority === 'Critical' ? 'var(--color-danger)' : resItem.priority === 'High' ? 'var(--color-orange)' : 'var(--color-warning)'
                        return (
                          <div key={resItem.skill} style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
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
<div key={planItem.skill || i} style={{ padding: 12, background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', display: 'flex', alignItems: 'center', gap: 14 }}>
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
 {[...new Set(simulationResult.improvement_suggestions)].map((s, i) => (
                           <div key={`${s}-${i}`} style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
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

      {/* TAB 3: SKILL DEPENDENCY GRAPH */}
      {activeTab === 'graph' && (
        <div style={{ padding: 'var(--p-space-4) 0' }}>
          {graphLoading ? (
            <div style={{ textAlign: 'center', padding: 50, color: 'var(--color-fg-muted)' }}>
              <RefreshCw size={24} className="spin" style={{ marginBottom: 12, color: 'var(--color-primary)' }} />
              <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)' }}>Synthesizing Skill Prerequisite Graph...</div>
              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>Mapping interconnected technical competencies across 32 domain nodes</div>
            </div>
          ) : graphNodes.length === 0 ? (
            <EmptyState
              title="No skill dependency data"
              description="The skill dependency graph could not be loaded."
              icon={Network}
            />
          ) : (() => {
            const getNodeId = (n) => typeof n === 'string' ? n : (n?.id || n?.label || n?.name || '')
            const getNodeLabel = (n) => typeof n === 'string' ? n : (n?.label || n?.name || n?.id || '')

            const inDegrees = {}
            const outDegrees = {}

            const normalizedNodes = (graphNodes || []).map((n) => ({
              id: getNodeId(n),
              label: getNodeLabel(n)
            })).filter((n) => Boolean(n.id))

            normalizedNodes.forEach((n) => {
              inDegrees[n.id] = 0
              outDegrees[n.id] = 0
            })

            const normalizedEdges = (graphEdges || []).map((e) => ({
              source: typeof e.source === 'string' ? e.source : (e.source?.id || e.source?.label || ''),
              target: typeof e.target === 'string' ? e.target : (e.target?.id || e.target?.label || '')
            })).filter((e) => Boolean(e.source && e.target))

            normalizedEdges.forEach((e) => {
              if (inDegrees[e.target] !== undefined) inDegrees[e.target]++
              if (outDegrees[e.source] !== undefined) outDegrees[e.source]++
            })

            const DOMAIN_MAP = {
              ds: { label: 'Data Science & AI', icon: '🧠', skills: ['python', 'sql', 'pandas', 'numpy', 'scikit-learn', 'pytorch', 'tensorflow', 'deep learning', 'nlp', 'computer vision', 'mlops', 'data engineering', 'statistics', 'linear algebra'] },
              web: { label: 'Web & Backend', icon: '⚡', skills: ['javascript', 'typescript', 'node.js', 'react', 'fastapi', 'django', 'rest apis', 'graphql', 'postgresql', 'mongodb', 'redis', 'microservices', 'system design'] },
              devops: { label: 'Cloud & DevOps', icon: '☁️', skills: ['linux', 'git', 'docker', 'kubernetes', 'ci/cd', 'aws', 'azure', 'terraform', 'monitoring', 'cloud architecture'] }
            }

            const activeSkills = normalizedNodes.filter((n) => {
              const label = (n.label || '').toLowerCase()
              const matchesSearch = !graphSearchTerm || label.includes(graphSearchTerm.toLowerCase())
              if (graphCategoryFilter === 'all') return matchesSearch
              const domainList = DOMAIN_MAP[graphCategoryFilter]?.skills || []
              return matchesSearch && domainList.some((s) => label.includes(s) || s.includes(label))
            })

            // Sort nodes into 4 visual stages
            const stage1 = activeSkills.filter((n) => (inDegrees[n.id] || 0) === 0)
            const stage2 = activeSkills.filter((n) => (inDegrees[n.id] || 0) === 1)
            const stage3 = activeSkills.filter((n) => (inDegrees[n.id] || 0) === 2)
            const stage4 = activeSkills.filter((n) => (inDegrees[n.id] || 0) >= 3)

            const stages = [
              { title: 'Stage 1: Core Foundations', subtitle: 'Prerequisites / Zero Dependencies', color: 'var(--color-primary)', bg: 'rgba(99, 102, 241, 0.1)', nodes: stage1 },
              { title: 'Stage 2: Core Tooling & Frameworks', subtitle: 'Built on Foundationals', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)', nodes: stage2 },
              { title: 'Stage 3: Applied Specialization', subtitle: 'Frameworks & Deep Applied', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)', nodes: stage3 },
              { title: 'Stage 4: Production Mastery', subtitle: 'Advanced Architecture & MLOps', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)', nodes: stage4 }
            ]

            const selectedNodePrereqs = graphSelectedNode
              ? normalizedEdges.filter((e) => e.target === graphSelectedNode).map((e) => e.source)
              : []
            const selectedNodeUnlocks = graphSelectedNode
              ? normalizedEdges.filter((e) => e.source === graphSelectedNode).map((e) => e.target)
              : []

            return (
              <>
                {/* Header & Controls */}
                <div style={{
                  marginBottom: 20,
                  padding: '16px 20px',
                  background: 'var(--color-bg-elevated)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-xl)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 16
                }}>
                  <div>
                    <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 800, color: 'var(--color-fg)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Network size={18} style={{ color: 'var(--color-primary)' }} />
                      Skill Dependency DAG & Career Pathway Map
                    </h3>
                    <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '4px 0 0' }}>
                      {graphNodes.length} Verified Competencies · {graphEdges.length} Directed Dependency Edges · Click any node to inspect prerequisite chains
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                    {/* Domain filter tabs */}
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      <button
                        onClick={() => setGraphCategoryFilter('all')}
                        className={`btn btn-sm ${graphCategoryFilter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                        style={{ fontSize: '11px', borderRadius: 'var(--radius-full)', padding: '4px 10px' }}
                      >
                        All Domains ({graphNodes.length})
                      </button>
                      {Object.entries(DOMAIN_MAP).map(([key, dom]) => (
                        <button
                          key={key}
                          onClick={() => setGraphCategoryFilter(key)}
                          className={`btn btn-sm ${graphCategoryFilter === key ? 'btn-primary' : 'btn-ghost'}`}
                          style={{ fontSize: '11px', borderRadius: 'var(--radius-full)', padding: '4px 10px' }}
                        >
                          {dom.icon} {dom.label}
                        </button>
                      ))}
                    </div>

                    {/* Search */}
                    <div style={{ position: 'relative', width: 180 }}>
                      <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
                      <input
                        type="text"
                        placeholder="Filter skills..."
                        value={graphSearchTerm}
                        onChange={(e) => setGraphSearchTerm(e.target.value)}
                        style={{ paddingLeft: 28, height: 32, fontSize: '11px' }}
                      />
                    </div>

                    <button onClick={loadGraph} className="btn btn-ghost btn-sm" title="Reload DAG Graph">
                      <RefreshCw size={13} />
                    </button>
                  </div>
                </div>

                {/* Selected Node Details Inspector Modal/Card */}
                {graphSelectedNode && (
                  <div style={{
                    marginBottom: 24,
                    padding: '20px 24px',
                    background: 'var(--color-bg-elevated)',
                    border: '2px solid var(--color-primary)',
                    borderRadius: 'var(--radius-xl)',
                    boxShadow: '0 8px 24px -6px rgba(99, 102, 241, 0.25)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 16
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{
                          width: 40,
                          height: 40,
                          borderRadius: 'var(--radius-lg)',
                          background: 'var(--color-primary)',
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '18px',
                          fontWeight: 900
                        }}>
                          🎯
                        </div>
                        <div>
                          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary)', letterSpacing: '0.06em' }}>
                            Selected Competency Pathway
                          </div>
                          <h4 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-fg)', margin: '2px 0 0' }}>
                            {graphSelectedNode}
                          </h4>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <a
                          href={`https://www.coursera.org/search?query=${encodeURIComponent(graphSelectedNode)}`}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary btn-sm"
                          style={{ fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                        >
                          <BookOpen size={13} /> View Verified Course <ExternalLink size={11} />
                        </a>
                        <button
                          onClick={() => setGraphSelectedNode(null)}
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: '11px' }}
                        >
                          Close Inspector
                        </button>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                      {/* Prerequisites Panel */}
                      <div style={{
                        padding: 14,
                        borderRadius: 'var(--radius-lg)',
                        background: 'var(--color-bg)',
                        border: '1px solid var(--color-border)'
                      }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-warning)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                          <Clock size={13} /> Direct Prerequisites ({selectedNodePrereqs.length})
                        </div>
                        {selectedNodePrereqs.length === 0 ? (
                          <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)', fontStyle: 'italic' }}>
                            ✨ Foundational skill — no prerequisites required to start learning!
                          </div>
                        ) : (
                          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                            {selectedNodePrereqs.map((pr) => (
                              <button
                                key={pr}
                                onClick={() => setGraphSelectedNode(pr)}
                                className="btn btn-ghost btn-sm"
                                style={{
                                  fontSize: '11px',
                                  borderRadius: 'var(--radius-full)',
                                  background: 'rgba(245, 158, 11, 0.12)',
                                  color: 'var(--color-warning)',
                                  border: '1px solid rgba(245, 158, 11, 0.3)'
                                }}
                              >
                                ← {pr}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Unlocks Panel */}
                      <div style={{
                        padding: 14,
                        borderRadius: 'var(--radius-lg)',
                        background: 'var(--color-bg)',
                        border: '1px solid var(--color-border)'
                      }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-success)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                          <CheckCircle2 size={13} /> Unlocks Higher-Level Competencies ({selectedNodeUnlocks.length})
                        </div>
                        {selectedNodeUnlocks.length === 0 ? (
                          <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)', fontStyle: 'italic' }}>
                            🎯 Capstone / Applied Production Competency.
                          </div>
                        ) : (
                          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                            {selectedNodeUnlocks.map((un) => (
                              <button
                                key={un}
                                onClick={() => setGraphSelectedNode(un)}
                                className="btn btn-ghost btn-sm"
                                style={{
                                  fontSize: '11px',
                                  borderRadius: 'var(--radius-full)',
                                  background: 'rgba(16, 185, 129, 0.12)',
                                  color: 'var(--color-success)',
                                  border: '1px solid rgba(16, 185, 129, 0.3)'
                                }}
                              >
                                → {un}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* 4-Stage Pathway Grid Visualization */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                  gap: 16,
                  alignItems: 'start'
                }}>
                  {stages.map((st, sIdx) => (
                    <div
                      key={sIdx}
                      style={{
                        background: 'var(--color-bg-elevated)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--radius-xl)',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 12
                      }}
                    >
                      <div style={{
                        paddingBottom: 10,
                        borderBottom: '1px solid var(--color-border)'
                      }}>
                        <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: st.color, letterSpacing: '0.05em' }}>
                          {st.title}
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                          {st.subtitle} ({st.nodes.length} skills)
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {st.nodes.length === 0 ? (
                          <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', padding: '12px 0', textAlign: 'center', fontStyle: 'italic' }}>
                            No matching skills in this stage
                          </div>
                        ) : (
                          st.nodes.map((node) => {
                            const isSelected = graphSelectedNode === node.id
                            const isPrereqOfSelected = selectedNodePrereqs.includes(node.id)
                            const isUnlockedBySelected = selectedNodeUnlocks.includes(node.id)
                            const preCount = inDegrees[node.id] || 0
                            const unlockCount = outDegrees[node.id] || 0

                            let cardBorder = '1px solid var(--color-border)'
                            let cardBg = 'var(--color-bg)'
                            let cardShadow = 'none'

                            if (isSelected) {
                              cardBorder = '2px solid var(--color-primary)'
                              cardBg = 'rgba(99, 102, 241, 0.12)'
                              cardShadow = '0 4px 14px rgba(99, 102, 241, 0.25)'
                            } else if (isPrereqOfSelected) {
                              cardBorder = '2px solid var(--color-warning)'
                              cardBg = 'rgba(245, 158, 11, 0.1)'
                            } else if (isUnlockedBySelected) {
                              cardBorder = '2px solid var(--color-success)'
                              cardBg = 'rgba(16, 185, 129, 0.1)'
                            }

                            return (
                              <div
                                key={node.id}
                                onClick={() => setGraphSelectedNode(isSelected ? null : node.id)}
                                style={{
                                  padding: '10px 14px',
                                  borderRadius: 'var(--radius-lg)',
                                  background: cardBg,
                                  border: cardBorder,
                                  boxShadow: cardShadow,
                                  cursor: 'pointer',
                                  transition: 'all 0.15s ease',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: 6
                                }}
                              >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <span style={{
                                    fontSize: '12px',
                                    fontWeight: 800,
                                    color: isSelected ? 'var(--color-primary)' : 'var(--color-fg)'
                                  }}>
                                    {node.label}
                                  </span>
                                  {isSelected && (
                                    <span style={{ fontSize: '10px', color: 'var(--color-primary)', fontWeight: 700 }}>
                                      Active
                                    </span>
                                  )}
                                </div>

                                <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
                                  <span style={{
                                    fontSize: '9px',
                                    fontWeight: 700,
                                    padding: '2px 6px',
                                    borderRadius: 'var(--radius-full)',
                                    background: preCount === 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                                    color: preCount === 0 ? 'var(--color-success)' : 'var(--color-warning)'
                                  }}>
                                    {preCount === 0 ? 'Core Base' : `${preCount} Pre-reqs`}
                                  </span>

                                  {unlockCount > 0 && (
                                    <span style={{
                                      fontSize: '9px',
                                      fontWeight: 700,
                                      padding: '2px 6px',
                                      borderRadius: 'var(--radius-full)',
                                      background: 'rgba(99, 102, 241, 0.15)',
                                      color: 'var(--color-primary)'
                                    }}>
                                      Unlocks {unlockCount}
                                    </span>
                                  )}
                                </div>
                              </div>
                            )
                          })
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )
          })()}
        </div>
      )}
    </div>
  )
}
