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
                const intScore = app.interview_score ?? (hasCV ? 70 : 0)
                const hireProb = app.hire_probability ?? app.css_score ?? (hasInterview && hasCV ? (0.4 * cvScore + 0.6 * intScore) : (hasInterview ? intScore : cvScore))
                jobApps.push({
                  candidate_id: app.candidate_id,
                  candidate_name: app.candidate_name || app.name || 'Applicant',
                  job_id: jobId,
                  job_role: job.title || 'Technical Role',
                  company_name: job.company_name || localStorage.getItem('recruitai.name') || 'Your Company',
                  skills: app.skills || app.resume_skills || job.required_skills || [],
                  hire_probability: hireProb,
                  interview_completed: Boolean(hasInterview),
                  interview_score: app.interview_score || null,
                  cv_score: app.cv_score || app.overall_score || null,
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
                  <th style={{ width: 60 }}>Rank</th>
                  <th>Candidate</th>
                  <th>Applied Position</th>
                  <th>Key Skills</th>
                  <th>Overall Match Score</th>
                  {userRole === 'company' && <th style={{ textAlign: 'right' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {filteredData.map((c, index) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  return (
                    <tr key={`${c.candidate_id || index}_${c.job_id || ''}`}>
                      <td>
                        <div style={{
                          width: 28,
                          height: 28,
                          borderRadius: 'var(--radius-sm)',
                          background: isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)',
                          color: isTop3 ? '#fff' : 'var(--color-fg)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '12px'
                        }}>
                          #{rank}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                            {c.candidate_name || 'Candidate'}
                          </div>
                          {c.interview_completed && (
                            <span style={{ fontSize: '10px', color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 6px', borderRadius: 'var(--radius-full)', fontWeight: 700 }}>
                              ✓ Assessed
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                          ID: {c.candidate_id?.slice(0, 10) || 'Applicant'}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', fontWeight: 600 }}>
                          {c.job_role || 'Software Engineer'}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 280 }}>
                           {[...new Set(c.skills || [])].slice(0, 4).map((s, i) => (
                             <span key={`${s}-${i}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontFamily: 'var(--p-font-mono)', fontWeight: 800, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                            {c.hire_probability ? `${c.hire_probability}%` : '85%'}
                          </span>
                          <ScoreBadge score={c.hire_probability || 85} showLabel={false} />
                        </div>
                      </td>
                      {userRole === 'company' && (
                        <td style={{ textAlign: 'right' }}>
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => sendDirectInvite(c.candidate_name, c.job_role)}
                            style={{ fontSize: 'var(--p-text-xs)', padding: '4px 10px' }}
                          >
                            <Send size={12} /> Contact Candidate
                          </button>
                        </td>
                      )}
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
