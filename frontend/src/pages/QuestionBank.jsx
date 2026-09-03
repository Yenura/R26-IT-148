import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  BookOpen, ArrowLeft, Code, FileText, CheckCircle2,
  ChevronDown, ChevronUp, BarChart3, Filter
} from 'lucide-react'
import { c2Questions, c3Roles } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function QuestionBank() {
  const navigate = useNavigate()
  const { role: roleParam } = useParams()
  useAuth()

  const [selectedRole, setSelectedRole] = useState(roleParam || '')
  const [roles, setRoles] = useState({})
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingRoles, setLoadingRoles] = useState(true)
  const [expandedIdx, setExpandedIdx] = useState(null)
  const [filterType, setFilterType] = useState('all')
  const [filterDifficulty, setFilterDifficulty] = useState('all')

  useEffect(() => {
    loadRoles()
  }, [])

  useEffect(() => {
    if (selectedRole) loadQuestions()
  }, [selectedRole])

  useEffect(() => {
    if (roleParam && roleParam !== selectedRole) {
      setSelectedRole(roleParam)
    }
  }, [roleParam])

  const loadRoles = async () => {
    setLoadingRoles(true)
    try {
      const r = await c3Roles()
      setRoles(r?.data?.jobs || r?.data || {})
    } catch {
      toast.error('Failed to load available roles')
    } finally {
      setLoadingRoles(false)
    }
  }

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const r = await c2Questions(selectedRole)
      const data = r?.data || {}
      setQuestions(data.questions || data.data || [])
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to load question bank')
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  const getRoleList = () => {
    if (Array.isArray(roles)) return roles.map(r => typeof r === 'string' ? r : r.role || r.name || r.title || '').filter(Boolean)
    if (typeof roles === 'object' && roles !== null) return Object.keys(roles)
    return []
  }

  const roleList = getRoleList()

  const getFilteredQuestions = () => {
    return questions.filter((q) => {
      const qType = (q.question_type || q.type || '').toLowerCase()
      const qDiff = (q.difficulty || q.level || '').toLowerCase()
      if (filterType !== 'all' && qType !== filterType.toLowerCase()) return false
      if (filterDifficulty !== 'all' && qDiff !== filterDifficulty.toLowerCase()) return false
      return true
    })
  }

  const filtered = getFilteredQuestions()
  const grouped = {
    MCQ: filtered.filter(q => (q.question_type || q.type || '').toUpperCase() === 'MCQ'),
    Coding: filtered.filter(q => (q.question_type || q.type || '').toUpperCase() === 'CODING'),
    Descriptive: filtered.filter(q => (q.question_type || q.type || '').toUpperCase() === 'DESCRIPTIVE'),
  }
  const otherTypes = filtered.filter(q => {
    const t = (q.question_type || q.type || '').toUpperCase()
    return t !== 'MCQ' && t !== 'CODING' && t !== 'DESCRIPTIVE'
  })
  if (otherTypes.length > 0) grouped['Other'] = otherTypes

  const typeIcon = (t) => {
    if (t === 'MCQ') return <CheckCircle2 size={14} />
    if (t === 'Coding') return <Code size={14} />
    return <FileText size={14} />
  }

  const difficultyColor = (d) => {
    if (!d) return { bg: 'var(--color-bg-elevated)', fg: 'var(--color-fg-muted)' }
    const l = d.toLowerCase()
    if (l === 'easy' || l === 'beginner') return { bg: 'var(--color-success-muted)', fg: 'var(--color-success)' }
    if (l === 'medium' || l === 'intermediate' || l === 'mid') return { bg: 'var(--color-warning-muted)', fg: 'var(--color-warning)' }
    if (l === 'hard' || l === 'advanced' || l === 'senior') return { bg: 'var(--color-danger-muted)', fg: 'var(--color-danger)' }
    return { bg: 'var(--color-bg-elevated)', fg: 'var(--color-fg-muted)' }
  }

  const toggleExpand = (idx) => {
    setExpandedIdx(expandedIdx === idx ? null : idx)
  }

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
      <PageHeader
        badge="C2 AI Engine · Question Bank"
        title="Interview Question Bank"
        description="Browse the AI-generated question repository for each technical role. Questions are grouped by type with difficulty ratings and sample answers."
        icon={BookOpen}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)}>
            <ArrowLeft size={14} /> Back
          </button>
        }
      />

      {/* Role Selector & Filters */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Filter size={16} style={{ color: 'var(--color-primary)' }} /> Select Target Role
          </h3>
          {questions.length > 0 && (
            <span className="chip" style={{ fontSize: '11px', fontWeight: 700, background: 'var(--color-primary-muted)', color: 'var(--color-primary)' }}>
              {questions.length} Question{questions.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 12, alignItems: 'center' }}>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
          >
            <option value="">Select a technical role...</option>
            {roleList.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <button
            className="btn btn-primary"
            onClick={loadQuestions}
            disabled={loading || !selectedRole}
            style={{ whiteSpace: 'nowrap' }}
          >
            {loading ? 'Loading...' : 'Load Questions'}
          </button>
        </div>

        {/* Filter Row */}
        {questions.length > 0 && (
          <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-fg-muted)' }}>Type:</span>
              {['all', 'MCQ', 'Coding', 'Descriptive'].map((t) => (
                <button
                  key={t}
                  className={`btn btn-sm ${filterType === t ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setFilterType(t)}
                  style={{ fontSize: '11px', padding: '4px 10px' }}
                >
                  {t === 'all' ? 'All' : t}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-fg-muted)' }}>Difficulty:</span>
              {['all', 'Easy', 'Medium', 'Hard'].map((d) => (
                <button
                  key={d}
                  className={`btn btn-sm ${filterDifficulty === d ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setFilterDifficulty(d)}
                  style={{ fontSize: '11px', padding: '4px 10px' }}
                >
                  {d === 'all' ? 'All' : d}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <SkeletonLoader type="card" count={3} />
      )}

      {/* Empty State */}
      {!loading && selectedRole && questions.length === 0 && (
        <EmptyState
          title="No Questions Available"
          description={`No questions have been generated for the "${selectedRole}" role yet. Questions are created dynamically based on the role and difficulty level.`}
          icon={BookOpen}
        />
      )}

      {/* No Role Selected */}
      {!loading && !selectedRole && (
        <EmptyState
          title="Select a Role to Browse Questions"
          description="Choose a technical role from the dropdown above to view the AI-generated question bank. Questions are organized by type and difficulty."
          icon={BookOpen}
        />
      )}

      {/* Question Stats */}
      {!loading && questions.length > 0 && (
        <>
          <div className="dashboard-grid dashboard-grid-equal" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
            <StatCard
              label="MCQ Questions"
              value={grouped.MCQ?.length || 0}
              icon={CheckCircle2}
              color="success"
              helperText="Multiple choice questions"
            />
            <StatCard
              label="Coding Questions"
              value={grouped.Coding?.length || 0}
              icon={Code}
              color="purple"
              helperText="Live code execution"
            />
            <StatCard
              label="Descriptive Questions"
              value={grouped.Descriptive?.length || 0}
              icon={FileText}
              color="info"
              helperText="Theory & explanations"
            />
            <StatCard
              label="Total Questions"
              value={filtered.length}
              icon={BarChart3}
              color="primary"
              helperText={`Filtered from ${questions.length}`}
            />
          </div>

          {/* Grouped Question List */}
          {Object.entries(grouped).map(([type, typeQuestions]) => {
            if (typeQuestions.length === 0) return null
            return (
              <div key={type} style={{ marginBottom: 'var(--p-space-5)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  {typeIcon(type)}
                  <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
                    {type} Questions ({typeQuestions.length})
                  </h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {typeQuestions.map((q, idx) => {
                    const qIdx = questions.indexOf(q)
                    const isExpanded = expandedIdx === qIdx
                    const diff = q.difficulty || q.level || 'Medium'
                    const dc = difficultyColor(diff)
                    const qText = q.question_text || q.question || `Question ${idx + 1}`
                    const sampleAnswer = q.sample_answer || q.answer || q.correct_answer || q.explanation || ''
                    const options = q.options || []

                    return (
                      <div key={q.id || q.question_id || idx} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                        <button
                          type="button"
                          onClick={() => toggleExpand(qIdx)}
                          style={{
                            width: '100%',
                            padding: '14px 18px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 12,
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            fontFamily: 'inherit',
                            fontSize: 'inherit'
                          }}
                        >
                          <span style={{
                            width: 28,
                            height: 28,
                            borderRadius: 'var(--radius-sm)',
                            background: 'var(--color-bg-elevated)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '11px',
                            fontWeight: 800,
                            color: 'var(--color-fg-muted)',
                            flexShrink: 0
                          }}>
                            {idx + 1}
                          </span>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{
                              fontSize: 'var(--p-text-sm)',
                              fontWeight: 600,
                              color: 'var(--color-fg)',
                              lineHeight: 1.4,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: isExpanded ? 'normal' : 'nowrap'
                            }}>
                              {qText}
                            </div>
                          </div>
                          <span style={{
                            fontSize: '10px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: 'var(--radius-full)',
                            background: dc.bg,
                            color: dc.fg,
                            border: `1px solid ${dc.fg}30`,
                            flexShrink: 0
                          }}>
                            {diff}
                          </span>
                          {isExpanded ? <ChevronUp size={16} style={{ color: 'var(--color-fg-muted)', flexShrink: 0 }} /> : <ChevronDown size={16} style={{ color: 'var(--color-fg-muted)', flexShrink: 0 }} />}
                        </button>

                        {isExpanded && (
                          <div style={{ padding: '0 18px 18px', borderTop: '1px solid var(--color-border-subtle)' }}>
                            {/* Full Question Text */}
                            <div style={{
                              padding: 14,
                              marginTop: 12,
                              background: 'var(--color-bg)',
                              borderRadius: 'var(--radius-md)',
                              border: '1px solid var(--color-border-subtle)',
                              fontSize: 'var(--p-text-sm)',
                              lineHeight: 1.6,
                              color: 'var(--color-fg)',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-word'
                            }}>
                              {qText}
                            </div>

                            {/* MCQ Options */}
                            {type === 'MCQ' && options.length > 0 && (
                              <div style={{ marginTop: 12 }}>
                                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Options</div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                  {options.map((opt, oIdx) => {
                                    const optText = typeof opt === 'string' ? opt : opt.text || opt.value || ''
                                    const isCorrectOpt = q.correct_option === oIdx || q.correct_option === String.fromCharCode(65 + oIdx)
                                    return (
                                      <div key={oIdx} style={{
                                        padding: '8px 12px',
                                        borderRadius: 'var(--radius-sm)',
                                        border: `1px solid ${isCorrectOpt ? 'rgba(16, 185, 129, 0.4)' : 'var(--color-border-subtle)'}`,
                                        background: isCorrectOpt ? 'var(--color-success-muted)' : 'var(--color-bg-elevated)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 10
                                      }}>
                                        <span style={{
                                          width: 22,
                                          height: 22,
                                          borderRadius: '50%',
                                          border: `2px solid ${isCorrectOpt ? 'var(--color-success)' : 'var(--color-border)'}`,
                                          display: 'flex',
                                          alignItems: 'center',
                                          justifyContent: 'center',
                                          fontSize: '11px',
                                          fontWeight: 800,
                                          color: isCorrectOpt ? 'var(--color-success)' : 'var(--color-fg-muted)',
                                          flexShrink: 0
                                        }}>
                                          {String.fromCharCode(65 + oIdx)}
                                        </span>
                                        <span style={{ fontSize: '12px', color: 'var(--color-fg)', flex: 1 }}>{optText}</span>
                                        {isCorrectOpt && <CheckCircle2 size={14} style={{ color: 'var(--color-success)', flexShrink: 0 }} />}
                                      </div>
                                    )
                                  })}
                                </div>
                              </div>
                            )}

                            {/* Sample Answer / Explanation */}
                            {sampleAnswer && (
                              <div style={{ marginTop: 12 }}>
                                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                                  {type === 'Coding' ? 'Sample Solution' : 'Sample Answer / Explanation'}
                                </div>
                                <div style={{
                                  padding: 14,
                                  background: 'var(--color-bg)',
                                  borderRadius: 'var(--radius-md)',
                                  border: '1px solid var(--color-border-subtle)',
                                  fontFamily: type === 'Coding' ? 'var(--p-font-mono)' : 'inherit',
                                  fontSize: type === 'Coding' ? '12px' : '12px',
                                  lineHeight: 1.6,
                                  color: 'var(--color-fg)',
                                  whiteSpace: 'pre-wrap',
                                  wordBreak: 'break-word'
                                }}>
                                  {sampleAnswer}
                                </div>
                              </div>
                            )}

                            {/* Tags / Metadata */}
                            <div style={{ marginTop: 12, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                              {q.topic && (
                                <span className="chip" style={{ fontSize: '10px', padding: '2px 8px' }}>{q.topic}</span>
                              )}
                              {q.skills && (Array.isArray(q.skills) ? q.skills : [q.skills]).map((s, sIdx) => (
                                <span key={sIdx} className="chip" style={{ fontSize: '10px', padding: '2px 8px' }}>{s}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </>
      )}
    </div>
  )
}
