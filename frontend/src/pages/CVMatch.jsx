import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { FileSearch, Upload, BarChart3, Trash2 } from 'lucide-react'
import axios from 'axios'
import { uResumeDelete } from '../api'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const C1 = 'http://127.0.0.1:8001'
const authHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('recruitai.token')}` } })

export default function CVMatch() {
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/login/candidate'); return }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [r1, r2] = await Promise.all([
        axios.get(`${API}/api/v1/resume/`, authHeader()),
        axios.get(`${API}/api/v1/jobs/all`).catch(() => ({ data: [] })),
      ])
      setResumes(r1.data)
      setJobs(r2.data)
    } catch {}
  }

  const match = async () => {
    if (!selectedResume) return toast.error('Select a resume')
    setBusy(true)
    try {
      const r = await axios.get(`${API}/api/v1/resume/match?resume_id=${selectedResume}${selectedJob ? `&job_id=${selectedJob}` : ''}`, authHeader())
      setResult(r.data)
      toast.success(`Score: ${r.data.overall_score.toFixed(1)}%`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Match failed')
    } finally { setBusy(false) }
  }

  const deleteResume = async (id) => {
    if (!confirm('Delete this resume?')) return
    try {
      await uResumeDelete(id)
      toast.success('Resume deleted')
      if (selectedResume === id) setSelectedResume('')
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Delete failed')
    }
  }

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 800, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>CV Match</h1>
      <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>Upload your resume and match against jobs</p>

      <div className="card" style={{ padding: 24, marginBottom: 20 }}>
        <h3 style={{ marginBottom: 16 }}><FileSearch size={16} style={{ color: 'var(--accent)' }} /> Match Setup</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <label>Resume *</label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <select value={selectedResume} onChange={(e) => setSelectedResume(e.target.value)} style={{ flex: 1, padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14 }}>
                <option value="">Select resume...</option>
                {resumes.map((r) => <option key={r.id} value={r.id}>{r.filename}</option>)}
              </select>
              {selectedResume && (
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => deleteResume(selectedResume)} style={{ padding: 8, color: 'var(--danger)' }} title="Delete resume">
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          </div>
          <div>
            <label>Target Job (optional)</label>
            <select value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)} style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14 }}>
              <option value="">Any job...</option>
              {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}{j.company_name ? ` — ${j.company_name}` : ''}</option>)}
            </select>
          </div>
        </div>
        <button className="btn" onClick={match} disabled={busy} style={{ marginTop: 16, width: '100%' }}>
          <BarChart3 size={16} /> {busy ? 'Matching...' : 'Run Match'}
        </button>
      </div>

      {result && (
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Match Results</h3>
          <div className="grid grid-4" style={{ marginBottom: 16 }}>
            <div className="stat"><div className="stat-label">Overall</div><div className="stat-value" style={{ color: 'var(--accent)' }}>{result.overall_score.toFixed(1)}%</div></div>
            <div className="stat"><div className="stat-label">Skills</div><div className="stat-value">{result.skill_score.toFixed(1)}%</div></div>
            <div className="stat"><div className="stat-label">Experience</div><div className="stat-value">{result.experience_score.toFixed(1)}%</div></div>
            <div className="stat"><div className="stat-label">Semantic</div><div className="stat-value">{result.semantic_score.toFixed(1)}%</div></div>
          </div>
          <div className="grid grid-4" style={{ marginBottom: 16 }}>
            <div className="stat"><div className="stat-label">Education</div><div className="stat-value">{result.education_score?.toFixed(1) ?? 'N/A'}%</div></div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>Predicted Role: <strong>{result.predicted_role}</strong> ({(result.role_confidence * 100).toFixed(0)}%)</div>
          </div>
          {result.matched_skills?.length > 0 && (
            <div style={{ marginBottom: 8 }}><span className="muted" style={{ fontSize: 12 }}>Matched: </span>{result.matched_skills.map((s) => <span key={s} className="chip" style={{ fontSize: 11, borderColor: 'var(--accent-2)', color: 'var(--accent-2)' }}>{s}</span>)}</div>
          )}
          {result.missing_skills?.length > 0 && (
            <div><span className="muted" style={{ fontSize: 12 }}>Missing: </span>{result.missing_skills.map((s) => <span key={s} className="chip" style={{ fontSize: 11, borderColor: 'var(--danger)', color: 'var(--danger)' }}>{s}</span>)}</div>
          )}
          {result.career_suggestions?.length > 0 && (
            <div style={{ marginTop: 12, padding: 12, background: 'var(--bg)', borderRadius: 8, fontSize: 13 }}>
              {result.career_suggestions.map((s, i) => <div key={i} style={{ marginBottom: 4 }}>• {s}</div>)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
