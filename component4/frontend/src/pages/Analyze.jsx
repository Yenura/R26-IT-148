import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeSkillGap } from '../api'
import toast from 'react-hot-toast'
import { Brain, Plus, X, ChevronRight, Zap } from 'lucide-react'

/* ── Constants derived from new 10K dataset ───────────────────────────────── */
const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'Machine Learning Engineer',
  'Frontend Developer', 'Backend Developer', 'DevOps Engineer',
  'Cybersecurity Analyst', 'Cloud Solutions Architect',
  'Database Administrator', 'Mobile App Developer',
]

const JOB_LEVELS  = ['Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal / Staff']
const WORK_MODES  = ['Hybrid', 'On-Site', 'Remote']

const EDUCATION_OPTIONS = [
  'B.Sc. Computer Science', 'B.Sc. Information Technology', 'B.Sc. Software Engineering',
  'B.Sc. Mathematics', 'B.Sc. Statistics', 'B.Sc. Cognitive Science',
  'B.Sc. Physics (CS minor)', 'B.Eng. Electrical Engineering',
  'B.Eng. Electronics & Communication', 'Associate Degree in Computer Science',
  'Bootcamp + Self-Taught', 'MBA (IT / Analytics)',
  'M.Sc. Computer Science', 'M.Sc. Data Science', 'M.Sc. Machine Learning',
  'M.Sc. Cybersecurity', 'M.Sc. Artificial Intelligence', 'M.Sc. Information Systems',
  'Ph.D. Computer Science', 'Ph.D. Artificial Intelligence',
]

