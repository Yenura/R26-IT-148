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



const getRankBadgeStyle = (rankNum) => {

  if (rankNum <= 3) {

    return {

      color: 'var(--p-white)',

      bg: 'var(--color-primary)',

      border: '1px solid var(--color-primary)'

    }

  }

  return {

    color: 'var(--color-fg)',

    bg: 'rgba(255, 255, 255, 0.04)',

    border: '1px solid var(--color-border-subtle)'

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



      {/* Filter & Search Controls */}

      <div className="card glass-card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>

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

        <SkeletonLoader type="table" rows={6} cols={7} />

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

        <div className="card glass-card" style={{ padding: 0, overflow: 'hidden' }}>

          <div style={{ overflowX: 'auto' }}>

            {userRole === 'company' ? (

              <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>

                <thead style={{ background: 'rgba(255, 255, 255, 0.035)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>

                  <tr>

                    <th style={{ width: 56, textAlign: 'center', padding: '13px 10px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>Rank</th>

                    <th style={{ minWidth: 180, padding: '13px 14px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>Candidate</th>

                    <th style={{ width: 110, padding: '13px 14px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>Total Score</th>

                    <th style={{ width: 85, padding: '13px 14px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>CV Score</th>

                    <th style={{ minWidth: 185, padding: '13px 12px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>Skills / Exp / Edu</th>

                    <th style={{ width: 105, padding: '13px 14px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>Interview Score</th>

                    <th style={{ minWidth: 195, padding: '13px 16px', fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#94a3b8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>MCQ / Theory / Code</th>

                  </tr>

                </thead>

                <tbody>

                  {filteredData.map((cand, idx) => {

                    const rankNum = idx + 1

                    const hasCV = cand.has_cv !== false && (cand.cv_score != null || cand.S_cv != null)

                    const hasInt = Boolean(cand.interview_completed || cand.interview_score != null || cand.S_int != null)

                    const isPassed = cand.passed_hard_filter !== false

                    const isComplete = hasCV && hasInt && isPassed

                    const badgeStyle = getRankBadgeStyle(rankNum)



                    const sCvVal = hasCV ? (cand.cv_score ?? (cand.S_cv != null ? cand.S_cv * 100 : null)) : null
                      const sSkillVal = hasCV ? (cand.skill_score ?? (cand.S_skill != null ? cand.S_skill * 100 : null)) : null
                      const sExpVal = hasCV ? (cand.experience_score ?? (cand.S_exp != null ? cand.S_exp * 100 : null)) : null
                      const sEduVal = hasCV ? (cand.education_score ?? (cand.S_edu != null ? cand.S_edu * 100 : null)) : null

                      const sIntVal = hasInt ? (cand.interview_score ?? (cand.S_int != null ? cand.S_int * 100 : null)) : null

                      let cssVal = null
                      if (hasCV && hasInt && sCvVal != null && sIntVal != null) {
                        cssVal = 0.40 * Number(sCvVal) + 0.60 * Number(sIntVal)
                      } else if (hasCV && sCvVal != null) {
                        cssVal = Number(sCvVal)
                      } else if (hasInt && sIntVal != null) {
                        cssVal = Number(sIntVal)
                      } else {
                        cssVal = cand.final_score ?? (cand.CSS != null ? (cand.CSS <= 1 ? cand.CSS * 100 : cand.CSS) : (cand.blended_score ?? cand.hire_probability))
                      }
                      const cssLabel = (hasCV && hasInt) ? 'Combined Score' : (hasCV ? 'CV Fit' : (hasInt ? 'Interview Fit' : 'Fit Score'))

                    const pMcqVal = hasInt ? (cand.mcq_score ?? (cand.P_mcq != null ? cand.P_mcq * 100 : null)) : null

                    const pDescVal = hasInt ? (cand.descriptive_score ?? (cand.P_desc != null ? cand.P_desc * 100 : null)) : null

                    const pCodeVal = hasInt ? (cand.coding_score ?? (cand.P_code != null ? cand.P_code * 100 : null)) : null



                    return (

                      <tr

                        key={`${cand.candidate_id || idx}_${cand.job_id || ''}`}

                        style={{

                          borderBottom: '1px solid rgba(255, 255, 255, 0.04)',

                          opacity: isPassed ? 1 : 0.75,

                          transition: 'background 0.15s ease'

                        }}

                      >

                        <td>

                          <div

                            title={!isPassed && cand.filter_fail_reason ? cand.filter_fail_reason : undefined}

                            style={{

                              width: 34,

                              height: 28,

                              borderRadius: '6px',

                              background: badgeStyle.bg,

                              color: badgeStyle.color,

                              border: badgeStyle.border,

                              display: 'inline-flex',

                              alignItems: 'center',

                              justifyContent: 'center',

                              fontWeight: 800,

                              fontSize: '12px',

                              fontFamily: 'var(--p-font-mono)'

                            }}

                          >

                            #{rankNum}

                          </div>

                        </td>

                        <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>

                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'nowrap' }}>

                            <span

                              style={{

                                fontWeight: 700,

                                color: 'var(--color-fg)',

                                fontSize: '13.5px',

                                whiteSpace: 'nowrap',

                                overflow: 'hidden',

                                textOverflow: 'ellipsis',

                                maxWidth: 175

                              }}

                              title={cleanCandidateName(cand.candidate_name, cand.candidate_id)}

                            >

                              {cleanCandidateName(cand.candidate_name, cand.candidate_id)}

                            </span>

                            {hasCV && !hasInt ? (

                              <span

                                style={{

                                  fontSize: '9.5px',

                                  color: '#f59e0b',

                                  background: 'rgba(245, 158, 11, 0.12)',

                                  border: '1px solid rgba(245, 158, 11, 0.28)',

                                  padding: '1px 6px',

                                  borderRadius: '9999px',

                                  fontWeight: 700,

                                  whiteSpace: 'nowrap',

                                  flexShrink: 0,

                                  display: 'inline-flex',

                                  alignItems: 'center'

                                }}

                              >

                                Pending Interview

                              </span>

                            ) : !hasCV && hasInt ? (

                              <span

                                style={{

                                  fontSize: '9.5px',

                                  color: '#f59e0b',

                                  background: 'rgba(245, 158, 11, 0.12)',

                                  border: '1px solid rgba(245, 158, 11, 0.28)',

                                  padding: '1px 6px',

                                  borderRadius: '9999px',

                                  fontWeight: 700,

                                  whiteSpace: 'nowrap',

                                  flexShrink: 0,

                                  display: 'inline-flex',

                                  alignItems: 'center'

                                }}

                              >

                                Pending CV

                              </span>

                            ) : null}

                          </div>

                          <div style={{ fontSize: '11px', color: '#64748b', marginTop: 2 }}>

                            {cand.job_title || cand.job_role || 'Applied Role'}

                          </div>

                        </td>

                        <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>

                          <div style={{ fontSize: '15px', fontWeight: 900, color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>

                            {cssVal != null ? `${Math.round(Number(cssVal))}%` : '—'}

                          </div>

                          <div style={{ fontSize: '9.5px', color: '#64748b', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>

                            {cssLabel}

                          </div>

                        </td>

                        <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>

                          {hasCV && sCvVal != null ? (

                            <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>

                              {Math.round(Number(sCvVal))}%

                            </div>

                          ) : (

                            <span style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-warning)', background: 'var(--color-warning-muted)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>

                              Pending

                            </span>

                          )}

                        </td>

                        <td style={{ padding: '12px 12px', verticalAlign: 'middle' }}>

                          {hasCV && sSkillVal != null ? (

                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>

                              <span title="Skills Match" style={{ color: 'var(--color-primary)' }}>{Number(sSkillVal).toFixed(0)}%</span> / <span title="Experience Match" style={{ color: 'var(--color-success)' }}>{Number(sExpVal || 0).toFixed(0)}%</span> / <span title="Education Match" style={{ color: 'var(--color-purple)' }}>{Number(sEduVal || 0).toFixed(0)}%</span>

                            </div>

                          ) : (

                            <span style={{ color: 'var(--color-fg-muted)', fontSize: '12px' }}>—</span>

                          )}

                        </td>

                        <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>

                          {hasInt && sIntVal != null ? (

                            <div style={{ fontSize: '13px', color: '#c084fc', fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>

                              {Math.round(Number(sIntVal))}%

                            </div>

                          ) : (

                            <span style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-warning)', background: 'var(--color-warning-muted)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>

                              Pending

                            </span>

                          )}

                        </td>

                        <td style={{ padding: '12px 12px', verticalAlign: 'middle' }}>

                          {hasInt && pMcqVal != null ? (

                            <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexWrap: 'nowrap' }}>

                              <span

                                title={`MCQ Score: ${Math.round(Number(pMcqVal))}%`}

                                style={{

                                  fontSize: '11px',

                                  fontWeight: 700,

                                  fontFamily: 'var(--p-font-mono)',

                                  padding: '2px 6px',

                                  borderRadius: '4px',

                                  background: 'rgba(59, 130, 246, 0.12)',

                                  color: '#3b82f6',

                                  border: '1px solid rgba(59, 130, 246, 0.25)',

                                  whiteSpace: 'nowrap'

                                }}

                              >

                                MCQ: {Math.round(Number(pMcqVal))}%

                              </span>

                              <span

                                title={`Theory/Descriptive Score: ${Math.round(Number(pDescVal || 0))}%`}

                                style={{

                                  fontSize: '11px',

                                  fontWeight: 700,

                                  fontFamily: 'var(--p-font-mono)',

                                  padding: '2px 6px',

                                  borderRadius: '4px',

                                  background: 'rgba(14, 165, 233, 0.12)',

                                  color: '#38bdf8',

                                  border: '1px solid rgba(14, 165, 233, 0.25)',

                                  whiteSpace: 'nowrap'

                                }}

                              >

                                Desc: {Math.round(Number(pDescVal || 0))}%

                              </span>

                              <span

                                title={`Live Coding Score: ${Math.round(Number(pCodeVal || 0))}%${(pCodeVal || 0) < 25 ? ' (Below 25% prerequisite threshold)' : ''}`}

                                style={{

                                  fontSize: '11px',

                                  fontWeight: 700,

                                  fontFamily: 'var(--p-font-mono)',

                                  padding: '2px 6px',

                                  borderRadius: '4px',

                                  background: (pCodeVal || 0) < 25 ? 'rgba(239, 68, 68, 0.12)' : 'rgba(168, 85, 247, 0.12)',

                                  color: (pCodeVal || 0) < 25 ? '#ef4444' : '#c084fc',

                                  border: `1px solid ${(pCodeVal || 0) < 25 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(168, 85, 247, 0.25)'}`,

                                  whiteSpace: 'nowrap'

                                }}

                              >

                                Code: {Math.round(Number(pCodeVal || 0))}%

                              </span>

                            </div>

                          ) : (

                            <span style={{ color: 'var(--color-fg-muted)', fontSize: '12px' }}>—</span>

                          )}

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

            )}

          </div>

        </div>

      )}

    </div>

  )

}

