import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Route as RouteIcon, ArrowLeft, Map, ChevronRight, BookOpen, Award, Target, Sparkles } from 'lucide-react'
import { c4CareerRoadmap, authGetProfile } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function CareerRoadmap() {
  const navigate = useNavigate()
  useAuth('candidate')
  const { candidateId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [candidateId])

  const load = async () => {
    setLoading(true)
    try {
      let cid = candidateId
      if (!cid) {
        const pr = await authGetProfile()
        cid = pr?.data?._id
      }
      if (!cid) { toast.error('No candidate ID'); setLoading(false); return }
      const r = await c4CareerRoadmap(cid)
      setData(r?.data)
    } catch {
      toast.error('Failed to load career roadmap')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="fade-in"><PageHeader title="Career Roadmap" icon={RouteIcon} /><SkeletonLoader type="card" count={3} /></div>
  if (!data) return <div className="fade-in"><PageHeader title="Career Roadmap" icon={RouteIcon} /><EmptyState icon={RouteIcon} title="No roadmap available" message="Complete a skill gap analysis to generate your career roadmap" /></div>

  const phases = data.phases || data.roadmap || data.milestones || []

  return (
    <div className="fade-in">
      <PageHeader
        title="Career Roadmap"
        description="Your personalized career development path"
        icon={RouteIcon}
        badge={data.target_role || data.role || 'Custom'}
        actions={<button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)}><ArrowLeft size={15} /> Back</button>}
      />

      {data.target_role && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Target size={20} style={{ color: 'var(--color-primary)' }} />
              <div>
                <div style={{ fontWeight: 700, color: 'var(--color-fg)' }}>Target Role: {data.target_role}</div>
                {data.current_role && <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>Current: {data.current_role}</div>}
              </div>
            </div>
          </div>
        </div>
      )}

      {phases.length === 0 ? (
        <EmptyState icon={Map} title="No phases defined" message="Your roadmap is being generated" />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {phases.map((phase, i) => (
            <div key={i} className="card">
              <div className="card-body">
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 'var(--radius-full)',
                    background: phase.completed ? 'var(--color-success-muted)' : 'var(--color-primary-muted)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
                  }}>
                    {phase.completed ? <Award size={18} style={{ color: 'var(--color-success)' }} /> : <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--color-primary)' }}>{i + 1}</span>}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: 'var(--color-fg)', marginBottom: 4 }}>{phase.title || phase.name || `Phase ${i + 1}`}</div>
                    {phase.description && <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', marginBottom: 8 }}>{phase.description}</div>}
                    {phase.skills && phase.skills.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                        {phase.skills.map((s, j) => (
                          <span key={j} className="chip" style={{ fontSize: 11, padding: '2px 8px' }}>{typeof s === 'string' ? s : s.name || s.skill}</span>
                        ))}
                      </div>
                    )}
                    {phase.duration && <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 8 }}><BookOpen size={12} style={{ verticalAlign: -2 }} /> {phase.duration}</div>}
                  </div>
                  <ChevronRight size={16} style={{ color: 'var(--color-fg-muted)', marginTop: 8 }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {data.tips && data.tips.length > 0 && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-body">
            <div style={{ fontWeight: 700, color: 'var(--color-fg)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={16} style={{ color: 'var(--color-warning)' }} /> Tips
            </div>
            <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--color-fg-muted)', fontSize: 'var(--p-text-sm)' }}>
              {data.tips.map((tip, i) => <li key={i} style={{ marginBottom: 6 }}>{tip}</li>)}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
