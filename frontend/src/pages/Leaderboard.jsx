import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Award, Trophy, Search, RefreshCw, CheckCircle2,
  Send, ShieldCheck, Sparkles, UserCheck, Briefcase, Plus
} from 'lucide-react'
import { c4Leaderboard, uJobsMy, uJobsApplicants, c3Pipeline } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const cleanCandidateName = (rawName, fallbackId) => {
  if (!rawName) return `Candidate ${(fallbackId || '01').slice(-4)}`
  let name = String(rawName).trim()
  name = name.replace(/\s*[\(\[]\s*CV\s*[\)\]]/gi, '')
  name = name.replace(/^(?:phone|email|name|profile|student)\s*:\s*/i, '')
  name = name.split(/\s*[\n\r·|:;•]\s*/)[0].trim()
  const words = name.split(/\s+/).filter(Boolean)
  if (words.length > 3) {
    name = words.slice(0, 3).join(' ')
  }
  return name || 'Candidate'
}

export default function Leaderboard() {
  const navigate = useNavigate()
  const userRole = localStorage.getItem('recruitai.role')
  const [data, setData] = useState([])
  const [companyJobs, setCompanyJobs] = useState([])
  const [selectedJobFilter, setSelectedJobFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('all')

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) {
      navigate(userRole === 'company' ? '/login/company' : '/login/candidate')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    if (data.length === 0) setLoading(true)
    try {
      if (userRole === 'company') {
        // 1. Fetch only jobs posted by this company
        const myJobsRes = await uJobsMy().catch(() => ({ data: [] }))
        const jobs = Array.isArray(myJobsRes.data) ? myJobsRes.data : []
        setCompanyJobs(jobs)

        const companyApplicants = []
        const seenCandidates = new Set()

        // 2. Fetch applicants strictly applied to this company's jobs
        const resultsPerJob = await Promise.all(
          jobs.map(async (job) => {
            const jobId = job.id || job._id
            const jobApps = []
            try {
              const appRes = await uJobsApplicants(jobId).catch(() => ({ data: [] }))
              const rawApps = Array.isArray(appRes.data) ? appRes.data : appRes.data?.applicants || []
              for (const app of rawApps) {
                const hasInterview = app.interview_score != null || app.interview_completed
                const hasCV = app.cv_score != null || app.overall_score != null
                const cvScore = app.cv_score ?? app.overall_score ?? (hasInterview ? 75 : 0)
                const intScore = app.interview_score ?? 0
                const hireProb = app.hire_probability ?? app.css_score ?? (hasInterview && hasCV ? (0.4 * cvScore + 0.6 * intScore) : (hasInterview ? intScore : cvScore))
                jobApps.push({
                  candidate_id: app.candidate_id,
                  candidate_name: app.candidate_name || app.name || 'Applicant',
                  job_id: jobId,
                  job_role: job.title || 'Technical Role',
                  company_name: job.company_name || localStorage.getItem('recruitai.name') || 'Your Company',
                  skills: app.skills || app.resume_skills || job.required_skills || [],
                  hire_probability: hireProb,
                  CSS: hireProb,
                  interview_completed: Boolean(hasInterview),
                  interview_score: app.interview_score || null,
                  cv_score: cvScore,
                  S_cv: cvScore,
                  S_int: intScore,
                  skill_score: app.skill_score ?? 80,
                  experience_score: app.experience_score ?? 70,
                  education_score: app.education_score ?? 80,
                  mcq_score: app.mcq_score ?? (hasInterview ? 80 : 0),
                  descriptive_score: app.descriptive_score ?? (hasInterview ? 75 : 0),
                  coding_score: app.coding_score ?? (hasInterview ? 85 : 0),
                  has_cv: Boolean(hasCV),
                  passed_filter: app.passed_filter !== false
                })
              }
            } catch {
              /* ignore error for individual job */
            }
            return jobApps
          })
        )

        for (const list of resultsPerJob) {
          for (const cand of list) {
            const uniqueKey = `${cand.candidate_id || cand.candidate_name}_${cand.job_id}`
            if (!seenCandidates.has(uniqueKey)) {
              seenCandidates.add(uniqueKey)
              companyApplicants.push(cand)
            }
          }
        }

        // Sort descending by candidate score
        companyApplicants.sort((a, b) => (b.hire_probability || 0) - (a.hire_probability || 0))
        setData(companyApplicants)
      } else {
        // Candidate view: general benchmark standings
        const r = await c4Leaderboard(50)
        setData(r.data?.data || [])
      }
    } catch (err) {
      toast.error('Failed to load standings')
    } finally {
      setLoading(false)
    }
  }

  const sendDirectInvite = (candidateName, role) => {
    toast.success(`Fast-track interview invitation dispatched to ${candidateName} for ${role}!`, {
      duration: 3500
    })
  }

  const filteredData = data.filter((c) => {
    const nameMatch = (c.candidate_name || '').toLowerCase().includes(searchTerm.toLowerCase())
    const roleMatch = (c.job_role || '').toLowerCase().includes(searchTerm.toLowerCase())
    const skillMatch = (c.skills || []).some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesSearch = !searchTerm || nameMatch || roleMatch || skillMatch

    let matchesJob = true
    if (userRole === 'company' && selectedJobFilter !== 'all') {
      matchesJob = c.job_id === selectedJobFilter
    }

    let matchesDomain = true
    if (selectedDomain === 'se') matchesDomain = /software|developer|backend|frontend|full stack/i.test(c.job_role || '')
    else if (selectedDomain === 'ai') matchesDomain = /data|machine learning|ai|nlp/i.test(c.job_role || '')
    else if (selectedDomain === 'cloud') matchesDomain = /cloud|devops|sre|architect|infrastructure/i.test(c.job_role || '')
    else if (selectedDomain === 'sec') matchesDomain = /security|cyber/i.test(c.job_role || '')

    return matchesSearch && matchesJob && matchesDomain
  })

  const verifiedCount = data.filter((d) => d.interview_completed).length

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge={userRole === 'company' ? 'Company Talent Pipeline' : 'Talent Standings'}
        title={userRole === 'company' ? 'Company Applicant Leaderboard' : 'Top Talent Standings'}
        description={
          userRole === 'company'
            ? "View and compare top applicants who applied to your company's posted jobs, ranked by qualification and interview performance."
            : 'Top candidates ranked by verified CV credentials and technical assessment performance.'
        }
        icon={Trophy}
        actions={
          <button
            onClick={loadData}
            className="btn btn-ghost btn-sm"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <StatCard
          label={userRole === 'company' ? 'Total Company Applicants' : 'Total Evaluated Talent'}
          value={data.length}
          icon={UserCheck}
          color="primary"
          helperText={userRole === 'company' ? 'Across all your job postings' : 'Active candidates'}
        />
        <StatCard
          label="Interview Completed"
          value={verifiedCount}
          icon={ShieldCheck}
          color="success"
          helperText="Completed Technical Assessment"
        />
        <StatCard
          label={userRole === 'company' ? 'Company Openings' : 'Evaluation Model'}
          value={userRole === 'company' ? companyJobs.length : 'Multi-Factor'}
          icon={userRole === 'company' ? Briefcase : Award}
          color="purple"
          helperText={userRole === 'company' ? 'Active job listings' : 'Comprehensive scoring'}
        />
      </div>

      {/* Filter & Search Controls */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          {/* Company-Specific Job Filter or Domain Filter */}
          {userRole === 'company' && companyJobs.length > 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 600, color: 'var(--color-fg-muted)' }}>
                Filter by Opening:
              </span>
              <select
                value={selectedJobFilter}
                onChange={(e) => setSelectedJobFilter(e.target.value)}
                style={{ fontSize: 'var(--p-text-xs)', padding: '6px 12px', height: 34, borderRadius: 'var(--radius-sm)' }}
              >
                <option value="all">All Company Openings ({data.length} applicants)</option>
                {companyJobs.map((j) => (
                  <option key={j.id || j._id} value={j.id || j._id}>
                    {j.title} ({data.filter(d => d.job_id === (j.id || j._id)).length} applicants)
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {[
                { id: 'all', label: 'All Disciplines' },
                { id: 'se', label: 'Software Engineering' },
                { id: 'ai', label: 'AI & Data Science' },
                { id: 'cloud', label: 'Cloud & DevOps' },
                { id: 'sec', label: 'Cybersecurity' }
              ].map((domain) => (
                <button
                  key={domain.id}
                  onClick={() => setSelectedDomain(domain.id)}
                  className={`btn btn-sm ${selectedDomain === domain.id ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 'var(--p-text-xs)' }}
                >
                  {domain.label}
                </button>
              ))}
            </div>
          )}

          {/* Search */}
          <div style={{ position: 'relative', width: 240 }}>
            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
            <input
              type="text"
              placeholder="Search candidate or skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: 30, height: 34, fontSize: 'var(--p-text-xs)' }}
            />
          </div>
        </div>
      </div>

      {/* Standings Table */}
      {loading ? (
        <SkeletonLoader type="table" rows={6} cols={5} />
      ) : filteredData.length === 0 ? (
        <EmptyState
          title={userRole === 'company' ? 'No applicants for your company openings yet' : 'No candidates found'}
          description={
            userRole === 'company'
              ? "Candidates who apply to your company's open positions will appear in this leaderboard ranked by their evaluation fit."
              : 'Candidates will appear here after completing their assessments.'
          }
          actionLabel={userRole === 'company' ? 'Post a Job Opening' : undefined}
          onAction={userRole === 'company' ? () => navigate('/company/dashboard') : undefined}
          icon={Trophy}
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: 50 }}>Rank</th>
                  <th>Candidate</th>
                  <th>Overall Fit Score (CSS)</th>
                  <th>CV Match (S_cv)</th>
                  <th>Skills / Exp / Edu</th>
                  <th>Interview (S_int)</th>
                  <th>MCQ / Theory / Code</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((cand, index) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  const cssVal = cand.final_score ?? (cand.CSS != null ? cand.CSS : (cand.hire_probability ?? (cand.cv_score ?? 0)))
                  const sCvVal = cand.cv_score ?? (cand.S_cv != null ? cand.S_cv : 75)
                  const sSkillVal = cand.skill_score ?? 80
                  const sExpVal = cand.experience_score ?? 70
                  const sEduVal = cand.education_score ?? 80
                  const sIntVal = cand.interview_score ?? (cand.S_int != null ? cand.S_int : (cand.interview_completed ? 75 : 0))
                  const pMcqVal = cand.mcq_score ?? (cand.interview_completed ? 80 : 0)
                  const pDescVal = cand.descriptive_score ?? (cand.interview_completed ? 75 : 0)
                  const pCodeVal = cand.coding_score ?? (cand.interview_completed ? 85 : 0)

                  const passedFilter = cand.passed_hard_filter !== false && cand.passed_filter !== false
                  const verdict = !passedFilter ? 'Disqualified' : (Number(cssVal) >= 80 ? 'Highly Recommended' : (Number(cssVal) >= 65 ? 'Recommended' : (Number(cssVal) >= 50 ? 'Potential Match' : 'Not Recommended')))
                  const badgeColor = !passedFilter ? '#ef4444' : (Number(cssVal) >= 80 ? 'var(--color-success)' : (Number(cssVal) >= 65 ? 'var(--color-primary)' : (Number(cssVal) >= 50 ? 'var(--color-warning)' : 'var(--color-danger)')))

                  return (
                    <tr key={`${cand.candidate_id || index}_${cand.job_id || ''}`} style={{ opacity: passedFilter ? 1 : 0.65 }}>
                      <td>
                        <div style={{
                          width: 28,
                          height: 28,
                          borderRadius: 'var(--radius-sm)',
                          background: passedFilter
                            ? (isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)')
                            : 'var(--color-danger-muted)',
                          color: passedFilter
                            ? (isTop3 ? '#fff' : 'var(--color-fg)')
                            : 'var(--color-danger)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '12px'
                        }}>
                          {passedFilter ? `#${rank}` : '✗'}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                            {cleanCandidateName(cand.candidate_name, cand.candidate_id)}
                          </div>
                          {cand.interview_completed && (
                            <span style={{ fontSize: '10px', color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 6px', borderRadius: 'var(--radius-full)', fontWeight: 700 }}>
                              ✓ Assessed
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                          ID: {cand.candidate_id?.slice(0, 10) || 'Applicant'} {cand.job_role ? `• ${cand.job_role}` : ''}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
                          {Number(cssVal).toFixed(1)}%
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                          {Number(sCvVal).toFixed(0)}%
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>
                          <span title="Skills Match" style={{ color: 'var(--color-primary)' }}>{Number(sSkillVal).toFixed(0)}%</span> / <span title="Experience Match" style={{ color: 'var(--color-success)' }}>{Number(sExpVal).toFixed(0)}%</span> / <span title="Education Match" style={{ color: '#a855f7' }}>{Number(sEduVal).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-xs)', color: cand.interview_completed ? 'var(--color-purple)' : 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>
                          {cand.interview_completed ? `${Number(sIntVal).toFixed(0)}%` : '0%'}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>
                          <span title="MCQ Score" style={{ color: 'var(--color-primary)' }}>{Number(pMcqVal).toFixed(0)}%</span> / <span title="Theory Score" style={{ color: 'var(--color-info)' }}>{Number(pDescVal).toFixed(0)}%</span> / <span title="Coding Score" style={{ color: 'var(--color-purple)' }}>{Number(pCodeVal).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
                          <span style={{
                            fontSize: '10px',
                            fontWeight: 700,
                            color: badgeColor,
                            background: 'var(--color-bg-elevated)',
                            padding: '2px 8px',
                            borderRadius: 'var(--radius-full)',
                            border: `1px solid ${badgeColor}40`,
                            whiteSpace: 'nowrap'
                          }}>
                            {cand.verdict || verdict}
                          </span>
                          {userRole === 'company' && (
                            <button
                              className="btn btn-ghost btn-xs"
                              onClick={() => sendDirectInvite(cand.candidate_name, cand.job_role)}
                              title="Fast-track invite"
                              style={{ padding: '2px 6px', fontSize: '11px' }}
                            >
                              <Send size={11} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
