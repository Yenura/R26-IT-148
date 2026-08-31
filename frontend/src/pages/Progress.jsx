import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  TrendingUp, CheckCircle2, Clock, AlertCircle, Download, Sparkles,
  Rocket, Plus, Search, ChevronRight, BookOpen, ExternalLink, Award, Check, Trash2, RotateCcw
} from 'lucide-react'
import {
  c4Progress, c4ProgressSync, c4ProgressPopulate, c4ProgressUpdate,
  c4ProgressDelete, c4ProgressDeleteSkill, authGetProfile
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
  const [candidateId, setCandidateId] = useState(() => localStorage.getItem('recruitai.user_id') || 'web-user')

  const [data, setData] = useState(() => {
    try {
      const uId = localStorage.getItem('recruitai.user_id') || 'web-user'
      const cached = sessionStorage.getItem(`recruitai.progress.${uId}`)
      return cached ? JSON.parse(cached) : null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(false)
  const [syncBusy, setSyncBusy] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [newSkillInput, setNewSkillInput] = useState('')
  const [addBusy, setAddBusy] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  const [selectedRoleFilter, setSelectedRoleFilter] = useState('all')

  useEffect(() => { loadData() }, [])

  const resolveCandidateId = async () => {
    let uId = localStorage.getItem('recruitai.user_id')
    if (!uId || uId === 'web-user') {
      try {
        const pr = await authGetProfile()
        if (pr?.data?._id) {
          uId = String(pr.data._id)
          localStorage.setItem('recruitai.user_id', uId)
          setCandidateId(uId)
        }
      } catch {}
    }
    return uId || candidateId || 'web-user'
  }

  const loadData = async () => {
    if (!data) setLoading(true)
    try {
      const uId = await resolveCandidateId()
      let r = await c4Progress(uId)
      if (!r?.data?.skills || r.data.skills.length === 0) {
        try {
          r = await c4ProgressSync(uId)
        } catch {
          // ignore fallback
        }
      }
      if (r?.data) {
        setData(r.data)
        try {
          sessionStorage.setItem(`recruitai.progress.${uId}`, JSON.stringify(r.data))
        } catch {}
      }
    } catch {
      toast.error('Failed to load progress data')
    } finally {
      setLoading(false)
    }
  }

  const syncFromInterviews = async () => {
    setSyncBusy(true)
    try {
      const uId = await resolveCandidateId()
      let r = null
      try {
        r = await c4ProgressSync(uId)
      } catch {
        r = await c4ProgressPopulate({ candidate_id: uId })
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
      const uId = await resolveCandidateId()
      await c4ProgressUpdate({
        candidate_id: uId,
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
      const uId = await resolveCandidateId()
      await c4ProgressUpdate({
        candidate_id: uId,
        skill: sk,
        status: 'in_progress',
        source_role: selectedRoleFilter !== 'all' ? selectedRoleFilter : 'Custom Goal',
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
          const uId = await resolveCandidateId()
          await c4ProgressDeleteSkill(uId, skill)
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
          const uId = await resolveCandidateId()
          await c4ProgressDelete(uId)
          toast.success('Learning goals reset')
          await loadData()
        } catch {
          toast.error('Failed to reset goals')
        }
      }
    })
  }

  const skills = data?.skills || []

  // Extract all unique target career roles from diagnosed goals
  const uniqueRoles = Array.from(
    new Set(skills.map((s) => s.source_role).filter(Boolean))
  )

  // Scope skills by the selected career/role
  const roleScopedSkills = selectedRoleFilter === 'all'
    ? skills
    : skills.filter((s) => s.source_role?.toLowerCase() === selectedRoleFilter.toLowerCase())

  const roleCompletedCount = roleScopedSkills.filter((s) => s.status === 'completed').length
  const roleInProgressCount = roleScopedSkills.filter((s) => s.status === 'in_progress').length
  const roleTotalCount = roleScopedSkills.length
  const pct = roleTotalCount > 0 ? Math.round((roleCompletedCount / roleTotalCount) * 100) : 0

  const careerTier = pct >= 85
    ? {
        title: selectedRoleFilter === 'all' ? 'Full Competency Mastery' : `Full ${selectedRoleFilter} Mastery`,
        level: 'Level 4 · Mastery Stage',
        color: 'var(--color-purple)',
        desc: `Outstanding progress! You have mastered almost all technical competencies diagnosed across ${selectedRoleFilter === 'all' ? 'your job applications' : selectedRoleFilter}.`
      }
    : pct >= 60
    ? {
        title: selectedRoleFilter === 'all' ? 'Advanced Upskilling Standing' : `Advanced ${selectedRoleFilter} Standing`,
        level: 'Level 3 · Advanced Stage',
        color: 'var(--color-success)',
        desc: `Great momentum! Over half of your diagnosed technical competencies for ${selectedRoleFilter === 'all' ? 'your applications' : selectedRoleFilter} are completed.`
      }
    : pct >= 30
    ? {
        title: selectedRoleFilter === 'all' ? 'Active Learning & Progression' : `Active ${selectedRoleFilter} Upskilling`,
        level: 'Level 2 · Intermediate Stage',
        color: 'var(--color-primary)',
        desc: `You are actively closing critical skill gaps for ${selectedRoleFilter === 'all' ? 'your application goals' : selectedRoleFilter}. Keep advancing your in-progress competencies.`
      }
    : {
        title: selectedRoleFilter === 'all' ? 'Foundation & Diagnostics Stage' : `${selectedRoleFilter} Diagnostic Baseline`,
        level: 'Level 1 · Foundation Stage',
        color: 'var(--color-warning)',
        desc: `Track and complete your diagnosed technical skill deficits below to increase your job match fit for ${selectedRoleFilter === 'all' ? 'all applied roles' : selectedRoleFilter}.`
      }

  const filteredSkills = roleScopedSkills.filter((s) => {
    const matchesSearch = !searchTerm ||
      s.skill?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.source_role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.source_company?.toLowerCase().includes(searchTerm.toLowerCase())

    if (activeTab === 'in_progress') return matchesSearch && s.status === 'in_progress'
    if (activeTab === 'completed') return matchesSearch && s.status === 'completed'
    if (activeTab === 'not_started') return matchesSearch && (s.status === 'not_started' || !s.status)
    return matchesSearch
  })

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

      {/* Target Career Filter Bar */}
      {uniqueRoles.length > 0 && (
        <div style={{
          marginBottom: 'var(--p-space-5)',
          padding: '12px 16px',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sparkles size={16} style={{ color: 'var(--color-primary)' }} />
            <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Target Career Focus:
            </span>
          </div>

          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            {uniqueRoles.length > 1 && (
              <button
                onClick={() => setSelectedRoleFilter('all')}
                className={`btn btn-sm ${selectedRoleFilter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                style={{ fontSize: 'var(--p-text-xs)', borderRadius: 'var(--radius-full)', padding: '4px 12px' }}
              >
                All Careers ({skills.length})
              </button>
            )}
            {uniqueRoles.map((role) => {
              const count = skills.filter((s) => s.source_role === role).length
              const isSelected = selectedRoleFilter.toLowerCase() === role.toLowerCase() || uniqueRoles.length === 1
              return (
                <button
                  key={role}
                  onClick={() => setSelectedRoleFilter(role)}
                  className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-ghost'}`}
                  style={{
                    fontSize: 'var(--p-text-xs)',
                    borderRadius: 'var(--radius-full)',
                    padding: '4px 14px',
                    border: isSelected ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                    fontWeight: 700
                  }}
                >
                  🎯 {role} ({count} {count === 1 ? 'goal' : 'goals'})
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* KPI & Skill Trajectory Banner */}
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
              Roadmap Standing · {careerTier.level}
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, margin: '0 0 6px 0', color: 'var(--color-fg)', letterSpacing: '-0.02em' }}>
              {careerTier.title}
            </h2>
            <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', margin: 0, maxWidth: 640, lineHeight: 1.5 }}>
              {careerTier.desc}
            </p>
          </div>
        </div>
      </div>

      {/* KPI Stat Strip with Auto CountUp */}
      <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
        <StatCard
          label={selectedRoleFilter === 'all' ? "Total Goals" : `${selectedRoleFilter} Goals`}
          value={roleTotalCount}
          icon={Award}
          color="primary"
          helperText="Target skills identified"
        />
        <StatCard
          label="Mastered"
          value={roleCompletedCount}
          icon={CheckCircle2}
          color="success"
          helperText="Verified competencies"
        />
        <StatCard
          label="In Progress"
          value={roleInProgressCount}
          icon={Clock}
          color="info"
          helperText="Actively studying"
        />
        <StatCard
          label="Goal Completion"
          value={`${pct.toFixed(0)}%`}
          icon={TrendingUp}
          color="purple"
          helperText="Role roadmap index"
        />
      </div>

      {/* Add Custom Skill Form */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)', borderRadius: 'var(--radius-lg)' }}>
        <form onSubmit={addCustomSkill} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            type="text"
            placeholder={selectedRoleFilter !== 'all' ? `Add custom learning target for ${selectedRoleFilter}...` : "Add custom learning target (e.g. System Design, PyTorch, GraphQL, Docker)..."}
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
              { id: 'all', label: `All (${roleTotalCount})` },
              { id: 'in_progress', label: `In Progress (${roleInProgressCount})` },
              { id: 'completed', label: `Mastered (${roleCompletedCount})` },
              { id: 'not_started', label: `Not Started (${roleTotalCount - roleCompletedCount - roleInProgressCount})` }
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
              placeholder="Search skills, roles, tags..."
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
            title="No learning goals match your filters"
            description="Sync diagnostic goals from applied positions or switch to All Careers above."
            actionLabel="Sync from Skill Gap"
            onAction={syncFromInterviews}
            icon={Award}
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filteredSkills.map((item, idx) => {
              const isMastered = item.status === 'completed'
              const isInProgress = item.status === 'in_progress'
              const priority = item.priority || 'High'
              const priorityBg = priority === 'Critical' ? 'rgba(239, 68, 68, 0.15)' : priority === 'High' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(99, 102, 241, 0.15)'
              const priorityColor = priority === 'Critical' ? 'var(--color-danger)' : priority === 'High' ? 'var(--color-warning)' : 'var(--color-primary)'

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
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid var(--color-border)',
                    borderLeft: `4px solid ${accentBorderColor}`,
                    background: 'var(--color-bg-elevated)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 16,
                    flexWrap: 'wrap',
                    marginBottom: 0,
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, flex: 1, minWidth: 260 }}>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: 'var(--radius-full)',
                      background: isMastered ? 'var(--color-success-muted)' : isInProgress ? 'var(--color-primary-muted)' : 'var(--color-warning-muted)',
                      color: isMastered ? 'var(--color-success)' : isInProgress ? 'var(--color-primary)' : 'var(--color-warning)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 800,
                      flexShrink: 0,
                      marginTop: 2
                    }}>
                      {isMastered ? '✓' : idx + 1}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 800, fontSize: 'var(--p-text-base)', color: 'var(--color-fg)' }}>
                          {item.skill}
                        </span>
                        <span style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-full)',
                          background: priorityBg,
                          color: priorityColor,
                          border: `1px solid ${priorityColor}40`
                        }}>
                          {priority} Priority
                        </span>
                      </div>

                      {/* Deficit Reason & Job Tags */}
                      <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)', marginTop: 4, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                        {item.source_role && (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontWeight: 600, color: 'var(--color-fg-secondary)' }}>
                            🎯 {item.source_role}
                          </span>
                        )}
                        {item.source_company && (
                          <span style={{ color: 'var(--color-fg-muted)' }}>
                            • 🏢 {item.source_company}
                          </span>
                        )}
                      </div>

                      {item.deficit_reason && (
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4, fontStyle: 'italic' }}>
                          💡 {item.deficit_reason}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <a
                      href={item.course_url || `https://www.coursera.org/search?query=${encodeURIComponent(item.skill)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: 4, color: 'var(--color-primary)' }}
                      title={item.course_name || "Explore courses"}
                    >
                      <BookOpen size={13} /> {item.course_name ? 'Course' : 'Explore'} <ExternalLink size={11} />
                    </a>

                    <button
                      className={`btn btn-sm ${isInProgress ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => updateStatus(item.skill, 'in_progress')}
                      style={{ fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                    >
                      <Clock size={13} /> In Progress
                    </button>

                    <button
                      className={`btn btn-sm ${isMastered ? 'btn-success' : 'btn-ghost'}`}
                      onClick={() => updateStatus(item.skill, 'completed')}
                      style={{
                        fontSize: '11px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4,
                        background: isMastered ? 'var(--color-success)' : undefined,
                        color: isMastered ? '#fff' : undefined
                      }}
                    >
                      <Check size={13} /> Mastered
                    </button>

                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => deleteSingleSkill(item.skill)}
                      style={{ color: 'var(--color-danger)', padding: '6px 8px' }}
                      aria-label={`Remove ${item.skill} from goals`}
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
