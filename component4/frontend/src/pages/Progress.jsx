import { useEffect, useState } from 'react'
import { listReports, getProgress, updateProgress, resetProgress } from '../api'
import toast from 'react-hot-toast'
import { TrendingUp, RefreshCw } from 'lucide-react'

const STATUS_ORDER  = ['not_started', 'in_progress', 'completed']
const STATUS_LABEL  = { not_started: 'Not Started', in_progress: 'In Progress', completed: 'Completed' }
const STATUS_COLOR  = { not_started: '#6b7280', in_progress: '#f59e0b', completed: '#22c55e' }
const STATUS_BADGE  = { not_started: 'badge-info', in_progress: 'badge-warning', completed: 'badge-success' }

export default function Progress() {
  const [reports,  setReports]  = useState([])
  const [selId,    setSelId]    = useState('')
  const [progress, setProgress] = useState(null)
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    listReports().then(r => setReports(r.data.data)).catch(() => {})
  }, [])

  const loadProgress = id => {
    if (!id) return
    setLoading(true)
    getProgress(id)
      .then(r => setProgress(r.data))
      .catch(() => setProgress(null))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadProgress(selId) }, [selId])

  const cycle = async (skill, currentStatus) => {
    const next = STATUS_ORDER[(STATUS_ORDER.indexOf(currentStatus) + 1) % STATUS_ORDER.length]
    try {
      await updateProgress({ candidate_id: selId, skill, status: next, notes: '' })
      toast.success(`${skill} → ${STATUS_LABEL[next]}`)
      loadProgress(selId)
    } catch {
      toast.error('Update failed')
    }
  }

  const handleReset = async () => {
    if (!selId) return
    if (!confirm('Reset all progress for this candidate?')) return
    try {
      await resetProgress(selId)
      toast.success('Progress reset')
      setProgress(null)
    } catch {
      toast.error('Reset failed')
    }
  }

  const stats  = progress?.stats || {}
  const skills = progress?.skills || []
  const pct    = stats.completion_pct || 0

  return (
    <div>
      <div className="page-header">
        <h1>Progress Tracking</h1>
        <p>Track your learning journey skill by skill</p>
      </div>

      {/* Selector */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
              Select Candidate
            </label>
            <select className="form-control"
              value={selId} onChange={e => setSelId(e.target.value)}>
              <option value="">— Pick a candidate —</option>
              {reports.map(r => (
                <option key={r.candidate_id} value={r.candidate_id}>
                  {r.candidate_name} ({r.candidate_id}) — {r.job_role}
                </option>
              ))}
            </select>
          </div>
          {selId && (
            <button className="btn btn-ghost" style={{ marginTop: 22 }} onClick={handleReset}>
              <RefreshCw size={13} /> Reset
            </button>
          )}
        </div>
      </div>

      {!selId ? (
        <div className="empty-state">
          <TrendingUp size={48} />
          <p>Select a candidate to view and update their learning progress</p>
        </div>
      ) : loading ? (
        <div className="loading-wrap"><div className="spinner" /></div>
      ) : !progress ? (
        <div className="empty-state"><p>No progress data yet — run an analysis first</p></div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid-4" style={{ marginBottom: 24 }}>
            {[
              { label: 'Total Skills',  value: stats.total       || 0, color: undefined },
              { label: 'Completed',     value: stats.completed   || 0, color: '#22c55e' },
              { label: 'In Progress',   value: stats.in_progress || 0, color: '#f59e0b' },
              { label: 'Not Started',   value: stats.not_started || 0, color: '#6b7280' },
            ].map(({ label, value, color }) => (
              <div key={label} className="stat-tile">
                <span className="label">{label}</span>
                <span className="value" style={color ? { color } : {}}>{value}</span>
              </div>
            ))}
          </div>

          {/* Completion bar */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
              <p className="card-title" style={{ margin: 0 }}>Overall Completion</p>
              <span style={{ fontWeight: 800, fontSize: 18, color: pct >= 75 ? '#22c55e' : pct >= 40 ? '#f59e0b' : '#ef4444' }}>
                {pct}%
              </span>
            </div>
            <div style={{ background: 'var(--bg-primary)', borderRadius: 999, height: 10, overflow: 'hidden' }}>
              <div style={{
                width: `${pct}%`, height: '100%', borderRadius: 999,
                background: pct >= 75 ? 'linear-gradient(90deg,#22c55e,#16a34a)' :
                            pct >= 40 ? 'linear-gradient(90deg,#f59e0b,#d97706)' :
                                        'linear-gradient(90deg,#ef4444,#dc2626)',
                transition: 'width .5s ease',
              }} />
            </div>
          </div>

          {/* Skill list */}
          <div className="card">
            <p className="card-title">Skill Progress (click status to cycle)</p>
            {skills.length ? (
              <div>
                {skills.map((sk, i) => (
                  <div key={sk.skill} style={{
                    display: 'flex', alignItems: 'center', gap: 14, padding: '12px 0',
                    borderBottom: i < skills.length - 1 ? '1px solid var(--border)' : 'none',
                  }}>
                    {/* Status dot */}
                    <div style={{
                      width: 12, height: 12, borderRadius: '50%', flexShrink: 0,
                      background: STATUS_COLOR[sk.status] || '#6b7280',
                      boxShadow: `0 0 6px ${STATUS_COLOR[sk.status] || '#6b7280'}66`,
                    }} />
                    <span style={{ flex: 1, fontWeight: 600, fontSize: 14 }}>{sk.skill}</span>
                    {sk.notes && (
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {sk.notes}
                      </span>
                    )}
                    {/* Cycle button */}
                    <button
                      className={`badge ${STATUS_BADGE[sk.status]}`}
                      onClick={() => cycle(sk.skill, sk.status)}
                      style={{ cursor: 'pointer', border: 'none', fontSize: 11, padding: '4px 10px' }}
                      title="Click to advance status">
                      {STATUS_LABEL[sk.status]}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state"><p>No skills tracked yet</p></div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
