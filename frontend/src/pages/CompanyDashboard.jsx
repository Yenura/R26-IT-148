import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Briefcase, Plus, Users, Trash2, MapPin, Clock, ChevronRight, MessageSquare, Sparkles } from 'lucide-react'
import { C0 } from '../api'
import ConfirmDialog from '../components/ConfirmDialog'

const STANDARD_ROLES = {
  'Software Engineer': 'Python, Java, Git, REST APIs, SQL, Data Structures',
  'Data Scientist': 'Python, R, Machine Learning, SQL, Statistics, Pandas',
  'Machine Learning Engineer': 'Python, PyTorch, TensorFlow, MLOps, Docker, NLP',
  'DevOps Engineer': 'Docker, Kubernetes, CI/CD, AWS, Terraform, Linux',
  'Cybersecurity Analyst': 'Network Security, SIEM, Firewalls, Threat Analysis, Linux',
  'Cloud Solutions Architect': 'AWS, Azure, Cloud Architecture, Terraform, Docker, Microservices',
  'Database Administrator': 'PostgreSQL, MySQL, Database Tuning, SQL, Backup & Recovery',
  'Frontend Developer': 'React, JavaScript, TypeScript, HTML/CSS, Redux, Tailwind',
  'Backend Developer': 'Node.js, Python, REST APIs, PostgreSQL, Redis, Docker',
  'Mobile App Developer': 'Flutter, React Native, iOS, Android, Swift, Kotlin',
  'Full Stack Developer': 'React, Node.js, TypeScript, PostgreSQL, Docker, Git',
  'QA/Test Automation Engineer': 'Selenium, Cypress, TestNG, Python, JIRA, CI/CD',
  'Data Engineer': 'SQL, Apache Spark, Python, ETL Pipelines, Kafka, BigQuery',
  'Site Reliability Engineer (SRE)': 'Kubernetes, Prometheus, Linux, Incident Management, Python',
  'UI/UX Designer': 'Figma, Adobe XD, Wireframing, User Research, Prototyping',
  'Network Engineer': 'Cisco, Routing & Switching, TCP/IP, Firewalls, VPN, Wireshark',
  'Business/Systems Analyst': 'Requirements Gathering, SQL, Agile, UML, JIRA, Business Process',
  'AI/NLP Engineer': 'NLP, Transformers, HuggingFace, PyTorch, LLMs, Python',
  'Blockchain Developer': 'Solidity, Ethereum, Smart Contracts, Web3.js, Rust',
  'Embedded Systems Engineer': 'C, C++, RTOS, Microcontrollers, Embedded Linux, I2C/SPI',
}

const emptyForm = {
  title: '',
  description: '',
  department: '',
  location: '',
  employment_type: 'Full-time',
  required_skills: '',
  experience_required: 0,
  education_required: 'Bachelor Degree',
  interview_required: true,
  interview_question_count: 10,
}

