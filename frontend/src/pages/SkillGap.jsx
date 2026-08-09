import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Target, CheckCircle } from 'lucide-react'
import axios from 'axios'

const C4 = 'http://127.0.0.1:8004'
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const authHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('recruitai.token')}` } })

export default function SkillGap() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState([])
  const [form, setForm] = useState({ candidate_name: '', job_role: '', skills: '', experience_years: 0, education: '' })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    axios.get(`${C4}/api/v1/skill-gap/roles`).then((r) => setRoles(r.data.roles || [])).catch(() => {})
    loadResumeData()
  }, [])

  const loadResumeData = async () => {
    try {
      const r = await axios.get(`${API}/api/v1/resume/`, authHeader())
      const resumes = r.data
      if (resumes.length > 0) {
        const latest = resumes[0]
        setForm(f => ({
          ...f,
          candidate_name: latest.candidate_name || localStorage.getItem('recruitai.name') || '',
          skills: (latest.skills || []).join(', '),
          experience_years: latest.experience_years || 0,
          education: latest.education || '',
        }))
      } else {
        setForm(f => ({ ...f, candidate_name: localStorage.getItem('recruitai.name') || '' }))
      }
    } catch {}
  }

  const analyze = async (e) => {
    e.preventDefault()
    if (!form.candidate_name || !form.job_role || !form.skills) return toast.error('Fill required fields')
    setBusy(true)
    try {
      const r = await axios.post(`${C4}/api/v1/skill-gap/analyze`, {
        candidate_id: localStorage.getItem('recruitai.user_id') || 'web-user',
        candidate_name: form.candidate_name,
        job_role: form.job_role,
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
        experience_years: parseFloat(form.experience_years) || 0,
        education: form.education,
      })
      setResult(r.data.data || r.data)
    } catch (err) { toast.error('Analysis failed') } finally { setBusy(false) }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 800, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>Skill Gap Analysis</h1>
      <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>Identify missing skills and get a learning roadmap</p>

      <form onSubmit={analyze} className="card" style={{ padding: 24, marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div><label>Your Name *</label><input type="text" value={form.candidate_name} onChange={set('candidate_name')} placeholder="John Doe" /></div>
          <div>
            <label>Target Role *</label>
            <select value={form.job_role} onChange={set('job_role')} style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14 }}>
              <option value="">Select role...</option>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>
        <div style={{ marginTop: 12 }}><label>Your Skills (comma-separated) *</label><input type="text" value={form.skills} onChange={set('skills')} placeholder="Python, SQL, React" /></div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div><label>Years of Experience</label><input type="number" value={form.experience_years} onChange={set('experience_years')} min="0" max="50" /></div>
          <div><label>Education</label><input type="text" value={form.education} onChange={set('education')} placeholder="BSc Computer Science" /></div>
        </div>
        <button className="btn" type="submit" disabled={busy} style={{ marginTop: 16, width: '100%' }}><Target size={16} /> {busy ? 'Analyzing...' : 'Analyze Skills'}</button>
      </form>

      {result && (
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Results</h3>
          <div className="grid grid-3" style={{ marginBottom: 16 }}>
            <div className="stat"><div className="stat-label">Gap Score</div><div className="stat-value" style={{ color: 'var(--accent)' }}>{(result.gap_score * 100).toFixed(0)}%</div></div>
            <div className="stat"><div className="stat-label">Hire Probability</div><div className="stat-value" style={{ color: 'var(--accent-2)' }}>{result.hire_probability?.toFixed(1)}%</div></div>
            <div className="stat"><div className="stat-label">Severity</div><div className="stat-value" style={{ color: result.gap_severity === 'Low' ? 'var(--accent-2)' : 'var(--danger)' }}>{result.gap_severity}</div></div>
          </div>
          {result.missing_required?.length > 0 && (
            <div style={{ marginBottom: 12 }}><span className="muted" style={{ fontSize: 12 }}>Missing Skills: </span>{result.missing_required.map((s) => <span key={s} className="chip" style={{ fontSize: 11, borderColor: 'var(--danger)', color: 'var(--danger)' }}>{s}</span>)}</div>
          )}
          {result.learning_plan?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>Learning Plan:</div>
              {result.learning_plan.map((l, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0', fontSize: 13 }}>
                  <CheckCircle size={14} style={{ color: 'var(--accent-2)', flexShrink: 0 }} />
                  <span>{l.title || l.phase}: {(l.skills || []).join(', ')}</span>
                  {l.resources?.length > 0 && <span className="muted" style={{ fontSize: 11 }}>({l.resources.length} resources)</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
