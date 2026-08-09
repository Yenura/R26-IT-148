import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { TrendingUp, CheckCircle, Clock, AlertCircle, Download } from 'lucide-react'
import axios from 'axios'

const C4 = 'http://127.0.0.1:8004'
const authHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('recruitai.token')}` } })

export default function Progress() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [popBusy, setPopBusy] = useState(false)
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const r = await axios.get(`${C4}/api/v1/progress/${candidateId}`, authHeader())
      setData(r.data)
    } catch {}
  }

  const populate = async () => {
    setPopBusy(true)
    try {
      const r = await axios.post(`${C4}/api/v1/progress/populate`, { candidate_id: candidateId }, authHeader())
      toast.success(`Added ${r.data.populated} skills from skill gap analysis`)
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'No skill gap report found')
    } finally { setPopBusy(false) }
  }

  const updateStatus = async (skill, status) => {
    try {
      await axios.post(`${C4}/api/v1/progress/update`, {
        candidate_id: candidateId, skill, status, notes: ''
      }, authHeader())
      toast.success(`${skill}: ${status.replace('_', ' ')}`)
      loadData()
    } catch { toast.error('Failed') }
  }

  const stats = data?.stats || {}
  const skills = data?.skills || []
  const pct = stats.completion_pct || 0

  const statusIcon = (s) => s === 'completed' ? <CheckCircle size={16} style={{ color: 'var(--color-success)' }} />
    : s === 'in_progress' ? <Clock size={16} style={{ color: 'var(--color-primary)' }} />
    : <AlertCircle size={16} style={{ color: 'var(--color-fg-muted)' }} />

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <div className="page-head">
        <h1>Skill Progress</h1>
        <p>Track your learning progress across all skills</p>
      </div>

      {/* Stat Strip */}
      <div className="grid grid-4" style={{ marginBottom: 20 }}>
        <div className="stat" style={{ textAlign: 'center' }}>
          <div style={{ position: 'relative', width: 64, height: 64, margin: '0 auto 8px' }}>
            <svg width="64" height="64" viewBox="0 0 64 64">
              <circle cx="32" cy="32" r="28" fill="none" stroke="var(--color-border)" strokeWidth="4" />
              <circle cx="32" cy="32" r="28" fill="none" stroke="var(--color-primary)" strokeWidth="4"
                strokeDasharray={`${pct * 1.76} 176`} strokeLinecap="round" transform="rotate(-90 32 32)" />
            </svg>
            <span style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 800 }}>
              {pct.toFixed(0)}%
            </span>
          </div>
          <div className="stat-label">Complete</div>
        </div>
        <div className="stat"><div className="stat-label">Not Started</div><div className="stat-value">{stats.not_started || 0}</div></div>
        <div className="stat"><div className="stat-label">In Progress</div><div className="stat-value" style={{ color: 'var(--color-primary)' }}>{stats.in_progress || 0}</div></div>
        <div className="stat"><div className="stat-label">Completed</div><div className="stat-value" style={{ color: 'var(--color-success)' }}>{stats.completed || 0}</div></div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
        <button className="btn btn-ghost" onClick={populate} disabled={popBusy}>
          <Download size={16} /> {popBusy ? 'Populating...' : 'Auto-populate from Skill Gap'}
        </button>
      </div>

      {/* Skills List */}
      {skills.length > 0 ? (
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Skills ({skills.length})</h3>
          {skills.map((p) => (
            <div key={p.skill} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 0',
              borderBottom: '1px solid var(--color-border)',
            }}>
              {statusIcon(p.status)}
              <span style={{ flex: 1, fontSize: 14, fontWeight: 500 }}>{p.skill}</span>
              <div style={{ display: 'flex', gap: 4 }}>
                {['not_started', 'in_progress', 'completed'].map((s) => (
                  <button key={s} className={`btn btn-sm ${p.status === s ? 'btn-success' : 'btn-ghost'}`}
                    onClick={() => updateStatus(p.skill, s)}
                    style={{ fontSize: 11, padding: '4px 8px' }}>
                    {s === 'not_started' ? 'New' : s === 'in_progress' ? 'Learning' : 'Done'}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="empty">
            <div className="empty-icon">📊</div>
            <p>No skills tracked yet</p>
            <p style={{ fontSize: 13, marginTop: 8 }}>Run a Skill Gap analysis first, then click "Auto-populate" to import skills.</p>
          </div>
        </div>
      )}
    </div>
  )
}
