import { useEffect, useState, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ListOrdered, Trophy, Briefcase, Users } from 'lucide-react'
import { uJobsMy, c3Pipeline } from '../api'
import PageHeader from '../components/PageHeader'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'
import CandidateRankingTable from '../components/CandidateRankingTable'

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

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') {
      navigate('/login/company')
      return
    }
    // Instant hydrate & pipeline computation from cached jobs
    if (jobs.length > 0) {
      const initialJobId = paramJobId || selectedJob || (jobs[0].id || jobs[0]._id)
      if (initialJobId) {
        setSelectedJob(initialJobId)
        computePipeline(initialJobId)
      }
    }
    loadCompanyJobs()
  }, [])

  const loadCompanyJobs = async () => {
    try {
      const myRes = await uJobsMy().catch(() => ({ data: [] }))
      const raw = myRes?.data
      const userCompanyJobs = Array.isArray(raw) ? raw : (raw?.jobs || (raw?.data && Array.isArray(raw.data) ? raw.data : []))

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
            <div style={{ marginBottom: 'var(--p-space-6)' }}>
              <CandidateRankingTable
                candidates={candidatesList}
                jobTitle={selectedJobObj?.title || 'Selected Position'}
              />
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
