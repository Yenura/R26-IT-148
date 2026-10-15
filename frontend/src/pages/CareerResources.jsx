import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  BookOpen, RefreshCw, ExternalLink, Filter,
  GraduationCap, FileText, Award, Search
} from 'lucide-react'
import { c4CareerResources, c4CareerRoles } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const TYPE_CONFIG = {
  course: { icon: GraduationCap, color: 'var(--color-primary)', bg: 'var(--color-primary-muted)', label: 'Course' },
  article: { icon: FileText, color: 'var(--color-info)', bg: 'var(--color-info-muted)', label: 'Article' },
  certification: { icon: Award, color: 'var(--color-warning)', bg: 'var(--color-warning-muted)', label: 'Certification' },
  tutorial: { icon: BookOpen, color: 'var(--color-success)', bg: 'var(--color-success-muted)', label: 'Tutorial' },
  video: { icon: BookOpen, color: 'var(--color-purple)', bg: 'var(--color-purple-muted)', label: 'Video' },
  default: { icon: BookOpen, color: 'var(--color-fg-muted)', bg: 'var(--color-bg-elevated)', label: 'Resource' },
}

function getTypeConfig(type) {
  const t = (type || '').toLowerCase().replace(/[\s-]/g, '_')
  return TYPE_CONFIG[t] || TYPE_CONFIG.default
}

const DIFFICULTY_COLORS = {
  beginner: { bg: 'var(--color-success-muted)', fg: 'var(--color-success)' },
  intermediate: { bg: 'var(--color-primary-muted)', fg: 'var(--color-primary)' },
  advanced: { bg: 'var(--color-danger-muted)', fg: 'var(--color-danger)' },
}

function getDifficultyColor(d) {
  return DIFFICULTY_COLORS[(d || '').toLowerCase()] || DIFFICULTY_COLORS.beginner
}

