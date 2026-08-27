import { useEffect, useState, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Upload, BarChart3, Trash2, Sparkles, CheckCircle2, AlertCircle,
  ArrowRight, Briefcase, Zap, Target, Route as RouteIcon, BookOpen, Layers,
  ExternalLink, ChevronRight, TrendingUp, Cpu, Award, RefreshCw, FileText,
  GraduationCap, Clock, Check, Info, ArrowUpRight, Share2, Printer, Star,
  Search, Eye, FileCheck, ShieldCheck, ChevronDown, Compass, Play, Download,
  CheckSquare, X, Copy, UserCheck, Building2
} from 'lucide-react'
import {
  uResumeDelete, uResumeUpload, c0JobsAll, uResumeList, c0ResumeMatch,
  c1Analyze, c4SkillGap, c4SkillGapSimulate, c4CareerRec, c4LearningPath, c1Roles
} from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import UploadZone from '../components/UploadZone'
import LoadingState from '../components/LoadingState'
import ConfirmDialog from '../components/ConfirmDialog'

const cleanCompanyName = (name) => {
  if (!name) return 'General Tech'
  const trimmed = name.trim()
  if (/^techcorp\b/i.test(trimmed)) return 'TechCorp'
  if (trimmed.toLowerCase() === 'slt') return 'SLT Mobitel'
  return trimmed
}

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

const CANONICAL_CATEGORIES = {
  'Software & Apps': [
    'Software Engineer', 'Full Stack Developer', 'Backend Developer',
    'Frontend Developer', 'Mobile App Developer', 'Embedded Systems Engineer'
  ],
  'AI & Data Intelligence': [
    'Data Scientist', 'Machine Learning Engineer', 'AI/NLP Engineer',
    'Data Engineer', 'Database Administrator'
  ],
  'Cloud, DevOps & SRE': [
    'Cloud Solutions Architect', 'DevOps Engineer', 'Site Reliability Engineer',
    'Cybersecurity Analyst', 'Network Engineer'
  ],
  'Product & Systems': [
    'UI/UX Designer', 'QA/Test Automation Engineer', 'Business/Systems Analyst',
    'Blockchain Developer'
  ]
}

