import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Route } from 'lucide-react'
import { c4CareerRoles, c4CareerPath } from '../api'
import { useAuth } from '../hooks/useAuth'

export default function CareerPath() {
  const navigate = useNavigate()
  useAuth('candidate')
  const [roles, setRoles] = useState([])
  const [form, setForm] = useState({ current_role: '', skills: '', experience_years: 0 })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    c4CareerRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => toast.error('Failed to load roles'))
  }, [])

  const compute = async (e) => {
    e.preventDefault()
    if (!form.current_role) return toast.error('Select a role')
    setBusy(true)
    try {
      const r = await c4CareerPath({
        candidate_id: localStorage.getItem('recruitai.user_id'),
        current_role: form.current_role,
        target_role: form.current_role,
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
        experience_years: parseFloat(form.experience_years) || 0,
      })
      setResult(r.data.data || r.data)
    } catch (err) { toast.error('Failed to compute path') } finally { setBusy(false) }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const difficultyColor = (d) => d === 'Easy' ? 'var(--accent-2)' : d === 'Medium' ? 'var(--accent)' : 'var(--danger)'

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <div className="page-head">
        <h1>Career Path</h1>
        <p>Explore vertical growth and lateral transitions from your current role</p>
      </div>

      <form onSubmit={compute} className="card">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label>Current Role *</label>
            <select value={form.current_role} onChange={set('current_role')}>
              <option value="">Select role...</option>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label>Years of Experience</label>
            <input type="number" value={form.experience_years} onChange={set('experience_years')} min="0" max="50" />
          </div>
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Your Skills (comma-separated)</label>
          <input type="text" value={form.skills} onChange={set('skills')} placeholder="Python, SQL, React, Docker" />
        </div>
        <button className="btn" type="submit" disabled={busy} style={{ marginTop: 16, width: '100%' }}>
          <Route size={16} /> {busy ? 'Computing...' : 'Plan My Path'}
        </button>
      </form>

      {result && (
        <>
          {/* Vertical Path */}
          {result.vertical_path && result.vertical_path.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 16 }}>Growth Track: {result.current_role}</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                {result.vertical_path.map((node, i) => (
                  <div key={i} style={{ display: 'flex', gap: 12, position: 'relative' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div style={{
                        width: 28, height: 28, borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 12, fontWeight: 700, flexShrink: 0,
                        background: node.status === 'current' ? 'var(--color-primary)' : node.status === 'done' ? 'var(--color-success)' : 'var(--color-border)',
                        color: node.status === 'current' || node.status === 'done' ? 'white' : 'var(--color-fg-muted)',
                        boxShadow: node.status === 'current' ? '0 0 12px var(--color-primary-muted)' : 'none',
                      }}>
                        {node.status === 'done' ? '✓' : i + 1}
                      </div>
                      {i < result.vertical_path.length - 1 && (
                        <div style={{ width: 2, flex: 1, minHeight: 20, background: node.status === 'done' ? 'var(--color-success)' : 'var(--color-border)' }} />
                      )}
                    </div>
                    <div style={{ paddingBottom: 16 }}>
                      <div style={{
                        fontWeight: node.status === 'current' ? 700 : 500, fontSize: 14,
                        color: node.status === 'upcoming' ? 'var(--color-fg-muted)' : 'var(--color-fg)',
                      }}>
                        {node.title}
                        {node.status === 'current' && <span className="badge badge-blue" style={{ marginLeft: 8, fontSize: 10 }}>Current</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Lateral Transitions */}
          {result.transitions && result.transitions.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 4 }}>Lateral Transitions</h3>
              <p className="muted" style={{ fontSize: 13, marginBottom: 16 }}>Roles you can transition to based on your skills</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {result.transitions.map((t, i) => (
                  <div key={i} style={{
                    padding: 16, borderRadius: 8, border: '1px solid var(--color-border)',
                    background: 'var(--color-bg-elevated)',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ fontWeight: 600, fontSize: 15 }}>{t.target_role}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span className="badge" style={{
                          fontSize: 11,
                          background: difficultyColor(t.difficulty) + '20',
                          color: difficultyColor(t.difficulty),
                        }}>{t.difficulty}</span>
                        <span style={{ fontWeight: 700, fontSize: 14, color: difficultyColor(t.difficulty) }}>{t.readiness_pct}%</span>
                      </div>
                    </div>

                    {/* Readiness bar */}
                    <div className="progress-bar" style={{ marginBottom: 10 }}>
                      <div style={{ width: `${t.readiness_pct}%`, background: difficultyColor(t.difficulty) }} />
                    </div>

                    {t.matching_skills?.length > 0 && (
                      <div style={{ marginBottom: 6 }}>
                        <span className="muted" style={{ fontSize: 11 }}>You have: </span>
                        {t.matching_skills.map((s) => <span key={s} className="chip" style={{ fontSize: 10, borderColor: 'var(--color-success)', color: 'var(--color-success)' }}>{s}</span>)}
                      </div>
                    )}
                    {t.missing_required?.length > 0 && (
                      <div>
                        <span className="muted" style={{ fontSize: 11 }}>Need to learn: </span>
                        {t.missing_required.map((s) => <span key={s} className="chip" style={{ fontSize: 10, borderColor: 'var(--color-warning)', color: 'var(--color-warning)' }}>{s}</span>)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Role Gap */}
          {result.missing_for_current?.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 8 }}>Skills Gap for {result.current_role}</h3>
              <p className="muted" style={{ fontSize: 13, marginBottom: 12 }}>Skills you still need for your current role</p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {result.missing_for_current.map((s) => <span key={s} className="chip" style={{ fontSize: 11, borderColor: 'var(--color-warning)', color: 'var(--color-warning)' }}>{s}</span>)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