export default function CareerResources() {
  const navigate = useNavigate()
  const { role: roleParam } = useParams()
  useAuth('candidate')

  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState(roleParam || '')
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingRoles, setLoadingRoles] = useState(false)
  const [typeFilter, setTypeFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadRoles()
  }, [])

  useEffect(() => {
    if (roleParam && roleParam !== selectedRole) {
      setSelectedRole(roleParam)
      loadResources(roleParam)
    }
  }, [roleParam])

  const loadRoles = async () => {
    setLoadingRoles(true)
    try {
      const r = await c4CareerRoles()
      const roleList = r?.data?.roles || []
      setRoles(roleList)
      if (roleParam) {
        setSelectedRole(roleParam)
        loadResources(roleParam)
      } else if (roleList.length > 0 && !selectedRole) {
        setSelectedRole(roleList[0])
        loadResources(roleList[0])
      }
    } catch {
      toast.error('Failed to load career roles')
    } finally {
      setLoadingRoles(false)
    }
  }

  const loadResources = async (role) => {
    if (!role) return
    setLoading(true)
    try {
      const r = await c4CareerResources(role)
      const data = r?.data?.data || r?.data || {}
      setResources(data.resources || data || [])
    } catch {
      toast.error('Failed to load career resources')
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = (e) => {
    const role = e.target.value
    setSelectedRole(role)
    if (role) loadResources(role)
  }

  const filteredResources = resources.filter((res) => {
    const matchesType = typeFilter === 'all' || (res.type || '').toLowerCase() === typeFilter
    const matchesSearch = !searchTerm ||
      (res.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (res.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (res.skill || '').toLowerCase().includes(searchTerm.toLowerCase())
    return matchesType && matchesSearch
  })

  const typeCounts = resources.reduce((acc, r) => {
    const t = (r.type || 'other').toLowerCase()
    acc[t] = (acc[t] || 0) + 1
    return acc
  }, {})

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <PageHeader
        badge="Career Development"
        title="Career Resources"
        description="Discover curated learning resources for your target role — courses, articles, certifications, and more."
        icon={BookOpen}
        actions={
          <button onClick={() => loadResources(selectedRole)} className="btn btn-ghost btn-sm">
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        }
      />

      {/* Role Selector */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-sm)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <GraduationCap size={16} style={{ color: 'var(--color-primary)' }} /> Select Target Role
          </h3>
          <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>
            {roles.length} Roles Available
          </span>
        </div>
        <select
          value={selectedRole}
          onChange={handleRoleChange}
          style={{ width: '100%', height: 44, padding: '0 14px', background: 'var(--input-bg)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)', fontWeight: 600 }}
        >
          <option value="">Select a career role...</option>
          {roles.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </div>

      {loadingRoles ? (
        <SkeletonLoader type="card" count={2} />
      ) : !selectedRole ? (
        <EmptyState
          title="Select a Career Role"
          description="Choose a target role above to discover curated learning resources and career development materials."
          icon={BookOpen}
        />
      ) : loading ? (
        <SkeletonLoader type="card" count={4} />
      ) : (
        <>
          {/* Stats Strip */}
          <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
            <StatCard
              label="Total Resources"
              value={resources.length}
              icon={BookOpen}
              color="primary"
              helperText={`For ${selectedRole}`}
            />
            <StatCard
              label="Courses"
              value={typeCounts.course || 0}
              icon={GraduationCap}
              color="info"
              helperText="Structured learning"
            />
            <StatCard
              label="Certifications"
              value={typeCounts.certification || 0}
              icon={Award}
              color="success"
              helperText="Industry credentials"
            />
            <StatCard
              label="Articles"
              value={(typeCounts.article || 0) + (typeCounts.tutorial || 0)}
              icon={FileText}
              color="warning"
              helperText="Reading material"
            />
          </div>

          {/* Filters Bar */}
          <div className="card" style={{
            padding: '12px 16px', marginBottom: 'var(--p-space-5)',
            display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Filter size={14} style={{ color: 'var(--color-fg-muted)' }} />
              <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>Filter:</span>
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {[
                { id: 'all', label: `All (${resources.length})` },
                { id: 'course', label: `Courses (${typeCounts.course || 0})` },
                { id: 'article', label: `Articles (${typeCounts.article || 0})` },
                { id: 'certification', label: `Certifications (${typeCounts.certification || 0})` },
                { id: 'tutorial', label: `Tutorials (${typeCounts.tutorial || 0})` },
                { id: 'video', label: `Videos (${typeCounts.video || 0})` },
              ].filter((t) => (typeCounts[t.id] || t.id === 'all') && (typeCounts[t.id] || 0) > 0).map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTypeFilter(t.id)}
                  className={`btn btn-sm ${typeFilter === t.id ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 'var(--p-text-xs)' }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div style={{ marginLeft: 'auto', position: 'relative', width: 220 }}>
              <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="text"
                placeholder="Search resources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ paddingLeft: 30, height: 34, fontSize: 'var(--p-text-xs)' }}
              />
            </div>
          </div>

          {/* Resources Grid */}
          {filteredResources.length === 0 ? (
            <EmptyState
              title="No Resources Found"
              description="Try adjusting your filters or search term to find learning materials for this role."
              icon={BookOpen}
            />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
              {filteredResources.map((res, idx) => {
                const typeConfig = getTypeConfig(res.type)
                const TypeIcon = typeConfig.icon
                const diffColor = getDifficultyColor(res.difficulty || res.level)
                const title = res.title || res.name || res.course || 'Untitled Resource'
                const url = res.url || res.link || null
                const description = res.description || res.details || ''
                const skill = res.skill || res.topic || ''
                const difficulty = res.difficulty || res.level || ''

                return (
                  <div
                    key={idx}
                    className="card"
                    style={{
                      padding: 0, overflow: 'hidden',
                      display: 'flex', flexDirection: 'column',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {/* Type Header Bar */}
                    <div style={{
                      padding: '10px 16px',
                      background: typeConfig.bg,
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      borderBottom: `1px solid ${typeConfig.color}20`
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <TypeIcon size={14} style={{ color: typeConfig.color }} />
                        <span style={{ fontSize: '10px', fontWeight: 800, color: typeConfig.color, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          {typeConfig.label}
                        </span>
                      </div>
                      {difficulty && (
                        <span style={{
                          fontSize: '10px', fontWeight: 700, padding: '2px 8px',
                          borderRadius: 'var(--radius-full)',
                          background: diffColor.bg, color: diffColor.fg,
                          border: `1px solid ${diffColor.fg}30`
                        }}>
                          {difficulty}
                        </span>
                      )}
                    </div>

                    {/* Content */}
                    <div style={{ padding: '14px 16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <h4 style={{ margin: '0 0 8px 0', fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', lineHeight: 1.4 }}>
                        {title}
                      </h4>

                      {description && (
                        <p style={{ fontSize: '12px', color: 'var(--color-fg-muted)', margin: '0 0 10px 0', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {description}
                        </p>
                      )}

                      {skill && (
                        <span className="chip" style={{ fontSize: '10px', alignSelf: 'flex-start', marginBottom: 10 }}>
                          {skill}
                        </span>
                      )}

                      <div style={{ marginTop: 'auto' }}>
                        {url ? (
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-primary btn-sm"
                            style={{
                              width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                              fontSize: '12px', fontWeight: 700, padding: '8px 14px'
                            }}
                          >
                            Open Resource <ExternalLink size={13} />
                          </a>
                        ) : (
                          <div style={{
                            width: '100%', textAlign: 'center', padding: '8px 14px',
                            background: 'var(--color-bg-soft)', borderRadius: 'var(--radius-md)',
                            fontSize: '12px', color: 'var(--color-fg-muted)', fontWeight: 600
                          }}>
                            No link available
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}
