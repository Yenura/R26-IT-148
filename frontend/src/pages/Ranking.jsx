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

export default function Ranking() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const paramJobId = searchParams.get('job_id')
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [loadingJobs, setLoadingJobs] = useState(true)
  const [myJobs, setMyJobs] = useState([])
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
    setLoadingJobs(true)
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
          : (activeList[0].id || activeList[0]._id)
        setSelectedJob(targetJobId)
        computePipeline(targetJobId)
      }
    } catch {
      toast.error('Failed to load company jobs')
    } finally {
      setLoadingJobs(false)
    }
  }

  const computePipeline = async (targetJobId) => {
    const jobIdToUse = targetJobId || selectedJob
    if (!jobIdToUse) return toast.error('Please select a job opening')
    setBusy(true)
    try {
      const r = await c3Pipeline(jobIdToUse)
      setResult(r.data)
      toast.success('Applicant evaluation and ranking updated!')
    } catch {
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
                {[...new Set(selectedJobObj.required_skills || [])].map((s, i) => (
                  <span key={`${s}-${i}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
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
                      <th style={{ width: 60 }}>Rank</th>
                      <th>Candidate</th>
                      <th>Overall Fit Score</th>
                      <th>Skills Match</th>
                      <th>Experience Match</th>
                      <th>Education Match</th>
                      <th>Interview Score</th>
                      <th>Qualification</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidatesList.map((cand, idx) => {
                      const isTop3 = cand.rank <= 3 && cand.passed_hard_filter
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
                            <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                              {(cand.final_score || cand.blended_score || 0).toFixed(1)}%
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                              {(cand.skill_score || cand.s_skill || 0).toFixed(0)}%
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                              {(cand.experience_score || cand.s_exp || 0).toFixed(0)}%
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                              {(cand.education_score || cand.s_edu || 100).toFixed(0)}%
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-purple)', fontFamily: 'var(--p-font-mono)', fontWeight: 600 }}>
                              {(cand.interview_score || cand.p_int || 0).toFixed(0)}%
                            </div>
                          </td>
                          <td>
                            {cand.passed_hard_filter ? (
                              <span style={{
                                fontSize: '10px',
                                fontWeight: 700,
                                color: 'var(--color-success)',
                                background: 'var(--color-success-muted)',
                                padding: '2px 8px',
                                borderRadius: 'var(--radius-full)',
                                border: '1px solid rgba(16, 185, 129, 0.3)'
                              }}>
                                Qualified
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
