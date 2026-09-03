import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Shield, ArrowLeft, AlertTriangle, Eye, EyeOff, Monitor,
  Volume2, Clock, CheckCircle2, XCircle, AlertCircle, Webcam
} from 'lucide-react'
import { c2Proctoring } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const FLAG_TYPES = {
  tab_switch: { label: 'Tab Switch', icon: Monitor, color: 'warning', description: 'Candidate switched away from the interview tab' },
  face_not_detected: { label: 'Face Not Detected', icon: EyeOff, color: 'danger', description: 'No face detected in the webcam feed' },
  multiple_faces: { label: 'Multiple Faces', icon: Eye, color: 'danger', description: 'More than one face detected in the webcam' },
  audio_anomaly: { label: 'Audio Anomaly', icon: Volume2, color: 'warning', description: 'Unusual audio activity detected' },
  screen_share_off: { label: 'Screen Share Off', icon: Monitor, color: 'warning', description: 'Screen sharing was disabled' },
  movement: { label: 'Excessive Movement', icon: AlertTriangle, color: 'warning', description: 'Significant movement detected during assessment' },
  face_match_fail: { label: 'Face Mismatch', icon: EyeOff, color: 'danger', description: 'Face does not match the registered candidate' },
  tab_focus_lost: { label: 'Focus Lost', icon: AlertCircle, color: 'warning', description: 'Browser window lost focus' },
}

