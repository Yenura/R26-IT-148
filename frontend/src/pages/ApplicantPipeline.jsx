import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Users, Trophy, ArrowLeft, Mail, Briefcase, Star, Loader } from 'lucide-react'
import { C0, C3 } from '../api'

export default function ApplicantPipeline() {
  const navigate = useNavigate()
  const { jobId } = useParams()
  const [job, setJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [rankings, setRankings] = useState([])
  const [busy, setBusy] = useState(true)
  const [ranking, setRanking] = useState(false)

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
                  fontWeight: 800, fontSize: 14, color: r.passed_hard_filter && i < 2 ? '#fff' : 'var(--text)'
                }}>{r.passed_hard_filter ? r.rank : '✗'}</div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: 15 }}>{r.candidate_name}</span>
                    {r.passed_hard_filter ? (
                      <span className="chip" style={{ fontSize: 10, background: '#2ecc7120', color: '#2ecc71', borderColor: '#2ecc7150' }}>Qualified</span>
                    ) : (
                      <span className="chip" style={{ fontSize: 10, background: '#e74c3c20', color: '#e74c3c', borderColor: '#e74c3c50' }}>
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
                fontWeight: 700, fontSize: 14, color: '#fff'
              }}>
                {(app.candidate_name || '?')[0]?.toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{app.candidate_name || 'Unknown'}</div>
                <div className="muted" style={{ fontSize: 12 }}>
                  Applied {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>
              <button className="btn btn-sm" onClick={() => navigate(`/profile/${app.candidate_id}`)}>
                <Star size={14} /> View
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
