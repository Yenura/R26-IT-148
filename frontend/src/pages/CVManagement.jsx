import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FileSearch, ArrowLeft, Search, Trash2, Eye, Users, BarChart3,
  ChevronRight, Calendar
} from 'lucide-react'
import { c1ListCVs, c1GetCV, c1DeleteCV } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function CVManagement() {
  const navigate = useNavigate()
  useAuth('company')

  const [cvs, setCVs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedRole, setSelectedRole] = useState('all')
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    loadCVs()
  }, [])

  const loadCVs = async () => {
    setLoading(true)
    try {
      const res = await c1ListCVs()
      setCVs(Array.isArray(res.data) ? res.data : [])
    } catch (err) {
      toast.error('Failed to load CVs')
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetail = async (candidateId) => {
    try {
      const res = await c1GetCV(candidateId)
      toast.success('CV details loaded')
      return res.data
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to load CV')
    }
  }

  const handleDelete = (candidateId, name) => {
    setConfirm({
      open: true,
      title: `Delete CV for ${name || 'this candidate'}?`,
      message: 'This will permanently remove the analyzed CV and all associated data.',
      danger: true,
      action: async () => {
        try {
          await c1DeleteCV(candidateId)
          toast.success('CV deleted successfully')
          loadCVs()
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Delete failed')
        }
      }
    })
  }

  const roles = [...new Set(cvs.map((cv) => cv.target_role || cv.role || cv.predicted_role).filter(Boolean))]

  const filtered = cvs.filter((cv) => {
    const name = (cv.candidate_name || '').toLowerCase()
    const role = (cv.target_role || cv.role || cv.predicted_role || '').toLowerCase()
    const query = search.toLowerCase()
    const matchesSearch = !search || name.includes(query) || role.includes(query)
    const matchesRole = selectedRole === 'all' || role === selectedRole.toLowerCase()
    return matchesSearch && matchesRole
  })

  const totalScore = cvs.reduce((sum, cv) => sum + (cv.overall_score || cv.cv_matching_score || cv.score || 0), 0)
  const avgScore = cvs.length > 0 ? (totalScore / cvs.length).toFixed(1) : 0

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <PageHeader
        badge="CV Intelligence"
        title="CV Management"
        description="View, analyze, and manage candidate CVs analyzed by the AI screening engine."
        icon={FileSearch}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/company/dashboard')}>
            <ArrowLeft size={15} /> Dashboard
          </button>
        }
      />

      {/* Stats */}
      {loading ? (
        <SkeletonLoader type="stat" count={3} />
      ) : (
        <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
          <StatCard label="Total CVs" value={cvs.length} icon={Users} color="primary" helperText="Analyzed resumes" />
          <StatCard label="Average Score" value={avgScore} icon={BarChart3} color="success" helperText="Overall match" />
          <StatCard label="Unique Roles" value={roles.length} icon={FileSearch} color="info" helperText="Target positions" />
        </div>
      )}

      {/* Search & Filter */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-4)' }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: '1 1 280px' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
            <input
              type="text"
              placeholder="Search by candidate name or role..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: 36 }}
            />
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <button
              className={`btn btn-sm ${selectedRole === 'all' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setSelectedRole('all')}
              style={{ fontSize: 'var(--p-text-xs)' }}
            >
              All Roles
            </button>
            {roles.slice(0, 5).map((role) => (
              <button
                key={role}
                className={`btn btn-sm ${selectedRole === role ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setSelectedRole(role)}
                style={{ fontSize: 'var(--p-text-xs)' }}
              >
                {role}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* CV List */}
      {loading ? (
        <SkeletonLoader type="card" count={4} />
      ) : filtered.length === 0 ? (
        <EmptyState
          title={search ? "No matching CVs found" : "No CVs analyzed yet"}
          description={search ? "Try adjusting your search criteria or filters." : "Analyze a candidate CV to get started."}
          actionLabel={search ? "Clear Search" : undefined}
          onAction={search ? () => { setSearch(''); setSelectedRole('all') } : undefined}
          icon={FileSearch}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-3)' }}>
          {filtered.map((cv) => {
            const score = cv.overall_score || cv.cv_matching_score || cv.score || 0
            const scoreColor = score >= 80 ? 'var(--color-success)' : score >= 60 ? 'var(--color-warning)' : 'var(--color-danger)'
            const role = cv.target_role || cv.role || cv.predicted_role || 'N/A'
            const date = cv.created_at ? new Date(cv.created_at).toLocaleDateString('en-US', {
              month: 'short', day: 'numeric', year: 'numeric'
            }) : ''

            return (
              <div
                key={cv.candidate_id || cv.id}
                className="card card-interactive"
                style={{
                  padding: 'var(--p-space-5)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 16,
                  flexWrap: 'wrap',
                  cursor: 'default'
                }}
              >
                <div style={{ flex: '1 1 300px', minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)' }}>
                      {cv.candidate_name || 'Unknown Candidate'}
                    </h3>
                    <span
                      className="chip"
                      style={{
                        fontSize: '11px',
                        fontWeight: 700,
                        color: scoreColor,
                        background: score >= 80 ? 'var(--color-success-muted)' : score >= 60 ? 'var(--color-warning-muted)' : 'var(--color-danger-muted)',
                        border: `1px solid ${scoreColor}30`
                      }}
                    >
                      {score.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
                      <FileSearch size={12} /> {role}
                    </span>
                    {date && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Calendar size={12} /> {date}
                      </span>
                    )}
                  </div>
                  {cv.skills && cv.skills.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
                      {cv.skills.slice(0, 5).map((skill, i) => (
                        <span key={`${skill}-${i}`} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                          {skill}
                        </span>
                      ))}
                      {cv.skills.length > 5 && (
                        <span style={{ fontSize: '10px', color: 'var(--color-fg-muted)', alignSelf: 'center' }}>
                          +{cv.skills.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => navigate(`/company/cv-detail/${cv.candidate_id || cv.id}`)}
                    style={{ fontSize: 'var(--p-text-xs)' }}
                    title="View CV details"
                  >
                    <Eye size={14} /> View
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(cv.candidate_id || cv.id, cv.candidate_name)
                    }}
                    style={{ color: 'var(--color-danger)', fontSize: 'var(--p-text-xs)' }}
                    title="Delete CV"
                  >
                    <Trash2 size={14} /> Delete
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={confirm.open}
        title={confirm.title}
        message={confirm.message}
        danger={confirm.danger}
        confirmLabel="Delete"
        onConfirm={async () => {
          await confirm.action()
          setConfirm({ ...confirm, open: false })
        }}
        onCancel={() => setConfirm({ ...confirm, open: false })}
      />
    </div>
  )
}
