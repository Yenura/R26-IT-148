import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Award, Trophy, Search, RefreshCw,
  ShieldCheck, UserCheck, Briefcase
} from 'lucide-react'
import { c4Leaderboard, uJobsMy, c3Pipeline, c3PipelineBatch } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'
import CandidateRankingTable from '../components/CandidateRankingTable'

export default function Leaderboard() {
  const navigate = useNavigate()
  const userRole = localStorage.getItem('recruitai.role')

  const [data, setData] = useState(() => {
    try {
      const cached = sessionStorage.getItem(`recruitai.leaderboard.${userRole}`)
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
  const [companyJobs, setCompanyJobs] = useState(() => {
    try {
      const cached = sessionStorage.getItem('recruitai.company.jobs')
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
  const [selectedJobFilter, setSelectedJobFilter] = useState('all')
  const [loading, setLoading] = useState(() => {
    try {
      const cached = sessionStorage.getItem(`recruitai.leaderboard.${userRole}`)
      return !cached
    } catch {
      return true
    }
  })
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
        const myJobsRes = await uJobsMy().catch(() => ({ data: [] }))
        const raw = myJobsRes?.data
        const jobs = Array.isArray(raw) ? raw : (raw?.jobs || (raw?.data && Array.isArray(raw.data) ? raw.data : []))
        setCompanyJobs(jobs)

        if (jobs.length === 0) {
          setData([])
          return
        }

        const aggregated = []
        const seenCandidates = new Set()

        // Fast high-performance batch pipeline fetch
        const jobIds = jobs.map((job) => String(job.id || job._id)).filter(Boolean)
        let batchMap = {}
        try {
          const batchRes = await c3PipelineBatch(jobIds)
          batchMap = batchRes?.data?.data || {}
        } catch {
          batchMap = {}
        }

        const pipelineResults = await Promise.all(
          jobs.map(async (job) => {
            const jid = String(job.id || job._id)
            let list = batchMap[jid]
            if (!list || list.length === 0) {
              try {
                const res = await c3Pipeline(jid)
                list = res?.data?.data || res?.data?.rankings || []
              } catch {
                list = []
              }
            }
            return (list || []).map((cand) => ({
              ...cand,
              job_id: jid,
              job_title: job.title,
              job_role: job.title || cand.job_role || 'Software Engineer',
              company_name: job.company_name || 'Your Company',
            }))
          })
        )

        for (const list of pipelineResults) {
          for (const cand of list) {
            const key = `${cand.candidate_id}_${cand.job_id}`
            if (!seenCandidates.has(key)) {
              seenCandidates.add(key)
              aggregated.push(cand)
            }
          }
        }

        // Priority Ranking: Completed Both (Tier 1, score desc) > Incomplete (Tier 2, score desc)
        const getCandidateTier = (cand) => {
          const hasCV = cand.has_cv !== false && (cand.cv_score != null || cand.S_cv != null)
          const hasInt = Boolean(cand.interview_completed || cand.interview_score != null || cand.S_int != null)
          return (hasCV && hasInt) ? 1 : 2
        }

        const getCandidateScore = (cand) => {
          const hasCV = cand.has_cv !== false && (cand.cv_score != null || cand.S_cv != null)
          const hasInt = Boolean(cand.interview_completed || cand.interview_score != null || cand.S_int != null)
          const sCv = hasCV ? (cand.cv_score ?? (cand.S_cv != null ? cand.S_cv * 100 : null)) : null
          const sInt = hasInt ? (cand.interview_score ?? (cand.S_int != null ? cand.S_int * 100 : null)) : null
          if (hasCV && hasInt && sCv != null && sInt != null) {
            return 0.40 * Number(sCv) + 0.60 * Number(sInt)
          } else if (hasCV && sCv != null) {
            return Number(sCv)
          } else if (hasInt && sInt != null) {
            return Number(sInt)
          }
          const raw = cand.final_score ?? (cand.CSS != null ? (cand.CSS <= 1 ? cand.CSS * 100 : cand.CSS) : (cand.blended_score ?? cand.overall_score ?? cand.hire_probability ?? 0))
          return Number(raw) || 0
        }

        aggregated.sort((a, b) => {
          const tierA = getCandidateTier(a)
          const tierB = getCandidateTier(b)
          if (tierA !== tierB) return tierA - tierB
          return getCandidateScore(b) - getCandidateScore(a)
        })

        setData(aggregated)
        try {
          sessionStorage.setItem('recruitai.company.jobs', JSON.stringify(jobs))
          sessionStorage.setItem(`recruitai.leaderboard.${userRole}`, JSON.stringify(aggregated))
        } catch {}
      } else {
        // Candidate view: general benchmark standings
        const r = await c4Leaderboard(50)
        const standings = r.data?.data || []
        setData(standings)
        try {
          sessionStorage.setItem(`recruitai.leaderboard.${userRole}`, JSON.stringify(standings))
        } catch {}
      }
    } catch {
      toast.error('Failed to load standings')
    } finally {
      setLoading(false)
    }
  }

  const filteredData = data.filter((c) => {
    // For candidate view, apply search and domain
    if (userRole !== 'company') {
      const nameMatch = (c.candidate_name || '').toLowerCase().includes(searchTerm.toLowerCase())
      const roleMatch = (c.job_role || c.job_title || '').toLowerCase().includes(searchTerm.toLowerCase())
      const skillMatch = (c.skills || []).some((s) => String(s).toLowerCase().includes(searchTerm.toLowerCase()))
      const matchesSearch = !searchTerm || nameMatch || roleMatch || skillMatch

      let matchesDomain = true
      if (selectedDomain === 'se') matchesDomain = /software|developer|backend|frontend|full stack/i.test(c.job_role || '')
      else if (selectedDomain === 'ai') matchesDomain = /data|machine learning|ai|nlp/i.test(c.job_role || '')
      else if (selectedDomain === 'cloud') matchesDomain = /cloud|devops|sre|architect|infrastructure/i.test(c.job_role || '')
      else if (selectedDomain === 'sec') matchesDomain = /security|cyber/i.test(c.job_role || '')

      return matchesSearch && matchesDomain
    }

    // For company view: filter by opening
    if (selectedJobFilter !== 'all') {
      return c.job_id === selectedJobFilter
    }
    return true
  })

  const verifiedCount = data.filter((d) => d.interview_completed).length

  return (
    <div className="fade-in" style={{ maxWidth: 1240, margin: '0 auto', width: '100%' }}>
      {/* Header */}
      <PageHeader
        badge={userRole === 'company' ? 'Company Talent Pipeline' : 'Talent Standings'}
        title={userRole === 'company' ? 'Company Applicant Leaderboard' : 'Top Talent Standings'}
        description={
          userRole === 'company'
            ? "View and compare top applicants who applied to your company's posted jobs, ranked by verified qualifications and technical interview performance."
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
          helperText={userRole === 'company' ? 'Active job listings' : 'Composite Scoring System'}
        />
      </div>

      {/* Company Opening Selector */}
      {userRole === 'company' && companyJobs.length > 0 && (
        <div className="card glass-card" style={{ padding: 'var(--p-space-3) var(--p-space-4)', marginBottom: 'var(--p-space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <Briefcase size={16} style={{ color: 'var(--color-primary)' }} />
            <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)' }}>
              Filter by Company Job Opening:
            </span>
            <select
              value={selectedJobFilter}
              onChange={(e) => setSelectedJobFilter(e.target.value)}
              style={{ fontSize: 'var(--p-text-xs)', padding: '6px 12px', height: 34, borderRadius: 'var(--radius-sm)', minWidth: 260 }}
            >
              <option value="all">All Company Openings ({data.length} total applicants)</option>
              {companyJobs.map((j) => (
                <option key={j.id || j._id} value={j.id || j._id}>
                  {j.title} ({data.filter(d => d.job_id === (j.id || j._id)).length} applicants)
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Standings Content */}
      {loading ? (
        <SkeletonLoader type="table" rows={6} cols={7} />
      ) : filteredData.length === 0 && data.length === 0 ? (
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
      ) : userRole === 'company' ? (
        /* Company View of Candidate Ranking Leaderboard */
        <CandidateRankingTable
          candidates={filteredData}
          showJobColumn={selectedJobFilter === 'all'}
          emptyMessage="No applicants match the selected criteria for this job opening"
        />
      ) : (
        /* Candidate View of Leaderboard */
        <>
          <div className="card glass-card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
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

          <div className="card glass-card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 60 }}>Rank</th>
                    <th>Candidate</th>
                    <th>Domain / Role</th>
                    <th>Key Skills</th>
                    <th>Composite Fit Score</th>
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
                            color: isTop3 ? 'var(--p-white)' : 'var(--color-fg)',
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
                          <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                            {c.candidate_name || 'Candidate'}
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
                            <span style={{ fontFamily: 'var(--p-font-mono)', fontWeight: 800, fontSize: 'var(--p-text-sm)', color: 'var(--color-primary)' }}>
                              {c.hire_probability ? `${Math.round(Number(c.hire_probability))}%` : `${Math.round(Number(c.overall_score || 85))}%`}
                            </span>
                            <ScoreBadge score={Math.round(Number(c.hire_probability || c.overall_score || 85))} showLabel={false} />
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
