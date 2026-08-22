import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  TrendingUp, CheckCircle2, Clock, AlertCircle, Download, Sparkles,
  Rocket, Plus, Search, ChevronRight, BookOpen, ExternalLink, Award, Check
} from 'lucide-react'
import {
  c4Progress, c4ProgressPopulate, c4ProgressSync, c4ProgressUpdate
} from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function Progress() {
  const navigate = useNavigate()
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [syncBusy, setSyncBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [newSkillInput, setNewSkillInput] = useState('')
  const [addBusy, setAddBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') {
      navigate('/login/candidate')
      return
    }
    loadData()
  }, [])

  const loadData = async () => {
    setBusy(true)
    try {
      const r = await c4Progress(candidateId)
      setData(r.data)
    } catch {
      toast.error('Failed to load progress data')
    } finally {
      setBusy(false)
    }
  }

  const syncFromInterviews = async () => {
    setSyncBusy(true)
    try {
      let r = null
      try {
        r = await c4ProgressSync(candidateId)
      } catch {
        r = await c4ProgressPopulate({ candidate_id: candidateId })
      }
      const count = r?.data?.synced_count ?? r?.data?.populated ?? 0
      toast.success(`Synced ${count} target skills from your interview and application history!`)
      loadData()
    } catch {
      toast.error('Failed to sync from applied interviews')
    } finally {
      setSyncBusy(false)
    }
  }

  const updateStatus = async (skill, status) => {
    try {
      await c4ProgressUpdate({
        candidate_id: candidateId,
        skill,
        status,
        notes: ''
      })
      const label = status === 'completed' ? 'Mastered' : status === 'in_progress' ? 'In Progress' : 'Target Set'
      toast.success(`${skill}: ${label}`)
      loadData()
    } catch {
      toast.error('Failed to update progress status')
    }
  }

  const addCustomSkill = async (e) => {
    e.preventDefault()
    if (!newSkillInput.trim()) return
    setAddBusy(true)
    try {
      await c4ProgressUpdate({
        candidate_id: candidateId,
        skill: newSkillInput.trim(),
        status: 'in_progress',
        notes: 'Custom Goal'
      })
      toast.success(`Added "${newSkillInput.trim()}" to learning goals!`)
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

  const careerTier = pct >= 85
    ? { title: 'Principal Architect / Lead', level: 'Level 4 (Executive)', color: 'var(--color-purple)' }
    : pct >= 60
    ? { title: 'Senior Tech Specialist', level: 'Level 3 (Advanced)', color: 'var(--color-success)' }
    : pct >= 30
    ? { title: 'Mid-Level Engineer', level: 'Level 2 (Intermediate)', color: 'var(--color-primary)' }
    : { title: 'Junior / Associate Developer', level: 'Level 1 (Foundation)', color: 'var(--color-warning)' }

  const filteredSkills = skills.filter((s) => {
    const matchesSearch = !searchTerm ||
      s.skill?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.source_role?.toLowerCase().includes(searchTerm.toLowerCase())

    if (activeTab === 'in_progress') return matchesSearch && s.status === 'in_progress'
    if (activeTab === 'completed') return matchesSearch && s.status === 'completed'
    if (activeTab === 'not_started') return matchesSearch && s.status === 'not_started'
    return matchesSearch
  })

  const completedCount = skills.filter((s) => s.status === 'completed').length
  const inProgressCount = skills.filter((s) => s.status === 'in_progress').length

  return (
    <div className="fade-in" style={{ maxWidth: 1060, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Component 4 Career Development"
        title="Targeted Skill Progress & Mastery"
        description="Track and master competencies identified from your real applied positions and AI technical interview evaluations."
        icon={TrendingUp}
        actions={
          <button
            className="btn btn-primary btn-sm"
            onClick={syncFromInterviews}
            disabled={syncBusy}
          >
            <Download size={14} /> {syncBusy ? 'Syncing...' : 'Sync from Skill Gap History'}
          </button>
        }
      />

      {/* KPI & Career Trajectory Banner */}
      <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-6)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 24, alignItems: 'center' }}>
          {/* Progress Ring */}
          <div style={{ position: 'relative', width: 96, height: 96, flexShrink: 0 }}>
            <svg width="96" height="96" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="none" stroke="var(--color-border-subtle)" strokeWidth="8" />
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
              <span style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                {pct.toFixed(0)}%
              </span>
              <span style={{ fontSize: '9px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>
                Mastery
              </span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: careerTier.color, letterSpacing: '0.08em', marginBottom: 2 }}>
              Current Progression Standing · {careerTier.level}
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: '0 0 6px 0', color: 'var(--color-fg)' }}>
              {careerTier.title}
            </h2>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', margin: 0, maxWidth: 640 }}>
              Master remaining technical skills across your application targets to progress to the next engineering tier.
            </p>
          </div>
        </div>
      </div>

      {/* KPI Stat Strip */}
      <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
        <StatCard
          label="Total Goals"
          value={skills.length}
          icon={Award}
          color="primary"
          helperText="Target skills identified"
        />
        <StatCard
          label="Mastered"
          value={completedCount}
          icon={CheckCircle2}
          color="success"
          helperText="Verified competencies"
        />
        <StatCard
          label="In Progress"
          value={inProgressCount}
          icon={Clock}
          color="info"
          helperText="Actively studying"
        />
        <StatCard
          label="Goal Completion"
          value={`${pct.toFixed(0)}%`}
          icon={TrendingUp}
          color="purple"
          helperText="Overall milestone index"
        />
      </div>

      {/* Add Custom Skill Form */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <form onSubmit={addCustomSkill} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Add custom learning target (e.g. System Design, PyTorch, GraphQL)..."
            value={newSkillInput}
            onChange={(e) => setNewSkillInput(e.target.value)}
            style={{ flex: 1, fontSize: 'var(--p-text-sm)' }}
          />
          <button type="submit" className="btn btn-primary btn-sm" disabled={addBusy} style={{ whiteSpace: 'nowrap' }}>
            <Plus size={14} /> Add Target Goal
          </button>
        </form>
      </div>

      {/* Skill List & Filters */}
      <div className="card" style={{ padding: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-4)', flexWrap: 'wrap', gap: 12 }}>
          {/* Status Filter Pills */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {[
              { id: 'all', label: `All Goals (${skills.length})` },
              { id: 'in_progress', label: `In Progress (${inProgressCount})` },
              { id: 'completed', label: `Mastered (${completedCount})` },
              { id: 'not_started', label: 'Not Started' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`btn btn-sm ${activeTab === tab.id ? 'btn-primary' : 'btn-ghost'}`}
                style={{ fontSize: 'var(--p-text-xs)' }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div style={{ position: 'relative', width: 220 }}>
            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
            <input
              type="text"
              placeholder="Filter goals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: 30, height: 34, fontSize: 'var(--p-text-xs)' }}
            />
          </div>
        </div>

        {/* Skill Items List */}
        {filteredSkills.length === 0 ? (
          <EmptyState
            title="No skills found"
            description="Sync from applied interviews or add your first custom technical learning goal above."
            icon={Award}
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filteredSkills.map((item, idx) => {
              const isMastered = item.status === 'completed'
              const isInProgress = item.status === 'in_progress'

              return (
                <div
                  key={item.skill || idx}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)',
                    background: 'var(--color-bg-elevated)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 14,
                    flexWrap: 'wrap'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: isMastered ? 'var(--color-success-muted)' : isInProgress ? 'var(--color-primary-muted)' : 'var(--color-border-subtle)',
                      color: isMastered ? 'var(--color-success)' : isInProgress ? 'var(--color-primary)' : 'var(--color-fg-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '11px',
                      fontWeight: 800,
                      flexShrink: 0
                    }}>
                      {isMastered ? '✓' : idx + 1}
                    </div>

                    <div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                        {item.skill}
                      </div>
                      {item.source_role && (
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                          Target: {item.source_role}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <button
                      className={`btn btn-sm ${isInProgress ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => updateStatus(item.skill, 'in_progress')}
                      style={{ fontSize: '11px', padding: '4px 10px' }}
                    >
                      <Clock size={12} /> Learning
                    </button>
                    <button
                      className={`btn btn-sm ${isMastered ? 'btn-success' : 'btn-ghost'}`}
                      onClick={() => updateStatus(item.skill, 'completed')}
                      style={{ fontSize: '11px', padding: '4px 10px' }}
                    >
                      <Check size={12} /> Mastered
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
