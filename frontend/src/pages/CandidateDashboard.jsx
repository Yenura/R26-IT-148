import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Upload, Briefcase, MapPin, Clock, ChevronRight, Trash2, Edit3, X, Check } from 'lucide-react'
import { uResumeList, uResumeUpload, uResumeDelete, uResumeUpdate } from '../api'

export default function CandidateDashboard() {
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [applications, setApplications] = useState([])
  const [predictions, setPredictions] = useState([])
  const [uploading, setUploading] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') { navigate('/login/candidate'); return }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      const authH = { headers: { Authorization: `Bearer ${localStorage.getItem('recruitai.token')}` } }
      const [r1, r2, r3, r4] = await Promise.all([
        uResumeList(),
        fetch(`${API}/api/v1/jobs/all`, authH).then(r => r.json()).catch(() => []),
        fetch(`${API}/api/v1/resume/predictions`, authH).then(r => r.json()).catch(() => []),
        fetch(`${API}/api/v1/jobs/applications`, authH).then(r => r.json()).catch(() => []),
      ])
      setResumes(r1.data)
      setJobs(Array.isArray(r2) ? r2 : r2?.data || [])
      setPredictions(Array.isArray(r3) ? r3 : r3?.data || [])
      setApplications(Array.isArray(r4) ? r4 : r4?.applications || [])
    } catch {}
  }

  const upload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      await uResumeUpload(formData)
      toast.success('Resume uploaded')
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally { setUploading(false) }
  }

  const deleteResume = async (id) => {
    if (!confirm('Delete this resume and all its match predictions?')) return
    try {
      await uResumeDelete(id)
      toast.success('Resume deleted')
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Delete failed')
    }
  }

  const startEdit = (resume) => {
    setEditingId(resume.id)
    setEditForm({
      candidate_name: resume.candidate_name || '',
      email: resume.email || '',
      phone: resume.phone || '',
      education: resume.education || '',
      experience_years: resume.experience_years || 0,
      skills: (resume.skills || []).join(', '),
    })
  }

  const saveEdit = async () => {
    try {
      await uResumeUpdate(editingId, {
        candidate_name: editForm.candidate_name,
        email: editForm.email,
        phone: editForm.phone,
        education: editForm.education,
        experience_years: parseFloat(editForm.experience_years) || 0,
        skills: editForm.skills.split(',').map(s => s.trim()).filter(Boolean),
      })
      toast.success('Resume updated')
      setEditingId(null)
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    }
  }

  const appliedJobIds = new Set(applications.filter(a => a.status !== 'withdrawn').map(a => a.job_id))

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      <div className="page-head">
        <h1>Candidate Dashboard</h1>
        <p>Browse jobs, apply, and track your applications</p>
      </div>

      {/* Stat Strip */}
      <div className="grid grid-4 reveal" style={{ marginBottom: 20 }}>
        <div className="stat"><div className="stat-label">Resumes</div><div className="stat-value" style={{ fontFamily: 'var(--p-font-mono)' }}>{resumes.length}</div></div>
        <div className="stat"><div className="stat-label">Applied</div><div className="stat-value" style={{ color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>{applications.filter(a => a.status !== 'withdrawn').length}</div></div>
        <div className="stat"><div className="stat-label">Jobs Open</div><div className="stat-value" style={{ color: 'var(--color-success)', fontFamily: 'var(--p-font-mono)' }}>{jobs.length}</div></div>
        <div className="stat"><div className="stat-label">Matches</div><div className="stat-value" style={{ color: 'var(--color-info)', fontFamily: 'var(--p-font-mono)' }}>{predictions.length}</div></div>
      </div>

      {/* Resumes List */}
      <div className="card reveal" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <h3><Upload size={16} /> My Resumes</h3>
          <label className="btn btn-ghost btn-sm" style={{ cursor: 'pointer' }}>
            <Upload size={14} /> {uploading ? 'Uploading...' : 'Upload New'}
            <input type="file" accept=".pdf,.docx,.doc,.txt" onChange={upload} style={{ display: 'none' }} />
          </label>
        </div>
        {resumes.length === 0 ? (
          <div className="empty" style={{ padding: 24 }}>
            <p>No resumes uploaded yet</p>
            <p style={{ fontSize: 13, marginTop: 4 }}>Upload your first CV to get started with matching and interviews.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {resumes.map((r) => (
              <div key={r.id} style={{ padding: '12px 16px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
                {editingId === r.id ? (
                  /* Edit mode */
                  <div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                      <div><label style={{ fontSize: 11 }}>Name</label><input type="text" value={editForm.candidate_name} onChange={e => setEditForm(f => ({ ...f, candidate_name: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                      <div><label style={{ fontSize: 11 }}>Email</label><input type="email" value={editForm.email} onChange={e => setEditForm(f => ({ ...f, email: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                      <div><label style={{ fontSize: 11 }}>Phone</label><input type="text" value={editForm.phone} onChange={e => setEditForm(f => ({ ...f, phone: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                      <div><label style={{ fontSize: 11 }}>Experience (years)</label><input type="number" min={0} max={50} value={editForm.experience_years} onChange={e => setEditForm(f => ({ ...f, experience_years: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                      <div style={{ gridColumn: 'span 2' }}><label style={{ fontSize: 11 }}>Education</label><input type="text" value={editForm.education} onChange={e => setEditForm(f => ({ ...f, education: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                      <div style={{ gridColumn: 'span 2' }}><label style={{ fontSize: 11 }}>Skills (comma-separated)</label><input type="text" value={editForm.skills} onChange={e => setEditForm(f => ({ ...f, skills: e.target.value }))} style={{ fontSize: 13, padding: '6px 8px' }} /></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button className="btn btn-sm" onClick={saveEdit} style={{ fontSize: 12 }}><Check size={12} /> Save</button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setEditingId(null)} style={{ fontSize: 12 }}><X size={12} /> Cancel</button>
                    </div>
                  </div>
                ) : (
                  /* View mode */
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{r.filename}</div>
                      <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                        {r.candidate_name && <span>{r.candidate_name} · </span>}
                        {r.education && <span>{r.education} · </span>}
                        {r.experience_years > 0 && <span>{r.experience_years} yrs exp</span>}
                        {r.project_experience_years > 0 && <span> · {r.project_experience_years} yrs projects</span>}
                      </div>
                      {/* Academic Projects */}
                      {r.academic_projects?.length > 0 && (
                        <div style={{ marginTop: 6 }}>
                          <span style={{ fontSize: 10, color: 'var(--accent-2)', fontWeight: 600 }}>ACADEMIC</span>
                          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 2 }}>
                            {r.academic_projects.map((p, i) => (
                              <span key={i} className="chip" style={{ fontSize: 9, borderColor: 'var(--accent-2)', color: 'var(--accent-2)' }}>
                                {p.name}{p.dates ? ` (${p.dates})` : ''}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {/* Personal Projects */}
                      {r.personal_projects?.length > 0 && (
                        <div style={{ marginTop: 4 }}>
                          <span style={{ fontSize: 10, color: 'var(--accent)', fontWeight: 600 }}>PERSONAL</span>
                          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 2 }}>
                            {r.personal_projects.map((p, i) => (
                              <span key={i} className="chip" style={{ fontSize: 9, borderColor: 'var(--accent)', color: 'var(--accent)' }}>
                                {p.name}{p.dates ? ` (${p.dates})` : ''}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {/* Skills */}
                      {r.skills?.length > 0 && (
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                          {r.skills.slice(0, 6).map(s => <span key={s} className="chip" style={{ fontSize: 10 }}>{s}</span>)}
                          {r.skills.length > 6 && <span className="muted" style={{ fontSize: 10 }}>+{r.skills.length - 6}</span>}
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => startEdit(r)} style={{ padding: 6 }}><Edit3 size={13} /></button>
                      <button className="btn btn-ghost btn-sm" onClick={() => deleteResume(r.id)} style={{ padding: 6, color: 'var(--danger)' }}><Trash2 size={13} /></button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Jobs List */}
      <div className="card reveal">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3><Briefcase size={16} /> Open Positions</h3>
          <Link to="/candidate/jobs" className="btn btn-ghost btn-sm">View All</Link>
        </div>
        {jobs.length === 0 ? (
          <div className="empty" style={{ padding: 24 }}>
            <p>No jobs posted yet</p>
          </div>
        ) : (
          jobs.slice(0, 6).map((job) => {
            const applied = appliedJobIds.has(job.id)
            return (
              <div key={job.id} onClick={() => navigate(`/candidate/jobs/${job.id}`)}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '12px 0', borderBottom: '1px solid var(--color-border)', cursor: 'pointer',
                }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{job.title}</div>
                  <div className="muted" style={{ fontSize: 12, display: 'flex', gap: 12, marginTop: 4 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><MapPin size={12} /> {job.location || 'Remote'}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={12} /> {job.employment_type || 'Full-time'}</span>
                  </div>
                  {job.required_skills?.length > 0 && (
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                      {job.required_skills.slice(0, 5).map(s => <span key={s} className="chip" style={{ fontSize: 10 }}>{s}</span>)}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {applied && <span className="badge badge-green" style={{ fontSize: 10 }}>Applied</span>}
                  <ChevronRight size={16} style={{ color: 'var(--color-fg-muted)' }} />
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Recent Matches */}
      {predictions.length > 0 && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3 style={{ marginBottom: 12 }}>Recent Matches</h3>
          {predictions.slice(0, 3).map((p) => (
            <div key={p.id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '10px 0', borderBottom: '1px solid var(--color-border)',
            }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{p.predicted_role}</div>
                <div className="muted" style={{ fontSize: 12 }}>Confidence: {(p.role_confidence * 100).toFixed(0)}%</div>
              </div>
              <div style={{ fontSize: 18, fontWeight: 800, color: p.overall_score >= 60 ? 'var(--color-success)' : 'var(--color-primary)' }}>
                {p.overall_score.toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
