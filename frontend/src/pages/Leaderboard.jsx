import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Award, Trophy, Search, RefreshCw, CheckCircle2,
  Send, ShieldCheck, Sparkles, UserCheck, Briefcase, Plus
} from 'lucide-react'
import { c4Leaderboard, uJobsMy, c3Pipeline } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

function getRecommendationInfo(cand) {
  if (cand.passed_hard_filter === false) {
    return {
      label: 'Disqualified',
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.4)'
    }
  }

  const rawCss = cand.CSS != null ? (cand.CSS <= 1 ? cand.CSS * 100 : cand.CSS) : (cand.final_score ?? cand.blended_score ?? cand.composite_fit_score ?? cand.overall_score ?? cand.hire_probability ?? 0)
  const css = Number(rawCss) || 0

  if (css >= 80) {
    return {
      label: 'Highly Qualified',
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.15)',
      border: 'rgba(16, 185, 129, 0.4)'
    }
  }
  if (css >= 65) {
    return {
      label: 'Recommended',
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.15)',
      border: 'rgba(59, 130, 246, 0.4)'
    }
  }
  if (css >= 50) {
    return {
      label: 'Qualified',
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.15)',
      border: 'rgba(245, 158, 11, 0.4)'
    }
  }
  return {
    label: 'Disqualified',
    color: '#ef4444',
    bg: 'rgba(239, 68, 68, 0.15)',
    border: 'rgba(239, 68, 68, 0.4)'
  }
}

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
        const jobs = Array.isArray(myJobsRes.data) ? myJobsRes.data : []
        setCompanyJobs(jobs)

        if (jobs.length === 0) {
          setData([])
          return
        }

        const aggregated = []
        const seenCandidates = new Set()

        const pipelineResults = await Promise.all(
          jobs.map(async (job) => {
            const jid = job.id || job._id
            try {
              const res = await c3Pipeline(jid)
              const list = res?.data?.data || []
              return list.map((cand) => ({
                ...cand,
                job_id: jid,
                job_title: job.title,
                job_role: job.title || cand.job_role || 'Software Engineer',
                company_name: job.company_name || 'Your Company',
              }))
            } catch {
              return []
            }
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

        // Sort descending by CSS / final_score
        aggregated.sort((a, b) => (b.final_score ?? (b.CSS != null ? b.CSS * 100 : 0)) - (a.final_score ?? (a.CSS != null ? a.CSS * 100 : 0)))
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
    const roleMatch = (c.job_role || c.job_title || '').toLowerCase().includes(searchTerm.toLowerCase())
    const skillMatch = (c.skills || []).some((s) => String(s).toLowerCase().includes(searchTerm.toLowerCase()))
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
        <SkeletonLoader type="table" rows={6} cols={8} />
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
            {userRole === 'company' ? (
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
                    <th style={{ textAlign: 'right' }}>Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((cand, idx) => {
                    const isTop3 = (cand.rank <= 3 || idx < 3) && cand.passed_hard_filter !== false
                    const hasCV = cand.has_cv !== false && (cand.cv_score != null || cand.S_cv != null)
                    const hasInt = Boolean(cand.interview_completed || cand.interview_score != null || cand.S_int != null)

                    const cssVal = cand.final_score ?? (cand.CSS != null ? cand.CSS * 100 : (cand.blended_score ?? cand.hire_probability))
                    const cssLabel = (hasCV && hasInt) ? 'Combined CSS' : (hasCV ? 'CV Fit Score' : (hasInt ? 'Interview Score' : 'Fit Score'))

                    const sCvVal = hasCV ? (cand.cv_score ?? (cand.S_cv != null ? cand.S_cv * 100 : null)) : null
                    const sSkillVal = hasCV ? (cand.skill_score ?? (cand.S_skill != null ? cand.S_skill * 100 : null)) : null
                    const sExpVal = hasCV ? (cand.experience_score ?? (cand.S_exp != null ? cand.S_exp * 100 : null)) : null
                    const sEduVal = hasCV ? (cand.education_score ?? (cand.S_edu != null ? cand.S_edu * 100 : null)) : null

                    const sIntVal = hasInt ? (cand.interview_score ?? (cand.S_int != null ? cand.S_int * 100 : null)) : null
                    const pMcqVal = hasInt ? (cand.mcq_score ?? (cand.P_mcq != null ? cand.P_mcq * 100 : null)) : null
                    const pDescVal = hasInt ? (cand.descriptive_score ?? (cand.P_desc != null ? cand.P_desc * 100 : null)) : null
                    const pCodeVal = hasInt ? (cand.coding_score ?? (cand.P_code != null ? cand.P_code * 100 : null)) : null

                    return (
                      <tr
                        key={`${cand.candidate_id || idx}_${cand.job_id || ''}`}
                        style={{ opacity: cand.passed_hard_filter !== false ? 1 : 0.6 }}
                      >
                        <td>
                          <div style={{
                            width: 28,
                            height: 28,
                            borderRadius: 'var(--radius-sm)',
                            background: cand.passed_hard_filter !== false
                              ? (isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)')
                              : 'var(--color-danger-muted)',
                            color: cand.passed_hard_filter !== false
                              ? (isTop3 ? '#fff' : 'var(--color-fg)')
                              : 'var(--color-danger)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 800,
                            fontSize: '12px'
                          }}>
                            {cand.passed_hard_filter !== false ? `#${cand.rank || idx + 1}` : '✗'}
                          </div>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                              {cand.candidate_name || 'Candidate'}
                            </span>
                            {hasInt && (
                              <span style={{ fontSize: '9.5px', color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 5px', borderRadius: 'var(--radius-full)', fontWeight: 700 }}>
                                ✓ Assessed
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                            {cand.job_title || cand.job_role || 'Applied Role'}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
                            {cssVal != null ? `${Number(cssVal).toFixed(1)}%` : '—'}
                          </div>
                          <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>
                            {cssLabel}
                          </div>
                        </td>
                        <td>
                          {hasCV && sCvVal != null ? (
                            <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                              {Number(sCvVal).toFixed(0)}%
                            </div>
                          ) : (
                            <span style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-warning)', background: 'var(--color-warning-muted)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>
                              Pending
                            </span>
                          )}
                        </td>
                        <td>
                          {hasCV && sSkillVal != null ? (
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>
                              <span title="Skills Match" style={{ color: 'var(--color-primary)' }}>{Number(sSkillVal).toFixed(0)}%</span> / <span title="Experience Match" style={{ color: 'var(--color-success)' }}>{Number(sExpVal || 0).toFixed(0)}%</span> / <span title="Education Match" style={{ color: '#a855f7' }}>{Number(sEduVal || 0).toFixed(0)}%</span>
                            </div>
                          ) : (
                            <span style={{ color: 'var(--color-fg-muted)', fontSize: '12px' }}>—</span>
                          )}
                        </td>
                        <td>
                          {hasInt && sIntVal != null ? (
                            <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-purple)', fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>
                              {Number(sIntVal).toFixed(0)}%
                            </div>
                          ) : (
                            <span style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-warning)', background: 'var(--color-warning-muted)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>
                              Pending
                            </span>
                          )}
                        </td>
                        <td>
                          {hasInt && pMcqVal != null ? (
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>
                              <span title="MCQ Score" style={{ color: 'var(--color-primary)' }}>{Number(pMcqVal).toFixed(0)}%</span> / <span title="Theory Score" style={{ color: 'var(--color-info)' }}>{Number(pDescVal || 0).toFixed(0)}%</span> / <span title="Coding Score" style={{ color: 'var(--color-purple)' }}>{Number(pCodeVal || 0).toFixed(0)}%</span>
                            </div>
                          ) : (
                            <span style={{ color: 'var(--color-fg-muted)', fontSize: '12px' }}>—</span>
                          )}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          {(() => {
                            const rec = getRecommendationInfo(cand)
                            return (
                              <span style={{
                                fontSize: '10.5px',
                                fontWeight: 700,
                                color: rec.color,
                                background: rec.bg,
                                padding: '3px 8px',
                                borderRadius: 'var(--radius-full)',
                                border: `1px solid ${rec.border}`,
                                display: 'inline-block',
                                whiteSpace: 'nowrap'
                              }}>
                                {rec.label}
                              </span>
                            )
                          })()}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            ) : (
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
                              {c.hire_probability ? `${c.hire_probability}%` : `${c.overall_score || 85}%`}
                            </span>
                            <ScoreBadge score={c.hire_probability || c.overall_score || 85} showLabel={false} />
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
