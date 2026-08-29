import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Route, Sparkles } from 'lucide-react'
import { c4CareerRoles, c4CareerPath, uResumeList } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'

export default function CareerPath() {
  const navigate = useNavigate()
  useAuth('candidate')
  const [roles, setRoles] = useState([])
  const [form, setForm] = useState({ current_role: '', skills: '', experience_years: 0 })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    c4CareerRoles().then((r) => setRoles(r?.data?.roles || [])).catch(() => toast.error('Failed to load roles'))
    
    // Auto-populate from candidate's latest resume
    uResumeList().then((r) => {
      const resumeList = Array.isArray(r.data) ? r.data : []
      if (resumeList.length > 0) {
        const topResume = resumeList[0]
        setForm((f) => ({
          ...f,
          skills: (topResume.skills || []).join(', '),
          experience_years: topResume.experience_years || 0,
        }))
      }
    }).catch(() => {})
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

  const difficultyColor = (d) => d === 'Easy' ? 'var(--color-success)' : d === 'Medium' ? 'var(--color-primary)' : 'var(--color-danger)'

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <PageHeader
        badge="Component 4 Career Engine"
        title="Career Path Explorer"
        description="Explore vertical growth and lateral transitions from your current role."
        icon={Route}
      />

      <form onSubmit={compute} className="card" style={{ padding: 'var(--p-space-6)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Current Role *</label>
            <select
              value={form.current_role}
              onChange={set('current_role')}
              style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
            >
              <option value="">Select role...</option>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Years of Experience</label>
            <input
              type="number"
              value={form.experience_years}
              onChange={set('experience_years')}
              min="0"
              max="50"
              style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
            />
          </div>
        </div>
        <div style={{ marginTop: 12 }}>
          <label style={{ fontSize: '12px', marginTop: 0 }}>Your Skills (comma-separated)</label>
          <input
            type="text"
            value={form.skills}
            onChange={set('skills')}
            placeholder="Python, SQL, React, Docker"
            style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
          />
        </div>
        <button
          className="btn btn-primary"
          type="submit"
          disabled={busy}
          style={{ marginTop: 16, width: '100%', padding: '12px 20px', fontWeight: 700 }}
        >
          <Route size={16} /> {busy ? 'Computing...' : 'Plan My Path'}
        </button>
      </form>

      {result && (
        <>
          {/* Vertical Path */}
          {result.vertical_path && result.vertical_path.length > 0 && (
            <div className="card" style={{ padding: 'var(--p-space-6)' }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
                Growth Track: {result.current_role}
              </h3>
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
                        {node.status === 'current' && (
                          <span style={{
                            marginLeft: 8, fontSize: 10, fontWeight: 700,
                            padding: '2px 8px', borderRadius: 9999,
                            background: 'var(--color-primary-muted)', color: 'var(--color-primary)',
                          }}>Current</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Lateral Transitions */}
          {result.transitions && result.transitions.length > 0 && (
            <div className="card" style={{ padding: 'var(--p-space-6)' }}>
              <h3 style={{ margin: '0 0 4px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>Lateral Transitions</h3>
              <p style={{ fontSize: 13, color: 'var(--color-fg-muted)', margin: '0 0 16px 0' }}>Roles you can transition to based on your skills</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {result.transitions.map((t, i) => (
                  <div key={i} style={{
                    padding: 16, borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)',
                    background: 'var(--color-bg-elevated)',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--color-fg)' }}>{t.target_role}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{
                          fontSize: 11, fontWeight: 700,
                          padding: '2px 8px', borderRadius: 9999,
                          background: difficultyColor(t.difficulty) + '20',
                          color: difficultyColor(t.difficulty),
                        }}>{t.difficulty}</span>
                        <span style={{ fontWeight: 700, fontSize: 14, color: difficultyColor(t.difficulty) }}>{t.readiness_pct}%</span>
                      </div>
                    </div>

                    <div className="progress-bar" style={{ marginBottom: 10 }}>
                      <div style={{ width: `${t.readiness_pct}%`, background: difficultyColor(t.difficulty) }} />
                    </div>

                    {t.matching_skills?.length > 0 && (
                       <div style={{ marginBottom: 6 }}>
                         <span style={{ fontSize: 11, color: 'var(--color-fg-muted)' }}>You have: </span>
                         {[...new Set(t.matching_skills)].map((s, i) => (
                           <span key={`${s}-${i}`} className="chip" style={{
                            fontSize: 10, padding: '2px 8px',
                            background: 'var(--color-success-muted)', color: 'var(--color-success)',
                            border: '1px solid rgba(16, 185, 129, 0.3)',
                          }}>{s}</span>
                        ))}
                      </div>
                    )}
                    {t.missing_required?.length > 0 && (
                       <div>
                         <span style={{ fontSize: 11, color: 'var(--color-fg-muted)' }}>Need to learn: </span>
                         {[...new Set(t.missing_required)].map((s, i) => (
                           <span key={`${s}-${i}`} className="chip" style={{
                            fontSize: 10, padding: '2px 8px',
                            background: 'var(--color-warning-muted)', color: 'var(--color-warning)',
                            border: '1px solid rgba(245, 158, 11, 0.3)',
                          }}>{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Role Gap */}
          {result.missing_for_current?.length > 0 && (
            <div className="card" style={{ padding: 'var(--p-space-6)' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>Skills Gap for {result.current_role}</h3>
              <p style={{ fontSize: 13, color: 'var(--color-fg-muted)', margin: '0 0 12px 0' }}>Skills you still need for your current role</p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                 {[...new Set(result.missing_for_current)].map((s, i) => (
                   <span key={`${s}-${i}`} className="chip" style={{
                    fontSize: 11, padding: '3px 10px',
                    background: 'var(--color-warning-muted)', color: 'var(--color-warning)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                  }}>{s}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
