import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, CheckCircle2, AlertCircle, BookOpen, ExternalLink,
  Zap, Layers, Lightbulb
} from 'lucide-react'
import { uResumeList, c4SkillGapRoles, c4SkillGapAnalyze, c4SkillGapSimulate } from '../api'

export default function SkillGap() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState([])
  const [form, setForm] = useState({ candidate_name: '', job_role: '', skills: '', experience_years: 0, education: '' })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/login/candidate'); return }
    c4SkillGapRoles().then((r) => setRoles(r.data.roles || [])).catch(() => {})
    loadResumeData()
  }, [])

  const loadResumeData = async () => {
    try {
      const r = await uResumeList()
      const resumes = r.data || []
      if (resumes.length > 0) {
        const latest = resumes[0]
        setForm(f => ({
          ...f,
          candidate_name: latest.candidate_name || localStorage.getItem('recruitai.name') || 'Candidate',
          skills: (latest.skills || []).join(', '),
          experience_years: latest.experience_years || 0,
          education: latest.education || 'B.Sc. Computer Science',
        }))
      } else {
        setForm(f => ({ ...f, candidate_name: localStorage.getItem('recruitai.name') || 'Candidate' }))
      }
    } catch { toast.error('Failed to load resume data') }
  }

  const analyze = async (e) => {
    e.preventDefault()
    if (!form.candidate_name || !form.job_role || !form.skills) return toast.error('Please fill required fields')
    setBusy(true)
    try {
      const r = await c4SkillGapAnalyze({
        candidate_id: localStorage.getItem('recruitai.user_id'),
        candidate_name: form.candidate_name,
        job_role: form.job_role,
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
        experience_years: parseFloat(form.experience_years) || 0,
        education: form.education || 'B.Sc. Computer Science',
      })
      const data = r.data.data || r.data
      setResult(data)
      toast.success(`Skill Fit Score: ${(data.skill_match_pct || (data.gap_score * 100)).toFixed(0)}%`)
    } catch (err) {
      toast.error('Skill gap analysis failed')
    } finally {
      setBusy(false)
    }
  }

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 960, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="page-head" style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Target size={28} style={{ color: 'var(--accent)' }} /> AI Skill Gap & Course Recommendation Engine
        </h1>
        <p className="muted" style={{ fontSize: 14 }}>
          Evaluate your skill coverage against canonical IT job roles, discover critical missing skills, and enroll in verified course recommendations.
        </p>
      </div>

      {/* Analysis Form Card */}
      <form onSubmit={analyze} className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Zap size={18} style={{ color: 'var(--accent)' }} /> Skill Gap Setup
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Candidate Name *</label>
            <input type="text" value={form.candidate_name} onChange={set('candidate_name')} placeholder="e.g. Inuka Jathmal" style={{ height: 42, borderRadius: 8, fontSize: 14 }} />
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Target Job Role *</label>
            <select value={form.job_role} onChange={set('job_role')} style={{ width: '100%', height: 42, padding: '0 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14 }}>
              <option value="">Select a target role...</option>
              {roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Your Current Technical Skills (Comma-Separated) *</label>
          <input type="text" value={form.skills} onChange={set('skills')} placeholder="Python, SQL, React, FastAPI, Git, Docker" style={{ height: 42, borderRadius: 8, fontSize: 14 }} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Years of Experience</label>
            <input type="number" value={form.experience_years} onChange={set('experience_years')} min="0" max="50" style={{ height: 42, borderRadius: 8, fontSize: 14 }} />
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, display: 'block' }}>Education Degree</label>
            <input type="text" value={form.education} onChange={set('education')} placeholder="B.Sc. Computer Science / IT" style={{ height: 42, borderRadius: 8, fontSize: 14 }} />
          </div>
        </div>

        <button className="btn" type="submit" disabled={busy} style={{ width: '100%', height: 44, fontSize: 14, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, background: 'var(--color-primary)', color: 'var(--color-on-primary)' }}>
          <Target size={18} /> {busy ? 'Calculating Skill Coverage & Recommendations...' : 'Run Skill Gap Analysis'}
        </button>
      </form>

      {/* Results Section */}
      {result && (
        <div className="fade-in card" style={{ padding: 28, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
          {/* Header Banner */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: 20, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1 }}>
                Skill Gap & Career Readiness Report
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 800, marginTop: 4, color: 'var(--text)' }}>
                Target Role: <span style={{ color: 'var(--accent)' }}>{result.job_role}</span>
              </h2>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 32, fontWeight: 900, color: 'var(--accent)', lineHeight: 1 }}>
                {(result.skill_match_pct || (result.gap_score * 100)).toFixed(1)}%
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginTop: 4 }}>
                Skill Fit Score
              </div>
            </div>
          </div>

          {/* Metric Cards Grid */}
          <div className="grid grid-3" style={{ gap: 14, marginBottom: 24 }}>
            <div className="stat" style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <div className="stat-label" style={{ fontSize: 12 }}>Gap Score Fit</div>
              <div className="stat-value" style={{ color: 'var(--accent)', fontSize: 22 }}>{(result.gap_score * 100).toFixed(0)}%</div>
            </div>
            <div className="stat" style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <div className="stat-label" style={{ fontSize: 12 }}>Hiring Probability</div>
              <div className="stat-value" style={{ color: 'var(--color-success)', fontSize: 22 }}>{result.hire_probability?.toFixed(1)}%</div>
            </div>
            <div className="stat" style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <div className="stat-label" style={{ fontSize: 12 }}>Gap Severity</div>
              <div className="stat-value" style={{ color: result.gap_severity === 'Low' ? 'var(--color-success)' : result.gap_severity === 'Medium' ? 'var(--color-warning)' : 'var(--color-danger)', fontSize: 22 }}>
                {result.gap_severity}
              </div>
            </div>
          </div>

          {/* Missing Required & Optional Skills */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--danger)' }}>
                <AlertCircle size={16} /> Critical Missing Required Skills ({result.missing_required?.length || 0})
              </h4>
              {result.missing_required?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.missing_required.map((s) => (
                    <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-danger)', border: '1px solid rgba(239, 68, 68, 0.3)', fontWeight: 600 }}>
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: 13, color: 'var(--color-success)' }}>All core required skills present!</div>
              )}
            </div>

            <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-success)' }}>
                <CheckCircle2 size={16} /> Present Verified Skills ({result.present_skills?.length || 0})
              </h4>
              {result.present_skills?.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.present_skills.map((s) => (
                    <span key={s} className="chip" style={{ fontSize: 12, padding: '4px 10px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>No present skills provided.</div>
              )}
            </div>
          </div>

          {/* Recommended Courses & Learning Resources */}
          {result.resources?.length > 0 && (
            <div style={{ marginBottom: 24, padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text)' }}>
                <BookOpen size={20} style={{ color: 'var(--accent)' }} /> Recommended Learning Courses & Resources ({result.resources.length})
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                {result.resources.map((resItem, idx) => {
                  const pColor = resItem.priority === 'Critical' ? 'var(--color-danger)' : resItem.priority === 'High' ? 'var(--color-orange)' : resItem.priority === 'Medium' ? 'var(--color-warning)' : 'var(--color-success)'
                  return (
                    <div key={idx} style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <span className="chip" style={{ fontSize: 11, padding: '2px 8px', background: `${pColor}15`, color: pColor, border: `1px solid ${pColor}40`, fontWeight: 700 }}>
                            {resItem.priority} Priority
                          </span>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>
                            {resItem.level || 'Beginner'} · {resItem.duration || '4 weeks'}
                          </span>
                        </div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)', marginBottom: 4 }}>
                          {resItem.skill}: <span style={{ color: 'var(--accent)' }}>{resItem.course}</span>
                        </div>
                      </div>

                      <a
                        href={resItem.url || `https://www.coursera.org/search?query=${encodeURIComponent(resItem.skill)}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-ghost btn-sm"
                        style={{ marginTop: 12, fontSize: 12, border: '1px solid var(--border)', display: 'inline-flex', alignItems: 'center', gap: 6, alignSelf: 'flex-start' }}
                      >
                        Enroll / Explore Course <ExternalLink size={13} />
                      </a>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Structured Learning Roadmap */}
          {result.learning_plan?.length > 0 && (
            <div style={{ marginBottom: 24, padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Layers size={20} style={{ color: 'var(--color-primary)' }} /> Structured Monthly Skill Acquisition Plan
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {result.learning_plan.map((planItem, i) => (
                  <div key={i} style={{ padding: 14, background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--accent)', color: 'var(--color-on-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14 }}>
                      {planItem.phase || (i + 1)}
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>
                        {planItem.title || `Month ${i + 1}`}: <span style={{ color: 'var(--accent)' }}>{(planItem.skills || []).join(', ')}</span>
                      </div>
                      {planItem.resources?.length > 0 && (
                        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                          {planItem.resources.length} verified learning module(s)
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Improvement Suggestions */}
          {result.improvement_suggestions?.length > 0 && (
            <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Lightbulb size={20} style={{ color: 'var(--color-warning)' }} /> Actionable AI Profile Recommendations
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.improvement_suggestions.map((s, i) => (
                  <div key={i} style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                    <span style={{ color: 'var(--color-warning)' }}>•</span> {s}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