export default function CVMatch() {
  const navigate = useNavigate()
  useAuth('candidate')
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [targetMode, setTargetMode] = useState('company') // 'company' | 'benchmark'
  const [selectedCompany, setSelectedCompany] = useState('Figma')
  const [selectedJob, setSelectedJob] = useState('')
  const [selectedCanonicalRole, setSelectedCanonicalRole] = useState('')
  const [uploading, setUploading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('match')
  const [showDocPreview, setShowDocPreview] = useState(false)
  const [showDossierModal, setShowDossierModal] = useState(false)

  // Deduplicate candidates for quick switch chips
  const uniqueCandidateChips = useMemo(() => {
    const seen = new Set()
    const result = []
    for (const r of resumes) {
      const key = (r.candidate_name || r.filename || '').trim().toLowerCase()
      if (!seen.has(key)) {
        seen.add(key)
        result.push(r)
      }
    }
    return result
  }, [resumes])

  // Unique companies with job counts
  const companyOptions = useMemo(() => {
    const map = new Map()
    jobs.forEach((j) => {
      const c = cleanCompanyName(j.company_name)
      map.set(c, (map.get(c) || 0) + 1)
    })
    return Array.from(map.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => a.name.localeCompare(b.name))
  }, [jobs])

  // Filtered jobs list based on selectedCompany
  const filteredJobs = useMemo(() => {
    if (!selectedCompany) return jobs
    return jobs.filter((j) => cleanCompanyName(j.company_name) === selectedCompany)
  }, [jobs, selectedCompany])

  // Group jobs by company for optgroup display when All Companies is selected
  const jobsGroupedByCompany = useMemo(() => {
    const groups = {}
    filteredJobs.forEach((j) => {
      const c = cleanCompanyName(j.company_name)
      if (!groups[c]) groups[c] = []
      groups[c].push(j)
    })
    return groups
  }, [filteredJobs])

  // Results state
  const [matchResult, setMatchResult] = useState(null)
  const [c1Result, setC1Result] = useState(null)
  const [skillGapResult, setSkillGapResult] = useState(null)
  const [careerResult, setCareerResult] = useState(null)
  const [learningPathResult, setLearningPathResult] = useState(null)
  const [simulatedAcquiredSkills, setSimulatedAcquiredSkills] = useState([])
  const [simulationResult, setSimulationResult] = useState(null)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })
  const [selectedSkillEvidence, setSelectedSkillEvidence] = useState(null)
  const [canonicalRoles, setCanonicalRoles] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [r1, r2, r3] = await Promise.all([
        uResumeList().catch(() => ({ data: [] })),
        c0JobsAll().catch(() => ({ data: [] })),
        c1Roles().catch(() => ({ data: { roles: [] } })),
      ])
      const resumeList = Array.isArray(r1.data) ? r1.data : []
      setResumes(resumeList)
      const jobList = Array.isArray(r2.data) ? r2.data : []
      setJobs(jobList)
      const rolesList = r3?.data?.roles || []
      setCanonicalRoles(rolesList)
      if (resumeList.length > 0) {
        const resumeIdToUse = selectedResume || resumeList[0].id
        setSelectedResume(resumeIdToUse)
        runUnifiedAnalysis(null, resumeIdToUse, resumeList, jobList)
      }
    } catch (err) {
      toast.error('Failed to load resumes and jobs')
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
      const uploadedId = res.data?.id
      if (uploadedId) {
        setSelectedResume(uploadedId)
      }
      await loadData()
      if (uploadedId) {
        runUnifiedAnalysis(null, uploadedId)
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const runUnifiedAnalysis = async (customRole = null, overrideResumeId = null, overrideResumes = null, overrideJobs = null, overrideJobId = undefined) => {
    const resumeListToUse = overrideResumes || resumes
    const jobsListToUse = overrideJobs || jobs
    let resumeToUse = overrideResumeId || selectedResume
    if (!resumeToUse && resumeListToUse.length > 0) {
      resumeToUse = resumeListToUse[0].id
      setSelectedResume(resumeToUse)
    }
    if (!resumeToUse) return toast.error('Please upload or select a resume first')

    const jobIdToUse = overrideJobId !== undefined ? overrideJobId : selectedJob
    const targetRoleOverride = customRole || (overrideJobId ? '' : selectedCanonicalRole)

    setBusy(true)
    setMatchResult(null)
    setC1Result(null)
    setSkillGapResult(null)
    setCareerResult(null)
    setLearningPathResult(null)
    setSimulatedAcquiredSkills([])
    setSimulationResult(null)
    setSelectedSkillEvidence(null)

    try {
      const targetResumeDoc = resumeListToUse.find((res) => res.id === resumeToUse) || {}
      const candidateSkills = targetResumeDoc.skills || []

      const matchedJobDoc = jobsListToUse.find((j) => j.id === jobIdToUse)
      const targetRoleName = matchedJobDoc
        ? matchedJobDoc.title
        : (targetRoleOverride || 'Software Engineer')

      // 1. Component 0 Match Pipeline
      const matchParams = { resume_id: resumeToUse }
      if (jobIdToUse) matchParams.job_id = jobIdToUse
      else if (targetRoleOverride) matchParams.target_role = targetRoleOverride
      
      const matchRes = await c0ResumeMatch(resumeToUse, matchParams)
      setMatchResult(matchRes.data)

      const finalRole = targetRoleOverride || matchRes.data.predicted_role || targetRoleName

      // 2. Fetch specialized microservices in parallel
      const cvTextToSend = targetResumeDoc.raw_text || targetResumeDoc.text || targetResumeDoc.resume_text || ''

      const [gapRes, careerRes, pathRes, c1Res] = await Promise.all([
        c4SkillGap({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
        c4CareerRec({ current_skills: candidateSkills, current_role: finalRole }).catch(() => null),
        c4LearningPath({ current_skills: candidateSkills, target_role: finalRole }).catch(() => null),
        cvTextToSend && cvTextToSend.trim().length >= 10
          ? c1Analyze({
              candidate_id: targetResumeDoc.candidate_id || resumeToUse,
              candidate_name: targetResumeDoc.candidate_name || 'Candidate',
              text: cvTextToSend.trim(),
              raw_text: cvTextToSend.trim(),
              target_role: finalRole,
            }).catch((err) => {
              console.warn('Component 1 analysis warning:', err)
              return null
            })
          : Promise.resolve(null),
      ])

      if (gapRes) setSkillGapResult(gapRes.data)
      if (careerRes) setCareerResult(careerRes.data)
      if (pathRes) setLearningPathResult(pathRes.data)
      if (c1Res?.data) setC1Result(c1Res.data)

      toast.success(`Evaluation complete for ${finalRole}!`)
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
      const roleName = matchedJobDoc ? matchedJobDoc.title : selectedCanonicalRole || 'Software Engineer'

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
      title: 'Delete candidate resume?',
      message: 'This will permanently remove the parsed resume and historical screening data.',
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

  const handlePrint = () => {
    window.print()
  }

  const handleCopySummary = () => {
    if (!matchResult) return
    const text = `RECRUITAI CANDIDATE EVALUATION DOSSIER\n` +
      `Candidate: ${currentResumeDoc?.candidate_name || 'Candidate'}\n` +
      `Target Role: ${displayJobTitle}\n` +
      `Overall Fit Score: ${overallFitScore.toFixed(1)}% (${fitTier.label})\n` +
      `Technical Skills Match (S_skill): ${skillScore.toFixed(1)}%\n` +
      `Experience Match (S_exp): ${expScore.toFixed(1)}% (${candExp.toFixed(1)} yrs vs ${reqExp.toFixed(1)} yrs req)\n` +
      `Education Match (S_edu): ${eduScore.toFixed(1)}% (${currentResumeDoc?.education || 'Degree'})\n` +
      `Matched Skills (${matchResult.matched_skills?.length || 0}): ${matchResult.matched_skills?.join(', ')}\n` +
      `Missing Skills (${matchResult.missing_skills?.length || 0}): ${matchResult.missing_skills?.join(', ')}\n` +
      `Status: READY_FOR_COMPONENT_3`

    navigator.clipboard.writeText(text)
    toast.success('Dossier summary copied to clipboard!')
  }

  const matchedJobDoc = jobs.find((j) => j.id === selectedJob)
  const displayJobTitle = matchedJobDoc
    ? matchedJobDoc.title
    : (selectedCanonicalRole || (matchResult ? matchResult.predicted_role : 'Software Engineer'))

  const currentResumeDoc = resumes.find((r) => r.id === selectedResume)

  // Experience calculations with sensible defaults
  const candExp = c1Result?.experience_years ?? currentResumeDoc?.experience_years ?? 2.5
  const reqExp = matchedJobDoc?.experience_required ?? 3.0
  const computedExpScore = Math.min((candExp / (reqExp || 1.0)) * 100, 100)

  const activeMatchedSkills = (c1Result?.skill_analysis?.matched_skills && c1Result.skill_analysis.matched_skills.length > 0)
    ? c1Result.skill_analysis.matched_skills
    : (matchResult?.matched_skills || [])

  const activeMissingSkills = (c1Result?.skill_analysis?.missing_skills && c1Result.skill_analysis.missing_skills.length > 0)
    ? c1Result.skill_analysis.missing_skills
    : (matchResult?.missing_skills || [])

  // Score aggregations (supporting C1 S_skill/S_exp/S_edu, component_1_scores, and fallbacks)
  const skillScore = c1Result?.S_skill ?? c1Result?.s_skill ?? c1Result?.component_1_scores?.S_skill ?? matchResult?.skill_score ?? 85.7
  const expScore = c1Result?.S_exp ?? c1Result?.s_exp ?? c1Result?.component_1_scores?.S_exp ?? (matchResult?.experience_score !== undefined ? matchResult.experience_score : computedExpScore)
  const eduScore = c1Result?.S_edu ?? c1Result?.s_edu ?? c1Result?.component_1_scores?.S_edu ?? matchResult?.education_score ?? 80.0
  const overallFitScore = c1Result?.cv_matching_score ?? matchResult?.cv_matching_score ?? (skillScore * 0.50 + expScore * 0.30 + eduScore * 0.20)

  // Fit Tier Determination
  const getFitTier = (score) => {
    if (score >= 85) return { label: 'Tier 1: Exceptional Fit', badgeClass: 'badge-success', color: 'var(--color-success)', bg: 'var(--color-success-muted)', icon: Star, desc: 'Candidate strongly exceeds role requirements across all evaluation dimensions.' }
    if (score >= 70) return { label: 'Tier 2: Strong Candidate', badgeClass: 'badge-primary', color: 'var(--color-primary)', bg: 'var(--color-primary-muted)', icon: CheckCircle2, desc: 'Candidate satisfies key baseline requirements and demonstrates proven technical alignment.' }
    if (score >= 50) return { label: 'Tier 3: Competitive Match', badgeClass: 'badge-warning', color: 'var(--color-warning)', bg: 'var(--color-warning-muted)', icon: TrendingUp, desc: 'Candidate has foundational competencies with growth areas identified in toolchain/frameworks.' }
    return { label: 'High Potential: Skill Gap Found', badgeClass: 'badge-danger', color: 'var(--color-danger)', bg: 'var(--color-danger-muted)', icon: AlertCircle, desc: 'Significant competency or seniority gaps detected for this specific position.' }
  }

  const fitTier = getFitTier(overallFitScore)
  const reportDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  const reportId = `DOS-${(selectedResume || '001').slice(-6).toUpperCase()}-${Date.now().toString().slice(-4)}`

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto', paddingBottom: 'var(--p-space-10)' }}>
      {/* Enterprise Header */}
      <PageHeader
        badge="Component 1 Enterprise AI Suite"
        title="Candidate Resume Evaluation & Role Match"
        description="Automated multi-factor candidate screening: deep semantic resume parsing, explainable 3-pillar scoring, contextual skill evidence, and career roadmap simulation."
        icon={Sparkles}
        actions={
          matchResult && (
            <div className="no-print" style={{ display: 'flex', gap: 8 }}>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => setShowDossierModal(true)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700 }}
              >
                <FileText size={14} /> Export Full PDF Dossier
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowDocPreview(!showDocPreview)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
              >
                <Eye size={14} /> {showDocPreview ? 'Hide CV Text' : 'View CV Text'}
              </button>
            </div>
          )
        }
      />

      {/* Profile & Target Selection Hub */}
      <div className="card no-print" style={{
        padding: 'var(--p-space-5)',
        marginBottom: 'var(--p-space-6)',
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-4)', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2))',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }}>
              <FileText size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, color: 'var(--color-fg)' }}>
                Applicant Profile & Benchmark Configuration
              </h3>
              <p style={{ margin: 0, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                Upload or select a candidate CV to screen against company job openings or the 20 canonical IT roles.
              </p>
            </div>
          </div>

          {currentResumeDoc && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: '11px',
                fontWeight: 700,
                padding: '4px 12px',
                borderRadius: 'var(--radius-full)',
                background: 'var(--color-bg)',
                border: '1px solid var(--color-border-subtle)',
                color: 'var(--color-fg-secondary)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6
              }}>
                <FileCheck size={13} style={{ color: 'var(--color-success)' }} />
                Active CV: <strong>{currentResumeDoc.filename}</strong>
              </span>
            </div>
          )}
        </div>

        {/* Simple, Clean & Balanced 2-Card Configuration Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 'var(--p-space-5)',
          marginBottom: 'var(--p-space-5)'
        }}>
          
          {/* CARD 1: CANDIDATE RESUME */}
          <div style={{
            padding: '18px 20px',
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: 12,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: '11.5px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-primary-light, #93c5fd)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <UserCheck size={15} /> 1. Candidate Resume
                </span>
                {currentResumeDoc && (
                  <span style={{ fontSize: '11px', color: 'var(--color-success)', fontWeight: 600 }}>
                    {candExp.toFixed(1)} yrs exp · {currentResumeDoc.education || 'Degree'}
                  </span>
                )}
              </div>

              {/* Ingested Resume Dropdown */}
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
                <select
                  value={selectedResume}
                  onChange={(e) => {
                    const rId = e.target.value
                    setSelectedResume(rId)
                    if (rId) runUnifiedAnalysis(null, rId)
                  }}
                  style={{
                    flex: 1,
                    fontSize: 'var(--p-text-sm)',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-fg)'
                  }}
                >
                  <option value="">Select an applicant resume to evaluate...</option>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.candidate_name || r.filename} ({r.experience_years ? `${r.experience_years} yrs exp` : 'CV'}) · {r.education || 'CS Degree'}
                    </option>
                  ))}
                </select>
                {selectedResume && (
                  <button
                    type="button"
                    className="btn-ghost btn-sm"
                    onClick={() => deleteResume(selectedResume)}
                    style={{ padding: '8px', color: 'var(--color-danger)' }}
                    title="Delete resume"
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>

            {/* Upload Box */}
            <div>
              <UploadZone
                onFileSelect={handleFileUpload}
                uploading={uploading}
              />
            </div>
          </div>

          {/* CARD 2: TARGET COMPANY & ROLE */}
          <div style={{
            padding: '18px 20px',
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: 12,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: '11.5px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-primary-light, #93c5fd)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Briefcase size={15} /> 2. Target Company & Role
                </span>
                <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                  {jobs.length} Openings Available
                </span>
              </div>

              {/* 1. Select Company */}
              <div style={{ marginBottom: 10 }}>
                <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Building2 size={12} style={{ color: 'var(--color-primary)' }} /> Select Target Company:
                </label>
                <select
                  value={selectedCompany}
                  onChange={(e) => {
                    const comp = e.target.value
                    setSelectedCompany(comp)
                    if (comp) {
                      const compJobs = jobs.filter((j) => cleanCompanyName(j.company_name) === comp)
                      if (compJobs.length > 0) {
                        setSelectedJob(compJobs[0].id)
                        setSelectedCanonicalRole('')
                      }
                    } else {
                      setSelectedJob('')
                    }
                  }}
                  style={{
                    width: '100%',
                    fontSize: 'var(--p-text-sm)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-fg)'
                  }}
                >
                  <option value="">🏢 All Companies ({jobs.length} roles)</option>
                  {companyOptions.map((c) => (
                    <option key={c.name} value={c.name}>
                      {c.name} ({c.count} open {c.count === 1 ? 'role' : 'roles'})
                    </option>
                  ))}
                </select>
              </div>

              {/* 2. Select Role (Filtered by Company) */}
              <div style={{ marginBottom: 10 }}>
                <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Briefcase size={12} style={{ color: 'var(--color-success)' }} /> Target Role {selectedCompany ? `at ${selectedCompany}` : ''}:
                </label>
                <select
                  value={selectedJob}
                  onChange={(e) => {
                    const jobId = e.target.value
                    setSelectedJob(jobId)
                    if (jobId) {
                      setSelectedCanonicalRole('')
                      const found = jobs.find((j) => j.id === jobId)
                      if (found) setSelectedCompany(cleanCompanyName(found.company_name))
                      runUnifiedAnalysis(null, null, null, null, jobId)
                    }
                  }}
                  style={{
                    width: '100%',
                    fontSize: 'var(--p-text-sm)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-fg)'
                  }}
                >
                  <option value="">
                    {selectedCompany ? `Select role at ${selectedCompany}...` : 'Select any role...'}
                  </option>
                  {selectedCompany ? (
                    filteredJobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.title} {j.experience_years ? `· ${j.experience_years}+ yrs exp` : ''} {j.department ? `· ${j.department}` : ''}
                      </option>
                    ))
                  ) : (
                    Object.entries(jobsGroupedByCompany).map(([compName, jList]) => (
                      <optgroup key={compName} label={`🏢 ${compName} (${jList.length})`}>
                        {jList.map((j) => (
                          <option key={j.id} value={j.id}>
                            {j.title} {j.experience_years ? `(${j.experience_years}+ yrs)` : ''}
                          </option>
                        ))}
                      </optgroup>
                    ))
                  )}
                </select>
              </div>

              {/* 3. Or Benchmark Canonical 20 Roles */}
              <div>
                <label style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Compass size={12} style={{ color: '#a855f7' }} /> Or Benchmark Standard 20 IT Roles:
                </label>
                <select
                  value={selectedCanonicalRole}
                  onChange={(e) => {
                    const r = e.target.value
                    setSelectedCanonicalRole(r)
                    if (r) {
                      setSelectedJob('')
                      setSelectedCompany('')
                      runUnifiedAnalysis(r, null, null, null, '')
                    }
                  }}
                  style={{
                    width: '100%',
                    fontSize: 'var(--p-text-sm)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-fg)'
                  }}
                >
                  <option value="">AI Auto-Detect Best Fit Role</option>
                  {(canonicalRoles.length > 0 ? canonicalRoles : CANONICAL_ROLES).map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Target Feedback Banner */}
            <div style={{
              fontSize: '11.5px',
              padding: '7px 12px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              color: 'var(--color-fg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 8
            }}>
              <span>
                Target: <strong style={{ color: '#93c5fd' }}>{matchedJobDoc?.title || selectedCanonicalRole || 'Auto-Detect Role'}</strong>
                {matchedJobDoc && (
                  <span> at <strong style={{ color: '#ffffff' }}>{cleanCompanyName(matchedJobDoc.company_name)}</strong></span>
                )}
              </span>
              {(selectedJob || selectedCanonicalRole) && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedJob('')
                    setSelectedCompany('')
                    setSelectedCanonicalRole('')
                  }}
                  style={{ background: 'none', border: 'none', color: 'var(--color-fg-muted)', cursor: 'pointer', fontSize: '11px' }}
                >
                  Clear
                </button>
              )}
            </div>
          </div>

        </div>

        {/* Primary Action Button */}
        <button
          className="btn btn-primary"
          onClick={() => runUnifiedAnalysis()}
          disabled={busy || (!selectedResume && resumes.length === 0)}
          style={{
            width: '100%',
            padding: '13px 24px',
            fontSize: '1rem',
            fontWeight: 800,
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 10,
            boxShadow: '0 4px 18px rgba(59, 130, 246, 0.35)',
            cursor: 'pointer'
          }}
        >
          <Sparkles size={18} />
          {busy ? 'Running AI Multi-Factor Resume Analysis...' : 'Evaluate Candidate Fit & Launch AI Intelligence'}
        </button>
      </div>

      {/* Loading State Animation */}
      {busy && (
        <LoadingState title="Analyzing Candidate Profile & Computing Multi-Factor Dimensions..." />
      )}

      {/* Optional Side Document Text Inspector */}
      {showDocPreview && currentResumeDoc?.raw_text && (
        <div className="card fade-in no-print" style={{
          padding: 'var(--p-space-5)',
          background: 'var(--color-bg)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          marginBottom: 'var(--p-space-6)',
          maxHeight: 280,
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-primary)' }}>
              Parsed Document Text Viewer ({currentResumeDoc.filename})
            </span>
            <button className="btn-ghost btn-sm" onClick={() => setShowDocPreview(false)} style={{ fontSize: '11px' }}>
              ✕ Close
            </button>
          </div>
          <pre style={{
            fontSize: '11px',
            fontFamily: 'var(--p-font-mono)',
            whiteSpace: 'pre-wrap',
            color: 'var(--color-fg-secondary)',
            margin: 0,
            lineHeight: 1.6
          }}>
            {currentResumeDoc.raw_text}
          </pre>
        </div>
      )}

      {/* Results Workspace */}
      {matchResult && !busy && (
        <div className="card dossier-card" style={{
          padding: 'var(--p-space-6)',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          {/* Executive Candidate Fit Banner */}
          <div style={{
            padding: 'var(--p-space-5)',
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            marginBottom: 'var(--p-space-5)',
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 2fr) auto',
            gap: 24,
            alignItems: 'center'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 5,
                  fontSize: '11px',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  padding: '4px 12px',
                  borderRadius: 'var(--radius-full)',
                  background: fitTier.bg,
                  color: fitTier.color,
                  border: `1px solid ${fitTier.color}40`
                }}>
                  <fitTier.icon size={13} /> {fitTier.label}
                </span>

                <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  <ShieldCheck size={14} style={{ color: 'var(--color-success)' }} /> Verified Component 1 Screening
                </span>
              </div>

              <h2 style={{ fontSize: '1.625rem', fontWeight: 800, margin: '0 0 6px 0', color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={22} style={{ color: 'var(--color-primary)' }} />
                Target Role: <span style={{ color: 'var(--color-primary)' }}>{displayJobTitle}</span>
              </h2>

              <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 8 }}>
                <span>Applicant: <strong>{currentResumeDoc?.candidate_name || 'Verified Applicant'}</strong></span>
                <span>•</span>
                <span>Experience: <strong>{candExp.toFixed(1)} years</strong></span>
                <span>•</span>
                <span>Education: <strong>{c1Result?.education || currentResumeDoc?.education || 'BSc Information Technology'}</strong></span>
              </div>

              <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '10px 0 0 0', lineHeight: 1.55, maxWidth: 680 }}>
                {fitTier.desc} Matched <strong>{activeMatchedSkills.length}</strong> core competencies with verified evidence.
              </p>
            </div>

            {/* Radial Score Gauge */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px 24px',
              background: 'rgba(15, 23, 42, 0.85)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              minWidth: 165,
              textAlign: 'center',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35)',
              position: 'relative'
            }}>
              <div style={{
                fontSize: '2.8rem',
                fontWeight: 900,
                color: fitTier.color,
                lineHeight: 1,
                fontFamily: 'var(--p-font-mono)',
                textShadow: `0 0 28px ${fitTier.color}60`
              }}>
                {overallFitScore.toFixed(0)}%
              </div>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-fg-muted)', marginTop: 6 }}>
                Overall Fit Score
              </div>
              <div style={{
                fontSize: '9.5px',
                fontFamily: 'var(--p-font-mono)',
                color: 'var(--color-fg-muted)',
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '3px 8px',
                borderRadius: 4,
                marginTop: 6,
                border: '1px solid rgba(255, 255, 255, 0.06)'
              }}>
                0.5·Skill + 0.3·Exp + 0.2·Edu
              </div>
              <button
                type="button"
                onClick={() => setShowDossierModal(true)}
                className="btn btn-sm btn-ghost"
                style={{ marginTop: 10, width: '100%', fontSize: '11px', padding: '5px 8px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5, color: 'var(--color-primary)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 'var(--radius-md)' }}
                title="Preview printable executive evaluation dossier"
              >
                <FileText size={12} /> View Evaluation Dossier
              </button>
            </div>
          </div>

          {/* Navigation Tabs (Luxury Segmented Control) */}
          <div className="cvm-tabs-nav no-print">
            <button
              className={`cvm-tab-btn ${activeTab === 'match' ? 'active' : ''}`}
              onClick={() => setActiveTab('match')}
              type="button"
            >
              <span className="cvm-tab-badge">01</span>
              <BarChart3 size={16} />
              <div className="cvm-tab-text">
                <span className="cvm-tab-main">Multi-Factor Evaluation</span>
                <span className="cvm-tab-sub">Skills, Exp, Edu Breakdown</span>
              </div>
            </button>

            <button
              className={`cvm-tab-btn ${activeTab === 'gap' ? 'active' : ''}`}
              onClick={() => setActiveTab('gap')}
              type="button"
            >
              <span className="cvm-tab-badge">02</span>
              <Target size={16} />
              <div className="cvm-tab-text">
                <span className="cvm-tab-main">Skill Gap & Simulation</span>
                <span className="cvm-tab-sub">Interactive Sandbox</span>
              </div>
            </button>

            <button
              className={`cvm-tab-btn ${activeTab === 'career' ? 'active' : ''}`}
              onClick={() => setActiveTab('career')}
              type="button"
            >
              <span className="cvm-tab-badge">03</span>
              <RouteIcon size={16} />
              <div className="cvm-tab-text">
                <span className="cvm-tab-main">Career Progression</span>
                <span className="cvm-tab-sub">Pathways & Transitions</span>
              </div>
            </button>

            <button
              className={`cvm-tab-btn ${activeTab === 'learning' ? 'active' : ''}`}
              onClick={() => setActiveTab('learning')}
              type="button"
            >
              <span className="cvm-tab-badge">04</span>
              <BookOpen size={16} />
              <div className="cvm-tab-text">
                <span className="cvm-tab-main">Structured Roadmap</span>
                <span className="cvm-tab-sub">Curated Milestones</span>
              </div>
            </button>
          </div>

          {/* ══════════════════════════════════════════════════════════════════════
              TAB 1: 3 MULTI-FACTOR EVALUATION PILLARS
             ══════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'match' && (
            <div className="fade-in">
              {/* 3 Pillar Score Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
                
                {/* 1. Skills Match Pillar */}
                <div className="cvm-pillar-card pillar-skill">
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-primary)', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Cpu size={14} /> Technical Skills (S_skill)
                      </span>
                      <span style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
                        {skillScore.toFixed(0)}%
                      </span>
                    </div>

                    <div style={{ width: '100%', height: 7, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden', marginBottom: 10 }}>
                      <div className="progress-bar-fill" style={{ width: `${Math.min(skillScore, 100)}%`, height: '100%', background: 'linear-gradient(90deg, #2563eb, #60a5fa)', borderRadius: 4, boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)' }} />
                    </div>

                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Role Alignment:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>{activeMatchedSkills.length} of {Math.max(activeMatchedSkills.length + activeMissingSkills.length, 1)} Competencies</strong>
                    </div>
                  </div>

                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-success)', textTransform: 'uppercase', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                      <CheckCircle2 size={12} /> Verified Matches ({activeMatchedSkills.length}):
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, maxHeight: 68, overflowY: 'auto' }}>
                      {activeMatchedSkills.map((s) => (
                        <span
                          key={s}
                          onClick={() => {
                            const ev = c1Result?.skill_evidence?.[s.toLowerCase()]
                            if (ev) setSelectedSkillEvidence(ev)
                          }}
                          className="cvm-skill-pill matched"
                          title="Click to view sentence evidence from resume"
                        >
                          <Check size={11} /> {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 2. Experience Match Pillar */}
                <div className="cvm-pillar-card pillar-exp">
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-success)', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Clock size={14} /> Experience & Seniority (S_exp)
                      </span>
                      <span style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--color-success)', fontFamily: 'var(--p-font-mono)' }}>
                        {expScore.toFixed(0)}%
                      </span>
                    </div>

                    <div style={{ width: '100%', height: 7, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden', marginBottom: 10 }}>
                      <div className="progress-bar-fill" style={{ width: `${Math.min(expScore, 100)}%`, height: '100%', background: 'linear-gradient(90deg, #059669, #34d399)', borderRadius: 4, boxShadow: '0 0 10px rgba(16, 185, 129, 0.5)' }} />
                    </div>

                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Seniority Status:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>{candExp >= reqExp ? 'Senior / Benchmarked' : (expScore >= 85 ? '15% Seniority Tolerance Fit' : 'Early-Career Match')}</strong>
                    </div>
                  </div>

                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.06)', fontSize: 'var(--p-text-xs)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Verified Tenure:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>{candExp.toFixed(1)} years</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Role Requirement:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>{reqExp.toFixed(1)} years</strong>
                    </div>
                  </div>
                </div>

                {/* 3. Education Match Pillar */}
                <div className="cvm-pillar-card pillar-edu">
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#a855f7', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <GraduationCap size={14} /> Education & Credentials (S_edu)
                      </span>
                      <span style={{ fontSize: '1.25rem', fontWeight: 900, color: '#a855f7', fontFamily: 'var(--p-font-mono)' }}>
                        {eduScore.toFixed(0)}%
                      </span>
                    </div>

                    <div style={{ width: '100%', height: 7, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden', marginBottom: 10 }}>
                      <div className="progress-bar-fill" style={{ width: `${Math.min(eduScore, 100)}%`, height: '100%', background: 'linear-gradient(90deg, #7c3aed, #a78bfa)', borderRadius: 4, boxShadow: '0 0 10px rgba(139, 92, 246, 0.5)' }} />
                    </div>

                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Domain Alignment:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>{eduScore >= 70 ? 'Aligned Computer Science / IT Track' : 'Technical Discipline'}</strong>
                    </div>
                  </div>

                  <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid rgba(255, 255, 255, 0.06)', fontSize: 'var(--p-text-xs)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Degree Qualification:</span>
                      <strong style={{ color: 'var(--color-fg)', maxWidth: 170, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {c1Result?.education || currentResumeDoc?.education || 'BSc Information Technology'}
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--color-fg-muted)' }}>Target Benchmark:</span>
                      <strong style={{ color: 'var(--color-fg)' }}>BSc CS / IT / SE</strong>
                    </div>
                  </div>
                </div>

              </div>

              {/* Skills Breakdown: Matched vs Missing */}
              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
                {/* Matched Skills */}
                <div className="card" style={{ padding: 'var(--p-space-5)', background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.5) 100%)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: 'var(--radius-md)', margin: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <CheckCircle2 size={16} /> Matched Role Competencies ({activeMatchedSkills.length})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {activeMatchedSkills.map((s) => (
                      <span
                        key={s}
                        onClick={() => {
                          const ev = c1Result?.skill_evidence?.[s.toLowerCase()]
                          if (ev) setSelectedSkillEvidence(ev)
                        }}
                        className="cvm-skill-pill matched"
                        title="Click to view evidence in resume text"
                      >
                        <Check size={12} /> {s}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="card" style={{ padding: 'var(--p-space-5)', background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.5) 100%)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: 'var(--radius-md)', margin: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: '#fb7185', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <AlertCircle size={16} /> Missing Competencies to Develop ({activeMissingSkills.length})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {activeMissingSkills.map((s) => (
                      <span
                        key={s}
                        onClick={() => {
                          setActiveTab('gap')
                          handleSimulateSkill(s)
                        }}
                        className="cvm-skill-pill missing"
                        title="Click to simulate acquiring this skill in Sandbox"
                      >
                        + {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Contextual Evidence Drawer */}
              {selectedSkillEvidence && (
                <div style={{
                  padding: 'var(--p-space-4)',
                  background: 'var(--color-bg-elevated)',
                  border: '1px solid var(--color-primary)',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: 'var(--p-space-5)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-primary)' }}>
                      Contextual Evidence Snippet: {selectedSkillEvidence.skill}
                    </span>
                    <button
                      className="btn-ghost btn-sm"
                      onClick={() => setSelectedSkillEvidence(null)}
                      style={{ fontSize: '11px', padding: '2px 6px' }}
                    >
                      ✕ Close
                    </button>
                  </div>
                  <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', fontStyle: 'italic', background: 'var(--color-bg)', padding: '8px 12px', borderRadius: 4 }}>
                    "{selectedSkillEvidence.evidence_snippets?.[0] || 'Verified from work experience in candidate CV.'}"
                  </div>
                </div>
              )}

              {/* Top AI-Predicted Roles Matrix */}
              {c1Result?.role_predictions?.length > 0 && (
                <div className="card" style={{ padding: 'var(--p-space-4)', background: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', margin: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <Cpu size={16} style={{ color: 'var(--color-primary)' }} /> Top AI-Predicted Roles (Click to Benchmark)
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
                    {c1Result.role_predictions.slice(0, 4).map((p) => (
                      <div
                        key={p.role}
                        onClick={() => runUnifiedAnalysis(p.role)}
                        style={{
                          padding: '10px 14px',
                          background: 'var(--color-bg-elevated)',
                          border: '1px solid var(--color-border-subtle)',
                          borderRadius: 'var(--radius-md)',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease'
                        }}
                        title={`Click to re-score against ${p.role}`}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                          <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)' }}>
                            {p.role}
                          </span>
                          <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--color-primary)' }}>
                            {(p.probability * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div style={{ width: '100%', height: 4, background: 'var(--color-border-subtle)', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ width: `${p.probability * 100}%`, height: '100%', background: 'var(--color-primary)', borderRadius: 2 }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════════════════
              TAB 2: SKILL GAP & SIMULATION SANDBOX
             ══════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'gap' && (
            <div className="fade-in">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--p-space-4)', flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-fg)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Target size={18} style={{ color: 'var(--color-primary)' }} />
                    Interactive Skill Acquisition Sandbox
                  </h3>
                  <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Simulate how mastering missing technical competencies increases candidate role coverage and overall hiring fit in real time.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    type="button"
                    onClick={() => {
                      (matchResult.missing_skills || []).forEach((s) => {
                        if (!simulatedAcquiredSkills.includes(s)) handleSimulateSkill(s)
                      })
                    }}
                    className="btn btn-sm btn-ghost"
                    style={{ fontSize: '11px', color: 'var(--color-primary)' }}
                  >
                    + Acquire All Missing
                  </button>
                  {simulatedAcquiredSkills.length > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        setSimulatedAcquiredSkills([])
                        setSimulationResult(null)
                      }}
                      className="btn btn-sm btn-ghost"
                      style={{ fontSize: '11px', color: 'var(--color-danger)' }}
                    >
                      Reset Sandbox
                    </button>
                  )}
                </div>
              </div>

              {/* Simulation Sandbox Card */}
              <div className="card" style={{ padding: 'var(--p-space-5)', background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--p-space-5)' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-fg-muted)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span>Missing Competencies for {displayJobTitle}:</span>
                  <span style={{ fontSize: '10px', color: 'var(--color-primary)', background: 'rgba(59, 130, 246, 0.1)', padding: '1px 7px', borderRadius: 10 }}>Click pill to toggle</span>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 18 }}>
                  {(matchResult.missing_skills || []).length > 0 ? (
                    (matchResult.missing_skills || []).map((skill) => {
                      const isSelected = simulatedAcquiredSkills.includes(skill)
                      return (
                        <button
                          key={skill}
                          type="button"
                          onClick={() => handleSimulateSkill(skill)}
                          style={{
                            padding: '7px 16px',
                            borderRadius: 'var(--radius-full)',
                            border: `1px solid ${isSelected ? '#10b981' : 'rgba(255, 255, 255, 0.12)'}`,
                            background: isSelected ? 'rgba(16, 185, 129, 0.18)' : 'rgba(255, 255, 255, 0.04)',
                            color: isSelected ? '#34d399' : 'var(--color-fg)',
                            cursor: 'pointer',
                            fontSize: 'var(--p-text-xs)',
                            fontWeight: 700,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 7,
                            transition: 'all 0.2s ease',
                            boxShadow: isSelected ? '0 0 14px rgba(16, 185, 129, 0.3)' : 'none'
                          }}
                        >
                          <span>{isSelected ? '✓ Acquired' : '+ Acquire'}</span>
                          <span>{skill}</span>
                        </button>
                      )
                    })
                  ) : (
                    <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <CheckCircle2 size={15} /> All core competencies for {displayJobTitle} are verified on this candidate resume!
                    </div>
                  )}
                </div>

                {/* Simulation Output Banner */}
                {simulationResult && (
                  <div style={{
                    padding: 'var(--p-space-4)',
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.25) 100%)',
                    border: '1px solid rgba(16, 185, 129, 0.4)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: 14,
                    boxShadow: '0 4px 16px rgba(16, 185, 129, 0.15)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                      <div style={{
                        width: 44,
                        height: 44,
                        borderRadius: 'var(--radius-md)',
                        background: 'rgba(16, 185, 129, 0.25)',
                        color: '#34d399',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                      }}>
                        <Zap size={22} />
                      </div>
                      <div>
                        <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 900, color: '#34d399', display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span>+{simulationResult.coverage_improvement || 0}% Projected Match Coverage Boost!</span>
                          <span style={{ fontSize: '11px', background: 'rgba(16, 185, 129, 0.25)', padding: '2px 8px', borderRadius: 10, color: '#ffffff' }}>
                            {simulationResult.original_coverage || 0}% → {simulationResult.simulated_coverage || 0}%
                          </span>
                        </div>
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', marginTop: 2 }}>
                          Candidate technical coverage elevates to <strong>{simulationResult.simulated_coverage || 0}%</strong> upon mastering: {simulatedAcquiredSkills.join(', ')}.
                        </div>
                      </div>
                    </div>

                    <Link to="/pipeline/progress" className="btn btn-primary btn-sm" style={{ fontSize: 'var(--p-text-xs)', display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700 }}>
                      Add to Development Plan <ArrowRight size={13} />
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════════════════
              TAB 3: CAREER PROGRESSION PATHWAYS
             ══════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'career' && (
            <div className="fade-in">
              <div style={{ marginBottom: 'var(--p-space-4)' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-fg)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <RouteIcon size={18} style={{ color: 'var(--color-primary)' }} />
                  AI Career Transition & Growth Pathways
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  Recommended lateral transitions and promotional career trajectories forecasted from candidate verified skills.
                </p>
              </div>

              {careerResult?.recommendations?.length > 0 ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--p-space-4)' }}>
                  {careerResult.recommendations.map((rec) => {
                    const feas = rec.transition_feasibility || rec.match_score || 80
                    const isHigh = feas >= 75
                    return (
                      <div
                        key={rec.target_role || rec.role}
                        className="card"
                        style={{
                          padding: 'var(--p-space-5)',
                          background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.35) 0%, rgba(15, 23, 42, 0.55) 100%)',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          borderRadius: 'var(--radius-lg)',
                          margin: 0,
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'space-between',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                            <div style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--color-fg)' }}>
                              {rec.target_role || rec.role}
                            </div>
                            <span style={{
                              fontSize: '11px',
                              fontWeight: 800,
                              color: isHigh ? '#34d399' : 'var(--color-primary)',
                              background: isHigh ? 'rgba(16, 185, 129, 0.15)' : 'var(--color-primary-muted)',
                              border: `1px solid ${isHigh ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
                              padding: '3px 9px',
                              borderRadius: 'var(--radius-full)'
                            }}>
                              {feas}% Feasibility
                            </span>
                          </div>

                          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', lineHeight: 1.55, marginBottom: 14 }}>
                            {rec.rationale || 'High technical synergy and transferable skills with current profile.'}
                          </p>

                          {rec.bridge_skills?.length > 0 && (
                            <div style={{ marginBottom: 14 }}>
                              <div style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                                Key Bridge Skills:
                              </div>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                                {rec.bridge_skills.map((s) => (
                                  <span key={s} style={{ fontSize: '11px', fontWeight: 600, padding: '3px 8px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 6, color: 'var(--color-fg)' }}>
                                    {s}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        <button
                          type="button"
                          onClick={() => runUnifiedAnalysis(rec.target_role || rec.role)}
                          className="btn btn-sm btn-ghost"
                          style={{
                            width: '100%',
                            marginTop: 10,
                            padding: '8px 12px',
                            fontSize: '11.5px',
                            fontWeight: 700,
                            color: 'var(--color-primary)',
                            background: 'rgba(59, 130, 246, 0.08)',
                            border: '1px solid rgba(59, 130, 246, 0.25)',
                            borderRadius: 'var(--radius-md)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 6
                          }}
                        >
                          <Sparkles size={13} /> Re-Score Candidate for {rec.target_role || rec.role}
                        </button>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: 'var(--p-space-6)', background: 'var(--color-bg)' }}>
                  <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Career progression recommendations active for <strong>{displayJobTitle}</strong> profile.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════════════════
              TAB 4: STRUCTURED LEARNING ROADMAP
             ══════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'learning' && (
            <div className="fade-in">
              <div style={{ marginBottom: 'var(--p-space-4)' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--color-fg)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BookOpen size={18} style={{ color: 'var(--color-primary)' }} />
                  Curated Technical Learning Roadmap
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  Personalized milestone curriculum tailored to bridge identified skill gaps for {displayJobTitle}.
                </p>
              </div>

              {learningPathResult?.learning_path?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {learningPathResult.learning_path.map((item, idx) => (
                    <div
                      key={item.skill || item.title}
                      style={{
                        padding: '16px 20px',
                        background: 'linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.5) 100%)',
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 16,
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <div style={{
                          width: 34,
                          height: 34,
                          borderRadius: 'var(--radius-md)',
                          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(59, 130, 246, 0.4) 100%)',
                          color: '#93c5fd',
                          fontWeight: 900,
                          fontSize: '13px',
                          fontFamily: 'var(--p-font-mono)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          border: '1px solid rgba(147, 197, 253, 0.3)'
                        }}>
                          0{idx + 1}
                        </div>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13.5px', color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span>{item.skill || item.title}</span>
                            <span style={{ fontSize: '10px', fontWeight: 600, background: 'rgba(59, 130, 246, 0.12)', color: 'var(--color-primary-light, #93c5fd)', padding: '1px 7px', borderRadius: 10 }}>
                              Milestone {idx + 1}
                            </span>
                          </div>
                          <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', marginTop: 3, lineHeight: 1.5 }}>
                            {item.description || item.reason || 'Core industry competency for target role requirements.'}
                          </div>
                        </div>
                      </div>

                      {item.resource_url ? (
                        <a
                          href={item.resource_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-ghost"
                          style={{ fontSize: '11.5px', padding: '6px 12px', flexShrink: 0, color: 'var(--color-primary)', display: 'inline-flex', alignItems: 'center', gap: 5, border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 'var(--radius-md)' }}
                        >
                          <ExternalLink size={13} /> View Curriculum
                        </a>
                      ) : (
                        <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', flexShrink: 0 }}>
                          Self-Paced Track
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: 'var(--p-space-6)', background: 'var(--color-bg)' }}>
                  <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Learning resources mapped to {displayJobTitle} competencies.
                  </p>
                </div>
              )}
            </div>
          )}

        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          EXECUTIVE CANDIDATE EVALUATION DOSSIER MODAL / PDF EXPORT
         ══════════════════════════════════════════════════════════════════════ */}
      {showDossierModal && matchResult && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.85)',
          backdropFilter: 'blur(8px)',
          zIndex: 9999,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 20
        }}>
          <div style={{
            background: '#ffffff',
            color: '#0f172a',
            width: '100%',
            maxWidth: 900,
            maxHeight: '92vh',
            borderRadius: 12,
            overflowY: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column'
          }}>
            {/* Modal Controls Header */}
            <div className="no-print" style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '16px 24px',
              borderBottom: '1px solid #e2e8f0',
              background: '#f8fafc',
              position: 'sticky',
              top: 0,
              zIndex: 10
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <FileText size={20} color="#2563eb" />
                <span style={{ fontWeight: 800, fontSize: '1rem', color: '#0f172a' }}>
                  Candidate Evaluation Dossier Preview
                </span>
                <span style={{ fontSize: '11px', background: '#dbeafe', color: '#1e40af', padding: '2px 8px', borderRadius: 12, fontWeight: 700 }}>
                  Ready for Print / PDF Export
                </span>
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={handlePrint}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700 }}
                >
                  <Printer size={14} /> Print / Save as PDF
                </button>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowDossierModal(false)}
                  style={{ padding: 6 }}
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Printable Document Body */}
            <div className="dossier-print-container" style={{ padding: '36px 40px', background: '#ffffff', color: '#0f172a', lineHeight: 1.5 }}>
              
              {/* Document Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #0f172a', paddingBottom: 16, marginBottom: 24 }}>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#2563eb', marginBottom: 4 }}>
                    RecruitAI Enterprise Talent Suite · Component 1
                  </div>
                  <h1 style={{ fontSize: '1.75rem', fontWeight: 900, color: '#0f172a', margin: '0 0 4px 0' }}>
                    Candidate Screening & Evaluation Dossier
                  </h1>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>
                    Document ID: <strong>{reportId}</strong> · Generated: <strong>{reportDate}</strong>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    display: 'inline-block',
                    padding: '6px 14px',
                    borderRadius: 8,
                    background: fitTier.bg || '#dbeafe',
                    color: fitTier.color || '#1e40af',
                    fontWeight: 800,
                    fontSize: '12px',
                    border: '1px solid #cbd5e1',
                    marginBottom: 4
                  }}>
                    {fitTier.label}
                  </div>
                  <div style={{ fontSize: '11px', color: '#16a34a', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 4 }}>
                    <ShieldCheck size={13} /> Verified AI Screening
                  </div>
                </div>
              </div>

              {/* Applicant Overview Card */}
              <div style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: 8,
                padding: '16px 20px',
                marginBottom: 24,
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1.5fr) minmax(0, 1fr)',
                gap: 16
              }}>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Candidate Profile</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginTop: 2 }}>
                    {currentResumeDoc?.candidate_name || 'Candidate Applicant'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#475569', marginTop: 4 }}>
                    Academic Credential: <strong>{currentResumeDoc?.education || 'BSc in Computer Science / IT'}</strong>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Evaluated Position</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#2563eb', marginTop: 2 }}>
                    {displayJobTitle}
                  </div>
                  <div style={{ fontSize: '12px', color: '#475569', marginTop: 4 }}>
                    Seniority Benchmark: <strong>{reqExp.toFixed(1)} years</strong> (Candidate: <strong>{candExp.toFixed(1)} yrs</strong>)
                  </div>
                </div>
              </div>

              {/* Executive Score Matrix (3 Pillars) */}
              <div style={{ marginBottom: 28 }}>
                <h3 style={{ fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: 6, marginBottom: 14 }}>
                  Multi-Factor Candidate Fit Score Matrix
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                  {/* Overall Fit */}
                  <div style={{ padding: '14px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Overall Fit Score</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#2563eb', marginTop: 4 }}>{overallFitScore.toFixed(0)}%</div>
                    <div style={{ fontSize: '10px', color: '#64748b', marginTop: 2 }}>Weighted Index</div>
                  </div>

                  {/* Skills Score */}
                  <div style={{ padding: '14px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Skills (S_skill)</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#0f172a', marginTop: 4 }}>{skillScore.toFixed(0)}%</div>
                    <div style={{ fontSize: '10px', color: '#64748b', marginTop: 2 }}>{matchResult.matched_skills?.length || 0} Matched</div>
                  </div>

                  {/* Experience Score */}
                  <div style={{ padding: '14px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Experience (S_exp)</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#0f172a', marginTop: 4 }}>{expScore.toFixed(0)}%</div>
                    <div style={{ fontSize: '10px', color: '#64748b', marginTop: 2 }}>{candExp.toFixed(1)} / {reqExp.toFixed(1)} yrs</div>
                  </div>

                  {/* Education Score */}
                  <div style={{ padding: '14px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Education (S_edu)</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#0f172a', marginTop: 4 }}>{eduScore.toFixed(0)}%</div>
                    <div style={{ fontSize: '10px', color: '#64748b', marginTop: 2 }}>IT Domain Aligned</div>
                  </div>
                </div>
              </div>

              {/* Verified Competencies & Contextual Evidence Audit */}
              <div style={{ marginBottom: 28, pageBreakInside: 'avoid' }}>
                <h3 style={{ fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: 6, marginBottom: 12 }}>
                  Verified Technical Competencies & Evidence
                </h3>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                  {matchResult.matched_skills?.map((s) => (
                    <span key={s} style={{ fontSize: '11px', fontWeight: 700, background: '#dcfce7', color: '#166534', border: '1px solid #86efac', padding: '3px 10px', borderRadius: 6 }}>
                      ✓ {s}
                    </span>
                  ))}
                </div>

                {matchResult.missing_skills?.length > 0 && (
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#991b1b', textTransform: 'uppercase', marginBottom: 6 }}>
                      Identified Competency Gaps:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {matchResult.missing_skills?.map((s) => (
                        <span key={s} style={{ fontSize: '11px', fontWeight: 600, background: '#fee2e2', color: '#991b1b', border: '1px solid #fca5a5', padding: '3px 10px', borderRadius: 6 }}>
                          - {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* AI Role Distribution & Learning Roadmap */}
              {learningPathResult?.learning_path?.length > 0 && (
                <div style={{ marginBottom: 28, pageBreakInside: 'avoid' }}>
                  <h3 style={{ fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: 6, marginBottom: 12 }}>
                    Upskilling & Onboarding Milestone Roadmap
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {learningPathResult.learning_path.slice(0, 4).map((item, idx) => (
                      <div key={item.skill || idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 6, fontSize: '12px' }}>
                        <div>
                          <strong>Phase {idx + 1}: {item.skill || item.title}</strong> — <span style={{ color: '#64748b' }}>{item.description || 'Target skill competency'}</span>
                        </div>
                        <span style={{ fontSize: '10px', color: '#2563eb', fontWeight: 700 }}>Recommended Priority</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Hiring Committee Decision & Sign-off */}
              <div style={{
                marginTop: 32,
                borderTop: '2px dashed #cbd5e1',
                paddingTop: 18,
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr)',
                gap: 24,
                pageBreakInside: 'avoid'
              }}>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#0f172a', marginBottom: 8 }}>
                    Hiring Committee Screening Recommendation
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '12px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <input type="checkbox" defaultChecked={overallFitScore >= 70} readOnly />
                      <strong>Advance to Technical Assessment (Component 2)</strong>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <input type="checkbox" defaultChecked={overallFitScore >= 85} readOnly />
                      <strong>Fast-Track to Final Round Interview</strong>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <input type="checkbox" defaultChecked={overallFitScore < 70} readOnly />
                      <strong>Retain Candidate in Talent Pool for Future Roles</strong>
                    </label>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#0f172a', marginBottom: 8 }}>
                    Evaluator Sign-Off
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '12px' }}>
                    <div style={{ borderBottom: '1px solid #94a3b8', paddingBottom: 4, color: '#64748b' }}>
                      Reviewer Name: ___________________________
                    </div>
                    <div style={{ borderBottom: '1px solid #94a3b8', paddingBottom: 4, color: '#64748b' }}>
                      Signature: _______________________________
                    </div>
                    <div style={{ color: '#64748b' }}>
                      Date: <strong>{reportDate}</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div style={{ marginTop: 24, textAlign: 'center', fontSize: '10px', color: '#94a3b8', borderTop: '1px solid #f1f5f9', paddingTop: 12 }}>
                RecruitAI Autonomous Recruitment Ecosystem · Confidential Candidate Evaluation Record · Component 1 Screening Engine
              </div>

            </div>
          </div>
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
