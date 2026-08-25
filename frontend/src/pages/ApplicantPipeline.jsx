import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Users, Trophy, ArrowLeft, X, CheckCircle2, Code, FileText,
  Building2, MapPin, Sparkles, Eye, AlertCircle
} from 'lucide-react'
import { c0JobsAll, uJobsApplicants, c3Pipeline, uInterviewDetail } from '../api'
import PageHeader from '../components/PageHeader'
import Modal from '../components/Modal'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function ApplicantPipeline() {
  const navigate = useNavigate()
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [rankings, setRankings] = useState([])
  const [busy, setBusy] = useState(true)
  const [ranking, setRanking] = useState(false)
  const [detail, setDetail] = useState(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [detailBusy, setDetailBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') {
      navigate('/login/company')
      return
    }
    loadData()
  }, [jobId])

  const loadData = async () => {
    setBusy(true)
    try {
      const [jobRes, appsRes] = await Promise.all([
        c0JobsAll().catch(() => ({ data: [] })),
        uJobsApplicants(jobId).catch(() => ({ data: [] })),
      ])
      const jobList = Array.isArray(jobRes.data) ? jobRes.data : []
      const j = jobList.find((x) => x.id === jobId)
      setJob(j)
      const apps = Array.isArray(appsRes.data) ? appsRes.data : []
      setApplicants(apps)
    } catch (err) {
      toast.error('Failed to load applicant pipeline')
    } finally {
      setBusy(false)
    }
  }

  const runRanking = async () => {
    setRanking(true)
    try {
      const r = await c3Pipeline(jobId)
      setRankings(r?.data?.data || [])
      toast.success(`Evaluated & ranked ${r?.data?.data?.length || 0} applicants`)
    } catch (err) {
      toast.error('Failed to run candidate ranking')
    } finally {
      setRanking(false)
    }
  }

  const openDetail = async (candidateId) => {
    setDetailBusy(true)
    try {
      const r = await uInterviewDetail(candidateId)
      setDetail(r.data?.[0] || null)
      setDetailModalOpen(true)
    } catch (err) {
      toast.error('No detailed interview data found for this candidate')
    } finally {
      setDetailBusy(false)
    }
  }

  if (busy) {
    return (
      <div style={{ maxWidth: 1040, margin: '0 auto' }}>
        <SkeletonLoader type="table" rows={4} cols={4} />
      </div>
    )
  }

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      {/* Back to Dashboard */}
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate('/company/dashboard')}
        style={{ marginBottom: 'var(--p-space-4)' }}
      >
        <ArrowLeft size={14} /> Back to Dashboard
      </button>

      {/* Header */}
      <PageHeader
        badge="Applicant Pipeline"
        title={job?.title || 'Job Pipeline'}
        description={`${applicants.length} Total Applicant(s) · ${job?.location || 'Remote'} · ${job?.employment_type || 'Full-time'}`}
        icon={Users}
        actions={
          <button
            className="btn btn-primary btn-sm"
            onClick={runRanking}
            disabled={ranking || applicants.length === 0}
          >
            <Trophy size={14} /> {ranking ? 'Ranking Applicants...' : 'Rank Applicants'}
          </button>
        }
      />

      {/* Applicant Rankings or Raw List */}
      {rankings.length > 0 ? (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 'var(--p-space-6)' }}>
          <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Trophy size={18} style={{ color: 'var(--color-primary)' }} /> Ranked Applicant Standings
            </h3>
            <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
              Multi-Criteria Evaluation
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
                  <th>Interview Score</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((r, i) => (
                  <tr key={r.candidate_id || i} style={{ opacity: r.passed_hard_filter ? 1 : 0.65 }}>
                    <td>
                      <div style={{
                        width: 28,
                        height: 28,
                        borderRadius: 'var(--radius-sm)',
                        background: r.passed_hard_filter ? (i < 3 ? 'var(--color-primary)' : 'var(--color-border-subtle)') : 'var(--color-danger-muted)',
                        color: r.passed_hard_filter ? (i < 3 ? '#fff' : 'var(--color-fg)') : 'var(--color-danger)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 800,
                        fontSize: '12px'
                      }}>
                        {r.passed_hard_filter ? `#${r.rank || i + 1}` : '✗'}
                      </div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--color-fg)' }}>{r.candidate_name || 'Candidate'}</div>
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                        <span title={r.candidate_id}>ID: {r.candidate_id?.slice(0, 8)}</span>
                      </div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                        {(r.final_score || r.blended_score || 0).toFixed(1)}%
                      </div>
                    </td>
                    <td>
                      <div style={{ fontFamily: 'var(--p-font-mono)', fontSize: 'var(--p-text-xs)' }}>
                        {(r.skill_score || 0).toFixed(0)}%
                      </div>
                    </td>
                    <td>
                      <div style={{ fontFamily: 'var(--p-font-mono)', fontSize: 'var(--p-text-xs)' }}>
                        {(r.experience_score || 0).toFixed(0)}%
                      </div>
                    </td>
                    <td>
                      <div style={{ fontFamily: 'var(--p-font-mono)', fontSize: 'var(--p-text-xs)', color: 'var(--color-purple)', fontWeight: 700 }}>
                        {(r.interview_score || 0).toFixed(0)}%
                      </div>
                    </td>
                    <td>
                      {r.passed_hard_filter ? (
                        <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                          Qualified
                        </span>
                      ) : (
                        <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-danger)', background: 'var(--color-danger-muted)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                          {r.filter_fail_reason || 'Disqualified'}
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => openDetail(r.candidate_id)}
                        disabled={detailBusy}
                        style={{ fontSize: 'var(--p-text-xs)' }}
                      >
                        <Eye size={13} /> Assessment Detail
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : applicants.length > 0 ? (
        /* Unranked Applicants List */
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Users size={18} style={{ color: 'var(--color-primary)' }} /> Applicants in Pipeline ({applicants.length})
            </h3>
            <button className="btn btn-primary btn-sm" onClick={runRanking}>
              <Trophy size={14} /> Rank Applicants
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Candidate Name</th>
                  <th>Candidate ID</th>
                  <th>Application Date</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {applicants.map((app) => (
                  <tr key={app.candidate_id || app.id}>
                    <td style={{ fontWeight: 700, color: 'var(--color-fg)' }}>
                      {app.candidate_name || 'Verified Applicant'}
                    </td>
                    <td style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                      {app.candidate_id?.slice(0, 12) || '—'}
                    </td>
                    <td style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)' }}>
                      {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'Recent'}
                    </td>
                    <td>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-primary)', background: 'var(--color-primary-muted)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                        {app.status || 'Applied'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => openDetail(app.candidate_id)}
                        disabled={detailBusy}
                      >
                        <Eye size={13} /> View Detail
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <EmptyState
          title="No applicants yet for this opening"
          description="When candidates apply to this position, their CV extractions and technical assessment scores will be evaluated here."
          icon={Users}
        />
      )}

      {/* Candidate Assessment Detail Modal */}
      <Modal
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title="Candidate Assessment Transcript"
        subtitle={`Detailed review of technical interview responses and sandbox execution.`}
        icon={FileText}
        maxWidth={720}
      >
        {detail ? (
          <div>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 20 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>MCQ Accuracy</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                    {(detail.mcq_score || 0).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Theory Cosine</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-info)' }}>
                    {(detail.descriptive_score || 0).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Coding Sandbox</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-purple)' }}>
                    {(detail.coding_score || 0).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Answer items */}
            {detail.answers?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {detail.answers.map((ans, idx) => (
                  <div key={ans.question_id} style={{ padding: 12, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                    <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-primary)', marginBottom: 4 }}>
                      Question #{idx + 1}
                    </div>
                    {ans.code_text ? (
                      <pre style={{ margin: 0, padding: 8, background: 'var(--color-bg)', borderRadius: 4, fontFamily: 'var(--p-font-mono)', fontSize: '12px', overflowX: 'auto' }}>
                        {ans.code_text}
                      </pre>
                    ) : (
                      <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                        {ans.answer_text || `Selected option: ${ans.selected_option}`}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center' }}>
                Summary score attached without raw question transcript.
              </p>
            )}
          </div>
        ) : (
          <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center' }}>
            No assessment data loaded.
          </p>
        )}
      </Modal>
    </div>
  )
}
