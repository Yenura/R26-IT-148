import { useEffect, useState } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  ListOrdered, Trophy, Briefcase, Award, Brain,
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
  const [allJobs, setAllJobs] = useState([])
  const [viewScope, setViewScope] = useState('my') // 'my' | 'all'

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
      const [myRes, allRes] = await Promise.all([
        uJobsMy().catch(() => ({ data: [] })),
        c0JobsAll().catch(() => ({ data: [] }))
      ])
      const userCompanyJobs = Array.isArray(myRes.data) ? myRes.data : []
      const platformAllJobs = Array.isArray(allRes.data) ? allRes.data : []
      
      setMyJobs(userCompanyJobs)
      setAllJobs(platformAllJobs)

      const activeList = userCompanyJobs.length > 0 ? userCompanyJobs : platformAllJobs
      setJobs(activeList)

      if (activeList.length > 0) {
        const targetJobId = (paramJobId && activeList.some(j => (j.id || j._id) === paramJobId))
          ? paramJobId
          : (selectedJob || activeList[0].id || activeList[0]._id)
        setSelectedJob(targetJobId)
        computePipeline(targetJobId)
      }
    } catch {
      toast.error('Failed to load job openings')
    } finally {
      setLoadingJobs(false)
    }
  }

  const handleScopeChange = (newScope) => {
    setViewScope(newScope)
    const activeList = newScope === 'my' && myJobs.length > 0 ? myJobs : allJobs
    setJobs(activeList)
    if (activeList.length > 0) {
      const firstJobId = activeList[0].id || activeList[0]._id
      setSelectedJob(firstJobId)
      computePipeline(firstJobId)
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
  const candidatesList = result?.data || result?.rankings || []

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
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
          <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Select Target Job Opening
                </h3>
                {myJobs.length > 0 && (
                  <div style={{ display: 'flex', gap: 4, background: 'var(--color-bg)', padding: '2px 4px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                    <button
                      className={`btn btn-xs ${viewScope === 'my' ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => handleScopeChange('my')}
                      style={{ fontSize: '11px', padding: '2px 8px' }}
                    >
                      🏢 My Openings ({myJobs.length})
                    </button>
                    <button
                      className={`btn btn-xs ${viewScope === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => handleScopeChange('all')}
                      style={{ fontSize: '11px', padding: '2px 8px' }}
                    >
                      🌐 All 20 IT Roles ({allJobs.length})
                    </button>
                  </div>
                )}
              </div>
              <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                {jobs.length} Active Role{jobs.length > 1 ? 's' : ''} Available
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
            <SkeletonLoader type="table" rows={5} cols={6} />
          ) : result && candidatesList.length > 0 ? (
            <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 'var(--p-space-6)' }}>
              <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Trophy size={18} style={{ color: 'var(--color-primary)' }} />
                    Ranked Applicants for {selectedJobObj?.title || 'Selected Position'}
                  </h3>
                  <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0 0' }}>
                    Sorted by Overall Fit Score combining CV qualifications and interview scores.
                  </p>
                </div>
                <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-primary)', background: 'var(--color-primary-muted)', padding: '3px 10px', borderRadius: 'var(--radius-full)' }}>
                  {candidatesList.length} Applicant{candidatesList.length > 1 ? 's' : ''} Evaluated
                </span>
              </div>

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
                    {candidatesList.map((cand, idx) => {
                      const isTop3 = (cand.rank <= 3 || idx < 3) && cand.passed_hard_filter
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
                          key={cand.candidate_id || idx}
                          style={{ opacity: cand.passed_hard_filter ? 1 : 0.6 }}
                        >
                          <td>
                            <div style={{
                              width: 28,
                              height: 28,
                              borderRadius: 'var(--radius-sm)',
                              background: cand.passed_hard_filter
                                ? (isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)')
                                : 'var(--color-danger-muted)',
                              color: cand.passed_hard_filter
                                ? (isTop3 ? '#fff' : 'var(--color-fg)')
                                : 'var(--color-danger)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 800,
                              fontSize: '12px'
                            }}>
                              {cand.passed_hard_filter ? `#${cand.rank || idx + 1}` : '✗'}
                            </div>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                              <span style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                                {cleanCandidateName(cand.candidate_name, cand.candidate_id)}
                              </span>
                              {hasInt && (
                                <span style={{ fontSize: '9.5px', color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 5px', borderRadius: 'var(--radius-full)', fontWeight: 700 }}>
                                  ✓ Assessed
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                              ID: {cand.candidate_id?.slice(0, 10) || 'Verified'}
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
                          <td>
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
              </div>
            </div>
          ) : result && candidatesList.length === 0 ? (
            <EmptyState
              title="No applicants found for this position"
              description="Candidates who apply to this job opening will appear here automatically with their evaluation scores."
              icon={Users}
            />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--p-space-6)' }}>
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
