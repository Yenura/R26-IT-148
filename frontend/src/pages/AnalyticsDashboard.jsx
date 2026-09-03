import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  BarChart3, Users, Briefcase, TrendingUp, CheckCircle2,
  Clock, Award, Target, Activity
} from 'lucide-react'
import { c4AnalyticsSummary } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

function BarChart({ data, maxValue }) {
  const max = maxValue || Math.max(...data.map(d => d.value), 1)
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 120, padding: '0 4px' }}>
      {data.map((item, i) => {
        const height = Math.max((item.value / max) * 100, 4)
        return (
          <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <span style={{ fontSize: '10px', fontWeight: 700, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg-secondary)' }}>
              {item.value}
            </span>
            <div style={{
              width: '100%',
              height: `${height}%`,
              background: item.color || 'var(--color-primary)',
              borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0',
              transition: 'height 0.4s ease',
              minHeight: 4,
            }} />
            <span style={{ fontSize: '9px', color: 'var(--color-fg-muted)', textAlign: 'center', lineHeight: 1.2 }}>
              {item.label}
            </span>
          </div>
        )
      })}
    </div>
  )
}

export default function AnalyticsDashboard() {
  useAuth('company')
  const navigate = useNavigate()

  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setBusy(true)
    try {
      const res = await c4AnalyticsSummary()
      setData(res?.data || null)
    } catch (err) {
      console.error('loadAnalytics error:', err)
      toast.error('Failed to load analytics data')
    } finally {
      setBusy(false)
    }
  }

  const summary = data?.summary || data || {}
  const recentActivity = data?.recent_activity || data?.activity || []
  const skillDemand = data?.skill_demand || data?.top_skills || []
  const jobStats = data?.job_stats || {}

  const statCards = [
    { label: 'Total Candidates', value: summary.total_candidates || summary.total_candidates_count || 0, icon: Users, color: 'primary', helperText: 'In the system' },
    { label: 'Active Jobs', value: summary.total_jobs || summary.active_jobs || jobStats.active || 0, icon: Briefcase, color: 'purple', helperText: 'Open positions' },
    { label: 'Avg Score', value: summary.avg_score != null ? `${Math.round(summary.avg_score)}%` : '—', icon: TrendingUp, color: 'success', helperText: 'Across all candidates' },
    { label: 'Completion Rate', value: summary.completion_rate != null ? `${Math.round(summary.completion_rate)}%` : '—', icon: CheckCircle2, color: 'info', helperText: 'Interviews completed' },
  ]

  const skillChartData = (Array.isArray(skillDemand) ? skillDemand : []).slice(0, 8).map((s, i) => ({
    label: s.skill || s.name || s,
    value: s.count || s.demand || s.value || 1,
    color: ['var(--color-primary)', 'var(--color-purple)', 'var(--color-info)', 'var(--color-success)', 'var(--color-warning)', 'var(--color-primary)', 'var(--color-purple)', 'var(--color-info)'][i % 8],
  }))

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
      <PageHeader
        badge="Analytics"
        title="Analytics Dashboard"
        description="Platform-wide recruitment metrics, candidate performance insights, and hiring pipeline analytics."
        icon={BarChart3}
      />

      {/* Stat Cards */}
      {busy ? (
        <SkeletonLoader type="stat" count={4} />
      ) : (
        <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
          {statCards.map((s) => (
            <StatCard
              key={s.label}
              label={s.label}
              value={s.value}
              icon={s.icon}
              color={s.color}
              helperText={s.helperText}
            />
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--p-space-5)', marginBottom: 'var(--p-space-6)' }}>
        {/* Skill Demand Chart */}
        <div className="card" style={{ padding: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={16} style={{ color: 'var(--color-primary)' }} /> Top Skill Demand
          </h3>
          {busy ? (
            <SkeletonLoader type="card" count={1} />
          ) : skillChartData.length > 0 ? (
            <BarChart data={skillChartData} />
          ) : (
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center', margin: '20px 0' }}>
              No skill demand data available yet.
            </p>
          )}
        </div>

        {/* Job Distribution */}
        <div className="card" style={{ padding: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={16} style={{ color: 'var(--color-purple)' }} /> Job Pipeline Status
          </h3>
          {busy ? (
            <SkeletonLoader type="card" count={1} />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                { label: 'Active Jobs', value: jobStats.active || summary.active_jobs || 0, color: 'var(--color-success)', max: (jobStats.active || 0) + (jobStats.closed || 0) + (jobStats.draft || 0) || 1 },
                { label: 'Closed Jobs', value: jobStats.closed || summary.closed_jobs || 0, color: 'var(--color-fg-muted)', max: (jobStats.active || 0) + (jobStats.closed || 0) + (jobStats.draft || 0) || 1 },
                { label: 'Draft Jobs', value: jobStats.draft || summary.draft_jobs || 0, color: 'var(--color-warning)', max: (jobStats.active || 0) + (jobStats.closed || 0) + (jobStats.draft || 0) || 1 },
              ].map((item) => (
                <div key={item.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)' }}>{item.label}</span>
                    <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg)' }}>{item.value}</span>
                  </div>
                  <div style={{ height: 8, background: 'var(--color-bg-soft)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${(item.value / item.max) * 100}%`,
                      background: item.color,
                      borderRadius: 'var(--radius-full)',
                      transition: 'width 0.4s ease',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card" style={{ padding: 'var(--p-space-5)' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Activity size={16} style={{ color: 'var(--color-info)' }} /> Recent Activity
        </h3>
        {busy ? (
          <SkeletonLoader type="table" rows={4} cols={3} />
        ) : Array.isArray(recentActivity) && recentActivity.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentActivity.slice(0, 10).map((item, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 14px',
                background: 'var(--color-bg-elevated)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border-subtle)',
              }}>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 'var(--radius-full)',
                  background: 'var(--color-primary-muted)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  {item.type === 'application' ? <Users size={14} /> :
                   item.type === 'interview' ? <Award size={14} /> :
                   item.type === 'ranking' ? <TrendingUp size={14} /> :
                   <Clock size={14} />}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 600, color: 'var(--color-fg)' }}>
                    {item.title || item.description || item.event || 'Activity'}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                    {item.detail || item.subtitle || item.candidate || ''}
                  </div>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', whiteSpace: 'nowrap', fontFamily: 'var(--p-font-mono)' }}>
                  {item.time || item.created_at ? new Date(item.time || item.created_at).toLocaleDateString() : ''}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', textAlign: 'center', margin: '20px 0' }}>
            No recent activity to display.
          </p>
        )}
      </div>
    </div>
  )
}