/* Top skills per role from dataset Required Skills column */
const ROLE_PRESETS = {
  'Software Engineer':         ['Python', 'REST APIs', 'Microservices', 'Docker', 'SQL'],
  'Data Scientist':            ['Python', 'SQL', 'Machine Learning', 'Statistics', 'Feature Engineering'],
  'Machine Learning Engineer': ['Python', 'PyTorch/TensorFlow', 'MLOps', 'Feature Engineering', 'Docker'],
  'Frontend Developer':        ['React', 'TypeScript', 'HTML/CSS', 'Web Performance', 'Accessibility'],
  'Backend Developer':         ['Python', 'PostgreSQL', 'REST APIs', 'Microservices', 'Docker'],
  'DevOps Engineer':           ['Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'AWS'],
  'Cybersecurity Analyst':     ['Cybersecurity', 'Networking', 'Incident Response', 'Cloud Security', 'Linux'],
  'Cloud Solutions Architect': ['AWS/Azure/GCP', 'Terraform', 'Cloud Security', 'Architecture Design', 'Networking'],
  'Database Administrator':    ['SQL', 'PostgreSQL', 'MongoDB', 'Performance Tuning', 'Backup & Recovery'],
  'Mobile App Developer':      ['React Native', 'TypeScript', 'REST APIs', 'Firebase', 'iOS/Android'],
}

/* Colour-coded skill chip by category */
const ALL_QUICK_SKILLS = [
  'Python', 'Java', 'TypeScript', 'Go', 'Rust',
  'React', 'REST APIs', 'GraphQL', 'Microservices',
  'SQL', 'PostgreSQL', 'MongoDB',
  'Machine Learning', 'Deep Learning', 'MLOps', 'Feature Engineering', 'Statistics',
  'Docker', 'Kubernetes', 'Terraform', 'AWS/Azure/GCP', 'CI/CD',
  'Cybersecurity', 'Networking', 'Linux', 'Incident Response',
]

const F = ({ label, children }) => (
  <div className="form-group"><label>{label}</label>{children}</div>
)

const BLANK = {
  candidate_id: '', candidate_name: '', job_role: 'Software Engineer',
  job_level: 'Mid-Level', work_mode: 'Hybrid',
  experience_years: 3, education: 'B.Sc. Computer Science',
  certifications: 'None', certifications_count: 0, projects_count: 5,
  cv_matching_score: '', interview_score: '', mcq_score: '',
  descriptive_score: '', coding_score: '',
  skills: [], weak_topics: [], failed_mcq_topics: [],
}

export default function Analyze() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [tab,     setTab]     = useState('basic')
  const [form,    setForm]    = useState(BLANK)
  const [si, setSi] = useState('')
  const [wi, setWi] = useState('')
  const [mi, setMi] = useState('')

  const set    = (k, v) => setForm(f => ({ ...f, [k]: v }))
  const toggle = s => set('skills',
    form.skills.includes(s) ? form.skills.filter(x => x !== s) : [...form.skills, s])
  const addCustom = () => {
    const v = si.trim()
    if (v && !form.skills.includes(v)) set('skills', [...form.skills, v])
    setSi('')
  }
  const addTag = (field, val, clr) => {
    const v = val.trim()
    if (v && !form[field].includes(v)) set(field, [...form[field], v])
    clr('')
  }
  const rmTag = (field, i) => set(field, form[field].filter((_, j) => j !== i))

  const applyPreset = () => {
    const preset = ROLE_PRESETS[form.job_role] || []
    set('skills', [...new Set([...form.skills, ...preset])])
  }

  const handleSubmit = async e => {
    e.preventDefault()
    if (!form.candidate_id.trim())  return toast.error('Candidate ID required')
    if (!form.candidate_name.trim()) return toast.error('Name required')
    if (!form.skills.length)         return toast.error('Add at least one skill')

    const payload = {
      ...form,
      candidate_id:        form.candidate_id.trim(),
      candidate_name:      form.candidate_name.trim(),
      experience_years:    Number(form.experience_years),
      certifications_count: Number(form.certifications_count),
      projects_count:      Number(form.projects_count),
      cv_matching_score:   form.cv_matching_score !== '' ? Number(form.cv_matching_score) : null,
      interview_score:     form.interview_score   !== '' ? Number(form.interview_score)   : null,
      mcq_score:           form.mcq_score         !== '' ? Number(form.mcq_score)         : null,
      descriptive_score:   form.descriptive_score !== '' ? Number(form.descriptive_score) : null,
      coding_score:        form.coding_score       !== '' ? Number(form.coding_score)       : null,
    }
    setLoading(true)
    try {
      await analyzeSkillGap(payload)
      toast.success('Analysis complete!')
      navigate(`/report/${form.candidate_id.trim()}`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const TABS = [
    ['basic',  'Candidate Info'],
    ['scores', 'Interview Scores'],
    ['topics', 'Weak Topics'],
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Analyse Candidate</h1>
        <p>Enter candidate details from the new 10 000-record dataset to generate a Skill Gap Report &amp; Career Plan</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Tabs */}
        <div className="tabs">
          {TABS.map(([k, l]) => (
            <button key={k} type="button"
              className={`tab-btn${tab === k ? ' active' : ''}`}
              onClick={() => setTab(k)}>{l}
            </button>
          ))}
        </div>

        {/* ── Tab 1: Basic Info ── */}
        {tab === 'basic' && (
          <div className="grid-2" style={{ gap: 20 }}>
            {/* Left: candidate details */}
            <div className="card">
              <p className="card-title"><Brain size={15} /> Candidate Details</p>

              <F label="CANDIDATE ID *">
                <input className="form-control" placeholder="CAND-001"
                  value={form.candidate_id} onChange={e => set('candidate_id', e.target.value)} style={{ width: '100%' }} />
              </F>
              <F label="FULL NAME *">
                <input className="form-control" placeholder="Jane Smith"
                  value={form.candidate_name} onChange={e => set('candidate_name', e.target.value)} style={{ width: '100%' }} />
              </F>
              <F label="JOB ROLE">
                <select className="form-control" value={form.job_role} onChange={e => set('job_role', e.target.value)}>
                  {JOB_ROLES.map(r => <option key={r}>{r}</option>)}
                </select>
              </F>
              <div className="grid-2" style={{ gap: 12 }}>
                <F label="JOB LEVEL">
                  <select className="form-control" value={form.job_level} onChange={e => set('job_level', e.target.value)}>
                    {JOB_LEVELS.map(l => <option key={l}>{l}</option>)}
                  </select>
                </F>
                <F label="WORK MODE">
                  <select className="form-control" value={form.work_mode} onChange={e => set('work_mode', e.target.value)}>
                    {WORK_MODES.map(m => <option key={m}>{m}</option>)}
                  </select>
                </F>
              </div>
              <div className="grid-2" style={{ gap: 12 }}>
                <F label="EXPERIENCE (YRS)">
                  <input className="form-control" type="number" min={0} max={30}
                    value={form.experience_years} onChange={e => set('experience_years', e.target.value)} />
                </F>
                <F label="PROJECTS COUNT">
                  <input className="form-control" type="number" min={0} max={99}
                    value={form.projects_count} onChange={e => set('projects_count', e.target.value)} />
                </F>
              </div>
              <F label="EDUCATION">
                <select className="form-control" value={form.education} onChange={e => set('education', e.target.value)}>
                  {EDUCATION_OPTIONS.map(o => <option key={o}>{o}</option>)}
                </select>
              </F>
              <div className="grid-2" style={{ gap: 12 }}>
                <F label="CERTIFICATIONS">
                  <input className="form-control" placeholder="AWS Certified | Google ML…"
                    value={form.certifications} onChange={e => set('certifications', e.target.value)} />
                </F>
                <F label="CERT COUNT">
                  <input className="form-control" type="number" min={0} max={10}
                    value={form.certifications_count} onChange={e => set('certifications_count', e.target.value)} />
                </F>
              </div>
            </div>

            {/* Right: skills */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <p className="card-title" style={{ margin: 0 }}>Skills *</p>
                <button type="button" className="btn btn-ghost" style={{ fontSize: 11, padding: '5px 10px' }}
                  onClick={applyPreset}>
                  <Zap size={12} /> Preset for {form.job_role.split(' ')[0]}
                </button>
              </div>

              {/* Quick-select chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                {ALL_QUICK_SKILLS.map(s => (
                  <button key={s} type="button" onClick={() => toggle(s)} style={{
                    padding: '4px 10px', borderRadius: 999, fontSize: 11, fontWeight: 600,
                    cursor: 'pointer', transition: 'all .2s',
                    border: '1px solid var(--border)',
                    background: form.skills.includes(s) ? 'var(--accent-glow)' : 'var(--bg-primary)',
                    color:      form.skills.includes(s) ? 'var(--accent-light)' : 'var(--text-muted)',
                  }}>{s}</button>
                ))}
              </div>

              {/* Custom skill input */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <input className="form-control" placeholder="Custom skill (e.g. LangChain)…"
                  value={si} onChange={e => setSi(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addCustom())} />
                <button type="button" className="btn btn-primary" style={{ flexShrink: 0 }}
                  onClick={addCustom}><Plus size={14} /></button>
              </div>

              {/* Selected skills */}
              <div>
                {!form.skills.length
                  ? <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>No skills selected — click chips above or type a custom skill</p>
                  : form.skills.map((s, i) => (
                    <span key={i} className="skill-chip chip-has">{s}
                      <X size={11} style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => rmTag('skills', i)} />
                    </span>
                  ))
                }
              </div>
            </div>
          </div>
        )}

        {/* ── Tab 2: Interview Scores ── */}
        {tab === 'scores' && (
          <div className="card">
            <p className="card-title">Component 1 &amp; 2 Scores</p>
            <div className="alert alert-info" style={{ marginBottom: 16 }}>
              These scores come from CV Matching (Component 1) and AI Interview (Component 2). Leave blank if not yet available.
            </div>
            <div className="grid-2">
              {[
                ['cv_matching_score', 'CV MATCHING SCORE (C1, 0–100)'],
                ['interview_score',   'INTERVIEW SCORE   (C2, 0–100)'],
                ['mcq_score',         'MCQ SCORE         (0–100)'],
                ['descriptive_score', 'DESCRIPTIVE SCORE (0–100)'],
                ['coding_score',      'CODING SCORE      (0–100)'],
              ].map(([k, l]) => (
                <F key={k} label={l}>
                  <input className="form-control" type="number" min={0} max={100} placeholder="e.g. 72"
                    value={form[k]} onChange={e => set(k, e.target.value)} />
                </F>
              ))}
            </div>
          </div>
        )}

        {/* ── Tab 3: Weak Topics ── */}
        {tab === 'topics' && (
          <div className="grid-2" style={{ gap: 20 }}>
            {[
              { label: 'WEAK TOPICS (from descriptive answers)', field: 'weak_topics',       val: wi, setVal: setWi },
              { label: 'FAILED MCQ TOPICS',                       field: 'failed_mcq_topics', val: mi, setVal: setMi },
            ].map(({ label, field, val, setVal }) => (
              <div key={field} className="card">
                <p className="card-title" style={{ fontSize: 13 }}>{label}</p>
                <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                  <input className="form-control" placeholder="Topic name…" value={val}
                    onChange={e => setVal(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag(field, val, setVal))} />
                  <button type="button" className="btn btn-primary" style={{ flexShrink: 0 }}
                    onClick={() => addTag(field, val, setVal)}><Plus size={14} /></button>
                </div>
                <div>
                  {!form[field].length
                    ? <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>None added</p>
                    : form[field].map((t, i) => (
                      <span key={i} className="skill-chip chip-required">{t}
                        <X size={11} style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => rmTag(field, i)} />
                      </span>
                    ))
                  }
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Submit */}
        <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading
              ? <><span style={{ display: 'inline-block', width: 14, height: 14, border: '2px solid #ffffff55', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin .8s linear infinite' }} /> Analysing…</>
              : <><ChevronRight size={14} /> Run Analysis</>
            }
          </button>
          <button type="button" className="btn btn-ghost"
            onClick={() => setForm(BLANK)}>Reset</button>
        </div>
      </form>
    </div>
  )
}
