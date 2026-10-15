import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  BarChart3, Briefcase, Target, TrendingUp, AlertTriangle,
  DollarSign, ArrowLeft, ChevronRight, Brain, Users
} from 'lucide-react'
import { c4RoleInsights, c4CareerRoles, c3Roles } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

function SkillBar({ skill, demand, color = 'var(--color-primary)' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', minWidth: 120, fontWeight: 600 }}>{skill}</span>
      <div style={{ flex: 1, height: 8, background: 'var(--color-bg-soft)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
        <div style={{
          height: '100%',
          width: `${Math.min(demand, 100)}%`,
          background: color,
          borderRadius: 'var(--radius-full)',
          transition: 'width 0.4s ease',
        }} />
      </div>
      <span style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg)', minWidth: 36, textAlign: 'right' }}>
        {Math.round(demand)}%
      </span>
    </div>
  )
}

export default function RoleInsights() {
  useAuth('company')
  const navigate = useNavigate()
  const { role: urlRole } = useParams()

  const [roles, setRoles] = useState([])
  const [loadingRoles, setLoadingRoles] = useState(true)
  const [selectedRole, setSelectedRole] = useState(urlRole || '')
  const [insights, setInsights] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    loadRoles()
  }, [])

  useEffect(() => {
    if (selectedRole) {
      loadInsights(selectedRole)
    }
  }, [selectedRole])

  const loadRoles = async () => {
    setLoadingRoles(true)
    try {
      const [careerRes, c3Res] = await Promise.all([
        c4CareerRoles().catch(() => ({ data: [] })),
        c3Roles().catch(() => ({ data: [] })),
      ])
      const careerRoles = Array.isArray(careerRes?.data) ? careerRes.data : careerRes?.data?.roles || []
      const c3RoleList = Array.isArray(c3Res?.data) ? c3Res.data : c3Res?.data?.jobs || []
      const combined = [...careerRoles, ...c3RoleList]
      const unique = combined.filter((r, i, arr) => {
        const name = r.title || r.role || r.name || r
        return arr.findIndex(x => (x.title || x.role || x.name || x) === name) === i
      })
      setRoles(unique)
      if (urlRole && !selectedRole) {
        setSelectedRole(urlRole)
      }
    } catch {
      toast.error('Failed to load roles')
    } finally {
      setLoadingRoles(false)
    }
  }

  const loadInsights = async (roleName) => {
    setBusy(true)
    setInsights(null)
    try {
      const res = await c4RoleInsights(roleName)
      setInsights(res?.data || null)
    } catch (err) {
      console.error('loadInsights error:', err)
      toast.error('Failed to load role insights')
    } finally {
      setBusy(false)
    }
  }

  const data = insights?.insights || insights || {}
  const demandLevel = data.demand_level || data.market_demand || '—'
  const avgSkillGap = data.avg_skill_gap || data.skill_gap_avg || 0
  const topMissingSkills = data.top_missing_skills || data.missing_skills || []
  const salaryRange = data.salary_range || data.compensation || {}
  const marketAvg = data.market_average || data.benchmark || {}
  const skillDemand = data.skill_demand || data.skill_breakdown || []
  const roleMetrics = data.metrics || data

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate(-1)}
        style={{ marginBottom: 'var(--p-space-4)' }}
      >
        <ArrowLeft size={14} /> Back
      </button>

      <PageHeader
        badge="Role Analytics"
        title="Role Insights"
        description="In-depth analytics for a specific job role including market demand, skill gaps, and salary benchmarks."
        icon={BarChart3}
        actions={
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            style={{ fontSize: 'var(--p-text-sm)', padding: '8px 12px' }}
          >
            <option value="">Select a role...</option>
            {roles.map((r) => {
              const roleName = r.title || r.role || r.name || r
              return (
                <option key={roleName} value={roleName}>{roleName}</option>
              )
            })}
          </select>
        }
      />

      {!selectedRole ? (
        <EmptyState
          title="Select a role to view insights"
          description="Choose a job role from the dropdown above to see detailed market analytics, skill demand, and salary benchmarks."
          icon={Briefcase}
        />
      ) : busy ? (
        <SkeletonLoader type="stat" count={4} />
      ) : !insights ? (
        <EmptyState
          title="No insights available"
          description={`No analytics data found for "${selectedRole}". Try selecting a different role.`}
          icon={AlertTriangle}
        />
      ) : (
        <>
          {/* Role Metric Cards */}
          <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
            <StatCard
              label="Market Demand"
              value={typeof demandLevel === 'number' ? `${demandLevel}%` : demandLevel}
              icon={TrendingUp}
              color={demandLevel === 'High' || (typeof demandLevel === 'number' && demandLevel >= 70) ? 'success' : demandLevel === 'Medium' || (typeof demandLevel === 'number' && demandLevel >= 40) ? 'warning' : 'danger'}
              helperText="Market demand level"
            />
            <StatCard
              label="Avg Skill Gap"
              value={typeof avgSkillGap === 'number' ? `${Math.round(avgSkillGap)}%` : avgSkillGap}
              icon={Target}
              color={avgSkillGap > 40 ? 'danger' : avgSkillGap > 20 ? 'warning' : 'success'}
              helperText="Candidate skill shortfall"
            />
            <StatCard
              label="Salary Range"
              value={salaryRange.min != null ? `$${Number(salaryRange.min).toLocaleString()}–$${Number(salaryRange.max).toLocaleString()}` : salaryRange.range || '—'}
              icon={DollarSign}
              color="success"
              helperText="Annual compensation"
            />
            <StatCard
              label="Open Positions"
              value={roleMetrics.open_positions || roleMetrics.openings || 0}
              icon={Briefcase}
              color="purple"
              helperText="Currently hiring"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--p-space-5)', marginBottom: 'var(--p-space-6)' }}>
            {/* Skill Demand Chart */}
            <div className="card" style={{ padding: 'var(--p-space-5)' }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Brain size={16} style={{ color: 'var(--color-primary)' }} /> Skill Demand Breakdown
              </h3>
              {(Array.isArray(skillDemand) ? skillDemand : []).length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {(Array.isArray(skillDemand) ? skillDemand : []).slice(0, 10).map((s, i) => (
                    <SkillBar
                      key={i}
                      skill={s.skill || s.name || s}
                      demand={s.demand || s.percentage || s.value || 50}
                      color={['var(--color-primary)', 'var(--color-purple)', 'var(--color-info)', 'var(--color-success)', 'var(--color-warning)'][i % 5]}
                    />
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center', margin: '20px 0' }}>
                  No skill demand data available.
                </p>
              )}
            </div>

            {/* Top Missing Skills */}
            <div className="card" style={{ padding: 'var(--p-space-5)' }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={16} style={{ color: 'var(--color-warning)' }} /> Top Missing Skills
              </h3>
              {(Array.isArray(topMissingSkills) ? topMissingSkills : []).length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {(Array.isArray(topMissingSkills) ? topMissingSkills : []).map((item, i) => {
                    const skillName = typeof item === 'string' ? item : item.skill || item.name || '—'
                    const gap = typeof item === 'object' ? (item.gap || item.percentage || item.value || 0) : 0
                    return (
                      <div key={i} style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        background: 'var(--color-bg-elevated)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border-subtle)',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{
                            width: 22,
                            height: 22,
                            borderRadius: 'var(--radius-full)',
                            background: 'var(--color-warning-muted)',
                            color: 'var(--color-warning)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '10px',
                            fontWeight: 800,
                          }}>
                            {i + 1}
                          </span>
                          <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 600, color: 'var(--color-fg)' }}>{skillName}</span>
                        </div>
                        {gap > 0 && (
                          <span style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--p-font-mono)', color: 'var(--color-warning)' }}>
                            {Math.round(gap)}% gap
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center', margin: '20px 0' }}>
                  No missing skills data available.
                </p>
              )}
            </div>
          </div>

          {/* Market Comparison */}
          {(marketAvg.avg_skill_score || marketAvg.avg_experience || marketAvg.avg_overall) && (
            <div className="card" style={{ padding: 'var(--p-space-5)' }}>
              <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Users size={16} style={{ color: 'var(--color-info)' }} /> Market Comparison
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                {[
                  { label: 'Avg Skill Score', value: marketAvg.avg_skill_score, suffix: '%' },
                  { label: 'Avg Experience', value: marketAvg.avg_experience, suffix: ' yrs' },
                  { label: 'Avg Overall', value: marketAvg.avg_overall, suffix: '%' },
                ].map((item) => (
                  <div key={item.label} style={{
                    padding: 14,
                    background: 'var(--color-bg-elevated)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)',
                    textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 4 }}>{item.label}</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg)' }}>
                      {item.value != null ? `${Math.round(item.value)}${item.suffix}` : '—'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
