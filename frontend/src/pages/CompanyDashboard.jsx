import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Briefcase, Plus, Users, Trash2, MapPin, Clock, ChevronRight,
  MessageSquare, Sparkles, Building2, Trophy, Eye, CheckCircle2, ListOrdered
} from 'lucide-react'
import { uJobsMy, uJobsCreate, uJobsDelete, uJobsApplicants } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

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
  const companyName = localStorage.getItem('recruitai.name') || 'Employer'

  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [applicantCounts, setApplicantCounts] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

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
    setLoading(true)
    try {
      const r = await uJobsMy().catch(() => ({ data: [] }))
      const jobList = Array.isArray(r.data) ? r.data : []
      setJobs(jobList)

      const counts = {}
      for (const job of jobList) {
        try {
          const ar = await uJobsApplicants(job.id).catch(() => ({ data: [] }))
          const apps = Array.isArray(ar.data) ? ar.data : []
          counts[job.id] = apps.length
        } catch {
          counts[job.id] = 0
        }
      }
      setApplicantCounts(counts)
    } catch {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
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
      await uJobsCreate(payload)
      toast.success('Job posting created successfully!')
      setShowModal(false)
      setForm(emptyForm)
      loadJobs()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to create job')
    } finally {
      setSubmitting(false)
    }
  }

  const deleteJob = (jobId) => {
    setConfirm({
      open: true,
      title: 'Delete this job opening?',
      message: 'This will permanently remove the job and all associated applicant rankings.',
      danger: true,
      action: async () => {
        try {
          await uJobsDelete(jobId)
          toast.success('Job deleted')
          loadJobs()
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Delete failed')
        }
      }
    })
  }

  const totalApplicants = Object.values(applicantCounts).reduce((a, b) => a + b, 0)
  const interviewRequiredCount = jobs.filter((j) => j.interview_required).length

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto' }}>
      {/* Header & Primary CTAs */}
      <PageHeader
        badge="Employer Console"
        title={`Recruitment Overview · ${companyName}`}
        description="Post new technical roles, monitor incoming applicants, and rank candidates with LambdaMART Learning-to-Rank."
        actions={
          <>
            <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
              <Plus size={15} /> Post New Job
            </button>
            <Link to="/pipeline/ranking" className="btn btn-ghost btn-sm">
              <Trophy size={15} /> Candidate Ranking
            </Link>
          </>
        }
      />

      {/* KPI Metrics Strip */}
      {loading ? (
        <SkeletonLoader type="stat" count={4} />
      ) : (
        <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
          <StatCard
            label="Active Positions"
            value={jobs.length}
            icon={Briefcase}
            color="primary"
            helperText="Open for applications"
          />
          <StatCard
            label="Total Applicants"
            value={totalApplicants}
            icon={Users}
            color="purple"
            helperText="Across all postings"
          />
          <StatCard
            label="AI Interview Active"
            value={interviewRequiredCount}
            icon={MessageSquare}
            color="info"
            helperText="Automated tech screening"
          />
          <StatCard
            label="Ranking Pipeline"
            value="Active"
            icon={ListOrdered}
            color="success"
            helperText="LambdaMART LTR Ready"
          />
        </div>
      )}

      {/* Active Jobs Data Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Briefcase size={18} style={{ color: 'var(--color-primary)' }} /> Active Job Postings ({jobs.length})
            </h3>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0 0' }}>
              Manage your company's posted roles and inspect applicant pipelines.
            </p>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
            <Plus size={14} /> Add Role
          </button>
        </div>

        {loading ? (
          <SkeletonLoader type="table" rows={4} cols={5} />
        ) : jobs.length === 0 ? (
          <div style={{ padding: 'var(--p-space-6)' }}>
            <EmptyState
              title="No jobs posted yet"
              description="Create your first technical job posting to start receiving CVs, AI screening scores, and applicant rankings."
              actionLabel="Create Job Opening"
              icon={Briefcase}
              onAction={() => setShowModal(true)}
            />
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Job Title & Details</th>
                  <th>Department / Location</th>
                  <th>Required Skills</th>
                  <th>Applicants</th>
                  <th>AI Interview</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => {
                  const count = applicantCounts[job.id] || 0
                  return (
                    <tr key={job.id}>
                      <td style={{ fontWeight: 600 }}>
                        <div style={{ color: 'var(--color-fg)', fontSize: 'var(--p-text-base)' }}>{job.title}</div>
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                          {job.employment_type || 'Full-time'} · {job.experience_required || 0}+ yrs exp · {job.education_required || 'Degree'}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>{job.department || 'Engineering'}</div>
                        <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                          <MapPin size={11} /> {job.location || 'Remote'}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 260 }}>
                          {(job.required_skills || []).slice(0, 3).map((s) => (
                            <span key={s} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                              {s}
                            </span>
                          ))}
                          {(job.required_skills || []).length > 3 && (
                            <span style={{ fontSize: '10px', color: 'var(--color-fg-muted)' }}>
                              +{(job.required_skills || []).length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 4,
                          fontSize: 'var(--p-text-xs)',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-full)',
                          background: count > 0 ? 'var(--color-primary-muted)' : 'var(--color-border-subtle)',
                          color: count > 0 ? 'var(--color-primary)' : 'var(--color-fg-muted)'
                        }}>
                          <Users size={12} /> {count} candidate{count !== 1 ? 's' : ''}
                        </span>
                      </td>
                      <td>
                        {job.interview_required ? (
                          <span style={{
                            fontSize: '11px',
                            fontWeight: 700,
                            color: 'var(--color-success)',
                            background: 'var(--color-success-muted)',
                            padding: '2px 8px',
                            borderRadius: 'var(--radius-full)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4
                          }}>
                            <CheckCircle2 size={12} /> Active ({job.interview_question_count || 10} Qs)
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>Optional</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: 6 }}>
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => navigate(`/company/pipeline/${job.id}`)}
                            title="View candidate pipeline and rank"
                            style={{ fontSize: '12px', padding: '4px 10px' }}
                          >
                            <Trophy size={13} /> Pipeline
                          </button>
                          <button
                            className="btn-ghost btn-sm"
                            onClick={() => navigate(`/company/jobs/${job.id}`)}
                            title="Inspect job preview"
                            style={{ padding: '6px 8px' }}
                          >
                            <Eye size={14} />
                          </button>
                          <button
                            className="btn-ghost btn-sm"
                            onClick={() => deleteJob(job.id)}
                            title="Delete job"
                            style={{ padding: '6px 8px', color: 'var(--color-danger)' }}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Job Modal */}
      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        title="Post New Technical Position"
        subtitle="Specify role requirements, required skills, and AI technical screening parameters."
        icon={Briefcase}
        maxWidth={640}
      >
        <form onSubmit={createJob}>
          {/* Quick canonical role filler */}
          <div style={{ marginBottom: 'var(--p-space-3)' }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Auto-Fill Standard IT Role (Optional)</label>
            <select
              onChange={(e) => handleRoleSelect(e.target.value)}
              defaultValue=""
              style={{ fontSize: 'var(--p-text-sm)' }}
            >
              <option value="" disabled>Select a canonical IT role...</option>
              {Object.keys(STANDARD_ROLES).map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Job Title *</label>
              <input
                type="text"
                placeholder="e.g. Senior Full Stack Engineer"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Department</label>
              <input
                type="text"
                placeholder="e.g. Core Platform"
                value={form.department}
                onChange={(e) => setForm({ ...form, department: e.target.value })}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Location</label>
              <input
                type="text"
                placeholder="e.g. Remote, New York, London"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Employment Type</label>
              <select
                value={form.employment_type}
                onChange={(e) => setForm({ ...form, employment_type: e.target.value })}
              >
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Min Experience (Years)</label>
              <input
                type="number"
                min={0}
                max={40}
                value={form.experience_required}
                onChange={(e) => setForm({ ...form, experience_required: e.target.value })}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', marginTop: 0 }}>Education Level</label>
              <select
                value={form.education_required}
                onChange={(e) => setForm({ ...form, education_required: e.target.value })}
              >
                <option value="High School">High School</option>
                <option value="Associate Degree">Associate Degree</option>
                <option value="Bachelor Degree">Bachelor Degree</option>
                <option value="Master Degree">Master Degree</option>
                <option value="PhD">PhD</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Required Technical Skills (Comma Separated) *</label>
            <input
              type="text"
              placeholder="e.g. React, Node.js, TypeScript, PostgreSQL, Docker"
              value={form.required_skills}
              onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
              required
            />
          </div>

          <div style={{ marginTop: 12 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Job Description & Responsibilities</label>
            <textarea
              placeholder="Describe the mission, technical stack, and responsibilities for this role..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>

          {/* AI Interview Settings */}
          <div style={{ marginTop: 16, padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>
                  Require AI Technical Interview
                </div>
                <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                  Candidates complete automated MCQs, technical theory, and coding sandbox.
                </div>
              </div>
              <input
                type="checkbox"
                checked={form.interview_required}
                onChange={(e) => setForm({ ...form, interview_required: e.target.checked })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
            </div>

            {form.interview_required && (
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 12 }}>
                <label style={{ fontSize: '12px', margin: 0 }}>Question Count:</label>
                <input
                  type="number"
                  min={3}
                  max={30}
                  value={form.interview_question_count}
                  onChange={(e) => setForm({ ...form, interview_question_count: e.target.value })}
                  style={{ width: 80, padding: '4px 8px' }}
                />
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
            <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Creating Posting...' : 'Publish Job Posting'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
