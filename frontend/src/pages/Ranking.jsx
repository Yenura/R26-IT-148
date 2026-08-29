import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
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

export default function Ranking() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [loadingJobs, setLoadingJobs] = useState(true)

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
    setLoadingJobs(true)
    try {
      let companyJobs = []
      try {
        const r = await uJobsMy()
        companyJobs = Array.isArray(r.data) ? r.data : []
      } catch (e) {
        console.warn('uJobsMy error, trying all jobs:', e)
      }
      if (companyJobs.length === 0) {
        const allRes = await c0JobsAll().catch(() => ({ data: [] }))
        companyJobs = Array.isArray(allRes.data) ? allRes.data : []
      }
      setJobs(companyJobs)
      if (companyJobs.length > 0) {
        const firstJobId = companyJobs[0].id || companyJobs[0]._id
        setSelectedJob(firstJobId)
        computePipeline(firstJobId)
      }
    } catch {
      toast.error('Failed to load company jobs')
    } finally {
      setLoadingJobs(false)
    }
  }

  const computePipeline = async (targetJobId) => {
    const jobIdToUse = targetJobId || selectedJob
    if (!jobIdToUse) return
    setBusy(true)
    try {
      const r = await c3Pipeline(jobIdToUse)
      if (r?.data) {
        setResult(r.data)
        toast.success('Applicant evaluation and ranking updated!')
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Select Your Company Job Opening
              </h3>
              <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                {jobs.length} Active Company Opening{jobs.length > 1 ? 's' : ''}
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
                  return (
                    <option key={id} value={id}>
                      {j.title} · {j.department || 'Engineering'} ({j.location || 'Remote'})
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
                      <th>Overall Fit Score</th>
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
                      const cssVal = cand.final_score ?? (cand.CSS != null ? cand.CSS * 100 : (cand.blended_score ?? 0))
                      const sCvVal = cand.cv_score ?? (cand.S_cv != null ? cand.S_cv * 100 : 75)
                      const sSkillVal = cand.skill_score ?? (cand.S_skill != null ? cand.S_skill * 100 : 80)
                      const sExpVal = cand.experience_score ?? (cand.S_exp != null ? cand.S_exp * 100 : 70)
                      const sEduVal = cand.education_score ?? (cand.S_edu != null ? cand.S_edu * 100 : 80)
                      const sIntVal = cand.interview_score ?? (cand.S_int != null ? cand.S_int * 100 : (cand.p_int ?? 0))
                      const pMcqVal = cand.mcq_score ?? (cand.P_mcq != null ? cand.P_mcq * 100 : 0)
                      const pDescVal = cand.descriptive_score ?? (cand.P_desc != null ? cand.P_desc * 100 : 0)
                      const pCodeVal = cand.coding_score ?? (cand.P_code != null ? cand.P_code * 100 : 0)

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
                            <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                              {cand.candidate_name || 'Candidate'}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                              ID: {cand.candidate_id?.slice(0, 10) || 'Verified'}
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
                            <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-purple)', fontFamily: 'var(--p-font-mono)', fontWeight: 800 }}>
                              {Number(sIntVal).toFixed(0)}%
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)' }}>
                              <span title="MCQ Score" style={{ color: 'var(--color-primary)' }}>{Number(pMcqVal).toFixed(0)}%</span> / <span title="Theory Score" style={{ color: 'var(--color-info)' }}>{Number(pDescVal).toFixed(0)}%</span> / <span title="Coding Score" style={{ color: 'var(--color-purple)' }}>{Number(pCodeVal).toFixed(0)}%</span>
                            </div>
                          </td>
                          <td>
                            {cand.passed_hard_filter ? (
                              <span style={{
                                fontSize: '10px',
                                fontWeight: 700,
                                color: cand.badge_color || 'var(--color-success)',
                                background: 'var(--color-bg-elevated)',
                                padding: '2px 8px',
                                borderRadius: 'var(--radius-full)',
                                border: `1px solid ${cand.badge_color || 'var(--color-success)'}40`
                              }}>
                                {cand.verdict || 'Qualified'}
                              </span>
                            ) : (
                              <span style={{
                                fontSize: '10px',
                                fontWeight: 700,
                                color: 'var(--color-danger)',
                                background: 'var(--color-danger-muted)',
                                padding: '2px 8px',
                                borderRadius: 'var(--radius-full)',
                                border: '1px solid rgba(244, 63, 94, 0.3)'
                              }}>
                                {cand.filter_fail_reason || 'Disqualified'}
                              </span>
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
