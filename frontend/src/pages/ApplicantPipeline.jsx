import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Users, Trophy, ArrowLeft, Mail, Briefcase, Star, Loader, X, CheckCircle, XCircle, Code, FileText } from 'lucide-react'
import { C0, C3, uInterviewDetail } from '../api'

export default function ApplicantPipeline() {
  const navigate = useNavigate()
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [rankings, setRankings] = useState([])
  const [busy, setBusy] = useState(true)
  const [ranking, setRanking] = useState(false)
  const [detail, setDetail] = useState(null)
  const [detailBusy, setDetailBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') { navigate('/login/company'); return }
    loadData()
  }, [jobId])

  const loadData = async () => {
    setBusy(true)
    try {
      const [jobRes, appsRes] = await Promise.all([
        C0.get('/jobs/all'),
        C0.get(`/jobs/${jobId}/applicants`)
      ])
      const j = jobRes.data.find(j => j.id === jobId)
      setJob(j)
      const apps = Array.isArray(appsRes.data) ? appsRes.data : appsRes.data.applicants || []
      setApplicants(apps)
    } catch (err) {
      toast.error('Failed to load data')
    } finally {
      setBusy(false)
    }
  }

  const runRanking = async () => {
    setRanking(true)
    try {
      const r = await C3.get(`/rank/pipeline/${jobId}`)
      setRankings(r.data.data || [])
      toast.success(`Ranked ${r.data.data?.length || 0} applicants`)
    } catch (err) {
      toast.error('Failed to run ranking')
    } finally {
      setRanking(false)
    }
  }

  const openDetail = async (candidateId) => {
    setDetailBusy(true)
    try {
      const r = await uInterviewDetail(candidateId)
      setDetail(r.data?.[0] || null)
    } catch (err) {
      toast.error('No interview data found')
    } finally {
      setDetailBusy(false)
    }
  }

  if (busy) return (
    <div className="fade-in" style={{ padding: 28, textAlign: 'center', paddingTop: 80 }}>
      <Loader size={32} className="spin" style={{ color: 'var(--accent)' }} />
      <p style={{ marginTop: 12 }}>Loading applicants...</p>
    </div>
  )

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      <button className="btn btn-ghost" onClick={() => navigate('/company/dashboard')} style={{ marginBottom: 16 }}>
        <ArrowLeft size={16} /> Back to Dashboard
      </button>

      <div className="page-head">
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 4 }}>
            <Users size={20} style={{ verticalAlign: -4, color: 'var(--accent)' }} /> {job?.title || 'Job'}
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {applicants.length} applicant(s) · {job?.location || 'N/A'}
          </p>
        </div>
        <button className="btn" onClick={runRanking} disabled={ranking}>
          <Trophy size={16} /> {ranking ? 'Ranking...' : 'Run Ranking'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-3" style={{ margin: '20px 0' }}>
        <div className="stat">
          <div className="stat-label">Applicants</div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{applicants.length}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Ranked</div>
          <div className="stat-value" style={{ color: 'var(--accent-2)' }}>{rankings.filter(r => r.rank > 0).length}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Interview Required</div>
          <div className="stat-value" style={{ color: job?.interview_required ? 'var(--accent-2)' : 'var(--text-muted)' }}>
            {job?.interview_required ? 'Yes' : 'No'}
          </div>
        </div>
      </div>

      {/* Rankings Table */}
      {rankings.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 16 }}><Trophy size={16} style={{ color: 'var(--accent)' }} /> Candidate Rankings & Score Distribution</h3>
          {rankings.map((r, i) => (
            <div key={r.candidate_id || i} style={{
              padding: '16px 0', borderBottom: '1px solid var(--border)',
              opacity: r.passed_hard_filter ? 1 : 0.65
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 34, height: 34, borderRadius: 8,
                  background: !r.passed_hard_filter ? 'var(--border)' : i === 0 ? 'var(--accent)' : i === 1 ? 'var(--accent-2)' : 'var(--border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 800, fontSize: 14, color: r.passed_hard_filter && i < 2 ? 'var(--color-on-primary)' : 'var(--text)'
                }}>{r.passed_hard_filter ? r.rank : '✗'}</div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: 15 }}>{r.candidate_name}</span>
                    {r.passed_hard_filter ? (
                      <span className="chip" style={{ fontSize: 10, background: 'rgba(34,197,94,0.12)', color: 'var(--color-success)', borderColor: 'rgba(34,197,94,0.3)' }}>Qualified</span>
                    ) : (
                      <span className="chip" style={{ fontSize: 10, background: 'rgba(239,68,68,0.12)', color: 'var(--color-danger)', borderColor: 'rgba(239,68,68,0.3)' }}>
                        {r.filter_fail_reason || 'Disqualified'}
                      </span>
                    )}
                  </div>
                  <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                    Candidate ID: {r.candidate_id}
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 20, fontWeight: 800, color: r.passed_hard_filter ? 'var(--accent)' : 'var(--text-muted)' }}>
                    {((r.CSS || 0) * 100).toFixed(1)}%
                  </div>
                  <div className="muted" style={{ fontSize: 11 }}>
                    CSS Score {r.ltr_score != null && `· LTR: ${(r.ltr_score * 100).toFixed(1)}%`}
                  </div>
                </div>
              </div>

              {/* 6 Marks Distribution (C1 & C2) */}
              <div style={{
                display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: 8, marginTop: 12, padding: '10px 12px', background: 'var(--bg)', borderRadius: 8, fontSize: 12
              }}>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C1: EDUCATION</span>
                  <strong>{((r.S_edu || 0) * 100).toFixed(0)}%</strong>
                </div>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C1: EXPERIENCE</span>
                  <strong>{((r.S_exp || 0) * 100).toFixed(0)}%</strong>
                </div>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C1: SKILL MATCH</span>
                  <strong>{((r.S_skill || 0) * 100).toFixed(0)}%</strong>
                </div>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C2: MCQ SCORE</span>
                  <strong>{((r.P_mcq || 0) * 100).toFixed(0)}%</strong>
                </div>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C2: DESCRIPTIVE</span>
                  <strong>{((r.P_desc || 0) * 100).toFixed(0)}%</strong>
                </div>
                <div>
                  <span className="muted" style={{ display: 'block', fontSize: 10, fontWeight: 600 }}>C2: CODING</span>
                  <strong>{((r.P_code || 0) * 100).toFixed(0)}%</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Applicant List */}
      <div className="card">
        <h3 style={{ marginBottom: 16 }}><Users size={16} /> Applicants</h3>
        {applicants.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">👥</div>
            <p>No applicants yet</p>
          </div>
        ) : (
          applicants.map((app) => (
            <div key={app.candidate_id} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 0', borderBottom: '1px solid var(--border)'
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: 14, color: 'var(--color-on-primary)'
              }}>
                {(app.candidate_name || '?')[0]?.toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{app.candidate_name || 'Unknown'}</div>
                <div className="muted" style={{ fontSize: 12 }}>
                  Applied {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>
              <button className="btn btn-sm btn-ghost" onClick={() => openDetail(app.candidate_id)} disabled={detailBusy}>
                <FileText size={14} /> Interview Details
              </button>
            </div>
          ))
        )}
      </div>

      {/* Interview Detail Modal */}
      {detail && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20
        }} onClick={() => setDetail(null)}>
          <div style={{
            background: 'var(--bg-elevated)', borderRadius: 16, maxWidth: 700, width: '100%',
            maxHeight: '85vh', overflow: 'auto', padding: 28, border: '1px solid var(--border)'
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 800, marginBottom: 2 }}>Interview Results</h2>
                <p className="muted" style={{ fontSize: 13 }}>
                  {detail.candidate_id} · {detail.job_role || 'N/A'} · {detail.grade || 'N/A'}
                </p>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setDetail(null)} style={{ padding: 6 }}>
                <X size={18} />
              </button>
            </div>

            {/* Score Summary */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
              {[
                { label: 'Overall', value: detail.interview_score, color: 'var(--accent)' },
                { label: 'MCQ', value: detail.mcq_score, color: 'var(--accent-2)' },
                { label: 'Descriptive', value: detail.descriptive_score, color: 'var(--color-warning)' },
                { label: 'Coding', value: detail.coding_score, color: 'var(--color-purple)' },
              ].map(s => (
                <div key={s.label} style={{ textAlign: 'center', padding: 12, background: 'var(--bg)', borderRadius: 8 }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{(s.value || 0).toFixed(1)}%</div>
                  <div className="muted" style={{ fontSize: 11 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Weak Topics */}
            {detail.weak_topics?.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>Weak Areas</h3>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {detail.weak_topics.map((t, i) => (
                    <span key={i} className="chip" style={{ fontSize: 11, borderColor: 'var(--danger)', color: 'var(--danger)' }}>{t}</span>
                  ))}
                </div>
              </div>
            )}

            {/* MCQ Details */}
            {detail.mcq_details?.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
                  <CheckCircle size={14} style={{ verticalAlign: -2, color: 'var(--accent-2)' }} /> MCQ Questions ({detail.mcq_correct || 0}/{detail.mcq_total || 0} correct)
                </h3>
                {detail.mcq_details.map((d, i) => (
                  <div key={i} style={{
                    padding: '8px 10px', marginBottom: 4, borderRadius: 6,
                    background: d.is_correct ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
                    border: `1px solid ${d.is_correct ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'}`,
                    fontSize: 13
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Q{i + 1}: {d.question_id}</span>
                      <span style={{ fontWeight: 600, color: d.is_correct ? 'var(--accent-2)' : 'var(--danger)' }}>
                        {d.is_correct ? 'Correct' : 'Wrong'}
                      </span>
                    </div>
                    <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      Selected: option {d.candidate_option} · Correct: option {d.correct_option}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Descriptive Details */}
            {detail.descriptive_details?.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
                  <FileText size={14} style={{ verticalAlign: -2, color: 'var(--color-warning)' }} /> Descriptive Questions
                </h3>
                {detail.descriptive_details.map((d, i) => (
                  <div key={i} style={{
                    padding: '8px 10px', marginBottom: 4, borderRadius: 6,
                    background: 'var(--bg)', fontSize: 13
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Q{i + 1}: {d.question_id}</span>
                      <span style={{ fontWeight: 600 }}>{(d.final_score || 0).toFixed(1)}%</span>
                    </div>
                    <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      Similarity: {((d.cosine_similarity || 0) * 100).toFixed(0)}% · Keywords: {((d.keyword_coverage || 0) * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Coding Details */}
            {detail.coding_details?.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>
                  <Code size={14} style={{ verticalAlign: -2, color: 'var(--color-purple)' }} /> Coding Questions
                </h3>
                {detail.coding_details.map((d, i) => (
                  <div key={i} style={{
                    padding: '8px 10px', marginBottom: 4, borderRadius: 6,
                    background: 'var(--bg)', fontSize: 13
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Q{i + 1}: {d.question_id}</span>
                      <span style={{ fontWeight: 600 }}>{(d.code_score || 0).toFixed(1)}%</span>
                    </div>
                    <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      Tests: {d.tests_passed || 0}/{d.total_tests || 0} passed · Syntax: {d.syntax_valid ? 'Valid' : 'Invalid'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
