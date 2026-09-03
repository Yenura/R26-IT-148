import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Target, ArrowLeft, Loader2, BarChart3, ChevronDown, CheckCircle2
} from 'lucide-react'
import { uResumeList, uResumePredictRole } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import SkeletonLoader from '../components/SkeletonLoader'
import EmptyState from '../components/EmptyState'

export default function RolePredict() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [loading, setLoading] = useState(true)
  const [predicting, setPredicting] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadResumes()
  }, [])

  const loadResumes = async () => {
    setLoading(true)
    try {
      const res = await uResumeList()
      const list = Array.isArray(res.data) ? res.data : []
      setResumes(list)
      if (list.length > 0) setSelectedResumeId(list[0].id)
    } catch {
      toast.error('Failed to load resumes')
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    if (!selectedResumeId) {
      return toast.error('Please select a resume first')
    }
    setPredicting(true)
    setResult(null)
    try {
      const res = await uResumePredictRole({ resume_id: selectedResumeId })
      setResult(res.data)
      toast.success('Role prediction complete!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to predict role')
    } finally {
      setPredicting(false)
    }
  }

  const topRoles = result?.top_roles || result?.predictions || []
  const primaryRole = result?.predicted_role || result?.role || (topRoles.length > 0 ? topRoles[0]?.role : null)
  const confidence = result?.role_confidence || result?.confidence || (topRoles.length > 0 ? topRoles[0]?.probability : null)

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <PageHeader
        badge="Role Prediction"
        title="Predict Role from Resume"
        description="Select a resume to predict the best-fitting IT role using AI classification."
        icon={Target}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/dashboard')}>
            <ArrowLeft size={15} /> Dashboard
          </button>
        }
      />

      {/* Resume Selector */}
      <div className="card" style={{ marginBottom: 'var(--p-space-5)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={18} style={{ color: 'var(--color-primary)' }} /> Select Resume
          </h3>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          {loading ? (
            <SkeletonLoader type="card" count={1} />
          ) : resumes.length === 0 ? (
            <EmptyState
              title="No resumes found"
              description="Upload a resume on the dashboard first, then come back to predict your role."
              actionLabel="Go to Dashboard"
              icon={Target}
              onAction={() => navigate('/candidate/dashboard')}
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  style={{ width: '100%', appearance: 'none', paddingRight: 36, fontSize: 'var(--p-text-sm)' }}
                >
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.filename || r.candidate_name || `Resume ${r.id}`}
                      {r.candidate_name ? ` — ${r.candidate_name}` : ''}
                    </option>
                  ))}
                </select>
                <ChevronDown
                  size={16}
                  style={{
                    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                    pointerEvents: 'none', color: 'var(--color-fg-muted)'
                  }}
                />
              </div>
              <button
                className="btn btn-primary"
                onClick={handlePredict}
                disabled={predicting || !selectedResumeId}
                style={{ alignSelf: 'flex-start' }}
              >
                {predicting ? (
                  <><Loader2 size={15} className="spin" /> Predicting...</>
                ) : (
                  <><Target size={15} /> Predict Role</>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Prediction Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-4)' }}>
          {/* Primary Prediction */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle2 size={18} style={{ color: 'var(--color-success)' }} /> Predicted Role
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                <span style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                  {primaryRole || 'Unknown'}
                </span>
              </div>
              {confidence && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{
                    flex: 1, maxWidth: 280, height: 8, borderRadius: 'var(--radius-full)',
                    background: 'var(--color-border-subtle)', overflow: 'hidden'
                  }}>
                    <div style={{
                      height: '100%', borderRadius: 'var(--radius-full)',
                      background: 'var(--color-primary)',
                      width: `${typeof confidence === 'number' && confidence <= 1 ? confidence * 100 : confidence}%`,
                      transition: 'width 0.6s ease'
                    }} />
                  </div>
                  <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>
                    {(typeof confidence === 'number' && confidence <= 1 ? confidence * 100 : confidence).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Top 3 Roles */}
          {topRoles.length > 0 && (
            <div className="card">
              <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BarChart3 size={18} style={{ color: 'var(--color-info)' }} /> Top Predicted Roles
                </h3>
              </div>
              <div style={{ padding: 'var(--p-space-5)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {topRoles.slice(0, 3).map((item, idx) => {
                    const roleName = item.role || item.predicted_role || item.name
                    const prob = item.probability || item.confidence || item.score || 0
                    const pct = typeof prob === 'number' && prob <= 1 ? prob * 100 : prob
                    const colors = ['var(--color-primary)', 'var(--color-info)', 'var(--color-purple)']
                    const bgs = ['var(--color-primary-muted)', 'var(--color-info-muted)', 'var(--color-purple-muted)']

                    return (
                      <div key={`${roleName}-${idx}`} style={{
                        display: 'flex', alignItems: 'center', gap: 12,
                        padding: '12px 16px', borderRadius: 'var(--radius-md)',
                        background: bgs[idx] || 'var(--color-bg-elevated)',
                        border: `1px solid ${colors[idx] || 'var(--color-border)'}`
                      }}>
                        <div style={{
                          width: 32, height: 32, borderRadius: 'var(--radius-full)',
                          background: colors[idx] || 'var(--color-primary)',
                          color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '13px', fontWeight: 800, flexShrink: 0
                        }}>
                          {idx + 1}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 700, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                            {roleName}
                          </div>
                          <div style={{
                            marginTop: 4, height: 6, borderRadius: 'var(--radius-full)',
                            background: 'var(--color-border-subtle)', overflow: 'hidden'
                          }}>
                            <div style={{
                              height: '100%', borderRadius: 'var(--radius-full)',
                              background: colors[idx] || 'var(--color-primary)',
                              width: `${pct}%`, transition: 'width 0.6s ease'
                            }} />
                          </div>
                        </div>
                        <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: colors[idx], minWidth: 50, textAlign: 'right' }}>
                          {pct.toFixed(1)}%
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button className="btn btn-ghost" onClick={() => setResult(null)}>
              Clear Results
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/candidate/dashboard')}>
              Back to Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
