import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Briefcase, Plus, Users, Trash2, MapPin, Clock, ChevronRight, MessageSquare } from 'lucide-react'
import { C0 } from '../api'

const emptyForm = { title: '', description: '', department: '', location: '', employment_type: 'Full-time', required_skills: '', experience_required: 0, interview_required: false, interview_question_count: 10 }

export default function CompanyDashboard() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [applicantCounts, setApplicantCounts] = useState({})

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') { navigate('/login/company'); return }
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const r = await C0.get('/jobs/')
      setJobs(r.data)
      const counts = {}
      for (const job of r.data) {
        try {
          const ar = await C0.get(`/jobs/${job.id}/applicants`)
          const apps = Array.isArray(ar.data) ? ar.data : ar.data.applicants || []
          counts[job.id] = apps.length
        } catch { counts[job.id] = 0 }
      }
      setApplicantCounts(counts)
    } catch {
      toast.error('Failed to load jobs')
    }
  }

  const createJob = async (e) => {
    e.preventDefault()
    if (!form.title) return toast.error('Title required')
    try {
      const payload = { ...form, required_skills: form.required_skills.split(',').map((s) => s.trim()).filter(Boolean) }
      await C0.post('/jobs/', payload)
      toast.success('Job posted!')
      setShowForm(false)
      setForm(emptyForm)
      loadJobs()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to create job')
    }
  }

  const deleteJob = async (id) => {
    if (!confirm('Delete this job? This cannot be undone.')) return
    try {
      await C0.delete(`/jobs/${id}`)
      toast.success('Deleted')
      loadJobs()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed')
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      <div className="page-head" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Company Dashboard</h1>
          <p>Post jobs and manage applicants</p>
        </div>
        <button className="btn btn-success" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} /> {showForm ? 'Cancel' : 'Post New Job'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-3" style={{ marginBottom: 20 }}>
        <div className="stat"><div className="stat-label">Posted Jobs</div><div className="stat-value">{jobs.length}</div></div>
        <div className="stat"><div className="stat-label">Active</div><div className="stat-value" style={{ color: 'var(--color-success)' }}>{jobs.filter(j => j.status === 'open').length || jobs.length}</div></div>
        <div className="stat"><div className="stat-label">Total Applicants</div><div className="stat-value" style={{ color: 'var(--color-primary)' }}>{Object.values(applicantCounts).reduce((a, b) => a + b, 0)}</div></div>
      </div>

      {/* Create Job Form */}
      {showForm && (
        <form onSubmit={createJob} className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 12 }}>Post New Job</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div><label>Title *</label><input type="text" value={form.title} onChange={set('title')} placeholder="Software Engineer" /></div>
            <div><label>Department</label><input type="text" value={form.department} onChange={set('department')} placeholder="Engineering" /></div>
            <div><label>Location</label><input type="text" value={form.location} onChange={set('location')} placeholder="Remote / New York" /></div>
            <div>
              <label>Type</label>
              <select value={form.employment_type} onChange={set('employment_type')}>
                <option>Full-time</option><option>Part-time</option><option>Contract</option><option>Internship</option>
              </select>
            </div>
            <div><label>Experience Required (years)</label><input type="number" min={0} max={30} value={form.experience_required} onChange={set('experience_required')} /></div>
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={form.interview_required} onChange={(e) => setForm(f => ({ ...f, interview_required: e.target.checked }))} style={{ width: 'auto' }} />
                Interview Required
              </label>
              {form.interview_required && (
                <div style={{ marginTop: 6 }}>
                  <label>Number of Questions</label>
                  <input type="number" min={3} max={30} value={form.interview_question_count} onChange={set('interview_question_count')} />
                </div>
              )}
            </div>
          </div>
          <div style={{ marginTop: 12 }}><label>Required Skills (comma-separated)</label><input type="text" value={form.required_skills} onChange={set('required_skills')} placeholder="Python, React, SQL" /></div>
          <div style={{ marginTop: 12 }}><label>Description</label><textarea value={form.description} onChange={set('description')} placeholder="Job description..." rows={3} /></div>
          <button className="btn btn-success" type="submit" style={{ marginTop: 12 }}>
            <Plus size={16} /> Post Job
          </button>
        </form>
      )}

      {/* Jobs List */}
      {jobs.length === 0 ? (
        <div className="card">
          <div className="empty">
            <div className="empty-icon">💼</div>
            <p>No jobs posted yet</p>
            <p style={{ fontSize: 13, marginTop: 8 }}>Click "Post New Job" to create your first listing.</p>
          </div>
        </div>
      ) : (
        <div className="card">
          {jobs.map((job) => (
            <div key={job.id} onClick={() => navigate(`/company/pipeline/${job.id}`)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 0', borderBottom: '1px solid var(--color-border)', cursor: 'pointer',
              }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 15 }}>{job.title}</div>
                <div className="muted" style={{ fontSize: 12, display: 'flex', gap: 12, marginTop: 4 }}>
                  {job.location && <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><MapPin size={12} /> {job.location}</span>}
                  {job.employment_type && <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={12} /> {job.employment_type}</span>}
                  {job.interview_required && <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-2)' }}><MessageSquare size={12} /> Interview</span>}
                </div>
                {job.required_skills?.length > 0 && (
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
                    {job.required_skills.slice(0, 5).map(s => <span key={s} className="chip" style={{ fontSize: 10 }}>{s}</span>)}
                  </div>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Users size={14} style={{ color: 'var(--color-primary)' }} />
                  <span style={{ fontWeight: 600, fontSize: 14 }}>{applicantCounts[job.id] || 0}</span>
                </div>
                <button className="btn btn-ghost btn-sm" style={{ color: 'var(--color-danger)' }}
                  onClick={(e) => { e.stopPropagation(); deleteJob(job.id) }}>
                  <Trash2 size={14} />
                </button>
                <ChevronRight size={16} style={{ color: 'var(--color-fg-muted)' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
