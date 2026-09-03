import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FileText, RefreshCw, Trash2, Eye, Calendar,
  BarChart3, AlertCircle, CheckCircle2
} from 'lucide-react'
import { c4SkillGapReports, c4SkillGapDeleteReport } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'
import ConfirmDialog from '../components/ConfirmDialog'

export default function SkillGapReports() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, candidateId: null })

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    setLoading(true)
    try {
      const r = await c4SkillGapReports()
      const data = r?.data?.data || r?.data || {}
      setReports(data.reports || data || [])
    } catch {
      toast.error('Failed to load skill gap reports')
    } finally {
      setLoading(false)
    }
  }

  const deleteReport = async (candidateId) => {
    try {
      await c4SkillGapDeleteReport(candidateId)
      toast.success('Report deleted successfully')
      setReports((prev) => prev.filter((r) => r.candidate_id !== candidateId))
    } catch {
      toast.error('Failed to delete report')
    }
  }

  const totalReports = reports.length
  const avgScore = reports.length > 0
    ? (reports.reduce((sum, r) => sum + (r.overall_score || 0), 0) / reports.length).toFixed(1)
    : 0
  const completedReports = reports.filter((r) => r.status === 'completed').length

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <PageHeader
        badge="Skill Gap Diagnostics"
        title="Skill Gap Reports"
        description="View all your role-specific skill gap analyses. Each report evaluates your qualifications against a target position."
        icon={FileText}
        actions={
          <button onClick={loadReports} className="btn btn-ghost btn-sm">
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        }
      />

      {/* Stats Strip */}
      <div className="grid grid-4" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-6)' }}>
        <StatCard
          label="Total Reports"
          value={totalReports}
          icon={FileText}
          color="primary"
          helperText="All analyses generated"
        />
        <StatCard
          label="Average Score"
          value={`${avgScore}%`}
          icon={BarChart3}
          color="info"
          helperText="Overall fit average"
        />
        <StatCard
          label="Completed"
          value={completedReports}
          icon={CheckCircle2}
          color="success"
          helperText="Post-interview reports"
        />
        <StatCard
          label="Pending"
          value={totalReports - completedReports}
          icon={AlertCircle}
          color="warning"
          helperText="Awaiting assessment"
        />
      </div>

      {/* Reports Table */}
      {loading ? (
        <SkeletonLoader type="table" rows={5} cols={6} />
      ) : reports.length === 0 ? (
        <EmptyState
          title="No Skill Gap Reports Yet"
          description="Apply for a position and complete your technical assessment to generate your first skill gap report."
          actionLabel="Browse Job Postings"
          onAction={() => navigate('/candidate/jobs')}
          icon={FileText}
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{
            padding: 'var(--p-space-4) var(--p-space-5)',
            borderBottom: '1px solid var(--color-border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <FileText size={18} style={{ color: 'var(--color-primary)' }} />
              All Reports
            </h3>
            <span style={{
              fontSize: 'var(--p-text-xs)', fontWeight: 700,
              color: 'var(--color-primary)', background: 'var(--color-primary-muted)',
              padding: '3px 10px', borderRadius: 'var(--radius-full)'
            }}>
              {totalReports} Report{totalReports !== 1 ? 's' : ''}
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Target Role</th>
                  <th>Date</th>
                  <th>Overall Score</th>
                  <th>Status</th>
                  <th style={{ width: 120 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report, idx) => {
                  const candidateId = report.candidate_id || `report-${idx}`
                  return (
                    <tr key={`${candidateId}-${idx}`}>
                      <td>
                        <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                          {report.candidate_name || 'Candidate'}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                          ID: {candidateId?.slice(0, 10) || 'N/A'}
                        </div>
                      </td>
                      <td>
                        <span className="chip" style={{ fontSize: '11px' }}>
                          {report.role || report.job_role || 'N/A'}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-fg-muted)', fontSize: 'var(--p-text-xs)' }}>
                          <Calendar size={13} />
                          {report.date || report.created_at
                            ? new Date(report.date || report.created_at).toLocaleDateString()
                            : 'N/A'}
                        </div>
                      </td>
                      <td>
                        <div style={{
                          fontSize: 'var(--p-text-base)', fontWeight: 800,
                          color: (report.overall_score || 0) >= 70
                            ? 'var(--color-success)'
                            : (report.overall_score || 0) >= 40
                            ? 'var(--color-warning)'
                            : 'var(--color-danger)',
                          fontFamily: 'var(--p-font-mono)'
                        }}>
                          {report.overall_score != null ? `${report.overall_score}%` : 'N/A'}
                        </div>
                      </td>
                      <td>
                        <span style={{
                          fontSize: '10px', fontWeight: 700,
                          padding: '2px 8px', borderRadius: 'var(--radius-full)',
                          background: report.status === 'completed' ? 'var(--color-success-muted)' : 'var(--color-warning-muted)',
                          color: report.status === 'completed' ? 'var(--color-success)' : 'var(--color-warning)',
                          border: `1px solid ${report.status === 'completed' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`
                        }}>
                          {report.status === 'completed' ? 'Completed' : 'Pending'}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <Link
                            to={`/candidate/skill-gap/reports/${candidateId}`}
                            className="btn btn-ghost btn-sm"
                            style={{ fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: 4, padding: '4px 8px' }}
                          >
                            <Eye size={13} /> View
                          </Link>
                          <button
                            onClick={() => setConfirm({ open: true, candidateId })}
                            className="btn btn-ghost btn-sm"
                            style={{ color: 'var(--color-danger)', padding: '4px 8px' }}
                            title="Delete report"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={confirm.open}
        title="Delete Skill Gap Report?"
        message="This will permanently remove this skill gap analysis. This action cannot be undone."
        danger
        confirmLabel="Delete"
        onConfirm={async () => {
          await deleteReport(confirm.candidateId)
          setConfirm({ open: false, candidateId: null })
        }}
        onCancel={() => setConfirm({ open: false, candidateId: null })}
      />
    </div>
  )
}
