import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ListOrdered, Trophy, Users, Briefcase } from 'lucide-react'
import { c3Roles, c3Rank, c0JobsAll, c3Pipeline } from '../api'

export default function Ranking() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState({})
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [selectedRole, setSelectedRole] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [mode, setMode] = useState('demo') // 'demo' or 'pipeline'

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadRoles()
    loadJobs()
  }, [])

  const loadRoles = async () => {
    try {
      const r = await c3Roles()
      setRoles(r.data.roles || {})
    } catch {}
  }

  const loadJobs = async () => {
    try {
      const r = await c0JobsAll()
      setJobs(r.data || [])
    } catch {}
  }

  const computeDemo = async () => {
    if (!selectedRole) return toast.error('Select a role')
    setBusy(true)
    try {
      const r = await c3Rank({
        job_role: selectedRole,
        candidates: [
          { candidate_id: 'C-1001', candidate_name: 'Ashan', skills: ['Python', 'SQL', 'AWS'], years_experience: 5, edu_level: 2, skill_score_raw: 0.85, P_mcq: 0.8, P_desc: 0.7, P_code: 0.9 },
          { candidate_id: 'C-1002', candidate_name: 'Bimal', skills: ['Java', 'Docker'], years_experience: 3, edu_level: 1, skill_score_raw: 0.60, P_mcq: 0.5, P_desc: 0.6, P_code: 0.4 },
        ],
        w_cv: 0.6, w_int: 0.4,
      })
      setResult(r.data)
    } catch (err) { toast.error('Failed') } finally { setBusy(false) }
  }

  const computePipeline = async () => {
    if (!selectedJob) return toast.error('Select a job')
    setBusy(true)
    try {
      const r = await c3Pipeline(selectedJob)
      setResult(r.data)
    } catch (err) { toast.error('Failed to fetch pipeline data') } finally { setBusy(false) }
  }

  const selectedJobObj = jobs.find(j => j.id === selectedJob)

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 800, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>Ranking</h1>
      <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>Rank candidates for a job role</p>

      {/* Mode toggle */}
      <div className="card" style={{ padding: 16, marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            className={mode === 'demo' ? 'btn' : ''}
            onClick={() => { setMode('demo'); setResult(null) }}
            style={{ flex: 1 }}
          >
            <ListOrdered size={16} /> Demo Mode
          </button>
          <button
            className={mode === 'pipeline' ? 'btn' : ''}
            onClick={() => { setMode('pipeline'); setResult(null) }}
            style={{ flex: 1 }}
          >
            <Users size={16} /> Real Pipeline
          </button>
        </div>
      </div>

      {mode === 'demo' ? (
        <div className="card" style={{ padding: 24, marginBottom: 20 }}>
          <label>Select Role</label>
          <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)} style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, marginBottom: 16 }}>
            <option value="">Choose role...</option>
            {Object.keys(roles).sort().map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <button className="btn" onClick={computeDemo} disabled={busy} style={{ width: '100%' }}><ListOrdered size={16} /> {busy ? 'Computing...' : 'Rank Candidates'}</button>
        </div>
      ) : (
        <div className="card" style={{ padding: 24, marginBottom: 20 }}>
          <label><Briefcase size={14} style={{ verticalAlign: -2 }} /> Select Job</label>
          <select value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)} style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, marginBottom: 16 }}>
            <option value="">Choose job...</option>
            {jobs.map((j) => <option key={j.id} value={j.id}>{j.title} — {j.company_name || 'Unknown'}</option>)}
          </select>
          {selectedJobObj && (
            <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, marginBottom: 16, fontSize: 13 }}>
              <div><strong>Skills:</strong> {selectedJobObj.required_skills?.join(', ') || 'N/A'}</div>
              <div><strong>Experience:</strong> {selectedJobObj.experience_required || 0} years</div>
            </div>
          )}
          <button className="btn" onClick={computePipeline} disabled={busy} style={{ width: '100%' }}><ListOrdered size={16} /> {busy ? 'Fetching & Ranking...' : 'Rank Real Applicants'}</button>
        </div>
      )}

      {result && (
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 16 }}><Trophy size={16} style={{ color: 'var(--accent)' }} /> Results {result.job_role && `— ${result.job_role.replace(/_/g, ' ')}`}</h3>
          {(result.data || []).filter(c => c.rank > 0).map((c, i) => (
            <div key={c.candidate_id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: i === 0 ? 'var(--accent)' : i === 1 ? 'var(--accent-2)' : 'var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14, color: i < 2 ? '#fff' : 'var(--text)' }}>{i + 1}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{c.candidate_name}</div>
                <div className="muted" style={{ fontSize: 12 }}>CSS: {((c.CSS || 0) * 100).toFixed(1)} | CV: {((c.S_cv || 0) * 100).toFixed(1)} | INT: {((c.S_int || 0) * 100).toFixed(1)}{c.ltr_score ? ` | LTR: ${(c.ltr_score * 100).toFixed(1)}` : ''}</div>
              </div>
              <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--accent)' }}>{((c.CSS || 0) * 100).toFixed(0)}%</div>
            </div>
          ))}
          {(result.data || []).filter(c => c.rank === 0).length > 0 && (
            <div style={{ marginTop: 12, padding: 12, background: 'var(--bg)', borderRadius: 8, fontSize: 13, color: 'var(--text-muted)' }}>
              {(result.data || []).filter(c => c.rank === 0).length} candidate(s) did not meet minimum requirements
            </div>
          )}
          {(!result.data || result.data.length === 0) && (
            <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, fontSize: 13, color: 'var(--text-muted)' }}>
              {result.message || 'No candidates found'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
