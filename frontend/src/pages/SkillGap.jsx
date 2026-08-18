import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, CheckCircle2, AlertCircle, BookOpen, ExternalLink,
  Zap, Layers, Lightbulb
} from 'lucide-react'
import { uResumeList, c4SkillGapRoles, c4SkillGapAnalyze, c4SkillGapSimulate } from '../api'

export default function SkillGap() {
  const navigate = useNavigate()
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [activeTab, setActiveTab] = useState('applied') // 'applied' or 'explorer'
  const [appliedReports, setAppliedReports] = useState([])
  const [selectedJobId, setSelectedJobId] = useState(null)
  const [loadingApplied, setLoadingApplied] = useState(false)
  const [syncingProgress, setSyncingProgress] = useState(false)

  // Real Job Openings & Explorer / What-If state
  const [availableJobs, setAvailableJobs] = useState([])
  const [selectedOpeningId, setSelectedOpeningId] = useState('')
  const [candidateProfile, setCandidateProfile] = useState({
    candidate_name: '',
    skills: [],
    experience_years: 0,
    education: 'B.Sc. Computer Science'
  })
  
  // What-If Simulator state
  const [simulatedSkills, setSimulatedSkills] = useState([])
  const [customSimSkill, setCustomSimSkill] = useState('')
  const [simulationResult, setSimulationResult] = useState(null)
  const [simulating, setSimulating] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') { navigate('/login/candidate'); return }
    c4SkillGapRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => toast.error('Failed to load roles'))
    loadResumeData()
  }, [])

  const loadAppliedJobsAnalysis = async () => {
    setLoadingApplied(true)
    try {
      const r = await uResumeList()
      const resumes = r.data || []
      if (resumes.length > 0) {
        const latest = resumes[0]
        setCandidateProfile({
          candidate_name: latest.candidate_name || localStorage.getItem('recruitai.name') || 'Candidate',
          skills: latest.skills || [],
          experience_years: latest.experience_years || 0,
          education: latest.education || 'B.Sc. Computer Science'
        })
      } else {
        setCandidateProfile(p => ({
          ...p,
          candidate_name: localStorage.getItem('recruitai.name') || 'Candidate',
          skills: ['Python', 'SQL', 'Git', 'FastAPI']
        }))
      }
    } catch { toast.error('Failed to load resume data') }
  }

  const syncToProgress = async () => {
    setSyncingProgress(true)
    try {
      const r = await c4SkillGapAnalyze({
        candidate_id: localStorage.getItem('recruitai.user_id'),
        candidate_name: form.candidate_name,
        job_role: form.job_role,
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
        experience_years: parseFloat(form.experience_years) || 0,
        education: form.education || 'B.Sc. Computer Science',
      })
      const data = r?.data?.data || r?.data || {}
      setResult(data)
      toast.success(`Skill Fit Score: ${(data.skill_match_pct || (data.gap_score * 100)).toFixed(0)}%`)
    } catch (err) {
      toast.error('Failed to sync to progress tracker')
    } finally {
      setSyncingProgress(false)
    }
  }

  // Selected Real Opening
  const currentOpening = availableJobs.find(j => (j.id || j._id) === selectedOpeningId) || availableJobs[0]

  // Calculate Explorer baseline for selected job opening
  const openingRequiredSkills = currentOpening?.required_skills || []
  const candSkillsLower = (candidateProfile.skills || []).map(s => s.toLowerCase().trim())

  const matchedOpeningSkills = openingRequiredSkills.filter(req =>
    candSkillsLower.some(c => c === req.toLowerCase().trim() || c.includes(req.toLowerCase().trim()) || req.toLowerCase().trim().includes(c))
  )
  const missingOpeningSkills = openingRequiredSkills.filter(req =>
    !candSkillsLower.some(c => c === req.toLowerCase().trim() || c.includes(req.toLowerCase().trim()) || req.toLowerCase().trim().includes(c))
  )

  const baselineMatchPct = openingRequiredSkills.length > 0
    ? Math.round((matchedOpeningSkills.length / openingRequiredSkills.length) * 100)
    : 70

  // What-If Simulation runner
  const runSimulation = () => {
    if (!currentOpening) return
    setSimulating(true)

    const allSimulated = Array.from(new Set([...candSkillsLower, ...simulatedSkills.map(s => s.toLowerCase().trim())]))
    const simMatched = openingRequiredSkills.filter(req =>
      allSimulated.some(c => c === req.toLowerCase().trim() || c.includes(req.toLowerCase().trim()) || req.toLowerCase().trim().includes(c))
    )
    const simMissing = openingRequiredSkills.filter(req =>
      !allSimulated.some(c => c === req.toLowerCase().trim() || c.includes(req.toLowerCase().trim()) || req.toLowerCase().trim().includes(c))
    )

    const simMatchPct = openingRequiredSkills.length > 0
      ? Math.round((simMatched.length / openingRequiredSkills.length) * 100)
      : 85

    const delta = simMatchPct - baselineMatchPct

    setSimulationResult({
      original_coverage: baselineMatchPct,
      simulated_coverage: simMatchPct,
      coverage_improvement: delta,
      simulated_matched: simMatched,
      remaining_missing: simMissing,
      job_title: currentOpening.title,
      company_name: currentOpening.company_name || 'Selected Employer'
    })
    setSimulating(false)
    toast.success(`Simulation Complete: +${delta}% readiness improvement!`)
  }

  const addSimSkill = (skill) => {
    if (!skill || !skill.trim()) return
    const s = skill.trim()
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
            <p className="muted" style={{ fontSize: 13, marginTop: 4, margin: 0 }}>
              Analyze your strengths & weaknesses across real applied jobs, or simulate skill acquisitions against available openings.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={loadAppliedJobsAnalysis}
              className="btn btn-ghost btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              title="Refresh analysis"
            >
              <RefreshCw size={14} className={loadingApplied ? 'spin' : ''} /> Refresh
            </button>
            <button
              onClick={syncToProgress}
              disabled={syncingProgress}
              className="btn btn-primary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <TrendingUp size={14} /> {syncingProgress ? 'Syncing...' : 'Sync Weaknesses to Progress'}
            </button>
          </div>
        </div>

        <button className="btn" type="submit" disabled={busy} style={{ width: '100%', height: 44, fontSize: 14, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, background: 'var(--color-primary)', color: 'var(--color-on-primary)' }}>
          <Target size={18} /> {busy ? 'Calculating Skill Coverage & Recommendations...' : 'Run Skill Gap Analysis'}
        </button>
      </form>

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
                  const isSelected = rep.job_id === (selectedReport?.job_id)
                  return (
                    <button
                      key={rep.job_id}
                      onClick={() => setSelectedJobId(rep.job_id)}
                      style={{
                        padding: '10px 16px',
                        borderRadius: 10,
                        border: isSelected ? '2px solid var(--accent)' : '1px solid var(--border)',
                        background: isSelected ? 'rgba(59, 130, 246, 0.08)' : 'var(--bg-elevated)',
                        cursor: 'pointer',
                        textAlign: 'left',
                        minWidth: 200,
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ fontSize: 13, fontWeight: 800, color: 'var(--text)' }}>
                        {rep.job_title}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span>{rep.company_name}</span>
                        <span style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '2px 6px',
                          borderRadius: 4,
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

              {/* Selected Job Report Details */}
              {selectedReport && (
                <div className="card" style={{ padding: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
                  {/* Job Header & Scores Banner */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, paddingBottom: 18, borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span className="chip" style={{ fontSize: 11, fontWeight: 700, background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent)' }}>
                          {selectedReport.company_name}
                        </span>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>• {selectedReport.location}</span>
                        {selectedReport.salary_range && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>• {selectedReport.salary_range}</span>}
                      </div>
                      <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text)', margin: 0 }}>
                        {selectedReport.job_title}
                      </h2>
                    </div>

                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>CV Match (C1)</div>
                        <div style={{ fontSize: 18, fontWeight: 900, color: 'var(--text)' }}>
                          {selectedReport.cv_score !== null ? `${selectedReport.cv_score}%` : 'N/A'}
                        </div>
                      </div>

                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Interview Score (C2)</div>
                        <div style={{ fontSize: 18, fontWeight: 900, color: selectedReport.interview_completed ? 'var(--color-success)' : '#f59e0b' }}>
                          {selectedReport.interview_score !== null ? `${selectedReport.interview_score}%` : 'Pending'}
                        </div>
                      </div>

                      <div style={{ textAlign: 'center', padding: '8px 14px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: 8, border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase' }}>Overall Fit Score</div>
                        <div style={{ fontSize: 20, fontWeight: 900, color: 'var(--accent)' }}>
                          {selectedReport.composite_score}%
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Interview Status Alert if not completed */}
                  {!selectedReport.interview_completed && (
                    <div style={{ padding: 14, borderRadius: 8, background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <HelpCircle size={18} style={{ color: '#f59e0b' }} />
                        <span style={{ fontSize: 13, color: 'var(--text)' }}>
                          You have applied for this position, but haven't faced the technical interview yet. Take the interview to unlock complete question-by-question topic insights!
                        </span>
                      </div>
                      <Link to={`/candidate/interview`} className="btn btn-sm" style={{ background: '#f59e0b', color: '#fff', fontWeight: 700 }}>
                        Start AI Interview
                      </Link>
                    </div>
                  )}

                  {/* Interview Breakdown if completed */}
                  {selectedReport.interview_breakdown && (
                    <div style={{ marginBottom: 24, padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                      <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Zap size={15} style={{ color: 'var(--accent)' }} /> AI Interview Performance Breakdown
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 12 }}>
                        <div style={{ padding: 10, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>MCQ Conceptual</div>
                          <div style={{ fontSize: 16, fontWeight: 800, color: selectedReport.interview_breakdown.mcq_score >= 70 ? '#22c55e' : '#ef4444' }}>
                            {selectedReport.interview_breakdown.mcq_score}%
                          </div>
                        </div>
                        <div style={{ padding: 10, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Descriptive Theory</div>
                          <div style={{ fontSize: 16, fontWeight: 800, color: selectedReport.interview_breakdown.descriptive_score >= 70 ? '#22c55e' : '#ef4444' }}>
                            {selectedReport.interview_breakdown.descriptive_score}%
                          </div>
                        </div>
                        <div style={{ padding: 10, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Coding / Practical</div>
                          <div style={{ fontSize: 16, fontWeight: 800, color: selectedReport.interview_breakdown.coding_score >= 70 ? '#22c55e' : '#ef4444' }}>
                            {selectedReport.interview_breakdown.coding_score}%
                          </div>
                        </div>
                        <div style={{ padding: 10, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Performance Grade</div>
                          <div style={{ fontSize: 15, fontWeight: 800, color: 'var(--accent)' }}>
                            {selectedReport.interview_breakdown.grade}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* STRENGTHS AND WEAKNESSES SIDE-BY-SIDE */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, marginBottom: 24 }}>
                    {/* STRENGTHS */}
                    <div style={{ padding: 18, background: 'rgba(34, 197, 94, 0.04)', borderRadius: 10, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#22c55e', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <CheckCircle2 size={18} /> Verified Strengths ({selectedReport.strengths?.length || 0})
                      </h3>
                      <p className="muted" style={{ fontSize: 12, marginBottom: 12 }}>
                        Skills verified on your CV and technical interview questions where you achieved strong marks.
                      </p>

                      {selectedReport.strengths?.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                          {selectedReport.strengths.map((st, idx) => (
                            <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 6, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{st.skill}</span>
                                <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4, background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' }}>
                                  {st.source}
                                </span>
                              </div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>
                                {st.details}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="muted" style={{ fontSize: 12, fontStyle: 'italic' }}>No verified strengths recorded yet. Complete the interview to demonstrate skills.</div>
                      )}
                    </div>

                    {/* WEAKNESSES & SKILL GAPS */}
                    <div style={{ padding: 18, background: 'rgba(239, 68, 68, 0.04)', borderRadius: 10, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <AlertCircle size={18} /> Identified Weaknesses & Gaps ({selectedReport.weaknesses?.length || 0})
                      </h3>
                      <p className="muted" style={{ fontSize: 12, marginBottom: 12 }}>
                        Low-scoring interview topics and job requirements missing from your CV profile that you must improve.
                      </p>

                      {selectedReport.weaknesses?.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                          {selectedReport.weaknesses.map((wk, idx) => (
                            <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 6, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)' }}>{wk.skill}</span>
                                <span style={{
                                  fontSize: 10,
                                  fontWeight: 700,
                                  padding: '2px 6px',
                                  borderRadius: 4,
                                  background: wk.severity === 'Critical' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                  color: wk.severity === 'Critical' ? '#ef4444' : '#f59e0b'
                                }}>
                                  {wk.source}
                                </span>
                              </div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>
                                {wk.details}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="muted" style={{ fontSize: 12, fontStyle: 'italic', color: '#22c55e' }}>🎉 Outstanding! No critical skill gaps identified for this role.</div>
                      )}
                    </div>
                  </div>

                  {/* TOPIC-BY-TOPIC INTERVIEW RESULTS */}
                  {selectedReport.topic_performance?.length > 0 && (
                    <div style={{ marginBottom: 24, padding: 18, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                      <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Code size={16} style={{ color: 'var(--accent)' }} /> Question-by-Question Skill Topic Marks
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
                        {selectedReport.topic_performance.map((tp, idx) => {
                          const isGood = tp.score >= 70
                          return (
                            <div key={idx} style={{ padding: 12, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text)' }}>{tp.topic}</span>
                                <span style={{ fontSize: 11, fontWeight: 800, color: isGood ? '#22c55e' : '#ef4444' }}>{tp.score}%</span>
                              </div>
                              <div style={{ height: 6, background: 'var(--border)', borderRadius: 3, overflow: 'hidden' }}>
                                <div style={{ width: `${tp.score}%`, height: '100%', background: isGood ? '#22c55e' : '#ef4444', borderRadius: 3 }} />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* ACTIONABLE COURSE RECOMMENDATIONS */}
                  {selectedReport.course_recommendations?.length > 0 && (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                        <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 8, margin: 0 }}>
                          <BookOpen size={18} style={{ color: 'var(--accent)' }} /> Targeted Courses to Close Weaknesses ({selectedReport.course_recommendations.length})
                        </h3>
                        <button onClick={syncToProgress} className="btn btn-ghost btn-sm" style={{ fontSize: 12, color: 'var(--accent)' }}>
                          Track in Progress Matrix →
                        </button>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
                        {selectedReport.course_recommendations.map((c, idx) => (
                          <div key={idx} style={{ padding: 14, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--accent)', textTransform: 'uppercase' }}>{c.skill}</span>
                                <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4, background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                                  {c.priority} Priority
                                </span>
                              </div>
                              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>
                                {c.course}
                              </div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 10 }}>
                                {c.duration} • {c.level} Level
                              </div>
                            </div>
                            <a
                              href={c.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn btn-sm"
                              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, background: 'var(--color-primary)', color: '#fff', fontSize: 11, fontWeight: 700 }}
                            >
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

      {/* TAB 2: AVAILABLE JOB OPENINGS EXPLORER & WHAT-IF SIMULATOR */}
      {activeTab === 'explorer' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Real Job Openings Selector Card */}
          <div className="card" style={{ padding: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Building2 size={18} style={{ color: 'var(--accent)' }} /> Select Available Job Opening with Company
                </h3>
                <p className="muted" style={{ fontSize: 12, margin: '2px 0 0' }}>
                  Choose from active, verified job postings across top global companies.
                </p>
              </div>
              <span className="chip" style={{ fontSize: 11, fontWeight: 700, background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent)' }}>
                {availableJobs.length} Live Openings
              </span>
            </div>

            {/* Dropdown with Job Title & Company Name */}
            <div style={{ marginBottom: 16 }}>
              <select
                value={selectedOpeningId}
                onChange={(e) => {
                  setSelectedOpeningId(e.target.value)
                  setSimulationResult(null)
                  setSimulatedSkills([])
                }}
                style={{
                  width: '100%',
                  height: 46,
                  padding: '0 14px',
                  background: 'var(--input-bg)',
                  border: '2px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text)',
                  fontSize: 14,
                  fontWeight: 600
                }}
              >
                {availableJobs.map((j) => {
                  const id = j.id || j._id
                  const comp = j.company_name || 'Tech Company'
                  const loc = j.location || 'Remote'
                  return (
                    <option key={id} value={id}>
                      {j.title} @ {comp} ({loc}) — {j.salary_range || 'Competitive'}
                    </option>
                  )
                })}
              </select>
            </div>
            <div className="stat" style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <div className="stat-label" style={{ fontSize: 12 }}>Gap Severity</div>
              <div className="stat-value" style={{ color: result.gap_severity === 'Low' ? 'var(--color-success)' : result.gap_severity === 'Medium' ? 'var(--color-warning)' : 'var(--color-danger)', fontSize: 22 }}>
                {result.gap_severity}
              </div>
            )}
          </div>

          {/* Missing Required & Optional Skills */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--danger)' }}>
                <AlertCircle size={16} /> Critical Missing Required Skills ({result.missing_required?.length || 0})
              </h4>
              {result.missing_required?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.missing_required.map((s) => (
                    <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-danger)', border: '1px solid rgba(239, 68, 68, 0.3)', fontWeight: 600 }}>
                      {s}
                    </span>
                  ))}
                </div>
              )}

            <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                <CheckCircle2 size={16} /> Present Verified Skills ({result.present_skills?.length || 0})
              </h4>
              {result.present_skills?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.present_skills.map((s) => (
                    <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                      {s}
                      <button onClick={() => removeSimSkill(s)} style={{ border: 'none', background: 'transparent', color: 'inherit', cursor: 'pointer', padding: 0 }}>×</button>
                    </span>
                  ))}
                </div>
              )}

              {/* Run Simulation Button */}
              <button
                onClick={runSimulation}
                disabled={simulating || simulatedSkills.length === 0}
                className="btn btn-primary"
                style={{ width: '100%', height: 44, fontSize: 14, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Sparkles size={18} /> {simulating ? 'Calculating Impact...' : `Simulate Impact on ${currentOpening.title} @ ${currentOpening.company_name}`}
              </button>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                {result.resources.map((resItem, idx) => {
                  const pColor = resItem.priority === 'Critical' ? 'var(--color-danger)' : resItem.priority === 'High' ? 'var(--color-orange)' : resItem.priority === 'Medium' ? 'var(--color-warning)' : 'var(--color-success)'
                  return (
                    <div key={idx} style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: `${pColor}15`, color: pColor, border: `1px solid ${pColor}40`, fontWeight: 700 }}>
                            {resItem.priority} Priority
                          </span>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
                            {resItem.level || 'Beginner'} · {resItem.duration || '4 weeks'}
                          </span>
                        </div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>
                          {resItem.skill}: <span style={{ color: 'var(--accent)' }}>{resItem.course}</span>
                        </div>
                      </div>

                      <a
                        href={resItem.url || `https://www.coursera.org/search?query=${encodeURIComponent(resItem.skill)}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-ghost btn-sm"
                        style={{ marginTop: 12, fontSize: 12, border: '1px solid var(--border)', display: 'inline-flex', alignItems: 'center', gap: 6, alignSelf: 'flex-start' }}
                      >
                        Enroll / Explore Course <ExternalLink size={13} />
                      </a>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span className="chip" style={{ fontSize: 12, fontWeight: 800, background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e', padding: '4px 12px' }}>
                        +{simulationResult.coverage_improvement}% Readiness Boost
                      </span>
                    </div>
                  </div>

          {/* Structured Learning Roadmap */}
          {result.learning_plan?.length > 0 && (
            <div style={{ marginBottom: 24, padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Layers size={20} style={{ color: 'var(--color-primary)' }} /> Structured Monthly Skill Acquisition Plan
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {result.learning_plan.map((planItem, i) => (
                  <div key={i} style={{ padding: 14, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--accent)', color: 'var(--color-on-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14 }}>
                      {planItem.phase || (i + 1)}
                    </div>
                    <div style={{ padding: 14, background: 'rgba(34, 197, 94, 0.08)', borderRadius: 8, border: '1px solid rgba(34, 197, 94, 0.3)', textAlign: 'center' }}>
                      <div style={{ fontSize: 11, color: '#22c55e', fontWeight: 700 }}>Simulated Match with New Skills</div>
                      <div style={{ fontSize: 28, fontWeight: 900, color: '#22c55e' }}>
                        {simulationResult.simulated_coverage}%
                      </div>
                    </div>
                  </div>

          {/* AI Improvement Suggestions */}
          {result.improvement_suggestions?.length > 0 && (
            <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Lightbulb size={20} style={{ color: 'var(--color-warning)' }} /> Actionable AI Profile Recommendations
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.improvement_suggestions.map((s, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <span style={{ color: 'var(--color-warning)' }}>•</span> {s}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
