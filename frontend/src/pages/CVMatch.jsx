import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Upload, BarChart3, Trash2, Sparkles, CheckCircle2, AlertCircle,
  ArrowRight, Briefcase, Zap, Target, Route as RouteIcon, BookOpen, Layers,
  ExternalLink, ChevronRight, TrendingUp
} from 'lucide-react'
import { uResumeDelete, uResumeUpload, c0JobsAll, uResumeList, c0ResumeMatch, c1Analyze, c4SkillGap, c4SkillGapSimulate, c4CareerRec, c4LearningPath } from '../api'
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
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', action: null })

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
    } catch { toast.error('Simulation failed') }
  }

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) {
      navigate('/login/candidate')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [r1, r2] = await Promise.all([
        uResumeList(),
        c0JobsAll().catch(() => ({ data: [] })),
      ])
      const resumeList = r1.data || []
      setResumes(resumeList)
      setJobs(r2.data || [])
      if (resumeList.length > 0) {
        setSelectedResume((prev) => prev || resumeList[0].id)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
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
    if (!resumeToUse) return toast.error('Please upload a resume first')

    setBusy(true)
    setMatchResult(null)
    setC1Result(null)
    setSkillGapResult(null)
    setCareerResult(null)
    setLearningPathResult(null)

    try {
      const targetResumeDoc = resumes.find(res => res.id === resumeToUse) || {}
      const candidateSkills = targetResumeDoc.skills || []

      const matchedJobDoc = jobs.find(j => j.id === selectedJob)
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

      // 2. Parallel Fetch Component 4 Analysis (Skill Gap, Career Recommendations, Learning Path)
      const [gapRes, careerRes, pathRes] = await Promise.all([
        c4SkillGap({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
        c4CareerRec({ current_skills: candidateSkills, current_role: finalRole }).catch(() => null),
        c4LearningPath({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
      ])

      if (gapRes) setSkillGapResult(gapRes.data)
      if (careerRes) setCareerResult(careerRes.data)
      if (pathRes) setLearningPathResult(pathRes.data)

      // 3. Optional C1 Deep Analysis if raw text exists
      if (targetResumeDoc.raw_text) {
        try {
          const c1Res = await c1Analyze({
            candidate_id: targetResumeDoc.candidate_id || resumeToUse,
            candidate_name: targetResumeDoc.candidate_name || 'Candidate',
            raw_text: targetResumeDoc.raw_text,
            target_role: finalRole
          })
          if (c1Res.data) setC1Result(c1Res.data)
        } catch {}
      }

      toast.success(`Analysis Complete! Overall Fit: ${matchRes.data.overall_score.toFixed(1)}%`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setBusy(false)
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

  const matchedJobDoc = jobs.find(j => j.id === selectedJob)
  const displayJobTitle = matchedJobDoc
    ? matchedJobDoc.title
    : (selectedCanonicalRole || (matchResult ? matchResult.predicted_role : 'Target IT Role'))

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 1040, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="page-head" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Sparkles size={30} style={{ color: 'var(--accent)' }} /> CV Match, AI Screening & Career Progression
        </h1>
        <p className="muted" style={{ fontSize: 14 }}>
          Unified AI suite: Upload your CV to get instant match scoring, explainable skill gap priority, career progression paths, and dependency learning roadmaps.
        </p>
      </div>

      {/* Control Setup Card */}
      <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Zap size={18} style={{ color: 'var(--accent)' }} /> Match Setup & Target Configuration
          </h3>
          <label className="btn btn-ghost btn-sm" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, background: 'var(--bg)', border: '1px solid var(--border)' }}>
            <Upload size={14} /> {uploading ? 'Processing CV...' : 'Upload New Resume'}
            <input type="file" accept=".pdf,.docx,.doc,.txt" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 20 }}>
          {/* Resume Dropdown */}
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              My Resumes *
            </label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <select
                value={selectedResume}
                onChange={(e) => setSelectedResume(e.target.value)}
                style={{ flex: 1, padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 13 }}
              >
                <option value="">Select a resume...</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.filename} {r.candidate_name ? `(${r.candidate_name})` : ''}
                  </option>
                ))}
              </select>
              {selectedResume && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => deleteResume(selectedResume)}
                  style={{ padding: 8, color: 'var(--danger)' }}
                  title="Delete resume"
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          </div>

          {/* Posted Job Dropdown */}
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              Posted Company Job (Optional)
            </label>
            <select
              value={selectedJob}
              onChange={(e) => {
                setSelectedJob(e.target.value)
                if (e.target.value) setSelectedCanonicalRole('')
              }}
              style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 13 }}
            >
              <option value="">Any open company job...</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} {j.company_name ? `— ${j.company_name}` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Canonical Role Dropdown */}
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>
              Or Target IT Role (20 Canonical)
            </label>
            <select
              value={selectedCanonicalRole}
              onChange={(e) => {
                setSelectedCanonicalRole(e.target.value)
                if (e.target.value) setSelectedJob('')
              }}
              style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 13 }}
            >
              <option value="">AI Auto-Detect Role</option>
              {CANONICAL_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          className="btn"
          onClick={runUnifiedAnalysis}
          disabled={busy || (!selectedResume && resumes.length === 0)}
          style={{ width: '100%', padding: '14px', fontSize: 15, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, background: 'var(--color-primary)', color: 'var(--color-on-primary)' }}
        >
          <BarChart3 size={18} /> {busy ? 'Running AI Screening & Career Progression Analysis...' : 'Run AI CV Match & Unified Career Analysis'}
        </button>
      </div>

      {/* Unified Tabbed Output */}
      {matchResult && (
        <div className="fade-in card" style={{ padding: 28, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          {/* Top Overview Banner */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: 20, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1 }}>
                Unified AI Evaluation
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 800, marginTop: 4, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={22} style={{ color: 'var(--color-primary)' }} />
                Target Job Role: <span style={{ color: 'var(--accent)' }}>{displayJobTitle}</span>
              </h2>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: 'var(--accent)', lineHeight: 1 }}>
                {matchResult.overall_score.toFixed(1)}%
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginTop: 4 }}>
                Overall Fit Score
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--border)', paddingBottom: 12, marginBottom: 24 }}>
            <button
              className={`btn btn-sm ${activeTab === 'match' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('match')}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}
            >
              <BarChart3 size={15} /> 1. Match & Screening
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'gap' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('gap')}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}
            >
              <Target size={15} /> 2. Skill Gap Matrix
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'career' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('career')}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}
            >
              <RouteIcon size={15} /> 3. Career Progression
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'learning' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('learning')}
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13 }}
            >
              <BookOpen size={15} /> 4. Dependency Roadmap
            </button>
          </div>

          {/* TAB 1: AI MATCH & SCREENING (COMPONENT 1 INDEPENDENT SCORES) */}
          {activeTab === 'match' && (
            <div className="fade-in">
              <div style={{ marginBottom: 20, padding: 16, background: 'rgba(59, 130, 246, 0.06)', borderRadius: 10, border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <h3 style={{ fontSize: 16, fontWeight: 800, margin: 0, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Layers size={18} style={{ color: 'var(--accent)' }} /> Component 1 Assessment — 3 Independent Feature Scores
                    </h3>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
                      CV → Text & Entity Extraction → Job Requirement Engine → 3 Separate Feature Scores ($S_{`{skill}`}$, $S_{`{exp}`}$, $S_{`{edu}`}$) passed to Component 3.
                    </p>
                  </div>
                  <span className="chip" style={{ background: 'rgba(34, 197, 94, 0.15)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)', fontWeight: 700, fontSize: 12 }}>
                    ✓ Ready for Component 3
                  </span>
                </div>
              </div>

              {/* 3 Independent Score Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 24 }}>
                {/* 1. SKILLS MATCH SCORE */}
                <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 12, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>1. SKILLS MATCH (S_skill)</span>
                      <span style={{ fontSize: 18, fontWeight: 900, color: 'var(--color-success)' }}>{matchResult.skill_score?.toFixed(0) || 0} / 100</span>
                    </div>
                    <div style={{ width: '100%', height: 8, background: 'var(--border)', borderRadius: 4, overflow: 'hidden', marginBottom: 12 }}>
                      <div style={{ width: `${Math.min(100, matchResult.skill_score || 0)}%`, height: '100%', background: 'var(--color-success)', borderRadius: 4, transition: 'width 0.5s ease' }} />
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      <strong>{matchResult.matched_skills?.length || 0}</strong> matched of <strong>{(matchResult.matched_skills?.length || 0) + (matchResult.missing_skills?.length || 0)}</strong> required skills.
                    </div>
                  </div>
                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-success)', marginBottom: 4 }}>MATCHED SKILLS:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxHeight: 60, overflowY: 'auto' }}>
                      {matchResult.matched_skills?.map((s) => (
                        <span key={s} style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', borderRadius: 4, border: '1px solid rgba(34, 197, 94, 0.2)' }}>{s}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 2. EXPERIENCE MATCH SCORE */}
                <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 12, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>2. EXPERIENCE MATCH (S_exp)</span>
                      <span style={{ fontSize: 18, fontWeight: 900, color: 'var(--color-info)' }}>{matchResult.experience_score?.toFixed(0) || 0} / 100</span>
                    </div>
                    <div style={{ width: '100%', height: 8, background: 'var(--border)', borderRadius: 4, overflow: 'hidden', marginBottom: 12 }}>
                      <div style={{ width: `${Math.min(100, matchResult.experience_score || 0)}%`, height: '100%', background: 'var(--color-info)', borderRadius: 4, transition: 'width 0.5s ease' }} />
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      Ratio formula: min(Candidate Years / Required Years, 1.0) × 100
                    </div>
                  </div>
                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)', fontSize: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span className="muted">Candidate Experience:</span>
                      <strong>{(resumes.find(r => r.id === selectedResume)?.experience_years || 2.5).toFixed(1)} years</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span className="muted">Job Required Experience:</span>
                      <strong>{(matchedJobDoc?.experience_required || 3.0).toFixed(1)} years</strong>
                    </div>
                  </div>
                </div>

                {/* 3. EDUCATION MATCH SCORE */}
                <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 12, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>3. EDUCATION MATCH (S_edu)</span>
                      <span style={{ fontSize: 18, fontWeight: 900, color: 'var(--color-purple)' }}>{(matchResult.education_score ?? 100).toFixed(0)} / 100</span>
                    </div>
                    <div style={{ width: '100%', height: 8, background: 'var(--border)', borderRadius: 4, overflow: 'hidden', marginBottom: 12 }}>
                      <div style={{ width: `${Math.min(100, matchResult.education_score ?? 100)}%`, height: '100%', background: 'var(--color-purple)', borderRadius: 4, transition: 'width 0.5s ease' }} />
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      Level & Domain Relevance: <strong>{matchResult.education_score >= 80 ? 'Full Match (Degree Level)' : 'Partial / Related Match'}</strong>
                    </div>
                  </div>
                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)', fontSize: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span className="muted">Candidate Edu:</span>
                      <strong style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 120 }}>
                        {resumes.find(r => r.id === selectedResume)?.education || 'BSc IT / CS'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span className="muted">Required Degree:</span>
                      <strong>BSc IT / CS / SE</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Component 3 Integration Handoff View */}
              <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 12, border: '1px solid var(--border)', marginBottom: 24 }}>
                <h4 style={{ fontSize: 15, fontWeight: 700, margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text)' }}>
                  <TrendingUp size={18} style={{ color: 'var(--accent)' }} /> Component 3 Input Payload Handoff
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16, alignItems: 'center' }}>
                  <div style={{ padding: 14, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 6 }}>COMPONENT 1 OUTPUT VECTOR</div>
                    <div style={{ fontFamily: 'monospace', fontSize: 13, color: 'var(--accent)' }}>
                      S_skill = <strong>{matchResult.skill_score.toFixed(1)}</strong><br />
                      S_exp &nbsp;&nbsp;= <strong>{matchResult.experience_score.toFixed(1)}</strong><br />
                      S_edu &nbsp;&nbsp;= <strong>{(matchResult.education_score ?? 100).toFixed(1)}</strong>
                    </div>
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    <p style={{ margin: '0 0 6px 0' }}>
                      <strong style={{ color: 'var(--text)' }}>Architecture Guarantee:</strong> Component 1 calculates these 3 independent scores without collapsing them into a single final ranking score.
                    </p>
                    <p style={{ margin: 0 }}>
                      Component 3 consumes C_1 = &#123;S_skill, S_exp, S_edu&#125; alongside interview evaluation scores (P_mcq, P_desc, P_code) to produce the final weighted candidate ranking.
                    </p>
                  </div>
                </div>
              </div>

              {/* Matched vs Missing Skills breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
                <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                    <CheckCircle2 size={16} /> Matched Skills ({matchResult.matched_skills?.length || 0})
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {matchResult.matched_skills?.map((s) => (
                      <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--danger)' }}>
                    <AlertCircle size={16} /> Missing Skills ({matchResult.missing_skills?.length || 0})
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {matchResult.missing_skills?.map((s) => (
                      <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-danger)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SKILL GAP MATRIX */}
          {activeTab === 'gap' && (
            <div className="fade-in">
              <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)', marginBottom: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                  <h4 style={{ fontSize: 15, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Target size={18} style={{ color: 'var(--accent)' }} /> Skill Coverage & Priority Breakdown
                  </h4>
                  <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--accent)' }}>
                    Skill Coverage: {skillGapResult?.skill_coverage ?? matchResult.skill_score.toFixed(1)}%
                  </div>
                </div>

                {/* Missing Skills with Priority Scores & Simulation Checkboxes */}
                {skillGapResult?.missing_skills?.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
                      💡 Click missing skills below to simulate acquiring them in real-time:
                    </div>
                    {skillGapResult.missing_skills.map((item, idx) => {
                      const isSimulated = simulatedAcquiredSkills.includes(item.skill)
                      const pColor = item.priority === 'Critical' ? 'var(--color-danger)' : item.priority === 'High' ? 'var(--color-orange)' : item.priority === 'Medium' ? 'var(--color-warning)' : 'var(--color-success)'
                      return (
                        <div
                          key={idx}
                          onClick={() => handleSimulateSkill(item.skill)}
                          style={{
                            padding: '12px 16px',
                            background: isSimulated ? 'rgba(34, 197, 94, 0.08)' : 'var(--bg-elevated)',
                            borderRadius: 8,
                            border: isSimulated ? '1px solid var(--color-success)' : '1px solid var(--border)',
                            display: 'flex',
                            alignItems: 'center',
                            justify: 'space-between',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <input type="checkbox" checked={isSimulated} onChange={() => {}} style={{ cursor: 'pointer' }} />
                            <div>
                              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>
                                {item.skill} {isSimulated && <span style={{ color: 'var(--color-success)', fontSize: 12 }}>(Simulated Acquired)</span>}
                              </div>
                              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                                Priority Score: <strong>{item.priority_score}</strong> / 100
                              </div>
                            </div>
                          </div>
                          <span className="chip" style={{ fontSize: 12, padding: '4px 12px', background: `${pColor}15`, color: pColor, border: `1px solid ${pColor}40`, fontWeight: 700 }}>
                            {item.priority} Priority
                          </span>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: 'var(--color-success)' }}>All required skills satisfied!</div>
                )}
              </div>

              {/* Simulation Result Card */}
              {simulationResult && (
                <div style={{ padding: 20, background: 'rgba(34, 197, 94, 0.08)', borderRadius: 10, border: '1px solid rgba(34, 197, 94, 0.3)', marginBottom: 20 }}>
                  <div style={{ fontSize: 14, fontWeight: 800, color: 'var(--text)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Sparkles size={18} style={{ color: 'var(--color-success)' }} /> Interactive What-If Simulation Result
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Original Coverage</div>
                      <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text)' }}>{simulationResult.original_coverage}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Simulated Coverage</div>
                      <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--color-success)' }}>{simulationResult.simulated_coverage}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Boost Improvement</div>
                      <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--color-success)' }}>+{simulationResult.coverage_improvement}%</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CAREER PROGRESSION */}
          {activeTab === 'career' && (
            <div className="fade-in">
              {/* Vertical Growth Track */}
              <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)', marginBottom: 20 }}>
                <h4 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <TrendingUp size={18} style={{ color: 'var(--accent)' }} /> Vertical Progression Path ({displayJobTitle})
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                  {(careerResult?.vertical_progression || ['Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal']).map((level, i) => (
                    <div key={level} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="chip" style={{ padding: '8px 14px', fontSize: 13, fontWeight: 700, background: i === 1 ? 'var(--color-primary)' : 'var(--bg-elevated)', color: i === 1 ? 'var(--color-on-primary)' : 'var(--text)', border: '1px solid var(--border)' }}>
                        {level}
                      </span>
                      {i < 4 && <ChevronRight size={16} style={{ color: 'var(--text-muted)' }} />}
                    </div>
                  ))}
                </div>
              </div>

              {/* Lateral Role Transitions */}
              {careerResult?.recommendations?.length > 0 && (
                <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                  <h4 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Layers size={18} style={{ color: 'var(--accent)' }} /> Recommended Lateral Role Moves (Jaccard Match)
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                    {careerResult.recommendations.map((rec, idx) => (
                      <div key={idx} style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)' }}>{rec.role}</div>
                          <div style={{ fontSize: 14, fontWeight: 800, color: 'var(--accent)' }}>{rec.match_percentage}% Match</div>
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                          Missing: {rec.missing_skills?.slice(0, 3).join(', ') || 'None'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: DEPENDENCY ROADMAP */}
          {activeTab === 'learning' && (
            <div className="fade-in">
              <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
                <h4 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BookOpen size={18} style={{ color: 'var(--accent)' }} /> Step-by-Step Dependency Learning Sequence
                </h4>
                {learningPathResult?.learning_path?.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {learningPathResult.learning_path.map((stepItem) => (
                      <div key={stepItem.step} style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--color-primary)', color: 'var(--color-on-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14 }}>
                            {stepItem.step}
                          </div>
                          <div>
                            <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text)' }}>{stepItem.skill}</div>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                              Priority: <strong style={{ color: stepItem.priority === 'Critical' ? 'var(--color-danger)' : 'var(--color-orange)' }}>{stepItem.priority}</strong>
                            </div>
                          </div>
                        </div>
                        <a
                          href={`https://www.coursera.org/search?query=${encodeURIComponent(stepItem.skill)}`}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: 12, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 4 }}
                        >
                          Find Courses <ExternalLink size={12} />
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>No additional learning steps required.</div>
                )}
              </div>
            </div>
          )}

          {/* Action Footer */}
          <div style={{ display: 'flex', gap: 12, marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
            <button
              className="btn"
              onClick={() => navigate('/candidate/interview')}
              style={{ flex: 1, padding: '12px 16px', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
            >
              Take AI Mock Interview <ArrowRight size={14} />
            </button>
            <button
              className="btn btn-ghost"
              onClick={() => navigate('/candidate/jobs')}
              style={{ flex: 1, padding: '12px 16px', fontSize: 13, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
            >
              Browse Open Jobs <Briefcase size={14} />
            </button>
          </div>
        </div>
      )}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => { await confirm.action(); setConfirm({ ...confirm, open: false }) }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
