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
          <h3 style={{ marginBottom: 16 }}><Trophy size={16} style={{ color: 'var(--accent)' }} /> Candidate Rankings</h3>
          {rankings.filter(r => r.rank > 0).map((r, i) => (
            <div key={r.candidate_id} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 0', borderBottom: '1px solid var(--border)'
            }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                background: i === 0 ? 'var(--accent)' : i === 1 ? 'var(--accent-2)' : 'var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: 14, color: i < 2 ? '#fff' : 'var(--text)'
              }}>{i + 1}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{r.candidate_name}</div>
                <div className="muted" style={{ fontSize: 12 }}>
                  CSS: {((r.CSS || 0) * 100).toFixed(1)}% · CV: {((r.S_cv || 0) * 100).toFixed(1)}% · INT: {((r.S_int || 0) * 100).toFixed(1)}%
                  {r.ltr_score ? ` · LTR: ${(r.ltr_score * 100).toFixed(1)}%` : ''}
                </div>
              </div>
              <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--accent)' }}>
                {((r.CSS || 0) * 100).toFixed(0)}%
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
