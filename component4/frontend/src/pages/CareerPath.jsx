import { useEffect, useState } from 'react'
import { listReports, generateCareerPath, getCareerResources } from '../api'
import { MapPin, ExternalLink, ChevronRight } from 'lucide-react'

const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'Machine Learning Engineer',
  'Frontend Developer', 'Backend Developer', 'DevOps Engineer',
  'Cybersecurity Analyst', 'Cloud Solutions Architect',
  'Database Administrator', 'Mobile App Developer',
]

const LEVEL_COLOR = {
  'Junior': '#6c63ff', 'Mid-Level': '#3b82f6', 'Senior': '#06b6d4',
  'Lead': '#f59e0b', 'Principal / Staff': '#ef4444',
}

export default function CareerPath() {
  const [reports,    setReports]    = useState([])
  const [selId,      setSelId]      = useState('')
  const [selRole,    setSelRole]    = useState('Data Scientist')
  const [path,       setPath]       = useState(null)
  const [resources,  setResources]  = useState([])
  const [loading,    setLoading]    = useState(false)
  const [resLoading, setResLoading] = useState(false)

  useEffect(() => {
    listReports().then(r => setReports(r.data.data)).catch(() => {})
    fetchResources('Data Scientist')
  }, [])

  const fetchResources = role => {
    setResLoading(true)
    getCareerResources(role)
      .then(r => setResources(r.data.resources || []))
      .catch(() => setResources([]))
      .finally(() => setResLoading(false))
  }

  const handleGenerate = async () => {
    const cand = reports.find(r => r.candidate_id === selId)
    if (!cand) return
    setLoading(true)
    try {
      const res = await generateCareerPath({
        candidate_id:     cand.candidate_id,
        current_role:     cand.job_role,
        skills:           cand.present_skills || [],
        experience_years: cand.experience_years || 3,
        job_level:        cand.job_level || 'Mid-Level',
      })
      setPath(res.data.data)
    } catch { } finally { setLoading(false) }
  }

  const handleRoleChange = role => {
    setSelRole(role)
    fetchResources(role)
  }

  return (
    <div>
      <div className="page-header">
        <h1>Career Path &amp; Learning Resources</h1>
        <p>Visualise your growth track and access curated learning resources per job role</p>
      </div>

      {/* Controls */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="grid-2" style={{ gap: 16, alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
              Select Candidate
            </label>
            <select className="form-control"
              value={selId} onChange={e => setSelId(e.target.value)}>
              <option value="">— Pick a candidate —</option>
              {reports.map(r => (
                <option key={r.candidate_id} value={r.candidate_id}>
                  {r.candidate_name} — {r.job_role}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: 6 }}>
              Job Role (for resources)
            </label>
            <select className="form-control"
              value={selRole} onChange={e => handleRoleChange(e.target.value)}>
              {JOB_ROLES.map(r => <option key={r}>{r}</option>)}
            </select>
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <button className="btn btn-primary" disabled={!selId || loading} onClick={handleGenerate}>
            {loading
              ? <><span style={{ display: 'inline-block', width: 14, height: 14, border: '2px solid #ffffff55', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin .8s linear infinite' }} /> Generating…</>
              : <><MapPin size={14} /> Generate Path</>}
          </button>
        </div>
      </div>

      {/* Career path nodes */}
      {path && (
        <div className="card" style={{ marginBottom: 24 }}>
          <p className="card-title"><MapPin size={15} /> Career Track — {path.current_role}</p>
          <div style={{ display: 'flex', gap: 0, overflowX: 'auto', paddingBottom: 8 }}>
            {path.vertical_path.map((node, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{
                  padding: '10px 18px', borderRadius: 10, minWidth: 120, textAlign: 'center',
                  background: node.current
                    ? 'linear-gradient(135deg, rgba(108,99,255,.35), rgba(108,99,255,.15))'
                    : 'var(--bg-secondary)',
                  border: `2px solid ${node.current ? '#6c63ff' : 'var(--border)'}`,
                  color: node.current ? 'var(--accent-light)' : 'var(--text-muted)',
                  fontWeight: node.current ? 800 : 500,
                  fontSize: 12,
                  flexShrink: 0,
                }}>
                  <div style={{ fontSize: 10, marginBottom: 4, opacity: 0.7 }}>L{node.level}</div>
                  {node.title}
                  {node.current && <div style={{ fontSize: 9, marginTop: 4, color: '#22c55e' }}>◀ You are here</div>}
                </div>
                {i < path.vertical_path.length - 1 && (
                  <ChevronRight size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, margin: '0 4px' }} />
                )}
              </div>
            ))}
          </div>

          <div className="grid-2" style={{ marginTop: 20, gap: 16 }}>
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Current Level</p>
              <span className="badge badge-info" style={{ fontSize: 13 }}>{path.current_level}</span>
            </div>
            <div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Skill Match</p>
              <span style={{ fontSize: 18, fontWeight: 800, color: '#6c63ff' }}>{path.skill_match_pct}%</span>
            </div>
            {path.missing_for_current?.length > 0 && (
              <div style={{ gridColumn: '1/-1' }}>
                <p style={{ fontSize: 12, color: 'var(--warning)', marginBottom: 8 }}>To reach next level, learn:</p>
                {path.missing_for_current.map((s, i) => (
                  <span key={i} className="skill-chip chip-required">{s}</span>
                ))}
              </div>
            )}
            {path.transitions?.length > 0 && (
              <div style={{ gridColumn: '1/-1' }}>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Lateral career moves:</p>
                {path.transitions.map((s, i) => (
                  <span key={i} className="skill-chip chip-optional">{s}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resources */}
      <div className="card">
        <p className="card-title" style={{ marginBottom: 16 }}>
          📚 Learning Resources — {selRole}
        </p>
        {resLoading ? (
          <div className="loading-wrap" style={{ minHeight: 120 }}>
            <div className="spinner" />
          </div>
        ) : resources.length ? (
          <div>
            {resources.map((r, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 14,
                padding: '14px 0',
                borderBottom: i < resources.length - 1 ? '1px solid var(--border)' : 'none',
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                  background: 'rgba(108,99,255,.15)', border: '1px solid rgba(108,99,255,.25)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, fontWeight: 800, color: 'var(--accent-light)',
                }}>{i + 1}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 700, fontSize: 13 }}>{r.skill}</p>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{r.course}</p>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.duration} · {r.level}</p>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
                  <span className={`badge ${r.priority === 'Required' ? 'badge-danger' : 'badge-info'}`}>{r.priority}</span>
                  <a href={r.url} target="_blank" rel="noreferrer"
                    className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}>
                    Open <ExternalLink size={11} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state"><p>No resources found for this role</p></div>
        )}
      </div>
    </div>
  )
}
