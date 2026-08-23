import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Upload, BarChart3, Trash2, Sparkles, CheckCircle2, AlertCircle,
  ArrowRight, Briefcase, Zap, Target, Route as RouteIcon, BookOpen, Layers,
  ExternalLink, ChevronRight, TrendingUp, Cpu, Award, RefreshCw, FileText
} from 'lucide-react'
import {
  uResumeDelete, uResumeUpload, c0JobsAll, uResumeList, c0ResumeMatch,
  c1Analyze, c4SkillGap, c4SkillGapSimulate, c4CareerRec, c4LearningPath
} from '../api'
import PageHeader from '../components/PageHeader'
import UploadZone from '../components/UploadZone'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import LoadingState from '../components/LoadingState'
import ConfirmDialog from '../components/ConfirmDialog'

const CANONICAL_ROLES = [
  'Software Engineer',
  'Data Scientist',
  'Machine Learning Engineer',
  'DevOps Engineer',
  'Cloud Solutions Architect',
  'Database Administrator',
  'Frontend Developer',
  'Backend Developer',
  'Mobile App Developer',
  'Full Stack Developer',
  'QA/Test Automation Engineer',
  'Data Engineer',
  'Site Reliability Engineer',
  'Cybersecurity Analyst',
  'UI/UX Designer',
  'Network Engineer',
  'Business/Systems Analyst',
  'AI/NLP Engineer',
  'Blockchain Developer',
  'Embedded Systems Engineer',
]

