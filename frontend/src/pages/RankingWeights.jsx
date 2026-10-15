import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Sliders, Save, RotateCcw, Briefcase, BarChart3,
  Target, Brain, Award, CheckCircle2
} from 'lucide-react'
import { c3Roles, c3SetWeights } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const DEFAULT_WEIGHTS = {
  skill: 0.30,
  experience: 0.25,
  education: 0.15,
  mcq: 0.15,
  interview: 0.15,
}

const WEIGHT_META = [
  { key: 'skill', label: 'Skill Match', icon: Target, description: 'How well the candidate\'s technical skills match the job requirements' },
  { key: 'experience', label: 'Experience', icon: Briefcase, description: 'Years and relevance of professional experience' },
  { key: 'education', label: 'Education', icon: Award, description: 'Academic qualifications and degree level' },
  { key: 'mcq', label: 'MCQ Score', icon: CheckCircle2, description: 'Multiple choice question accuracy from AI interview' },
  { key: 'interview', label: 'Interview Score', icon: Brain, description: 'Overall performance in the AI technical interview' },
]

export default function RankingWeights() {
  useAuth('company')
  const navigate = useNavigate()

  const [roles, setRoles] = useState([])
  const [loadingRoles, setLoadingRoles] = useState(true)
  const [selectedRole, setSelectedRole] = useState('')
  const [weights, setWeights] = useState({ ...DEFAULT_WEIGHTS })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    loadRoles()
  }, [])

  const loadRoles = async () => {
    setLoadingRoles(true)
    try {
      const res = await c3Roles()
      const data = Array.isArray(res?.data) ? res.data : res?.data?.jobs || []
      setRoles(data)
    } catch {
      toast.error('Failed to load available roles')
    } finally {
      setLoadingRoles(false)
    }
  }

  const handleWeightChange = (key, value) => {
    const num = parseFloat(value)
    if (isNaN(num) || num < 0 || num > 1) return
    setWeights((prev) => ({ ...prev, [key]: num }))
    setSaved(false)
  }

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0)

  const handleSave = async () => {
    if (Math.abs(totalWeight - 1) > 0.05) {
      toast.error(`Weights must sum to 1.0 (currently ${totalWeight.toFixed(2)})`)
      return
    }
    setSaving(true)
    try {
      const payload = {
        ...weights,
        role: selectedRole || undefined,
      }
      await c3SetWeights(payload)
      toast.success('Ranking weights saved successfully')
      setSaved(true)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to save weights')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setWeights({ ...DEFAULT_WEIGHTS })
    setSelectedRole('')
    setSaved(false)
    toast('Weights reset to defaults', { icon: '↺' })
  }

  return (
    <div className="fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate(-1)}
        style={{ marginBottom: 'var(--p-space-4)' }}
      >
        ← Back
      </button>

      <PageHeader
        badge="Ranking Configuration"
        title="Ranking Weights"
        description="Customize how candidate scores are weighted when computing final ranking positions. Weights must sum to 1.0."
        icon={Sliders}
      />

      {/* Role Selector */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={16} style={{ color: 'var(--color-primary)' }} /> Role Preset (Optional)
          </h3>
        </div>
        <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '0 0 12px' }}>
          Select a role to load role-specific default weights, or configure custom weights below.
        </p>
        {loadingRoles ? (
          <SkeletonLoader type="card" count={1} />
        ) : (
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            style={{ fontSize: 'var(--p-text-sm)' }}
          >
            <option value="">Use custom weights (no preset)</option>
            {roles.map((r) => {
              const roleId = r.id || r._id || r.role || r.title
              const roleName = r.title || r.role || r.name || roleId
              return (
                <option key={roleId} value={roleId}>{roleName}</option>
              )
            })}
          </select>
        )}
      </div>

      {/* Weight Sliders */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BarChart3 size={16} style={{ color: 'var(--color-primary)' }} /> Score Weights
          </h3>
          <div style={{
            fontSize: 'var(--p-text-xs)',
            fontWeight: 700,
            fontFamily: 'var(--p-font-mono)',
            padding: '3px 10px',
            borderRadius: 'var(--radius-full)',
            background: Math.abs(totalWeight - 1) <= 0.05 ? 'var(--color-success-muted)' : 'var(--color-danger-muted)',
            color: Math.abs(totalWeight - 1) <= 0.05 ? 'var(--color-success)' : 'var(--color-danger)',
            border: `1px solid ${Math.abs(totalWeight - 1) <= 0.05 ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}`,
          }}>
            Total: {totalWeight.toFixed(2)}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {WEIGHT_META.map(({ key, label, icon: Icon, description }) => {
            const value = weights[key]
            const pct = Math.round(value * 100)
            return (
              <div key={key}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-primary-muted)',
                    color: 'var(--color-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <Icon size={16} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{label}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>{description}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, fontFamily: 'var(--p-font-mono)', minWidth: 48, textAlign: 'right' }}>
                      {pct}%
                    </span>
                  </div>
                </div>
                <div style={{ position: 'relative', height: 8, background: 'var(--color-bg-soft)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    height: '100%',
                    width: `${pct}%`,
                    background: 'var(--color-primary)',
                    borderRadius: 'var(--radius-full)',
                    transition: 'width 0.2s ease',
                  }} />
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={value}
                  onChange={(e) => handleWeightChange(key, e.target.value)}
                  aria-label={`${label} weight`}
                  style={{
                    width: '100%',
                    height: 30,
                    cursor: 'pointer',
                    accentColor: 'var(--color-primary)',
                  }}
                />
              </div>
            )
          })}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          className="btn btn-ghost"
          onClick={handleReset}
        >
          <RotateCcw size={14} /> Reset to Defaults
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {saved && (
            <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-success)', fontWeight: 600 }}>
              ✓ Saved
            </span>
          )}
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={saving}
          >
            <Save size={14} /> {saving ? 'Saving...' : 'Save Weights'}
          </button>
        </div>
      </div>
    </div>
  )
}
