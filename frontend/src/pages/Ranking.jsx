import { useEffect, useState, useMemo } from 'react'

import { useNavigate, Link, useSearchParams } from 'react-router-dom'

import toast from 'react-hot-toast'

import {

  ListOrdered, Trophy, Briefcase, Award, Brain, Shield,

  CheckCircle2, Users, ArrowRight, Eye, ChevronRight, Plus

} from 'lucide-react'

import { uJobsMy, c3Pipeline, c0JobsAll } from '../api'

import PageHeader from '../components/PageHeader'

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



export default function Ranking() {

  const navigate = useNavigate()

  const [searchParams] = useSearchParams()

  const paramJobId = searchParams.get('jobId') || ''



  const [jobs, setJobs] = useState(() => {

    try {

      const cached = sessionStorage.getItem('recruitai.company.jobs')

      return cached ? JSON.parse(cached) : []

    } catch {

      return []

    }

  })

  const [selectedJob, setSelectedJob] = useState(paramJobId || '')

  const [result, setResult] = useState(() => {

    try {

      if (paramJobId) {

        const cached = sessionStorage.getItem(`recruitai.ranking.${paramJobId}`)

        return cached ? JSON.parse(cached) : null

      }

      return null

    } catch {

      return null

    }

  })

  const [busy, setBusy] = useState(false)

  const [loadingJobs, setLoadingJobs] = useState(() => {

    try {

      const cached = sessionStorage.getItem('recruitai.company.jobs')

      return !cached

    } catch {

      return true

    }

  })

  const [myJobs, setMyJobs] = useState(() => {

    try {

      const cached = sessionStorage.getItem('recruitai.company.jobs')

      return cached ? JSON.parse(cached) : []

    } catch {

      return []

    }

  })



  useEffect(() => {

    const token = localStorage.getItem('recruitai.token')

    const role = localStorage.getItem('recruitai.role')

    if (!token || role !== 'company') {

      navigate('/login/company')

      return

    }

    loadCompanyJobs()

  }, [])



  const loadCompanyJobs = async () => {

    try {

      const myRes = await uJobsMy().catch(() => ({ data: [] }))

      const raw = myRes?.data

      const userCompanyJobs = Array.isArray(raw) ? raw : (raw?.jobs || (raw?.data && Array.isArray(raw.data) ? raw.data : []))

      

      setMyJobs(userCompanyJobs)

      setJobs(userCompanyJobs)

      try {

        sessionStorage.setItem('recruitai.company.jobs', JSON.stringify(userCompanyJobs))

      } catch {}



      if (userCompanyJobs.length > 0) {

        const targetJobId = (paramJobId && userCompanyJobs.some(j => (j.id || j._id) === paramJobId))

          ? paramJobId

          : ((selectedJob && userCompanyJobs.some(j => (j.id || j._id) === selectedJob)) ? selectedJob : (userCompanyJobs[0].id || userCompanyJobs[0]._id))

        setSelectedJob(targetJobId)

        computePipeline(targetJobId)

      } else {

        setSelectedJob('')

        setResult(null)

      }

    } catch {

      toast.error('Failed to load your company job openings')

    } finally {

      setLoadingJobs(false)

    }

  }



  const computePipeline = async (targetJobId) => {

    const jobIdToUse = targetJobId || selectedJob

    if (!jobIdToUse) return



    // Fast-hydrate from session cache if available

    try {

      const cached = sessionStorage.getItem(`recruitai.ranking.${jobIdToUse}`)

      if (cached) {

        setResult(JSON.parse(cached))

      } else {

        setBusy(true)

      }

    } catch {

      setBusy(true)

    }



    try {

      const r = await c3Pipeline(jobIdToUse)

      if (r?.data) {

        setResult(r.data)

        try {

          sessionStorage.setItem(`recruitai.ranking.${jobIdToUse}`, JSON.stringify(r.data))

        } catch {}

      }

    } catch (err) {

      console.error('computePipeline error:', err)

      toast.error('Failed to compute candidate rankings')

    } finally {

      setBusy(false)

    }

  }



  const selectedJobObj = jobs.find((j) => (j.id || j._id) === selectedJob)

  const rawCandidatesList = result?.data || result?.rankings || []

  const candidatesList = useMemo(() => {

    const list = [...rawCandidatesList]

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

    list.sort((a, b) => {

      const tierA = getCandidateTier(a)

      const tierB = getCandidateTier(b)

      if (tierA !== tierB) return tierA - tierB

      return getCandidateScore(b) - getCandidateScore(a)

    })

    return list

  }, [rawCandidatesList])



  return (

    <div className="fade-in" style={{ maxWidth: 1240, margin: '0 auto', width: '100%' }}>

      {/* Header */}

      <PageHeader

        badge="Applicant Evaluation"

        title="Candidate Ranking & Evaluation"

        description="Rank applicants who applied to your company's open roles by combining verified CV qualifications with technical interview performance."

        icon={ListOrdered}

      />



      {loadingJobs ? (

        <SkeletonLoader type="card" count={2} />

      ) : jobs.length === 0 ? (

        <EmptyState

          title="No Company Job Postings Yet"

          description="You haven't posted any job openings yet. Post your first technical opening to start receiving and ranking applicants."

          actionLabel="Post a Job Opening"

          onAction={() => navigate('/company/dashboard')}

          icon={Briefcase}

        />

      ) : (

        <>

          {/* Job Selection Card */}

          <div className="card glass-card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 10 }}>

              <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>

                <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Select Target Job Opening

              </h3>

              <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>

                {jobs.length} Active Posted Role{jobs.length > 1 ? 's' : ''}

              </span>

            </div>



            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) auto', gap: 12, alignItems: 'center' }}>

              <select

                value={selectedJob}

                onChange={(e) => {

                  const val = e.target.value

                  setSelectedJob(val)

                  if (val) computePipeline(val)

                }}

                style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}

              >

                {jobs.map((j) => {

                  const id = j.id || j._id

                  const compName = j.company_name ? ` [${j.company_name}]` : ''

                  return (

                    <option key={id} value={id}>

                      {j.title}{compName} · {j.experience_required ? `${j.experience_required}+ yrs` : (j.department || 'Engineering')} ({j.location || 'Remote'})

                    </option>

                  )

                })}

              </select>



              <button

                className="btn btn-primary"

                onClick={() => computePipeline()}

                disabled={busy || !selectedJob}

                style={{ padding: '10px 20px', whiteSpace: 'nowrap' }}

              >

                {busy ? 'Evaluating Applicants...' : 'Rank Applicants'}

              </button>

            </div>



            {selectedJobObj && (

              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>

                <span style={{ fontWeight: 600, color: 'var(--color-fg)' }}>Required Skills:</span>

                {(selectedJobObj.required_skills || []).map((s, idx) => (

                  <span key={`${s}-${idx}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>

                    {s}

                  </span>

                ))}

              </div>

            )}

          </div>



          {/* Ranking Results Table */}

          {busy ? (

            <SkeletonLoader type="table" rows={5} cols={7} />

          ) : result && candidatesList.length > 0 ? (

            <div className="card glass-card" style={{ padding: 0, overflow: 'hidden', marginBottom: 'var(--p-space-6)' }}>

              <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

                <div>

                  <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>

                    <Trophy size={18} style={{ color: 'var(--color-primary)' }} />

                    Ranked Applicants for {selectedJobObj?.title || 'Selected Position'}

                  </h3>

                  <p style={{ fontSize: 'var(--p-text-xs)', color: '#94a3b8', margin: '2px 0 0 0' }}>

                    Sorted by composite fit combining verified CV qualifications with technical interview performance.

                  </p>

                </div>

                <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-primary)', background: 'var(--color-primary-muted)', padding: '4px 12px', borderRadius: 'var(--radius-full)' }}>

                  {candidatesList.length} Applicant{candidatesList.length > 1 ? 's' : ''} Evaluated

                </span>

              </div>



              <div style={{ overflowX: 'auto', width: '100%' }}>

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

                    {candidatesList.map((cand, idx) => {

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

                          key={cand.candidate_id || idx}

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

                              ID: {cand.candidate_id?.slice(0, 10) || 'Verified'}

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

                              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>

                                <span style={{ fontSize: '13px', color: '#c084fc', fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>

                                  {Math.round(Number(sIntVal))}%

                                </span>

                                {cand.integrity_score != null && (

                                  <span title={`Proctored integrity score: ${Math.round(cand.integrity_score)}%`} style={{ display: 'inline-flex', alignItems: 'center', gap: 3, fontSize: '10px', fontWeight: 700, color: 'var(--color-fg-muted)', whiteSpace: 'nowrap' }}>

                                    <Shield size={11} /> {Math.round(cand.integrity_score)}%

                                  </span>

                                )}

                              </div>

                            ) : (

                              <span style={{ fontSize: '10.5px', fontWeight: 600, color: 'var(--color-warning)', background: 'var(--color-warning-muted)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>

                                Pending

                              </span>

                            )}

                          </td>

                          <td style={{ padding: '12px 16px', verticalAlign: 'middle' }}>

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

              </div>

            </div>

          ) : result && candidatesList.length === 0 ? (

            <EmptyState

              title="No applicants found for this position"

              description="Candidates who apply to this job opening will appear here automatically with their evaluation scores."

              icon={Users}

            />

          ) : (

            <div className="card glass-card" style={{ textAlign: 'center', padding: 'var(--p-space-6)' }}>

              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>

                Select a job opening above and click <strong>Rank Applicants</strong> to evaluate candidates.

              </p>

            </div>

          )}

        </>

      )}

    </div>

  )

}

