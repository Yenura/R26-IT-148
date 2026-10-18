import { useEffect, useState, useMemo } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, RefreshCw, TrendingUp, Briefcase, HelpCircle,
  Code, Building2, Sparkles, AlertCircle, CheckCircle2,
  ExternalLink, Layers, Lightbulb, ArrowRight,
  Search, Clock, BookOpen
} from 'lucide-react'
import { c0JobsAll, c4SkillGapAnalyze, c4SkillGapApplied, c4SkillGapSimulate, c4SkillGapRoles, c4ProgressSync, authGetProfile } from '../api'
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
  const [appliedReports, setAppliedReports] = useState(() => {
    try {
      const uId = localStorage.getItem('recruitai.user_id') || 'web-user'
      const cached = sessionStorage.getItem(`recruitai.skillgap.${uId}`)
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
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
  const [simulatorMode, setSimulatorMode] = useState('company') // 'company' | 'position'
  const [selectedSimCompany, setSelectedSimCompany] = useState('')
  const [selectedSimPosition, setSelectedSimPosition] = useState('')
  const [roles, setRoles] = useState([])
  const [simulatedSkills, setSimulatedSkills] = useState([])
  const [customSimSkill, setCustomSimSkill] = useState('')
  const [simulationResult, setSimulationResult] = useState(null)
  const [simulating, setSimulating] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    // Concurrent parallel background revalidation & pre-fetching
    Promise.all([
      c4SkillGapRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => {}),
      loadAppliedJobsAnalysis(),
      loadAvailableJobs(),
    ])
  }, [])

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
    if (!currentOpening) return
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
      if ((data.coverage_improvement || 0) > 0) {
        toast.success(`Simulation Complete: +${data.coverage_improvement}% improvement!`)
      } else {
        toast.success(`Simulation Complete: Baseline fit is ${data.simulated_coverage || 0}%.`)
      }
    } catch { toast.error('Simulation failed') }
    finally { setSimulating(false) }
  }

  const cleanCompName = (name) => {
    if (!name) return 'General Tech'
    const trimmed = name.trim()
    if (/^techcorp\b/i.test(trimmed)) return 'TechCorp'
    if (trimmed.toLowerCase() === 'slt') return 'SLT Mobitel'
    return trimmed
  }

  // Unique companies with counts
  const companyOptions = useMemo(() => {
    const map = new Map()
    availableJobs.forEach((j) => {
      const c = cleanCompName(j.company_name)
      map.set(c, (map.get(c) || 0) + 1)
    })
    return Array.from(map.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => a.name.localeCompare(b.name))
  }, [availableJobs])

  // Unique job positions / titles with counts
  const positionOptions = useMemo(() => {
    const map = new Map()
    availableJobs.forEach((j) => {
      const title = (j.title || j.job_role || 'Untitled Role').trim()
      map.set(title, (map.get(title) || 0) + 1)
    })
    return Array.from(map.entries())
      .map(([title, count]) => ({ title, count }))
      .sort((a, b) => a.title.localeCompare(b.title))
  }, [availableJobs])

  // Filtered jobs based on active company selection
  const filteredJobsByCompany = useMemo(() => {
    if (!selectedSimCompany) return availableJobs
    return availableJobs.filter((j) => cleanCompName(j.company_name) === selectedSimCompany)
  }, [availableJobs, selectedSimCompany])

  // Filtered jobs based on active position selection
  const filteredJobsByPosition = useMemo(() => {
    if (!selectedSimPosition) return availableJobs
    return availableJobs.filter((j) => (j.title || j.job_role || '').trim().toLowerCase() === selectedSimPosition.toLowerCase())
  }, [availableJobs, selectedSimPosition])

  const currentOpening = availableJobs.find(j => (j.id || j._id) === selectedOpeningId) || availableJobs[0]
  const openingRequiredSkills = currentOpening?.required_skills || []

  // Keep selected company & position in sync when opening changes
  useEffect(() => {
    if (currentOpening) {
      if (!selectedSimCompany) setSelectedSimCompany(cleanCompName(currentOpening.company_name))
      if (!selectedSimPosition) setSelectedSimPosition((currentOpening.title || currentOpening.job_role || '').trim())
    }
  }, [currentOpening])

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
                        padding: '12px 16px', borderRadius: 'var(--radius-lg)', minWidth: 260, textAlign: 'left', cursor: 'pointer',
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
                      {/* 3 Marks Quick Pill Strip */}
                      <div style={{ display: 'flex', gap: 6, marginTop: 8, fontSize: '10px', fontFamily: 'var(--p-font-mono)' }}>
                        <span style={{ padding: '2px 6px', borderRadius: 4, background: 'var(--color-bg)', color: rep.cv_score != null ? 'var(--color-primary)' : 'var(--color-fg-muted)', border: '1px solid var(--color-border-subtle)' }}>
                          CV: {rep.cv_score != null ? `${Number(rep.cv_score).toFixed(0)}%` : 'Pending'}
                        </span>
                        <span style={{ padding: '2px 6px', borderRadius: 4, background: 'var(--color-bg)', color: (rep.interview_completed && rep.interview_score != null) ? 'var(--color-purple)' : 'var(--color-fg-muted)', border: '1px solid var(--color-border-subtle)' }}>
                          Int: {(rep.interview_completed && rep.interview_score != null) ? `${Number(rep.interview_score).toFixed(0)}%` : 'Pending'}
                        </span>
                        <span style={{ padding: '2px 6px', borderRadius: 4, background: 'var(--color-bg)', fontWeight: 700, color: (rep.composite_score != null || rep.total_mark != null) ? 'var(--color-fg)' : 'var(--color-fg-muted)', border: '1px solid var(--color-border-subtle)' }}>
                          CSS: {rep.composite_score != null ? `${Number(rep.composite_score).toFixed(0)}%` : (rep.total_mark != null ? `${Number(rep.total_mark).toFixed(0)}%` : '—')}
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
                      {(() => {
                        const hasCV = selectedReport.cv_score != null
                        const hasInt = Boolean(selectedReport.interview_completed && selectedReport.interview_score != null)

                        let totalScore = '0'
                        let totalLabel = 'Final Total Mark'
                        if (hasCV && hasInt) {
                          totalLabel = 'Final Total Mark'
                          const rawVal = selectedReport.composite_score != null
                            ? Number(selectedReport.composite_score)
                            : (0.40 * Number(selectedReport.cv_score) + 0.60 * Number(selectedReport.interview_score))
                          totalScore = Math.round(rawVal).toString()
                        } else if (hasCV) {
                          totalLabel = 'Final CV Mark'
                          totalScore = Math.round(Number(selectedReport.cv_score)).toString()
                        } else if (hasInt) {
                          totalLabel = 'Final Interview Mark'
                          totalScore = Math.round(Number(selectedReport.interview_score)).toString()
                        } else {
                          totalLabel = 'Final Total Mark'
                          totalScore = '0'
                        }

                        return (
                          <>
                            <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>CV Mark</div>
                              <div style={{ fontSize: '1.15rem', fontWeight: 800, color: hasCV ? 'var(--color-primary)' : 'var(--color-warning)', fontFamily: 'var(--p-font-mono)' }}>
                                {hasCV ? `${Math.round(Number(selectedReport.cv_score))}%` : 'Pending'}
                              </div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                              <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Interview Mark</div>
                              <div style={{ fontSize: '1.15rem', fontWeight: 800, color: hasInt ? 'var(--color-purple)' : 'var(--color-warning)', fontFamily: 'var(--p-font-mono)' }}>
                                {hasInt ? `${Math.round(Number(selectedReport.interview_score))}%` : 'Pending'}
                              </div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '8px 14px', background: (hasCV && hasInt) ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: `1px solid ${(hasCV && hasInt) ? 'rgba(99, 102, 241, 0.4)' : 'var(--color-border)'}` }}>
                              <div style={{ fontSize: '10px', fontWeight: 700, color: (hasCV && hasInt) ? 'var(--color-primary)' : 'var(--color-fg-muted)', textTransform: 'uppercase' }}>
                                {totalLabel}
                              </div>
                              <div style={{ fontSize: '1.3rem', fontWeight: 900, color: (hasCV && hasInt) ? 'var(--color-primary)' : 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                                {totalScore}%
                              </div>
                            </div>
                          </>
                        )
                      })()}
                    </div>
                  </div>

                  {/* Interview / CV Completion Prompt Banners */}
                  {selectedReport.cv_score != null && !selectedReport.interview_completed && (
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

                  {selectedReport.cv_score == null && selectedReport.interview_completed && (
                    <div style={{
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-primary-muted)',
                      border: '1px solid rgba(99, 102, 241, 0.4)',
                      boxShadow: '0 0 20px -4px rgba(99, 102, 241, 0.25)',
                      marginBottom: 20,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: 12
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Sparkles size={20} style={{ color: 'var(--color-primary)', flexShrink: 0 }} />
                        <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg)' }}>
                          Your AI Interview evaluation is recorded! Complete your CV Match to unlock your final total score and top ranking.
                        </span>
                      </div>
                      <Link to="/candidate/cv-matching" className="btn btn-sm btn-primary" style={{ fontWeight: 700, whiteSpace: 'nowrap' }}>
                        Complete CV Match
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Building2 size={18} style={{ color: 'var(--color-primary)' }} /> Select Target Job Opening
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0' }}>
                  Filter and select your target opening by company name or by job position.
                </p>
              </div>
              <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>
                {availableJobs.length} Live Openings
              </span>
            </div>

            {/* 2 Tabs: Select by Company Name vs Select by Job Position */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--color-fg-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Select Mode:
              </span>
              <div style={{ display: 'inline-flex', background: 'var(--color-bg)', padding: 3, borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                <button
                  type="button"
                  onClick={() => setSimulatorMode('company')}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '12px',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    background: simulatorMode === 'company' ? 'var(--color-primary)' : 'transparent',
                    color: simulatorMode === 'company' ? '#fff' : 'var(--color-fg-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    transition: 'all 0.2s ease'
                  }}
                >
                  <Building2 size={13} /> Company Name
                </button>
                <button
                  type="button"
                  onClick={() => setSimulatorMode('position')}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '12px',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    background: simulatorMode === 'position' ? 'var(--color-primary)' : 'transparent',
                    color: simulatorMode === 'position' ? '#fff' : 'var(--color-fg-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    transition: 'all 0.2s ease'
                  }}
                >
                  <Briefcase size={13} /> Job Position
                </button>
              </div>
            </div>

            {/* Tab 1: By Company Name */}
            {simulatorMode === 'company' ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
                {/* 1. Select Company */}
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Building2 size={13} style={{ color: 'var(--color-primary)' }} /> 1. Company Name:
                  </label>
                  <select
                    value={selectedSimCompany}
                    onChange={(e) => {
                      const comp = e.target.value
                      setSelectedSimCompany(comp)
                      setSimulationResult(null)
                      setSimulatedSkills([])
                      if (comp) {
                        const compJobs = availableJobs.filter((j) => cleanCompName(j.company_name) === comp)
                        if (compJobs.length > 0) {
                          setSelectedOpeningId(compJobs[0].id || compJobs[0]._id)
                        }
                      } else if (availableJobs.length > 0) {
                        setSelectedOpeningId(availableJobs[0].id || availableJobs[0]._id)
                      }
                    }}
                    style={{
                      width: '100%', height: 42, padding: '0 12px',
                      background: 'var(--input-bg)', border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)', color: 'var(--color-fg)',
                      fontSize: 'var(--p-text-sm)', fontWeight: 600
                    }}
                  >
                    <option value="">🏢 All Companies ({availableJobs.length} openings)</option>
                    {companyOptions.map((c) => (
                      <option key={c.name} value={c.name}>
                        {c.name} ({c.count} open {c.count === 1 ? 'role' : 'roles'})
                      </option>
                    ))}
                  </select>
                </div>

                {/* 2. Select Job Position at Company */}
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Briefcase size={13} style={{ color: 'var(--color-success)' }} /> 2. Job Position {selectedSimCompany ? `at ${selectedSimCompany}` : ''}:
                  </label>
                  <select
                    value={selectedOpeningId}
                    onChange={(e) => {
                      setSelectedOpeningId(e.target.value)
                      setSimulationResult(null)
                      setSimulatedSkills([])
                    }}
                    style={{
                      width: '100%', height: 42, padding: '0 12px',
                      background: 'var(--input-bg)', border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)', color: 'var(--color-fg)',
                      fontSize: 'var(--p-text-sm)', fontWeight: 600
                    }}
                  >
                    {filteredJobsByCompany.map((j) => {
                      const id = j.id || j._id
                      return (
                        <option key={id} value={id}>
                          {j.title} {j.company_name ? `@ ${cleanCompName(j.company_name)}` : ''} ({j.location || 'Remote'})
                        </option>
                      )
                    })}
                  </select>
                </div>
              </div>
            ) : (
              /* Tab 2: By Job Position */
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
                {/* 1. Select Job Position */}
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Briefcase size={13} style={{ color: 'var(--color-primary)' }} /> 1. Job Position / Role:
                  </label>
                  <select
                    value={selectedSimPosition}
                    onChange={(e) => {
                      const pos = e.target.value
                      setSelectedSimPosition(pos)
                      setSimulationResult(null)
                      setSimulatedSkills([])
                      if (pos) {
                        const posJobs = availableJobs.filter((j) => (j.title || j.job_role || '').trim().toLowerCase() === pos.toLowerCase())
                        if (posJobs.length > 0) {
                          setSelectedOpeningId(posJobs[0].id || posJobs[0]._id)
                        }
                      } else if (availableJobs.length > 0) {
                        setSelectedOpeningId(availableJobs[0].id || availableJobs[0]._id)
                      }
                    }}
                    style={{
                      width: '100%', height: 42, padding: '0 12px',
                      background: 'var(--input-bg)', border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)', color: 'var(--color-fg)',
                      fontSize: 'var(--p-text-sm)', fontWeight: 600
                    }}
                  >
                    <option value="">💼 All Positions ({positionOptions.length} unique roles)</option>
                    {positionOptions.map((p) => (
                      <option key={p.title} value={p.title}>
                        {p.title} ({p.count} {p.count === 1 ? 'opening' : 'openings'})
                      </option>
                    ))}
                  </select>
                </div>

                {/* 2. Select Company Hiring For Position */}
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Building2 size={13} style={{ color: 'var(--color-success)' }} /> 2. Company {selectedSimPosition ? `hiring for ${selectedSimPosition}` : ''}:
                  </label>
                  <select
                    value={selectedOpeningId}
                    onChange={(e) => {
                      setSelectedOpeningId(e.target.value)
                      setSimulationResult(null)
                      setSimulatedSkills([])
                    }}
                    style={{
                      width: '100%', height: 42, padding: '0 12px',
                      background: 'var(--input-bg)', border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)', color: 'var(--color-fg)',
                      fontSize: 'var(--p-text-sm)', fontWeight: 600
                    }}
                  >
                    {filteredJobsByPosition.map((j) => {
                      const id = j.id || j._id
                      return (
                        <option key={id} value={id}>
                          {cleanCompName(j.company_name)} — {j.title} ({j.location || 'Remote'})
                        </option>
                      )
                    })}
                  </select>
                </div>
              </div>
            )}

            {/* Selected Role Summary Pill */}
            {currentOpening && (
              <div style={{
                marginTop: 16,
                padding: '12px 16px',
                background: 'var(--color-bg-elevated)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 12
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 'var(--radius-md)',
                    background: 'var(--color-primary-muted)',
                    color: 'var(--color-primary)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '13px'
                  }}>
                    {cleanCompName(currentOpening.company_name).slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 800, color: 'var(--color-fg)' }}>
                      {currentOpening.title || currentOpening.job_role}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                      🏢 {cleanCompName(currentOpening.company_name)} · 📍 {currentOpening.location || 'Remote'} {currentOpening.department ? `· 🏷️ ${currentOpening.department}` : ''}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {currentOpening.experience_required && (
                    <span className="chip" style={{ fontSize: '10px', padding: '3px 8px', background: 'var(--color-bg)', border: '1px solid var(--color-border)', fontWeight: 600 }}>
                      Exp: {currentOpening.experience_required}
                    </span>
                  )}
                  <span className="chip" style={{ fontSize: '10px', padding: '3px 8px', background: 'var(--color-primary-muted)', color: 'var(--color-primary)', fontWeight: 700 }}>
                    {openingRequiredSkills.length} Required Skills
                  </span>
                </div>
              </div>
            )}
          </div>

          {currentOpening && (
            <>
              {/* Missing Required Skills */}
<div className="dashboard-grid dashboard-grid-equal" style={{ gap: 16 }}>
                <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, flexWrap: 'wrap', gap: 6 }}>
                    <h4 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-danger)' }}>
                      <AlertCircle size={15} /> Job Required Skills ({openingRequiredSkills.length})
                    </h4>
                    {openingRequiredSkills.length > 0 && (
                      <button
                        type="button"
                        onClick={() => {
                          setSimulatedSkills(Array.from(new Set([...simulatedSkills, ...openingRequiredSkills])))
                          toast.success(`Added all ${openingRequiredSkills.length} skills to simulation`)
                        }}
                        className="btn btn-ghost btn-xs"
                        style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-primary)', border: '1px solid var(--color-border)', padding: '2px 8px', borderRadius: 'var(--radius-sm)' }}
                      >
                        + Add All to Simulation
                      </button>
                    )}
                  </div>
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, flexWrap: 'wrap', gap: 6 }}>
                    <h4 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                      <CheckCircle2 size={15} /> Simulated Acquired Skills ({simulatedSkills.length})
                    </h4>
                    {simulatedSkills.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setSimulatedSkills([])}
                        className="btn btn-ghost btn-xs"
                        style={{ fontSize: '10px', fontWeight: 600, color: 'var(--color-fg-muted)', padding: '2px 6px' }}
                      >
                        Clear All
                      </button>
                    )}
                  </div>
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
                disabled={simulating}
                className="btn btn-primary"
                style={{ width: '100%', padding: '12px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700, borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Sparkles size={16} /> {simulating ? 'Calculating Impact...' : simulatedSkills.length > 0 ? `Simulate Impact (+${simulatedSkills.length} skills) on ${currentOpening.title}` : `Simulate Impact on ${currentOpening.title}`}
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

                  {/* Guidance Tip when 0 skills were simulated */}
                  {simulatedSkills.length === 0 && (
                    <div style={{ padding: '12px 16px', background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
                      <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Lightbulb size={16} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
                        <span>Showing baseline fit for {currentOpening.title}. Click any skill chip above or click <strong>+ Add All to Simulation</strong> to simulate acquiring them!</span>
                      </div>
                      {openingRequiredSkills.length > 0 && (
                        <button
                          type="button"
                          onClick={() => {
                            setSimulatedSkills(Array.from(new Set(openingRequiredSkills)))
                            toast.success(`Added all ${openingRequiredSkills.length} skills! Click Simulate to see fit increase.`)
                          }}
                          className="btn btn-primary btn-xs"
                          style={{ fontSize: '11px', fontWeight: 700 }}
                        >
                          + Add All Skills Now
                        </button>
                      )}
                    </div>
                  )}

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
    </div>
  )
}
