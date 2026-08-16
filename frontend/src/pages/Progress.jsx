import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  TrendingUp, CheckCircle, Clock, AlertCircle, Download, Award, Sparkles,
  Target, Rocket, BookOpen, Layers, Plus, Search, ChevronRight, Zap, ShieldCheck,
  ExternalLink, Check, Briefcase, RefreshCw
} from 'lucide-react'
import axios from 'axios'

const C4 = import.meta.env.VITE_C4_URL || 'http://127.0.0.1:8004'
const authHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('recruitai.token')}` } })

export default function Progress() {
  const navigate = useNavigate()
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [syncBusy, setSyncBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('all') // 'all', 'in_progress', 'completed', 'not_started'
  const [searchTerm, setSearchTerm] = useState('')
  const [newSkillInput, setNewSkillInput] = useState('')
  const [addBusy, setAddBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/login/candidate'); return }
    loadData()
  }, [])

  const loadData = async () => {
    setBusy(true)
    try {
      const r = await axios.get(`${C4}/api/v1/progress/${candidateId}`, authHeader())
      setData(r.data)
    } catch {
    } finally {
      setBusy(false)
    }
  }

  const syncFromInterviews = async () => {
    setSyncBusy(true)
    try {
      const r = await axios.post(`${C4}/api/v1/progress/sync-from-applied-interviews/${candidateId}`, {}, authHeader())
      setData(r.data)
      toast.success(`Synced ${r.data.synced_count || 0} weak skill targets from your applied jobs & interviews!`)
    } catch (err) {
      toast.error('Failed to sync from applied interviews')
    } finally {
      setSyncBusy(false)
    }
  }

  const updateStatus = async (skill, status) => {
    try {
      await axios.post(`${C4}/api/v1/progress/update`, {
        candidate_id: candidateId,
        skill,
        status,
      }, authHeader())
      const label = status === 'completed' ? 'Mastered 🎉' : status === 'in_progress' ? 'In Progress 🚀' : 'Target Added'
      toast.success(`${skill}: ${label}`)
      loadData()
    } catch {
      toast.error('Failed to update progress')
    }
  }

  const addCustomSkill = async (e) => {
    e.preventDefault()
    if (!newSkillInput.trim()) return
    setAddBusy(true)
    try {
      await axios.post(`${C4}/api/v1/progress/update`, {
        candidate_id: candidateId,
        skill: newSkillInput.trim(),
        status: 'in_progress',
        notes: 'Custom target',
      }, authHeader())
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

  const careerTier = pct >= 80 ? { title: 'Senior Tech Specialist / Lead', level: 'Tier 3 (Mastery)', color: '#22c55e', badge: '👑 Advanced' }
    : pct >= 40 ? { title: 'Mid-Level Engineer', level: 'Tier 2 (Intermediate)', color: '#3b82f6', badge: '⚡ Mid-Level' }
    : { title: 'Associate / Foundation Developer', level: 'Tier 1 (Foundation)', color: '#f59e0b', badge: '🌱 Foundation' }

  const filteredSkills = skills.filter((s) => {
    const matchesSearch = s.skill?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.source_role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.source_company?.toLowerCase().includes(searchTerm.toLowerCase())
    if (activeTab === 'in_progress') return matchesSearch && s.status === 'in_progress'
    if (activeTab === 'completed') return matchesSearch && s.status === 'completed'
    if (activeTab === 'not_started') return matchesSearch && s.status === 'not_started'
    return matchesSearch
  })

  return (
    <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto', padding: '24px 16px' }}>
      {/* Page Header */}
      <div className="page-head" style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1.2, marginBottom: 4 }}>
            Component 4 · Career Improvement Matrix
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
            <TrendingUp size={28} style={{ color: 'var(--accent)' }} /> Targeted Skill Progress & Interview Mastery
          </h1>
          <p className="muted" style={{ fontSize: 13, marginTop: 4, margin: 0 }}>
            Personalized improvement pathways strictly derived from the jobs you applied for, your interview question scores, and technical deficits.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={syncFromInterviews}
            disabled={syncBusy}
            style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700 }}
          >
            <Download size={14} /> {syncBusy ? 'Syncing...' : 'Sync from Applied Jobs & Interviews'}
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={loadData}
            title="Refresh progress"
          >
            <RefreshCw size={14} className={busy ? 'spin' : ''} />
          </button>
        </div>
      </div>

      {/* Career Trajectory & Progress Banner */}
      <div className="card" style={{ padding: 24, marginBottom: 24, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 24, alignItems: 'center' }}>
          {/* Gauge */}
          <div style={{ textAlign: 'center', paddingRight: 24, borderRight: '1px solid var(--border)' }}>
            <div style={{ position: 'relative', width: 90, height: 90, margin: '0 auto 10px' }}>
              <svg width="90" height="90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="var(--border)" strokeWidth="8" />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke={careerTier.color}
                  strokeWidth="8"
                  strokeDasharray={`${pct * 2.51} 251`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                  style={{ transition: 'stroke-dasharray 0.8s ease' }}
                />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: 20, fontWeight: 900, color: 'var(--text)' }}>{pct.toFixed(0)}%</span>
                <span style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-muted)' }}>CLOSED</span>
              </div>
            </div>
            <div style={{ fontSize: 13, fontWeight: 800, color: careerTier.color }}>{careerTier.title}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{careerTier.level}</div>
          </div>

          {/* Metrics summary */}
          <div>
            <h3 style={{ fontSize: 15, fontWeight: 800, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={16} style={{ color: 'var(--accent)' }} /> Interview Improvement Overview
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Target Deficits</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text)' }}>{stats.total || 0}</div>
              </div>
              <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ fontSize: 11, color: '#3b82f6' }}>In Progress</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#3b82f6' }}>{stats.in_progress || 0}</div>
              </div>
              <div style={{ padding: 12, background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)', textAlign: 'center' }}>
                <div style={{ fontSize: 11, color: '#22c55e' }}>Mastered</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#22c55e' }}>{stats.completed || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs & Search */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 6 }}>
          {[
            { id: 'all', label: `All Targets (${skills.length})` },
            { id: 'not_started', label: `Not Started (${stats.not_started || 0})` },
            { id: 'in_progress', label: `In Progress (${stats.in_progress || 0})` },
            { id: 'completed', label: `Mastered (${stats.completed || 0})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="btn btn-sm"
              style={{
                background: activeTab === tab.id ? 'var(--color-primary)' : 'var(--bg-elevated)',
                color: activeTab === tab.id ? '#fff' : 'var(--text-muted)',
                border: '1px solid var(--border)',
                fontWeight: 600,
                fontSize: 12,
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ position: 'relative', minWidth: 220 }}>
          <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search skill, role or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ height: 34, paddingLeft: 30, fontSize: 12, borderRadius: 6, width: '100%' }}
          />
        </div>
      </div>

      {/* Tracked Skills List */}
      {filteredSkills.length === 0 ? (
        <div className="card" style={{ padding: 40, textAlign: 'center' }}>
          <Zap size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>No Skills in this Filter</h3>
          <p className="muted" style={{ fontSize: 13, marginBottom: 16 }}>
            Click below to sync deficits from the jobs you applied for and the technical interviews you faced.
          </p>
          <button onClick={syncFromInterviews} className="btn btn-primary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <Download size={14} /> Sync Deficits from Interviews
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filteredSkills.map((item, idx) => {
            const isCompleted = item.status === 'completed'
            const isInProgress = item.status === 'in_progress'

            return (
              <div
                key={idx}
                className="card"
                style={{
                  padding: 18,
                  borderRadius: 10,
                  border: isCompleted ? '1px solid rgba(34, 197, 94, 0.4)' : isInProgress ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid var(--border)',
                  background: 'var(--bg-elevated)',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
                  <div style={{ flex: 1, minWidth: 260 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <h3 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text)', margin: 0 }}>
                        {item.skill}
                      </h3>
                      {item.priority && (
                        <span style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '2px 6px',
                          borderRadius: 4,
                          background: item.priority === 'Critical' || item.priority === 'High' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                          color: item.priority === 'Critical' || item.priority === 'High' ? '#ef4444' : '#f59e0b'
                        }}>
                          {item.priority} Priority
                        </span>
                      )}
                    </div>

                    {/* Source context */}
                    {item.source_role && (
                      <div style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Briefcase size={12} /> Target: {item.source_role} {item.source_company ? `(${item.source_company})` : ''}
                      </div>
                    )}

                    {item.deficit_reason && (
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>
                        {item.deficit_reason}
                      </div>
                    )}

                    {/* Improvement tip */}
                    {item.improvement_tips && (
                      <div style={{ fontSize: 12, color: 'var(--text)', background: 'var(--bg)', padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)', marginBottom: 8 }}>
                        💡 <strong>Improvement Focus:</strong> {item.improvement_tips}
                      </div>
                    )}
                  </div>

                  {/* Right side: Course Link & Status Controls */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 10 }}>
                    {/* Status Toggle Buttons */}
                    <div style={{ display: 'flex', gap: 4, background: 'var(--bg)', padding: 3, borderRadius: 6, border: '1px solid var(--border)' }}>
                      <button
                        onClick={() => updateStatus(item.skill, 'not_started')}
                        style={{
                          padding: '4px 10px',
                          fontSize: 11,
                          fontWeight: 600,
                          border: 'none',
                          borderRadius: 4,
                          cursor: 'pointer',
                          background: item.status === 'not_started' ? 'rgba(245, 158, 11, 0.2)' : 'transparent',
                          color: item.status === 'not_started' ? '#f59e0b' : 'var(--text-muted)'
                        }}
                      >
                        Not Started
                      </button>
                      <button
                        onClick={() => updateStatus(item.skill, 'in_progress')}
                        style={{
                          padding: '4px 10px',
                          fontSize: 11,
                          fontWeight: 600,
                          border: 'none',
                          borderRadius: 4,
                          cursor: 'pointer',
                          background: item.status === 'in_progress' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                          color: item.status === 'in_progress' ? '#3b82f6' : 'var(--text-muted)'
                        }}
                      >
                        Learning 🚀
                      </button>
                      <button
                        onClick={() => updateStatus(item.skill, 'completed')}
                        style={{
                          padding: '4px 10px',
                          fontSize: 11,
                          fontWeight: 600,
                          border: 'none',
                          borderRadius: 4,
                          cursor: 'pointer',
                          background: item.status === 'completed' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
                          color: item.status === 'completed' ? '#22c55e' : 'var(--text-muted)'
                        }}
                      >
                        Mastered ✓
                      </button>
                    </div>

                    {/* Course Link */}
                    {item.course_url && (
                      <a
                        href={item.course_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-ghost btn-sm"
                        style={{ fontSize: 11, display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent)' }}
                      >
                        <BookOpen size={12} /> {item.course_name || 'Practice Course'} <ExternalLink size={10} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
