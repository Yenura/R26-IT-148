import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, ArrowLeft, RefreshCw, CheckCircle2,
  AlertCircle, BookOpen, Code, Layers, Lightbulb
} from 'lucide-react'
import { c4SkillGapReport } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const LEVEL_COLORS = {
  basic: { bg: 'var(--color-warning-muted)', fg: 'var(--color-warning)', label: 'Basic' },
  intermediate: { bg: 'var(--color-primary-muted)', fg: 'var(--color-primary)', label: 'Intermediate' },
  advanced: { bg: 'var(--color-success-muted)', fg: 'var(--color-success)', label: 'Advanced' },
}

export default function SkillGapReportDetail() {
  const navigate = useNavigate()
  const { candidateId } = useParams()
  useAuth('candidate')

  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (candidateId) loadReport()
  }, [candidateId])

  const loadReport = async () => {
    setLoading(true)
    try {
      const r = await c4SkillGapReport(candidateId)
      setReport(r?.data?.data || r?.data || null)
    } catch {
      toast.error('Failed to load skill gap report')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto' }}>
        <SkeletonLoader type="card" count={4} />
      </div>
    )
  }

  if (!report) {
    return (
      <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto' }}>
        <PageHeader
          badge="Skill Gap Detail"
          title="Report Not Found"
          description="The requested skill gap report could not be loaded."
          icon={Target}
          actions={
            <Link to="/candidate/skill-gap/reports" className="btn btn-ghost btn-sm">
              <ArrowLeft size={14} /> Back to Reports
            </Link>
          }
        />
        <EmptyState
          title="Report Not Found"
          description="This report may have been deleted or you may not have access to it."
          actionLabel="View All Reports"
          onAction={() => navigate('/candidate/skill-gap/reports')}
          icon={AlertCircle}
        />
      </div>
    )
  }

  const matchedSkills = report.matched_skills || report.strengths || []
  const missingSkills = report.missing_skills || report.weaknesses || []
  const skillLevels = report.skill_levels || report.skills || []
  const recommendedActions = report.recommended_actions || report.course_recommendations || []

  const overallScore = report.overall_score || 0
  const coveragePct = matchedSkills.length + missingSkills.length > 0
    ? Math.round((matchedSkills.length / (matchedSkills.length + missingSkills.length)) * 100)
    : 0

  return (
    <div className="fade-in" style={{ maxWidth: 1000, margin: '0 auto' }}>
      <PageHeader
        badge="Skill Gap Detail"
        title={`${report.candidate_name || 'Candidate'} — Skill Gap Report`}
        description={`Role: ${report.role || report.job_role || 'N/A'} • Analysis Date: ${report.date || report.created_at ? new Date(report.date || report.created_at).toLocaleDateString() : 'N/A'}`}
        icon={Target}
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <Link to="/candidate/skill-gap/reports" className="btn btn-ghost btn-sm">
              <ArrowLeft size={14} /> All Reports
            </Link>
            <button onClick={loadReport} className="btn btn-ghost btn-sm">
              <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        }
      />

      {/* Score Summary Strip */}
      <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
        <StatCard
          label="Overall Score"
          value={`${overallScore}%`}
          icon={Target}
          color="primary"
          helperText="Total fit assessment"
        />
        <StatCard
          label="Skills Matched"
          value={matchedSkills.length}
          icon={CheckCircle2}
          color="success"
          helperText="Verified competencies"
        />
        <StatCard
          label="Skills Missing"
          value={missingSkills.length}
          icon={AlertCircle}
          color="danger"
          helperText="Target skill deficits"
        />
        <StatCard
          label="Coverage"
          value={`${coveragePct}%`}
          icon={Layers}
          color="info"
          helperText="Role requirement coverage"
        />
      </div>

      {/* Skill Levels Bar Chart */}
      {skillLevels.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-fg)' }}>
            <BarChartIcon size={18} style={{ color: 'var(--color-primary)' }} /> Skill Level Breakdown
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {skillLevels.map((skill, idx) => {
              const name = skill.skill || skill.name || skill
              const level = (skill.level || skill.proficiency || 'basic').toLowerCase()
              const levelData = LEVEL_COLORS[level] || LEVEL_COLORS.basic
              const pct = skill.score || skill.level === 'advanced' ? 90 : skill.level === 'intermediate' ? 60 : 30

              return (
                <div key={name || idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{name}</span>
                    <span style={{
                      fontSize: '10px', fontWeight: 700, padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      background: levelData.bg, color: levelData.fg,
                      border: `1px solid ${levelData.fg}30`
                    }}>
                      {levelData.label}
                    </span>
                  </div>
                  <div style={{ height: 10, background: 'var(--color-border-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', width: `${pct}%`,
                      background: levelData.fg,
                      borderRadius: 'var(--radius-full)',
                      transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
                    }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Matched Skills */}
      {matchedSkills.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', borderRadius: 'var(--radius-xl)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
          <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-success)' }}>
            <CheckCircle2 size={18} /> Matched Skills ({matchedSkills.length})
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {matchedSkills.map((skill, idx) => {
              const name = typeof skill === 'string' ? skill : skill.skill || skill.name
              const details = typeof skill === 'object' ? (skill.details || skill.source || '') : ''
              return (
                <div key={name || idx} style={{
                  padding: '10px 14px', background: 'var(--color-bg-elevated)',
                  borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--color-success)',
                  border: '1px solid rgba(16, 185, 129, 0.2)'
                }}>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{name}</div>
                  {details && <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 3 }}>{details}</div>}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {missingSkills.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', borderRadius: 'var(--radius-xl)', border: '1px solid rgba(244, 63, 94, 0.25)' }}>
          <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-danger)' }}>
            <AlertCircle size={18} /> Missing Skills ({missingSkills.length})
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {missingSkills.map((skill, idx) => {
              const name = typeof skill === 'string' ? skill : skill.skill || skill.name
              const severity = typeof skill === 'object' ? (skill.severity || 'Medium') : 'Medium'
              const details = typeof skill === 'object' ? (skill.details || skill.reason || '') : ''
              const isCritical = severity === 'Critical'
              return (
                <div key={name || idx} style={{
                  padding: '10px 14px', background: 'var(--color-bg-elevated)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: `4px solid ${isCritical ? 'var(--color-danger)' : 'var(--color-warning)'}`,
                  border: `1px solid ${isCritical ? 'rgba(244, 63, 94, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>{name}</span>
                    <span style={{
                      fontSize: '10px', fontWeight: 700, padding: '2px 6px', borderRadius: 'var(--radius-full)',
                      background: isCritical ? 'var(--color-danger-muted)' : 'var(--color-warning-muted)',
                      color: isCritical ? 'var(--color-danger)' : 'var(--color-warning)'
                    }}>
                      {severity}
                    </span>
                  </div>
                  {details && <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 3 }}>{details}</div>}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommended Actions */}
      {recommendedActions.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-fg)' }}>
            <Lightbulb size={18} style={{ color: 'var(--color-warning)' }} /> Recommended Actions ({recommendedActions.length})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
            {recommendedActions.map((action, idx) => {
              const name = typeof action === 'string' ? action : action.skill || action.course || action.title
              const url = typeof action === 'object' ? (action.url || null) : null
              const priority = typeof action === 'object' ? (action.priority || 'Medium') : 'Medium'
              const duration = typeof action === 'object' ? (action.duration || '') : ''
              const level = typeof action === 'object' ? (action.level || '') : ''
              const pColor = priority === 'Critical' ? 'var(--color-danger)' : priority === 'High' ? 'var(--color-warning)' : 'var(--color-primary)'
              return (
                <div key={name || idx} style={{
                  padding: 14, background: 'var(--color-bg-elevated)',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                  display: 'flex', flexDirection: 'column', justifyContent: 'space-between'
                }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, color: pColor }}>{name}</span>
                      <span style={{
                        fontSize: '10px', fontWeight: 700, padding: '2px 6px',
                        borderRadius: 'var(--radius-full)', background: `${pColor}15`, color: pColor
                      }}>
                        {priority}
                      </span>
                    </div>
                    {(duration || level) && (
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4 }}>
                        {duration && <span>{duration}</span>}
                        {duration && level && <span> • </span>}
                        {level && <span>{level}</span>}
                      </div>
                    )}
                  </div>
                  {url && (
                    <a href={url} target="_blank" rel="noopener noreferrer"
                      className="btn btn-ghost btn-sm"
                      style={{ marginTop: 12, fontSize: '11px', border: '1px solid var(--color-border)', display: 'inline-flex', alignItems: 'center', gap: 6, alignSelf: 'flex-start' }}
                    >
                      <BookOpen size={13} /> Explore <ExternalLink size={11} />
                    </a>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function BarChartIcon({ size, style }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={style}>
      <rect x="3" y="12" width="4" height="9" rx="1" />
      <rect x="10" y="7" width="4" height="14" rx="1" />
      <rect x="17" y="3" width="4" height="18" rx="1" />
    </svg>
  )
}
