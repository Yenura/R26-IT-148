import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  TrendingUp, CheckCircle, Clock, AlertCircle, Download, Sparkles,
  Rocket, Plus, Search, ChevronRight
} from 'lucide-react'
import { c4Progress, c4ProgressPopulate, c4ProgressUpdate } from '../api'

export default function Progress() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [popBusy, setPopBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('all') // 'all', 'in_progress', 'completed', 'not_started'
  const [searchTerm, setSearchTerm] = useState('')
  const [newSkillInput, setNewSkillInput] = useState('')
  const [addBusy, setAddBusy] = useState(false)
  
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const r = await c4Progress(candidateId)
      setData(r.data)
    } catch { toast.error('Failed to load progress data') }
  }

  const populate = async () => {
    setPopBusy(true)
    try {
      const r = await c4ProgressPopulate({ candidate_id: candidateId })
      toast.success(`Added ${r?.data?.populated || 0} skills from your skill gap analysis!`)
      loadData()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'No skill gap report found. Run Skill Gap Analysis first.')
    } finally { setPopBusy(false) }
  }

  const updateStatus = async (skill, status) => {
    try {
      await c4ProgressUpdate({
        candidate_id: candidateId, skill, status, notes: ''
      })
      const label = status === 'completed' ? 'Mastered 🎉' : status === 'in_progress' ? 'Learning 🚀' : 'Target Added'
      toast.success(`${skill}: ${label}`)
      loadData()
    } catch { toast.error('Failed to update progress') }
  }

  const addCustomSkill = async (e) => {
    e.preventDefault()
    if (!newSkillInput.trim()) return
    setAddBusy(true)
    try {
      await c4ProgressUpdate({
        candidate_id: candidateId, skill: newSkillInput.trim(), status: 'in_progress', notes: 'Custom goal'
      })
      toast.success(`Added "${newSkillInput.trim()}" to your learning matrix!`)
      setNewSkillInput('')
      loadData()
    } catch {
      toast.error('Failed to add skill')
    } finally {
      setAddBusy(false)
    }
  }

  const stats = data?.stats || {}
  const skills = data?.skills || []
  const pct = stats.completion_pct || 0

  // Computed Career Tier
  const careerTier = pct >= 85 ? { title: 'Principal Architect / Lead', level: 'Level 4 (Executive)', color: 'var(--color-purple)', badge: '👑 Master' }
    : pct >= 60 ? { title: 'Senior Tech Specialist', level: 'Level 3 (Advanced)', color: 'var(--color-success)', badge: '🚀 Senior' }
    : pct >= 30 ? { title: 'Mid-Level Engineer', level: 'Level 2 (Intermediate)', color: 'var(--color-info)', badge: '⚡ Mid-Level' }
    : { title: 'Junior / Associate Developer', level: 'Level 1 (Foundation)', color: 'var(--color-warning)', badge: '🌱 Junior' }

  // Computed Estimated Learning Hours
  const totalHours = (stats.completed || 0) * 20 + (stats.in_progress || 0) * 8

  // Filtered skills
  const filteredSkills = skills.filter((s) => {
    const matchesSearch = s.skill.toLowerCase().includes(searchTerm.toLowerCase())
    if (activeTab === 'in_progress') return matchesSearch && s.status === 'in_progress'
    if (activeTab === 'completed') return matchesSearch && s.status === 'completed'
    if (activeTab === 'not_started') return matchesSearch && s.status === 'not_started'
    return matchesSearch
  })

  const statusIcon = (s) => s === 'completed' ? <CheckCircle size={18} style={{ color: 'var(--color-success)' }} />
    : s === 'in_progress' ? <Clock size={18} style={{ color: 'var(--color-info)' }} />
    : <AlertCircle size={18} style={{ color: 'var(--text-muted)' }} />

  return (
    <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto', padding: '24px 16px' }}>
      {/* Header */}
      <div className="page-head" style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1, marginBottom: 4 }}>
            Lifetime Career Growth Engine
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
            <TrendingUp size={30} style={{ color: 'var(--accent)' }} /> Career Skill Mastery & Growth Matrix
          </h1>
          <p className="muted" style={{ fontSize: 13, marginTop: 4, margin: 0 }}>
            Track continuous skill acquisition, unlock career progression tiers, and build a lifetime professional advantage.
          </p>
        </div>

        <button className="btn" onClick={populate} disabled={popBusy} style={{ padding: '10px 16px', fontSize: 13, fontWeight: 700, borderRadius: 8, display: 'flex', alignItems: 'center', gap: 8, background: 'var(--color-primary)', color: 'var(--color-on-primary)' }}>
          <Download size={16} /> {popBusy ? 'Syncing...' : 'Sync from Skill Gap Analysis'}
        </button>
      </div>

      {/* Career Trajectory & Level Banner */}
      <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg) 100%)', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 24, alignItems: 'center' }}>
          {/* Gauge & Level */}
          <div style={{ textAlign: 'center', paddingRight: 24, borderRight: '1px solid var(--border)' }}>
            <div style={{ position: 'relative', width: 100, height: 100, margin: '0 auto 12px' }}>
              <svg width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="var(--border)" strokeWidth="8" />
                <circle cx="50" cy="50" r="42" fill="none" stroke={careerTier.color} strokeWidth="8"
                  strokeDasharray={`${pct * 2.64} 264`} strokeLinecap="round" transform="rotate(-90 50 50)" style={{ transition: 'stroke-dasharray 1s ease' }} />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: 22, fontWeight: 900, color: 'var(--text)', lineHeight: 1 }}>{pct.toFixed(0)}%</span>
                <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', marginTop: 2 }}>MASTERY</span>
              </div>
            </div>
            <span className="chip" style={{ fontSize: 11, padding: '4px 10px', background: `${careerTier.color}20`, color: careerTier.color, border: `1px solid ${careerTier.color}40`, fontWeight: 800 }}>
              {careerTier.badge}
            </span>
          </div>

          {/* Trajectory Details */}
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: careerTier.color, letterSpacing: 0.5 }}>
              Current Career Tier: {careerTier.level}
            </div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text)', margin: '4px 0 8px 0' }}>
              {careerTier.title}
            </h2>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '0 0 16px 0', lineHeight: 1.5 }}>
              You have completed <strong>{stats.completed || 0}</strong> of <strong>{stats.total || 0}</strong> target skills. Completing remaining skill gaps unlocks senior market valuation (+25% earning potential).
            </p>

            {/* Career Stepper Bar */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, fontSize: 11, fontWeight: 700 }}>
              <div style={{ padding: '6px 8px', borderRadius: 6, background: pct >= 0 ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg)', color: pct >= 0 ? 'var(--color-warning)' : 'var(--text-muted)', border: '1px solid var(--border)', textAlign: 'center' }}>
                🌱 Junior (0-30%)
              </div>
              <div style={{ padding: '6px 8px', borderRadius: 6, background: pct >= 30 ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg)', color: pct >= 30 ? 'var(--color-info)' : 'var(--text-muted)', border: '1px solid var(--border)', textAlign: 'center' }}>
                ⚡ Mid (30-60%)
              </div>
              <div style={{ padding: '6px 8px', borderRadius: 6, background: pct >= 60 ? 'rgba(34, 197, 94, 0.15)' : 'var(--bg)', color: pct >= 60 ? 'var(--color-success)' : 'var(--text-muted)', border: '1px solid var(--border)', textAlign: 'center' }}>
                🚀 Senior (60-85%)
              </div>
              <div style={{ padding: '6px 8px', borderRadius: 6, background: pct >= 85 ? 'rgba(139, 92, 246, 0.15)' : 'var(--bg)', color: pct >= 85 ? 'var(--color-purple)' : 'var(--text-muted)', border: '1px solid var(--border)', textAlign: 'center' }}>
                👑 Lead (85%+)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Career Impact Stat Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ padding: 16, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-elevated)', textAlign: 'center' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Completed Skills</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--color-success)', marginTop: 4 }}>{stats.completed || 0}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Verified Competencies</div>
        </div>

        <div className="card" style={{ padding: 16, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-elevated)', textAlign: 'center' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Learning</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--color-info)', marginTop: 4 }}>{stats.in_progress || 0}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Skills in Progress</div>
        </div>

        <div className="card" style={{ padding: 16, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-elevated)', textAlign: 'center' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target Backlog</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--color-warning)', marginTop: 4 }}>{stats.not_started || 0}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Skills to Acquire</div>
        </div>

        <div className="card" style={{ padding: 16, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-elevated)', textAlign: 'center' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Learning Hours</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--accent)', marginTop: 4 }}>~{totalHours} hrs</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Career Investment</div>
        </div>
      </div>

      {/* Main Skill Matrix & Actions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
        {/* Left Column: Skill Matrix */}
        <div>
          {/* Controls Header: Tabs + Search */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', gap: 6, background: 'var(--bg-elevated)', padding: 4, borderRadius: 8, border: '1px solid var(--border)' }}>
              {[
                { id: 'all', label: `All (${skills.length})` },
                { id: 'in_progress', label: `Learning (${stats.in_progress || 0})` },
                { id: 'completed', label: `Done (${stats.completed || 0})` },
                { id: 'not_started', label: `New (${stats.not_started || 0})` },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  style={{
                    padding: '6px 12px', fontSize: 12, fontWeight: 700, borderRadius: 6, border: 'none', cursor: 'pointer',
                    background: activeTab === t.id ? 'var(--color-primary)' : 'transparent',
                    color: activeTab === t.id ? 'var(--color-on-primary)' : 'var(--text-muted)',
                    transition: 'all 0.2s'
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Quick Search */}
            <div style={{ position: 'relative', width: 200 }}>
              <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ width: '100%', paddingLeft: 30, height: 34, fontSize: 12, borderRadius: 6, border: '1px solid var(--border)', background: 'var(--input-bg)', color: 'var(--text)' }}
              />
            </div>
          </div>

          {/* Skill List Card */}
          <div className="card" style={{ padding: 20, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
            {filteredSkills.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {filteredSkills.map((p) => (
                  <div
                    key={p.skill}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
                      padding: '12px 14px', borderRadius: 8, background: 'var(--bg)', border: '1px solid var(--border)',
                      transition: 'border-color 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1 }}>
                      {statusIcon(p.status)}
                      <div>
                        <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)', display: 'block' }}>
                          {p.skill}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                          {p.status === 'completed' ? 'Mastered Competency' : p.status === 'in_progress' ? 'Currently Learning' : 'Target Skill Goal'}
                        </span>
                      </div>
                    </div>

                    {/* Status Action Buttons */}
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button
                        className={`btn btn-sm ${p.status === 'not_started' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => updateStatus(p.skill, 'not_started')}
                        style={{ fontSize: 11, padding: '4px 10px', borderRadius: 6, fontWeight: 600 }}
                      >
                        New
                      </button>
                      <button
                        className={`btn btn-sm ${p.status === 'in_progress' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => updateStatus(p.skill, 'in_progress')}
                        style={{ fontSize: 11, padding: '4px 10px', borderRadius: 6, fontWeight: 600, color: p.status === 'in_progress' ? 'var(--color-on-primary)' : 'var(--color-info)' }}
                      >
                        Learning
                      </button>
                      <button
                        className={`btn btn-sm ${p.status === 'completed' ? 'btn-success' : 'btn-ghost'}`}
                        onClick={() => updateStatus(p.skill, 'completed')}
                        style={{ fontSize: 11, padding: '4px 10px', borderRadius: 6, fontWeight: 600, color: p.status === 'completed' ? 'var(--color-on-primary)' : 'var(--color-success)' }}
                      >
                        Done ✓
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>
                <AlertCircle size={28} style={{ marginBottom: 8, color: 'var(--text-muted)' }} />
                <div style={{ fontSize: 14, fontWeight: 700 }}>No skills found</div>
                <p style={{ fontSize: 12, marginTop: 4 }}>
                  {skills.length === 0 ? 'Click "Sync from Skill Gap Analysis" above or add a custom skill to get started.' : 'Try adjusting your search filter.'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Custom Skill Adder & AI Advisor */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Add Custom Skill Card */}
          <div className="card" style={{ padding: 20, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 800, margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text)' }}>
              <Plus size={16} style={{ color: 'var(--accent)' }} /> Add Target Custom Skill
            </h3>
            <form onSubmit={addCustomSkill}>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
                Add any personal learning goal (e.g. <em>GraphQL, System Architecture, PyTorch</em>) to track in your matrix.
              </p>
              <input
                type="text"
                placeholder="e.g. AWS Solutions Architect"
                value={newSkillInput}
                onChange={(e) => setNewSkillInput(e.target.value)}
                maxLength={60}
                style={{ width: '100%', padding: '10px 12px', fontSize: 13, borderRadius: 8, border: '1px solid var(--border)', background: 'var(--input-bg)', color: 'var(--text)', marginBottom: 10 }}
              />
              <button
                type="submit"
                className="btn"
                disabled={addBusy || !newSkillInput.trim()}
                style={{ width: '100%', padding: 10, fontSize: 13, fontWeight: 700, borderRadius: 8, background: 'var(--color-primary)', color: 'var(--color-on-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
              >
                <Rocket size={15} /> Add to Growth Plan
              </button>
            </form>
          </div>

          {/* AI Lifetime Career Advisor Card */}
          <div className="card" style={{ padding: 20, borderRadius: 12, border: '1px dashed var(--accent)', background: 'rgba(59, 130, 246, 0.03)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 800, margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent)' }}>
              <Sparkles size={16} /> Strategic Growth Advice
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 16 }}>
              {pct < 30 ? (
                'Focus on foundational programming languages and Git version control before moving into advanced cloud architectures.'
              ) : pct < 70 ? (
                'Great progress! Prioritize microservices design, containerization (Docker/K8s), and cloud deployments to unlock Senior Engineer roles.'
              ) : (
                'Outstanding mastery! You are well-positioned for Lead Architect & Principal Engineer roles. Focus on system scalability and team mentoring.'
              )}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Link to="/pipeline/skill-gap" className="btn btn-ghost btn-sm" style={{ justifyContent: 'space-between', fontSize: 12, border: '1px solid var(--border)' }}>
                <span>Run Skill Gap Analysis</span> <ChevronRight size={14} />
              </Link>
              <Link to="/pipeline/cv-match" className="btn btn-ghost btn-sm" style={{ justifyContent: 'space-between', fontSize: 12, border: '1px solid var(--border)' }}>
                <span>Analyze Resume Match</span> <ChevronRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

