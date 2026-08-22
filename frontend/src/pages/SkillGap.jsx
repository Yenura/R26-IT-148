import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, RefreshCw, TrendingUp, Briefcase, HelpCircle,
  Code, Building2, Sparkles, AlertCircle, CheckCircle2,
  ExternalLink, Layers, Lightbulb, ArrowRight, Plus, X
} from 'lucide-react'
import {
  c0JobsAll, c4SkillGapAnalyze, c4SkillGapApplied,
  c4SkillGapSimulate, c4SkillGapRoles, c4ProgressSync
} from '../api'
import PageHeader from '../components/PageHeader'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

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
    if (!token || role !== 'candidate') {
      navigate('/login/candidate')
      return
    }
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
    } catch {
      toast.error('Failed to load applied jobs analysis')
    } finally {
      setLoadingApplied(false)
    }
  }

  const loadAvailableJobs = async () => {
    try {
      const r = await c0JobsAll()
      const jobs = r?.data?.jobs || r?.data || []
      setAvailableJobs(Array.isArray(jobs) ? jobs : [])
      if (jobs.length > 0) setSelectedOpeningId(jobs[0].id || jobs[0]._id)
    } catch {
      /* silent */
    }
  }

  const syncToProgress = async () => {
    setSyncingProgress(true)
    try {
      await c4ProgressSync(candidateId)
      toast.success('Skill gap goals synced to Progress Tracker!')
    } catch {
      toast.error('Failed to sync to progress tracker')
    } finally {
      setSyncingProgress(false)
    }
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
      toast.success(`Simulation complete: +${data.coverage_improvement || 0}% coverage boost!`)
    } catch {
      toast.error('Simulation failed')
    } finally {
      setSimulating(false)
    }
  }

  const currentOpening = availableJobs.find((j) => (j.id || j._id) === selectedOpeningId) || availableJobs[0]

  const addSimSkill = (skill) => {
    const s = skill?.trim()
    if (!s) return
    if (!simulatedSkills.some((x) => x.toLowerCase() === s.toLowerCase())) {
      setSimulatedSkills([...simulatedSkills, s])
    }
    setCustomSimSkill('')
  }

  const removeSimSkill = (skill) => {
    setSimulatedSkills(simulatedSkills.filter((s) => s.toLowerCase() !== skill.toLowerCase()))
  }

  const selectedReport = appliedReports.find((r) => r.job_id === selectedJobId) || appliedReports[0]

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Component 4 AI Analytics"
        title="Skill Gap & Career Readiness Matrix"
        description="Identify high-impact competencies across applied roles, and simulate skill acquisitions to boost your match scores."
        icon={Target}
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={loadAppliedJobsAnalysis}
              className="btn btn-ghost btn-sm"
              title="Refresh analysis"
            >
              <RefreshCw size={14} className={loadingApplied ? 'spin' : ''} /> Refresh
            </button>
            <button
              onClick={syncToProgress}
              disabled={syncingProgress}
              className="btn btn-primary btn-sm"
            >
              <TrendingUp size={14} /> {syncingProgress ? 'Syncing...' : 'Sync to Progress Tracker'}
            </button>
          </div>
        }
      />

      {/* Mode Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 'var(--p-space-5)' }}>
        <button
          className={`btn btn-sm ${activeTab === 'applied' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('applied')}
        >
          <Briefcase size={14} /> Applied Jobs Analysis ({appliedReports.length})
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'simulate' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('simulate')}
        >
          <Sparkles size={14} /> Interactive Skill Simulator
        </button>
      </div>

      {/* TAB 1: APPLIED JOBS ANALYSIS */}
      {activeTab === 'applied' && (
        <div>
          {loadingApplied ? (
            <SkeletonLoader type="card" count={2} />
          ) : appliedReports.length === 0 ? (
            <EmptyState
              title="No applied jobs to analyze yet"
              description="Apply to positions on the Job Board or run a CV Match to generate comprehensive skill gap evaluations."
              actionLabel="Explore Jobs"
              icon={Briefcase}
              onAction={() => navigate('/candidate/jobs')}
            />
          ) : (
            <div>
              {/* Job Selector Pills */}
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 'var(--p-space-5)' }}>
                {appliedReports.map((report) => (
                  <button
                    key={report.job_id}
                    onClick={() => setSelectedJobId(report.job_id)}
                    className={`btn btn-sm ${selectedJobId === report.job_id ? 'btn-primary' : 'btn-ghost'}`}
                    style={{ fontSize: 'var(--p-text-xs)' }}
                  >
                    {report.job_title || 'Position'}
                  </button>
                ))}
              </div>

              {selectedReport && (
                <div className="card" style={{ padding: 'var(--p-space-6)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-5)', paddingBottom: 16, borderBottom: '1px solid var(--color-border-subtle)', flexWrap: 'wrap', gap: 12 }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-fg)' }}>
                        {selectedReport.job_title}
                      </h3>
                      <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                        {selectedReport.company_name || 'Hiring Employer'}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div>
                        <div style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)', lineHeight: 1 }}>
                          {(selectedReport.coverage_percentage || selectedReport.skill_coverage || 0).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>Skill Coverage</div>
                      </div>
                      <ScoreBadge score={selectedReport.coverage_percentage || selectedReport.skill_coverage || 0} />
                    </div>
                  </div>

                  {/* Skills Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
                    <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
                      <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                        <CheckCircle2 size={16} /> Verified Skills ({(selectedReport.matched_skills || []).length})
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {(selectedReport.matched_skills || []).map((s) => (
                          <span key={s} className="chip" style={{ fontSize: '11px', margin: 0, padding: '3px 8px', background: 'var(--color-success-muted)', color: 'var(--color-success)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
                      <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-danger)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                        <AlertCircle size={16} /> Recommended Target Skills ({(selectedReport.missing_skills || []).length})
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {(selectedReport.missing_skills || []).map((s) => (
                          <span key={s} className="chip" style={{ fontSize: '11px', margin: 0, padding: '3px 8px', background: 'var(--color-danger-muted)', color: 'var(--color-danger)', borderColor: 'rgba(244, 63, 94, 0.3)' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Learning Roadmap Recommendations */}
                  {selectedReport.recommendations?.length > 0 && (
                    <div>
                      <h4 style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 10, color: 'var(--color-fg)' }}>
                        Recommended Next Steps to Close Gaps
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {selectedReport.recommendations.map((rec, i) => (
                          <div key={i} style={{ padding: 12, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Lightbulb size={14} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
                            <span>{rec}</span>
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

      {/* TAB 2: INTERACTIVE SIMULATION SANDBOX */}
      {activeTab === 'simulate' && (
        <div className="card" style={{ padding: 'var(--p-space-6)' }}>
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={18} style={{ color: 'var(--color-primary)' }} /> Select Target Opening & Add Skills to Simulate
            </h3>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '4px 0 0 0' }}>
              Add skills you plan to learn and observe real-time coverage improvements.
            </p>
          </div>

<<<<<<< HEAD
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: '11px', marginTop: 0 }}>Target Position</label>
              <select
                value={selectedOpeningId}
                onChange={(e) => setSelectedOpeningId(e.target.value)}
                style={{ fontSize: 'var(--p-text-sm)' }}
              >
                {availableJobs.map((j) => (
                  <option key={j.id || j._id} value={j.id || j._id}>
                    {j.title} {j.company_name ? `· ${j.company_name}` : ''}
                  </option>
                ))}
              </select>
            </div>
=======
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
>>>>>>> aa767b9e2a9a7cb46786d00c06bcc14e47f6b502

            <div>
              <label style={{ fontSize: '11px', marginTop: 0 }}>Add Custom Skill</label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="text"
                  placeholder="e.g. AWS, Docker, Kubernetes"
                  value={customSimSkill}
                  onChange={(e) => setCustomSimSkill(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSimSkill(customSimSkill))}
                  style={{ fontSize: 'var(--p-text-sm)' }}
                />
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => addSimSkill(customSimSkill)}
                >
                  <Plus size={14} />
                </button>
              </div>
            </div>
          </div>

          {/* Simulated Skills Chips */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
              Simulated Acquisition List:
            </div>
            {simulatedSkills.length === 0 ? (
              <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', fontStyle: 'italic' }}>
                No skills added yet. Type a skill above to begin simulation.
              </p>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {simulatedSkills.map((s) => (
                  <span
                    key={s}
                    className="chip"
                    style={{
                      fontSize: '12px',
                      padding: '4px 10px',
                      background: 'var(--color-primary-muted)',
                      color: 'var(--color-primary)',
                      borderColor: 'rgba(59, 130, 246, 0.3)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6
                    }}
                  >
                    <span>{s}</span>
                    <button
                      onClick={() => removeSimSkill(s)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--color-primary)' }}
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <button
            className="btn btn-primary"
            onClick={runSimulation}
            disabled={simulating || simulatedSkills.length === 0}
            style={{ width: '100%', padding: '10px 16px', fontSize: 'var(--p-text-sm)', fontWeight: 700 }}
          >
            {simulating ? 'Simulating...' : 'Run Real-Time Simulation'}
          </button>

          {/* Simulation Output Banner */}
          {simulationResult && (
            <div style={{
              marginTop: 20,
              padding: 18,
              background: 'var(--color-success-muted)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 14
            }}>
              <div>
                <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-success)' }}>
                  +{simulationResult.coverage_improvement || 0}% Projected Match Increase
                </div>
                <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', marginTop: 2 }}>
                  Coverage advances from {simulationResult.original_coverage || 0}% to <strong>{simulationResult.simulated_coverage || 0}%</strong> for {simulationResult.job_title}.
                </div>
              </div>

              <Link to="/pipeline/progress" className="btn btn-primary btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
                Add to Learning Plan <ArrowRight size={13} />
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