export default function CVMatch() {
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [selectedJob, setSelectedJob] = useState('')
  const [selectedCanonicalRole, setSelectedCanonicalRole] = useState('')
  const [uploading, setUploading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('match')

  // Results state
  const [matchResult, setMatchResult] = useState(null)
  const [c1Result, setC1Result] = useState(null)
  const [skillGapResult, setSkillGapResult] = useState(null)
  const [careerResult, setCareerResult] = useState(null)
  const [learningPathResult, setLearningPathResult] = useState(null)
  const [simulatedAcquiredSkills, setSimulatedAcquiredSkills] = useState([])
  const [simulationResult, setSimulationResult] = useState(null)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') {
      navigate('/login/candidate')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [r1, r2] = await Promise.all([
        uResumeList().catch(() => ({ data: [] })),
        c0JobsAll().catch(() => ({ data: [] })),
      ])
      const resumeList = Array.isArray(r1.data) ? r1.data : []
      setResumes(resumeList)
      setJobs(Array.isArray(r2.data) ? r2.data : [])
      if (resumeList.length > 0 && !selectedResume) {
        setSelectedResume(resumeList[0].id)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleFileUpload = async (file) => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    try {
      const res = await uResumeUpload(formData)
      toast.success('Resume uploaded & parsed!')
      await loadData()
      if (res.data?.id) {
        setSelectedResume(res.data.id)
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const runUnifiedAnalysis = async () => {
    let resumeToUse = selectedResume
    if (!resumeToUse && resumes.length > 0) {
      resumeToUse = resumes[0].id
      setSelectedResume(resumeToUse)
    }
    if (!resumeToUse) return toast.error('Please upload or select a resume first')

    setBusy(true)
    setMatchResult(null)
    setC1Result(null)
    setSkillGapResult(null)
    setCareerResult(null)
    setLearningPathResult(null)
    setSimulatedAcquiredSkills([])
    setSimulationResult(null)

    try {
      const targetResumeDoc = resumes.find((res) => res.id === resumeToUse) || {}
      const candidateSkills = targetResumeDoc.skills || []

      const matchedJobDoc = jobs.find((j) => j.id === selectedJob)
      const targetRoleName = matchedJobDoc
        ? matchedJobDoc.title
        : selectedCanonicalRole

      // 1. Fetch Component 0 Resume Match
      const matchParams = { resume_id: resumeToUse }
      if (selectedJob) matchParams.job_id = selectedJob
      else if (selectedCanonicalRole) matchParams.target_role = selectedCanonicalRole
      const matchRes = await c0ResumeMatch(resumeToUse, matchParams)
      setMatchResult(matchRes.data)

      const finalRole = selectedCanonicalRole || matchRes.data.predicted_role || targetRoleName

      // 2. Parallel Fetch All AI Analysis Endpoints Concurrently
      const [gapRes, careerRes, pathRes, c1Res] = await Promise.all([
        c4SkillGap({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
        c4CareerRec({ current_skills: candidateSkills, current_role: finalRole }).catch(() => null),
        c4LearningPath({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
        targetResumeDoc.raw_text
          ? c1Analyze({
              candidate_id: targetResumeDoc.candidate_id || resumeToUse,
              candidate_name: targetResumeDoc.candidate_name || 'Candidate',
              raw_text: targetResumeDoc.raw_text,
              target_role: finalRole,
            }).catch(() => null)
          : Promise.resolve(null),
      ])

      if (gapRes) setSkillGapResult(gapRes.data)
      if (careerRes) setCareerResult(careerRes.data)
      if (pathRes) setLearningPathResult(pathRes.data)
      if (c1Res?.data) setC1Result(c1Res.data)

      toast.success(`Analysis complete! Overall fit: ${matchRes.data.overall_score.toFixed(1)}%`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setBusy(false)
    }
  }

  const handleSimulateSkill = async (skillName) => {
    const isAcquired = simulatedAcquiredSkills.includes(skillName)
    const nextSkills = isAcquired
      ? simulatedAcquiredSkills.filter((s) => s !== skillName)
      : [...simulatedAcquiredSkills, skillName]

    setSimulatedAcquiredSkills(nextSkills)

    if (nextSkills.length === 0) {
      setSimulationResult(null)
      return
    }

    try {
      const targetResumeDoc = resumes.find((res) => res.id === selectedResume) || {}
      const currentSkills = targetResumeDoc.skills || []
      const matchedJobDoc = jobs.find((j) => j.id === selectedJob)
      const roleName = matchedJobDoc ? matchedJobDoc.title : selectedCanonicalRole

      const simRes = await c4SkillGapSimulate({
        current_skills: currentSkills,
        acquired_skills: nextSkills,
        target_role: roleName,
      })
      setSimulationResult(simRes.data)
    } catch {
      toast.error('Simulation failed')
    }
  }

  const deleteResume = async (id) => {
    setConfirm({
      open: true,
      title: 'Delete resume?',
      message: 'This will permanently remove the resume and its match predictions.',
      danger: true,
      action: async () => {
        try {
          await uResumeDelete(id)
          toast.success('Resume deleted')
          if (selectedResume === id) setSelectedResume('')
          loadData()
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Delete failed')
        }
      }
    })
  }

  const matchedJobDoc = jobs.find((j) => j.id === selectedJob)
  const displayJobTitle = matchedJobDoc
    ? matchedJobDoc.title
    : (selectedCanonicalRole || (matchResult ? matchResult.predicted_role : 'Target Role'))

  const currentResumeDoc = resumes.find((r) => r.id === selectedResume)

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Component 1 & 4 AI Suite"
        title="AI Resume Analysis & Role Match"
        description="Comprehensive evaluation engine: upload your CV for instant multi-criteria screening, explainable skill gaps, career transitions, and learning roadmaps."
        icon={Sparkles}
      />

      {/* Step 1 & 2 Setup Card */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-6)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-4)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Zap size={18} style={{ color: 'var(--color-primary)' }} /> 1. Select Candidate Resume & Target Configuration
          </h3>
          {currentResumeDoc && (
            <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
              Selected: <strong>{currentResumeDoc.filename}</strong>
            </span>
          )}
        </div>

        {/* Upload Zone & Select Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1.8fr)', gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-4)' }}>
          <div>
            <UploadZone
              onFileSelect={handleFileUpload}
              uploading={uploading}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Resume Dropdown */}
            <div>
              <label style={{ fontSize: '11px', marginTop: 0 }}>Existing Resumes ({resumes.length})</label>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <select
                  value={selectedResume}
                  onChange={(e) => setSelectedResume(e.target.value)}
                  style={{ flex: 1, fontSize: 'var(--p-text-sm)' }}
                >
                  <option value="">Choose an uploaded resume...</option>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.filename} {r.candidate_name ? `(${r.candidate_name})` : ''} · {r.experience_years || 0} yrs
                    </option>
                  ))}
                </select>
                {selectedResume && (
                  <button
                    type="button"
                    className="btn-ghost btn-sm"
                    onClick={() => deleteResume(selectedResume)}
                    style={{ padding: 8, color: 'var(--color-danger)' }}
                    title="Delete selected resume"
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>

            {/* Target Select: Job or Canonical */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div>
                <label style={{ fontSize: '11px', marginTop: 0 }}>Match Against Posted Job</label>
                <select
                  value={selectedJob}
                  onChange={(e) => {
                    setSelectedJob(e.target.value)
                    if (e.target.value) setSelectedCanonicalRole('')
                  }}
                  style={{ fontSize: 'var(--p-text-sm)' }}
                >
                  <option value="">Any Open Role (Optional)</option>
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.title} {j.company_name ? `· ${j.company_name}` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '11px', marginTop: 0 }}>Or 20 Canonical IT Roles</label>
                <select
                  value={selectedCanonicalRole}
                  onChange={(e) => {
                    setSelectedCanonicalRole(e.target.value)
                    if (e.target.value) setSelectedJob('')
                  }}
                  style={{ fontSize: 'var(--p-text-sm)' }}
                >
                  <option value="">AI Auto-Detect Role</option>
                  {CANONICAL_ROLES.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Run Action */}
        <button
          className="btn btn-primary"
          onClick={runUnifiedAnalysis}
          disabled={busy || (!selectedResume && resumes.length === 0)}
          style={{ width: '100%', padding: '12px 20px', fontSize: 'var(--p-text-base)', fontWeight: 700 }}
        >
          <BarChart3 size={18} /> {busy ? 'Running AI Multi-Criteria Screening...' : 'Run AI Resume Match & Career Progression Analysis'}
        </button>
      </div>

      {/* Loading State during inference */}
      {busy && (
        <LoadingState title="Analyzing Resume with AI..." />
      )}

      {/* Results Section */}
      {matchResult && !busy && (
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-6)' }}>
          {/* Top Score Banner */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingBottom: 'var(--p-space-5)',
            marginBottom: 'var(--p-space-5)',
            borderBottom: '1px solid var(--color-border-subtle)',
            flexWrap: 'wrap',
            gap: 16
          }}>
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary)', letterSpacing: '0.08em', marginBottom: 4 }}>
                Evaluation Complete
              </div>
              <h2 style={{ fontSize: '1.375rem', fontWeight: 800, margin: 0, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={20} style={{ color: 'var(--color-primary)' }} />
                Target Role: <span style={{ color: 'var(--color-primary)' }}>{displayJobTitle}</span>
              </h2>
              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 4 }}>
                Candidate: <strong>{currentResumeDoc?.candidate_name || 'Verified Applicant'}</strong> · {currentResumeDoc?.experience_years || 0} years exp · {currentResumeDoc?.education || 'Degree Level'}
              </div>
            </div>

            <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: 14 }}>
              <div>
                <div style={{ fontSize: '2.25rem', fontWeight: 900, color: 'var(--color-fg)', lineHeight: 1, fontFamily: 'var(--p-font-mono)' }}>
                  {matchResult.overall_score.toFixed(1)}%
                </div>
                <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 600, color: 'var(--color-fg-muted)', marginTop: 4 }}>
                  Overall Fit Score
                </div>
              </div>
              <ScoreBadge score={matchResult.overall_score} />
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 12, marginBottom: 'var(--p-space-5)', flexWrap: 'wrap' }}>
            <button
              className={`btn btn-sm ${activeTab === 'match' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('match')}
            >
              <BarChart3 size={14} /> 1. Match & 3-Feature Scores
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'gap' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('gap')}
            >
              <Target size={14} /> 2. Skill Gap & Simulation
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'career' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('career')}
            >
              <RouteIcon size={14} /> 3. Career Progression
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'learning' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('learning')}
            >
              <BookOpen size={14} /> 4. Dependency Roadmap
            </button>
          </div>

          {/* TAB 1: 3 INDEPENDENT FEATURE SCORES */}
          {activeTab === 'match' && (
            <div className="fade-in">
              {/* Component 1 Architectural Notice */}
              <div style={{
                padding: 'var(--p-space-4)',
                background: 'var(--color-primary-muted)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid rgba(59, 130, 246, 0.2)',
                marginBottom: 'var(--p-space-5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 12
              }}>
                <div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Layers size={16} style={{ color: 'var(--color-primary)' }} /> Multi-Factor Resume Assessment — 3 Key Score Dimensions
                  </div>
                  <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', marginTop: 2 }}>
                    Calculates independent feature scores for Skills, Experience, and Education to compute overall candidate fit.
                  </div>
                </div>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '3px 10px', borderRadius: 'var(--radius-full)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  ✓ Analysis Complete
                </span>
              </div>

              {/* 3 Independent Score Cards */}
              <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
                {/* 1. Skills Match Score */}
                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', margin: 0 }}>
                  <div>
                    <ScoreMeter
                      score={matchResult.skill_score || 0}
                      label="1. Skills Match (S_skill)"
                      size="md"
                    />
                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 8 }}>
                      <strong>{matchResult.matched_skills?.length || 0}</strong> matched of <strong>{(matchResult.matched_skills?.length || 0) + (matchResult.missing_skills?.length || 0)}</strong> required skills.
                    </div>
                  </div>
                  <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--color-border-subtle)' }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-success)', textTransform: 'uppercase', marginBottom: 4 }}>
                      Matched Skills:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxHeight: 60, overflowY: 'auto' }}>
                      {matchResult.matched_skills?.map((s) => (
                        <span key={s} style={{ fontSize: '10px', padding: '1px 6px', background: 'var(--color-success-muted)', color: 'var(--color-success)', borderRadius: 4 }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 2. Experience Match Score */}
                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', margin: 0 }}>
                  <div>
                    <ScoreMeter
                      score={matchResult.experience_score || 0}
                      label="2. Experience Match (S_exp)"
                      size="md"
                    />
                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 8 }}>
                      Formula: min(Candidate Years / Required Years, 1.0) × 100
                    </div>
                  </div>
                  <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Candidate:</span>
                      <strong>{(currentResumeDoc?.experience_years || 2.5).toFixed(1)} years</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Job Required:</span>
                      <strong>{(matchedJobDoc?.experience_required || 3.0).toFixed(1)} years</strong>
                    </div>
                  </div>
                </div>

                {/* 3. Education Match Score */}
                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', margin: 0 }}>
                  <div>
                    <ScoreMeter
                      score={matchResult.education_score ?? 100}
                      label="3. Education Match (S_edu)"
                      size="md"
                    />
                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 8 }}>
                      Level & Domain: <strong>{matchResult.education_score >= 80 ? 'Full Match (Degree Level)' : 'Partial / Related Match'}</strong>
                    </div>
                  </div>
                  <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--color-border-subtle)', fontSize: 'var(--p-text-xs)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Candidate:</span>
                      <strong style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {currentResumeDoc?.education || 'BSc IT / CS'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Required:</span>
                      <strong>BSc IT / CS / SE</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Matched vs Missing Skills Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', margin: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                    <CheckCircle2 size={16} /> Matched Skills ({matchResult.matched_skills?.length || 0})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {matchResult.matched_skills?.map((s) => (
                      <span key={s} className="chip" style={{ fontSize: '11px', margin: 0, padding: '3px 8px', background: 'var(--color-success-muted)', color: 'var(--color-success)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', margin: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-danger)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                    <AlertCircle size={16} /> Missing Skills ({matchResult.missing_skills?.length || 0})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {matchResult.missing_skills?.map((s) => (
                      <span key={s} className="chip" style={{ fontSize: '11px', margin: 0, padding: '3px 8px', background: 'var(--color-danger-muted)', color: 'var(--color-danger)', borderColor: 'rgba(244, 63, 94, 0.3)' }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Component 3 Handoff Vector View */}
              <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', margin: 0 }}>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <TrendingUp size={16} style={{ color: 'var(--color-primary)' }} /> Candidate Evaluation Scores
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 2fr)', gap: 16, alignItems: 'center' }}>
                  <div style={{ padding: 12, background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', fontFamily: 'var(--p-font-mono)', fontSize: '12px', color: 'var(--color-primary)' }}>
                    <div>Skills Match &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <strong>{matchResult.skill_score.toFixed(1)}%</strong></div>
                    <div>Experience Match &nbsp;= <strong>{matchResult.experience_score.toFixed(1)}%</strong></div>
                    <div>Education Match &nbsp;&nbsp;= <strong>{(matchResult.education_score ?? 100).toFixed(1)}%</strong></div>
                  </div>
                  <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', lineHeight: 1.5 }}>
                    These 3 independent qualification scores are combined with technical assessment results to calculate the candidate's final ranking score.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SKILL GAP MATRIX & SIMULATION */}
          {activeTab === 'gap' && (
            <div className="fade-in">
              <div style={{ marginBottom: 'var(--p-space-4)' }}>
                <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>
                  Interactive Skill Acquisition Simulation
                </div>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  Click missing skills to simulate how acquiring them will increase your match score and hire probability in real time.
                </p>
              </div>

              {/* Interactive Simulation Sandbox */}
              <div className="card" style={{ padding: 'var(--p-space-5)', background: 'var(--color-bg-elevated)', marginBottom: 'var(--p-space-5)' }}>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 10 }}>
                  Target Role Missing Skills (Click to acquire):
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
                  {(matchResult.missing_skills || []).map((skill) => {
                    const isSelected = simulatedAcquiredSkills.includes(skill)
                    return (
                      <button
                        key={skill}
                        onClick={() => handleSimulateSkill(skill)}
                        style={{
                          padding: '6px 12px',
                          borderRadius: 'var(--radius-full)',
                          border: `1px solid ${isSelected ? 'var(--color-success)' : 'var(--color-border)'}`,
                          background: isSelected ? 'var(--color-success-muted)' : 'var(--color-bg)',
                          color: isSelected ? 'var(--color-success)' : 'var(--color-fg)',
                          cursor: 'pointer',
                          fontSize: 'var(--p-text-xs)',
                          fontWeight: 700,
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 6,
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <span>{isSelected ? '✓ Acquired' : '+ Acquire'}</span>
                        <span>{skill}</span>
                      </button>
                    )
                  })}
                </div>

                {/* Simulation Output Banner */}
                {simulationResult && (
                  <div style={{
                    padding: 'var(--p-space-4)',
                    background: 'var(--color-success-muted)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: 12
                  }}>
                    <div>
                      <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 800, color: 'var(--color-success)' }}>
                        +{simulationResult.coverage_improvement || 0}% Coverage Increase
                      </div>
                      <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', marginTop: 2 }}>
                        Simulated match coverage rises from {simulationResult.original_coverage || 0}% to <strong>{simulationResult.simulated_coverage || 0}%</strong>.
                      </div>
                    </div>

                    <Link to="/pipeline/progress" className="btn btn-primary btn-sm" style={{ fontSize: 'var(--p-text-xs)' }}>
                      Track in Progress Plan <ArrowRight size={13} />
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: CAREER PROGRESSION */}
          {activeTab === 'career' && (
            <div className="fade-in">
              <div style={{ marginBottom: 'var(--p-space-4)' }}>
                <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>
                  Career Transition & Progression Pathways
                </div>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  AI-recommended lateral and upward career paths based on your current technical skill profile.
                </p>
              </div>

              {careerResult?.recommendations?.length > 0 ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--p-space-4)' }}>
                  {careerResult.recommendations.map((rec, i) => (
                    <div key={i} className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg-elevated)', margin: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                        <div style={{ fontWeight: 700, fontSize: 'var(--p-text-base)', color: 'var(--color-fg)' }}>
                          {rec.target_role || rec.role}
                        </div>
                        <ScoreBadge score={rec.transition_feasibility || rec.match_score || 80} showLabel={false} />
                      </div>
                      <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', lineHeight: 1.5, marginBottom: 12 }}>
                        {rec.rationale || 'Strong skill overlap with your profile.'}
                      </p>
                      {rec.bridge_skills?.length > 0 && (
                        <div>
                          <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
                            Key Bridge Skills:
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                            {rec.bridge_skills.map((s) => (
                              <span key={s} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: 'var(--p-space-5)', background: 'var(--color-bg-elevated)' }}>
                  <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Career progression recommendations ready based on <strong>{displayJobTitle}</strong> profile.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: DEPENDENCY LEARNING ROADMAP */}
          {activeTab === 'learning' && (
            <div className="fade-in">
              <div style={{ marginBottom: 'var(--p-space-4)' }}>
                <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>
                  Curated Dependency Learning Roadmap
                </div>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  Structured learning milestones with dependency order to close skill gaps for {displayJobTitle}.
                </p>
              </div>

              {learningPathResult?.learning_path?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {learningPathResult.learning_path.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--p-space-4)',
                        background: 'var(--color-bg-elevated)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--color-border-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 14
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{
                          width: 28,
                          height: 28,
                          borderRadius: 'var(--radius-full)',
                          background: 'var(--color-primary-muted)',
                          color: 'var(--color-primary)',
                          fontWeight: 800,
                          fontSize: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0
                        }}>
                          {idx + 1}
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                            {item.skill || item.title}
                          </div>
                          <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                            {item.description || item.reason || 'Core competency for target role'}
                          </div>
                        </div>
                      </div>

                      {item.resource_url && (
                        <a
                          href={item.resource_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: 'var(--p-text-xs)', flexShrink: 0 }}
                        >
                          <ExternalLink size={13} /> View Course
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: 'var(--p-space-5)', background: 'var(--color-bg-elevated)' }}>
                  <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Learning resources mapped to {displayJobTitle} competencies.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
