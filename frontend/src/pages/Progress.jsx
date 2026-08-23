import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  TrendingUp, CheckCircle2, Clock, AlertCircle, Download, Sparkles,
  Rocket, Plus, Search, ChevronRight, BookOpen, ExternalLink, Award, Check, Trash2, RotateCcw
} from 'lucide-react'
import {
  c4Progress, c4ProgressSync, c4ProgressPopulate, c4ProgressUpdate,
  c4ProgressDelete, c4ProgressDeleteSkill
} from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'
import ConfirmDialog from '../components/ConfirmDialog'

export default function Progress() {
  const navigate = useNavigate()
  useAuth('candidate')
  const candidateId = localStorage.getItem('recruitai.user_id') || 'web-user'

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncBusy, setSyncBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [newSkillInput, setNewSkillInput] = useState('')
  const [addBusy, setAddBusy] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const r = await c4Progress(candidateId)
      setData(r.data)
    } catch {
      toast.error('Failed to load progress data')
    } finally {
      setLoading(false)
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
      toast.success(`Synced ${count} target competencies into your learning path!`)
      await loadData()
    } catch {
      toast.error('Failed to sync progress goals')
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
      await loadData()
    } catch {
      toast.error('Failed to update progress status')
    }
  }

  const addCustomSkill = async (e) => {
    e.preventDefault()
    const sk = newSkillInput.trim()
    if (!sk) return
    setAddBusy(true)
    try {
      await c4ProgressUpdate({
        candidate_id: candidateId,
        skill: sk,
        status: 'in_progress',
        notes: 'Custom Goal'
      })
      toast.success(`Added "${sk}" to learning goals!`)
      setNewSkillInput('')
      await loadData()
    } catch {
      toast.error('Failed to add skill goal')
    } finally {
      setAddBusy(false)
    }
  }

  const deleteSingleSkill = (skill) => {
    setConfirm({
      open: true,
      title: `Remove "${skill}" from goals?`,
      message: 'This goal will be removed from your active progress tracking list.',
      danger: true,
      action: async () => {
        try {
          await c4ProgressDeleteSkill(candidateId, skill)
          toast.success(`Removed "${skill}"`)
          await loadData()
        } catch {
          toast.error('Failed to remove skill goal')
        }
      }
    })
  }

  const resetAllGoals = () => {
    setConfirm({
      open: true,
      title: 'Reset All Learning Goals?',
      message: 'This will clear all tracked skill progress. You can re-sync anytime from your application & interview history.',
      danger: true,
      action: async () => {
        try {
          await c4ProgressDelete(candidateId)
          toast.success('Learning goals reset')
          await loadData()
        } catch {
          toast.error('Failed to reset goals')
        }
      }
    })
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
    if (activeTab === 'not_started') return matchesSearch && (s.status === 'not_started' || !s.status)
    return matchesSearch
  })

  const completedCount = skills.filter((s) => s.status === 'completed').length
  const inProgressCount = skills.filter((s) => s.status === 'in_progress').length

  return (
    <div className="fade-in" style={{ maxWidth: 1080, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Career Progression & Mastery"
        title="Skill Development & Target Goals"
        description="Track and master key technical competencies diagnosed from your real job applications and technical interview assessments."
        icon={TrendingUp}
        actions={
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button
              className="btn btn-ghost btn-sm"
              onClick={resetAllGoals}
              disabled={skills.length === 0}
              title="Reset all goals"
            >
              <RotateCcw size={13} /> Reset
            </button>
            <button
              className="btn btn-primary btn-sm"
              onClick={syncFromInterviews}
              disabled={syncBusy}
            >
              <Download size={14} /> {syncBusy ? 'Syncing...' : 'Sync from Skill Gap'}
            </button>
          </div>
        }
      />

      {/* KPI & Career Trajectory Banner */}
      <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-6)', borderRadius: 'var(--radius-xl)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 24, alignItems: 'center' }}>
          {/* Progress Ring with Radial Glow */}
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
                style={{ transition: 'stroke-dasharray 0.8s cubic-bezier(0.16, 1, 0.3, 1)' }}
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
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: careerTier.color, letterSpacing: '0.08em', marginBottom: 3 }}>
              Progression Standing · {careerTier.level}
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, margin: '0 0 6px 0', color: 'var(--color-fg)', letterSpacing: '-0.02em' }}>
              {careerTier.title}
            </h2>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', margin: 0, maxWidth: 640, lineHeight: 1.5 }}>
              Complete remaining technical competencies across your application targets to advance to the next professional engineering tier.
            </p>
          </div>
        </div>
      </div>

      {/* KPI Stat Strip with Auto CountUp */}
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
          helperText="Overall roadmap index"
        />
      </div>

      {/* Add Custom Skill Form */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)', borderRadius: 'var(--radius-lg)' }}>
        <form onSubmit={addCustomSkill} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Add custom learning target (e.g. System Design, PyTorch, GraphQL, Docker)..."
            value={newSkillInput}
            onChange={(e) => setNewSkillInput(e.target.value)}
            style={{ flex: 1, fontSize: 'var(--p-text-sm)', height: 40 }}
          />
          <button type="submit" className="btn btn-primary btn-sm" disabled={addBusy} style={{ whiteSpace: 'nowrap', height: 40 }}>
            <Plus size={15} /> Add Target Goal
          </button>
        </form>
      </div>

      {/* Skill List & Filters */}
      <div className="card" style={{ padding: 'var(--p-space-5)', borderRadius: 'var(--radius-xl)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--p-space-4)', flexWrap: 'wrap', gap: 12 }}>
          {/* Status Filter Tabs */}
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
        {loading ? (
          <SkeletonLoader type="card" count={3} />
        ) : filteredSkills.length === 0 ? (
          <EmptyState
            title="No learning goals found"
            description="Sync your diagnostic results from applied positions or add custom competencies above."
            actionLabel="Sync from Skill Gap"
            onAction={syncFromInterviews}
            icon={Award}
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filteredSkills.map((item, idx) => {
              const isMastered = item.status === 'completed'
              const isInProgress = item.status === 'in_progress'
              const accentBorderColor = isMastered
                ? 'var(--color-success)'
                : isInProgress
                ? 'var(--color-primary)'
                : 'var(--color-warning)'

              return (
                <div
                  key={item.skill || idx}
                  className="card"
                  style={{
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid var(--color-border)',
                    borderLeft: `4px solid ${accentBorderColor}`,
                    background: 'var(--color-bg-elevated)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 14,
                    flexWrap: 'wrap',
                    marginBottom: 0
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 28,
                      height: 28,
                      borderRadius: 'var(--radius-full)',
                      background: isMastered ? 'var(--color-success-muted)' : isInProgress ? 'var(--color-primary-muted)' : 'var(--color-warning-muted)',
                      color: isMastered ? 'var(--color-success)' : isInProgress ? 'var(--color-primary)' : 'var(--color-warning)',
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
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
                        {item.source_role && <span>Target: {item.source_role}</span>}
                        {item.notes && <span>• {item.notes}</span>}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <a
                      href={`https://www.coursera.org/search?query=${encodeURIComponent(item.skill)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="goal-action-btn course"
                      title="Explore courses"
                    >
                      <BookOpen size={13} /> Course <ExternalLink size={11} />
                    </a>

                    <button
                      className={`goal-action-btn in-progress ${isInProgress ? 'active' : ''}`}
                      onClick={() => updateStatus(item.skill, 'in_progress')}
                    >
                      <Clock size={13} /> In Progress
                    </button>

                    <button
                      className={`goal-action-btn mastered ${isMastered ? 'active' : ''}`}
                      onClick={() => updateStatus(item.skill, 'completed')}
                    >
                      <Check size={13} /> Mastered
                    </button>

                    <button
                      className="goal-action-btn delete"
                      onClick={() => deleteSingleSkill(item.skill)}
                      title="Delete goal"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel={confirm.danger ? 'Confirm' : 'OK'}
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
