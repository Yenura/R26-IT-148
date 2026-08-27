import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Users, Trophy, ArrowLeft, X, CheckCircle2, Code, FileText,
  Building2, MapPin, Sparkles, Eye, AlertCircle, Clock, Shield,
  UserCheck, Volume2, Activity
} from 'lucide-react'
import { c0JobsAll, uJobsApplicants, c3Pipeline, uInterviewDetail, uJobsGet } from '../api'
import PageHeader from '../components/PageHeader'
import Modal from '../components/Modal'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

function AnalysisStat({ label, value, unit = '', threshold = 50, invert = false }) {
  const ok = invert ? value >= threshold : value >= threshold
  const color = ok ? 'var(--color-success)' : value >= threshold * 0.5 ? 'var(--color-warning)' : 'var(--color-danger)'
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', fontSize: '11px' }}>
      <span style={{ color: 'var(--color-fg-muted)' }}>{label}</span>
      <span style={{ fontWeight: 700, color, fontFamily: 'var(--p-font-mono)' }}>{value}{unit}</span>
    </div>
  )
}

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
        uJobsGet(jobId).catch(() => c0JobsAll().then((r) => ({ data: (Array.isArray(r.data) ? r.data : []).find((x) => x.id === jobId) }))).catch(() => ({ data: null })),
        uJobsApplicants(jobId).catch(() => ({ data: [] })),
      ])
      setJob(jobRes.data || null)
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
        subtitle={`Detailed review of technical interview responses, timing, and accuracy.`}
        icon={FileText}
        maxWidth={720}
      >
        {detail ? (
          <div>
            {/* Score Summary */}
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 16 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>MCQ Accuracy</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                    {(detail.mcq_score || 0).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>{detail.mcq_correct || 0}/{detail.mcq_total || 0} correct</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Theory Cosine</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-info)' }}>
                    {(detail.descriptive_score || 0).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>{detail.descriptive_total || 0} questions</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Coding Sandbox</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-purple)' }}>
                    {(detail.coding_score || 0).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>{detail.coding_tests_passed || 0} tests passed</div>
                </div>
              </div>
            </div>

            {/* Weak Topics */}
            {detail.weak_topics?.length > 0 && (
              <div style={{ padding: 12, background: 'var(--color-danger-muted)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239,68,68,0.2)', marginBottom: 16 }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-danger)', marginBottom: 4 }}>Weak Areas Identified</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {detail.weak_topics.map((t, i) => (
                    <span key={i} style={{ fontSize: '10px', padding: '2px 8px', background: 'var(--color-bg)', borderRadius: 'var(--radius-full)', color: 'var(--color-fg)' }}>{t}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Integrity Report (job interviews only) */}
            {detail.proctoring && (
              <div style={{ marginBottom: 16 }}>
                {(() => {
                  const p = detail.proctoring
                  const score = p.integrity_score ?? 100
                  const riskLevel = score >= 90 ? 'Low Risk' : score >= 70 ? 'Moderate Risk' : 'High Risk'
                  const riskColor = score >= 90 ? 'var(--color-success)' : score >= 70 ? 'var(--color-warning)' : 'var(--color-danger)'
                  const flags = p.flags || {}
                  const timeline = p.timeline || []
                  return (
                    <>
                      <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                          <Shield size={16} style={{ color: riskColor }} />
                          <div>
                            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>Integrity Report</div>
                            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>Live proctoring during interview</div>
                          </div>
                          <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: riskColor, fontFamily: 'var(--p-font-mono)' }}>{score}</div>
                            <div style={{ fontSize: '10px', color: riskColor, fontWeight: 700 }}>{riskLevel}</div>
                          </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                          {[
                            { label: 'Face absent', value: `${flags.face_absent_seconds || 0}s`, ok: !flags.face_absent_seconds },
                            { label: 'Multiple faces', value: `${flags.multiple_faces_count || 0}x`, ok: !flags.multiple_faces_count },
                            { label: 'Gaze off-screen', value: `${flags.gaze_off_screen_count || 0}x`, ok: !flags.gaze_off_screen_count },
                            { label: 'Second voice', value: `${flags.second_voice_count || 0}x`, ok: !flags.second_voice_count },
                            { label: 'Tab switches', value: `${flags.tab_switch_count || 0}x`, ok: !flags.tab_switch_count },
                            { label: 'Paste events', value: `${flags.paste_event_count || 0}x`, ok: !flags.paste_event_count },
                            { label: 'Code typed fast', value: flags.code_typed_too_fast ? 'Yes' : 'No', ok: !flags.code_typed_too_fast },
                            { label: 'DevTools opened', value: flags.devtools_opened ? 'Yes' : 'No', ok: !flags.devtools_opened },
                          ].map((item) => (
                            <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', fontSize: '11px' }}>
                              <span style={{ color: 'var(--color-fg-muted)' }}>{item.label}</span>
                              <span style={{ fontWeight: 700, color: item.ok ? 'var(--color-success)' : 'var(--color-danger)' }}>{item.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Non-Verbal Behaviour Analysis */}
                      {p.analysis?.nonverbal && (
                        <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 12 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                            <UserCheck size={16} style={{ color: 'var(--color-primary)' }} />
                            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>Non-Verbal Behaviour</div>
                          </div>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                            <AnalysisStat label="Eye Contact" value={p.analysis.nonverbal.eye_contact_pct} unit="%" threshold={70} />
                            <AnalysisStat label="Head Stability" value={p.analysis.nonverbal.head_movement_score} unit="%" threshold={60} />
                          </div>
                        </div>
                      )}

                      {/* Speech & Voice Analysis */}
                      {p.analysis?.speech && (
                        <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 12 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                            <Volume2 size={16} style={{ color: 'var(--color-primary)' }} />
                            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>Speech & Voice</div>
                          </div>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                            <AnalysisStat label="Speech Activity" value={Math.round(p.analysis.speech.speech_ratio * 100)} unit="%" threshold={40} />
                            <AnalysisStat label="Voice Energy" value={Math.round(p.analysis.speech.avg_energy * 100)} unit="%" threshold={30} />
                          </div>
                        </div>
                      )}

                      {/* Stress & Confidence Score */}
                      {p.analysis?.confidence && (
                        <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 12 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                            <Activity size={16} style={{ color: p.analysis.confidence.overall_score >= 70 ? 'var(--color-success)' : p.analysis.confidence.overall_score >= 40 ? 'var(--color-warning)' : 'var(--color-danger)' }} />
                            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>Stress & Confidence</div>
                          </div>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                            <AnalysisStat label="Confidence Score" value={p.analysis.confidence.overall_score} unit="%" threshold={60} invert />
                            <AnalysisStat label="Gaze Aversion" value={p.analysis.confidence.gaze_aversion_rate} unit="%" threshold={30} />
                          </div>
                        </div>
                      )}

                      {/* Timeline */}
                      {timeline.length > 0 && (
                        <div style={{ padding: 12, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', marginBottom: 12 }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Timeline</div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            {timeline.map((ev, i) => (
                              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '11px' }}>
                                <span style={{ fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg-muted)', minWidth: 40 }}>
                                  {Math.floor(ev.t / 60)}:{String(ev.t % 60).padStart(2, '0')}
                                </span>
                                <span style={{ color: 'var(--color-danger)' }}>{ev.event.replace(/_/g, ' ')}</span>
                                {ev.duration > 0 && <span style={{ color: 'var(--color-fg-muted)' }}>({ev.duration}s)</span>}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )
                })()}
              </div>
            )}

            {/* Answer items */}
            {detail.answers?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {detail.answers.map((ans, idx) => {
                  const isWrong = ans.question_type === 'MCQ' && ans.is_correct === false
                  const isCodingWrong = ans.question_type === 'Coding' && (ans.code_score || 0) < 50
                  const highlight = isWrong || isCodingWrong ? 'rgba(239,68,68,0.08)' : 'var(--color-bg-elevated)'
                  const borderColor = isWrong || isCodingWrong ? 'rgba(239,68,68,0.3)' : 'var(--color-border-subtle)'
                  return (
                    <div key={ans.question_id || idx} style={{ padding: 12, background: highlight, borderRadius: 'var(--radius-sm)', border: `1px solid ${borderColor}` }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: isWrong || isCodingWrong ? 'var(--color-danger)' : 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6 }}>
                          {isWrong || isCodingWrong ? <AlertCircle size={13} /> : <CheckCircle2 size={13} />}
                          Q{idx + 1} · {ans.question_type} · {ans.topic || 'General'}
                        </div>
                        {ans.time_taken_seconds > 0 && (
                          <span style={{ fontSize: '10px', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 3 }}>
                            <Clock size={10} /> {ans.time_taken_seconds}s
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', marginBottom: 6, lineHeight: 1.5 }}>
                        {ans.question_text || '(Question text not stored in legacy session)'}
                      </div>
                      {ans.question_type === 'MCQ' && (
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)' }}>
                          <span style={{ fontWeight: 700 }}>Selected:</span> Option {ans.selected_option ?? '?'} {ans.is_correct ? '✓' : `✗ (Correct: Option ${ans.correct_option})`}
                        </div>
                      )}
                      {ans.question_type === 'Descriptive' && (
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', fontStyle: 'italic' }}>
                          {ans.answer_text || '(No answer text stored)'}
                        </div>
                      )}
                      {ans.question_type === 'Coding' && (
                        <div>
                          {ans.code_text && (
                            <pre style={{ margin: '6px 0 0 0', padding: 8, background: 'var(--color-bg)', borderRadius: 4, fontFamily: 'var(--p-font-mono)', fontSize: '11px', overflowX: 'auto', maxHeight: 120 }}>
                              {ans.code_text}
                            </pre>
                          )}
                          <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', marginTop: 4 }}>
                            {ans.tests_passed != null && `Tests: ${ans.tests_passed}/${ans.total_tests} · `}
                            {ans.code_score != null && `Score: ${ans.code_score.toFixed(0)}%`}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
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