export default function ProctoringDashboard() {
  const navigate = useNavigate()
  const { interviewId } = useParams()
  useAuth('candidate')

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (interviewId) loadData()
  }, [interviewId])

  const loadData = async () => {
    setLoading(true)
    try {
      const r = await c2Proctoring(interviewId)
      setData(r?.data || r)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to load proctoring data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
        <SkeletonLoader type="card" count={3} />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
        <PageHeader
          badge="Proctoring"
          title="Proctoring Data Not Found"
          description="The proctoring data for this interview session could not be loaded."
          icon={Shield}
        />
        <EmptyState
          title="No Proctoring Data"
          description="Proctoring data is only available for company-assigned interviews. Practice sessions are not monitored."
          actionLabel="Back to Interview"
          onAction={() => navigate('/candidate/interview')}
          icon={Shield}
        />
      </div>
    )
  }

  const flags = data.flags || data.proctoring_flags || data.events || []
  const integrityScore = data.integrity_score ?? data.overall_score ?? 100
  const tabSwitches = data.tab_switches ?? data.tab_switch_count ?? flags.filter(f => f.type === 'tab_switch' || f.event_type === 'tab_switch').length
  const faceDetections = data.face_detections ?? data.face_detection_count ?? flags.filter(f => f.type === 'face_not_detected' || f.event_type === 'face_not_detected').length
  const audioAnomalies = data.audio_anomalies ?? data.audio_anomaly_count ?? flags.filter(f => f.type === 'audio_anomaly' || f.event_type === 'audio_anomaly').length
  const jobRole = data.job_role || data.role || 'Technical'
  const duration = data.duration || data.time_taken || 0

  const getSeverityColor = (severity) => {
    if (severity === 'high' || severity === 'critical') return 'var(--color-danger)'
    if (severity === 'medium' || severity === 'warning') return 'var(--color-warning)'
    return 'var(--color-success)'
  }

  const getSeverityBadge = (severity) => {
    const color = getSeverityColor(severity)
    const bg = severity === 'high' || severity === 'critical' ? 'var(--color-danger-muted)' : severity === 'medium' || severity === 'warning' ? 'var(--color-warning-muted)' : 'var(--color-success-muted)'
    return (
      <span style={{
        fontSize: '10px',
        fontWeight: 700,
        padding: '2px 8px',
        borderRadius: 'var(--radius-full)',
        background: bg,
        color: color,
        border: `1px solid ${color}40`,
        textTransform: 'uppercase'
      }}>
        {severity}
      </span>
    )
  }

  const getFlagInfo = (flagType) => {
    const normalized = (flagType || '').toLowerCase().replace(/[\s_-]+/g, '_')
    return FLAG_TYPES[normalized] || { label: flagType, icon: AlertTriangle, color: 'warning', description: '' }
  }

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
      <PageHeader
        badge="C2 AI Engine · Proctoring"
        title="Interview Proctoring Dashboard"
        description={`Integrity monitoring report for your ${jobRole} interview session. All flagged events are logged for review.`}
        icon={Shield}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/interview')}>
            <ArrowLeft size={14} /> Back to Interview
          </button>
        }
      />

      {/* Integrity Score Banner */}
      <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', textAlign: 'center' }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--color-fg-muted)',
          marginBottom: 6
        }}>
          Overall Integrity Score
        </div>
        <div style={{
          fontSize: '3rem',
          fontWeight: 900,
          color: integrityScore >= 80 ? 'var(--color-success)' : integrityScore >= 50 ? 'var(--color-warning)' : 'var(--color-danger)',
          lineHeight: 1,
          fontFamily: 'var(--p-font-mono)',
          marginBottom: 8
        }}>
          {integrityScore.toFixed(1)}%
        </div>
        <span style={{
          fontSize: '12px',
          fontWeight: 700,
          padding: '3px 12px',
          borderRadius: 'var(--radius-full)',
          background: integrityScore >= 80 ? 'var(--color-success-muted)' : integrityScore >= 50 ? 'var(--color-warning-muted)' : 'var(--color-danger-muted)',
          color: integrityScore >= 80 ? 'var(--color-success)' : integrityScore >= 50 ? 'var(--color-warning)' : 'var(--color-danger)',
          border: `1px solid ${integrityScore >= 80 ? 'rgba(16,185,129,0.3)' : integrityScore >= 50 ? 'rgba(245,158,11,0.3)' : 'rgba(244,63,94,0.3)'}`
        }}>
          {integrityScore >= 80 ? 'Clean Session' : integrityScore >= 50 ? 'Minor Flags Detected' : 'Multiple Integrity Violations'}
        </span>
      </div>

      {/* Flag Summary Stat Cards */}
      <div className="dashboard-grid dashboard-grid-equal" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <StatCard
          label="Tab Switches"
          value={tabSwitches}
          icon={Monitor}
          color={tabSwitches > 0 ? 'warning' : 'success'}
          helperText="Browser tab focus changes"
        />
        <StatCard
          label="Face Detection"
          value={faceDetections}
          icon={Webcam}
          color={faceDetections > 0 ? 'danger' : 'success'}
          helperText="Face not detected events"
        />
        <StatCard
          label="Audio Anomalies"
          value={audioAnomalies}
          icon={Volume2}
          color={audioAnomalies > 0 ? 'warning' : 'success'}
          helperText="Unusual audio activity"
        />
        <StatCard
          label="Total Flags"
          value={flags.length}
          icon={AlertTriangle}
          color={flags.length > 3 ? 'danger' : flags.length > 0 ? 'warning' : 'success'}
          helperText="All proctoring events"
        />
      </div>

      {/* Flag Type Breakdown */}
      {flags.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={16} style={{ color: 'var(--color-warning)' }} /> Flag Summary by Type
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
            {(() => {
              const grouped = {}
              flags.forEach((f) => {
                const type = f.type || f.event_type || 'unknown'
                if (!grouped[type]) grouped[type] = { count: 0, severity: f.severity || 'low' }
                grouped[type].count++
                if (f.severity === 'high' || f.severity === 'critical') grouped[type].severity = f.severity
              })
              return Object.entries(grouped).map(([type, info]) => {
                const flagInfo = getFlagInfo(type)
                const IconComp = flagInfo.icon
                return (
                  <div key={type} style={{
                    padding: 14,
                    background: 'var(--color-bg-elevated)',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${getSeverityColor(info.severity)}30`,
                    borderLeft: `4px solid ${getSeverityColor(info.severity)}`
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <IconComp size={14} style={{ color: getSeverityColor(info.severity) }} />
                        <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-fg)' }}>{flagInfo.label}</span>
                      </div>
                      {getSeverityBadge(info.severity)}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginBottom: 6 }}>{flagInfo.description}</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg)' }}>
                      {info.count} event{info.count > 1 ? 's' : ''}
                    </div>
                  </div>
                )
              })
            })()}
          </div>
        </div>
      )}

      {/* Timeline of Events */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Clock size={16} style={{ color: 'var(--color-primary)' }} /> Event Timeline
        </h3>
        {flags.length === 0 ? (
          <div style={{
            padding: 24,
            textAlign: 'center',
            background: 'var(--color-success-muted)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(16, 185, 129, 0.25)'
          }}>
            <CheckCircle2 size={32} style={{ color: 'var(--color-success)', margin: '0 auto 8px' }} />
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-success)' }}>No Proctoring Flags</div>
            <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4 }}>This interview session had a clean proctoring record.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {flags.map((flag, idx) => {
              const type = flag.type || flag.event_type || 'unknown'
              const timestamp = flag.timestamp || flag.time || flag.created_at || ''
              const flagInfo = getFlagInfo(type)
              const IconComp = flagInfo.icon
              const severity = flag.severity || 'low'

              const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : `Event ${idx + 1}`

              return (
                <div key={flag.id || idx} style={{
                  padding: '10px 14px',
                  background: 'var(--color-bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  border: `1px solid ${getSeverityColor(severity)}20`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 'var(--radius-full)',
                    background: `${getSeverityColor(severity)}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <IconComp size={15} style={{ color: getSeverityColor(severity) }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-fg)' }}>{flagInfo.label}</span>
                      {getSeverityBadge(severity)}
                    </div>
                    {flag.description && (
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 2 }}>{flag.description}</div>
                    )}
                  </div>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-fg-muted)', fontFamily: 'var(--p-font-mono)', flexShrink: 0 }}>
                    {formattedTime}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Session Details */}
      <div className="card" style={{ padding: 'var(--p-space-5)', background: 'var(--color-bg-elevated)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <Shield size={18} style={{ color: 'var(--color-primary)' }} />
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700 }}>Session Details</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Job Role</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{jobRole}</div>
          </div>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Duration</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2, fontFamily: 'var(--p-font-mono)' }}>
              {duration > 0 ? `${Math.floor(duration / 60)}m ${duration % 60}s` : 'N/A'}
            </div>
          </div>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Integrity</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: integrityScore >= 80 ? 'var(--color-success)' : integrityScore >= 50 ? 'var(--color-warning)' : 'var(--color-danger)', marginTop: 2, fontFamily: 'var(--p-font-mono)' }}>
              {integrityScore.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Back Button */}
      <div style={{ marginTop: 'var(--p-space-5)', textAlign: 'center' }}>
        <button className="btn btn-ghost" onClick={() => navigate('/candidate/interview')}>
          <ArrowLeft size={15} /> Back to Interview
        </button>
      </div>
    </div>
  )
}