export default function CompanyDashboard() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [applicantCounts, setApplicantCounts] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') {
      navigate('/login/company')
      return
    }
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      let r
      try {
        r = await C0.get('/jobs')
      } catch {
        r = await C0.get('/jobs/')
      }
      const jobList = Array.isArray(r.data) ? r.data : []
      setJobs(jobList)

      const counts = {}
      for (const job of jobList) {
        try {
          const ar = await C0.get(`/jobs/${job.id}/applicants`)
          const apps = Array.isArray(ar.data) ? ar.data : ar.data.applicants || []
          counts[job.id] = apps.length
        } catch {
          counts[job.id] = 0
        }
      }
      setApplicantCounts(counts)
    } catch (err) {
      toast.error('Failed to load jobs')
    }
  }

  const handleRoleSelect = (roleName) => {
    if (!roleName) return
    const suggestedSkills = STANDARD_ROLES[roleName] || ''
    setForm((f) => ({
      ...f,
      title: roleName,
      required_skills: f.required_skills ? f.required_skills : suggestedSkills,
    }))
  }

  const createJob = async (e) => {
    e.preventDefault()
    if (!form.title || !form.title.trim()) {
      return toast.error('Job Title is required')
    }

    const skillsArray = typeof form.required_skills === 'string'
      ? form.required_skills.split(',').map((s) => s.trim()).filter(Boolean)
      : form.required_skills || []

    const expReq = parseInt(form.experience_required, 10)
    const iqCount = parseInt(form.interview_question_count, 10)

    const payload = {
      title: form.title.trim(),
      department: form.department?.trim() || '',
      location: form.location?.trim() || '',
      employment_type: form.employment_type || 'Full-time',
      experience_required: isNaN(expReq) ? 0 : Math.max(0, expReq),
      education_required: form.education_required || 'Bachelor Degree',
      required_skills: skillsArray,
      preferred_skills: [],
      description: form.description?.trim() || '',
      responsibilities: '',
      salary_range: '',
      status: 'open',
      interview_required: Boolean(form.interview_required),
      interview_question_count: isNaN(iqCount) ? 10 : Math.max(3, Math.min(30, iqCount)),
    }

    setSubmitting(true)
    try {
      let r
      try {
        r = await C0.post('/jobs', payload)
      } catch (err) {
        if (err?.response?.status === 307 || err?.response?.status === 404) {
          r = await C0.post('/jobs/', payload)
        } else {
          throw err
        }
      }
      toast.success('Job posted successfully!')
      setShowForm(false)
      setForm(emptyForm)
      await loadJobs()
    } catch (err) {
      console.error('Job creation error:', err)
      const detail = err?.response?.data?.detail
      if (Array.isArray(detail)) {
        toast.error(detail.map((d) => d.msg || d.message).join(', '))
      } else if (typeof detail === 'string') {
        toast.error(detail)
      } else {
        toast.error('Failed to create job post. Check backend server.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const deleteJob = async (id) => {
    setConfirm({
      open: true,
      title: 'Delete this job?',
      message: 'This action cannot be undone. All applicant data for this job will be removed.',
      danger: true,
      action: async () => {
        try {
          await C0.delete(`/jobs/${id}`)
          toast.success('Deleted')
          loadJobs()
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Failed')
        }
      }
    })
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto', paddingBottom: 40 }}>
      <div className="page-head" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Company Dashboard</h1>
          <p>Post jobs, configure interview criteria, and manage candidate ranking</p>
        </div>
        <button className="btn btn-success" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} /> {showForm ? 'Cancel' : 'Post New Job'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-3 reveal" style={{ marginBottom: 20 }}>
        <div className="stat">
          <div className="stat-label">Posted Jobs</div>
          <div className="stat-value" style={{ fontFamily: 'var(--p-font-mono)' }}>{jobs.length}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Active</div>
          <div className="stat-value" style={{ color: 'var(--color-success)', fontFamily: 'var(--p-font-mono)' }}>
            {jobs.filter((j) => j.status === 'open').length || jobs.length}
          </div>
        </div>
        <div className="stat">
          <div className="stat-label">Total Applicants</div>
          <div className="stat-value" style={{ color: 'var(--color-primary)', fontFamily: 'var(--p-font-mono)' }}>
            {Object.values(applicantCounts).reduce((a, b) => a + b, 0)}
          </div>
        </div>
      </div>

      {/* Create Job Form */}
      {showForm && (
        <form onSubmit={createJob} className="card" style={{ marginBottom: 24, padding: 24 }}>
          <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Plus size={18} style={{ color: 'var(--color-primary)' }} /> Post New Job Listing
          </h3>

          {/* Quick role selector */}
          <div style={{ marginBottom: 16, padding: 12, background: 'var(--bg)', borderRadius: 8 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              <Sparkles size={14} style={{ color: 'var(--accent)' }} /> Quick Fill by Standard 20 IT Roles:
            </label>
            <select
              onChange={(e) => handleRoleSelect(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'var(--input-bg)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                fontSize: 13,
              }}
            >
              <option value="">Select a standard role to auto-fill...</option>
              {Object.keys(STANDARD_ROLES).map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div>
              <label>Job Title *</label>
              <input
                type="text"
                value={form.title}
                onChange={set('title')}
                placeholder="Software Engineer"
                required
              />
            </div>
            <div>
              <label>Department</label>
              <input
                type="text"
                value={form.department}
                onChange={set('department')}
                placeholder="Engineering"
              />
            </div>
            <div>
              <label>Location</label>
              <input
                type="text"
                value={form.location}
                onChange={set('location')}
                placeholder="Remote / Colombo / Hybrid"
              />
            </div>
            <div>
              <label>Employment Type</label>
              <select value={form.employment_type} onChange={set('employment_type')}>
                <option>Full-time</option>
                <option>Part-time</option>
                <option>Contract</option>
                <option>Internship</option>
              </select>
            </div>
            <div>
              <label>Experience Required (years)</label>
              <input
                type="number"
                min={0}
                max={30}
                value={form.experience_required}
                onChange={set('experience_required')}
              />
            </div>
            <div>
              <label>Education Required</label>
              <select value={form.education_required} onChange={set('education_required')}>
                <option>Bachelor Degree</option>
                <option>Master Degree</option>
                <option>Diploma</option>
                <option>PhD</option>
                <option>Any Education</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 14 }}>
            <label>Required Skills (comma-separated)</label>
            <input
              type="text"
              value={form.required_skills}
              onChange={set('required_skills')}
              placeholder="Python, React, SQL, Docker, AWS"
            />
          </div>

          <div style={{ marginTop: 14, padding: 12, background: 'var(--bg)', borderRadius: 8 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontWeight: 600 }}>
              <input
                type="checkbox"
                checked={form.interview_required}
                onChange={(e) => setForm((f) => ({ ...f, interview_required: e.target.checked }))}
                style={{ width: 'auto' }}
              />
              Require Component 2 AI Interview Assessment
            </label>
            {form.interview_required && (
              <div style={{ marginTop: 10, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: 12 }}>Number of Questions (3 - 30)</label>
                  <input
                    type="number"
                    min={3}
                    max={30}
                    value={form.interview_question_count}
                    onChange={set('interview_question_count')}
                  />
                </div>
                <div style={{ fontSize: 12, display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
                  Questions will evaluate MCQ ($P_{`{mcq}`}$), Descriptive ($P_{`{desc}`}$), and Coding ($P_{`{code}`}$) skills.
                </div>
              </div>
            )}
          </div>

          <div style={{ marginTop: 14 }}>
            <label>Job Description</label>
            <textarea
              value={form.description}
              onChange={set('description')}
              placeholder="Provide a detailed job description..."
              rows={3}
            />
          </div>

          <div style={{ marginTop: 16, display: 'flex', gap: 10 }}>
            <button className="btn btn-success" type="submit" disabled={submitting}>
              <Plus size={16} /> {submitting ? 'Posting Job...' : 'Publish Job Listing'}
            </button>
            <button className="btn btn-ghost" type="button" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Jobs List */}
      {jobs.length === 0 ? (
        <div className="card">
          <div className="empty">
            <Briefcase size={32} style={{ color: 'var(--color-fg-muted)', marginBottom: 12, opacity: 0.4 }} />
            <p>No jobs posted yet</p>
            <p style={{ fontSize: 13, marginTop: 8 }}>Click "Post New Job" to create your first listing.</p>
          </div>
        </div>
      ) : (
        <div className="card" style={{ padding: 16 }}>
          <h3 style={{ marginBottom: 12 }}><Briefcase size={16} /> Posted Job Listings ({jobs.length})</h3>
          {jobs.map((job) => (
            <div
              key={job.id}
              onClick={() => navigate(`/company/pipeline/${job.id}`)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 10px',
                borderBottom: '1px solid var(--color-border)',
                cursor: 'pointer',
                borderRadius: 6,
                transition: 'background 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--text)' }}>{job.title}</div>
                <div className="muted" style={{ fontSize: 12, display: 'flex', gap: 14, marginTop: 4 }}>
                  {job.location && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <MapPin size={12} /> {job.location}
                    </span>
                  )}
                  {job.employment_type && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Clock size={12} /> {job.employment_type}
                    </span>
                  )}
                  {job.interview_required && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-2)' }}>
                      <MessageSquare size={12} /> AI Interview Required
                    </span>
                  )}
                </div>
                {job.required_skills?.length > 0 && (
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 8 }}>
                    {job.required_skills.slice(0, 6).map((s) => (
                      <span key={s} className="chip" style={{ fontSize: 10 }}>
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'var(--bg)', padding: '6px 12px', borderRadius: 8 }}>
                  <Users size={14} style={{ color: 'var(--color-primary)' }} />
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{applicantCounts[job.id] || 0}</span>
                  <span className="muted" style={{ fontSize: 11 }}>Applicants</span>
                </div>
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ color: 'var(--color-danger)' }}
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteJob(job.id)
                  }}
                  title="Delete Job"
                >
                  <Trash2 size={14} />
                </button>
                <ChevronRight size={16} style={{ color: 'var(--color-fg-muted)' }} />
              </div>
            </div>
          ))}
        </div>
      )}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => { await confirm.action(); setConfirm({ ...confirm, open: false }) }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
