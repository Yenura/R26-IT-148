import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ListOrdered, Trophy, Briefcase } from 'lucide-react'
import { c0JobsAll, c3Pipeline } from '../api'

export default function Ranking() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const r = await c0JobsAll()
      setJobs(r.data || [])
    } catch {}
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

      {result && (
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 16 }}>
            <Trophy size={16} style={{ color: 'var(--accent)' }} /> Results {result.job_role && `— ${result.job_role.replace(/_/g, ' ')}`}
          </h3>
          {(result.data || []).map((c, i) => (
            <div key={c.candidate_id || i} style={{
              padding: '16px 0', borderBottom: '1px solid var(--border)',
              opacity: c.passed_hard_filter ? 1 : 0.65
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: !c.passed_hard_filter ? 'var(--border)' : i === 0 ? 'var(--accent)' : i === 1 ? 'var(--accent-2)' : 'var(--border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 800, fontSize: 14, color: c.passed_hard_filter && i < 2 ? '#fff' : 'var(--text)'
                }}>{c.passed_hard_filter ? c.rank : '✗'}</div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: 14 }}>{c.candidate_name}</span>
                    {c.passed_hard_filter ? (
                      <span className="chip" style={{ fontSize: 10, background: '#2ecc7120', color: '#2ecc71', borderColor: '#2ecc7150' }}>Qualified</span>
                    ) : (
                      <span className="chip" style={{ fontSize: 10, background: '#e74c3c20', color: '#e74c3c', borderColor: '#e74c3c50' }}>
                        {c.filter_fail_reason || 'Disqualified'}
                      </span>
                    )}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>
                    ID: {c.candidate_id} · CSS: {((c.CSS || 0) * 100).toFixed(1)}% · CV: {((c.S_cv || 0) * 100).toFixed(1)}% · INT: {((c.S_int || 0) * 100).toFixed(1)}%
                    {c.ltr_score ? ` · LTR: ${(c.ltr_score * 100).toFixed(1)}%` : ''}
                  </div>
                </div>

                <div style={{ fontSize: 20, fontWeight: 800, color: c.passed_hard_filter ? 'var(--accent)' : 'var(--text-muted)' }}>
                  {((c.CSS || 0) * 100).toFixed(0)}%
                </div>
              </div>

              {/* 6 Marks Breakdown */}
              <div style={{
                display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
                gap: 8, marginTop: 10, padding: '8px 10px', background: 'var(--bg)', borderRadius: 8, fontSize: 11
              }}>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C1: EDUCATION</span><strong>{((c.S_edu || 0) * 100).toFixed(0)}%</strong></div>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C1: EXPERIENCE</span><strong>{((c.S_exp || 0) * 100).toFixed(0)}%</strong></div>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C1: SKILL MATCH</span><strong>{((c.S_skill || 0) * 100).toFixed(0)}%</strong></div>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C2: MCQ</span><strong>{((c.P_mcq || 0) * 100).toFixed(0)}%</strong></div>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C2: DESCRIPTIVE</span><strong>{((c.P_desc || 0) * 100).toFixed(0)}%</strong></div>
                <div><span className="muted" style={{ display: 'block', fontSize: 9 }}>C2: CODING</span><strong>{((c.P_code || 0) * 100).toFixed(0)}%</strong></div>
              </div>
            </div>
          ))}
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
