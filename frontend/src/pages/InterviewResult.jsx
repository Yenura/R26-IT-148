import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Trophy, ArrowLeft, Clock, CheckCircle2, XCircle, Code,
  FileText, BarChart3, Target, Briefcase
} from 'lucide-react'
import { c2Result } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function InterviewResult() {
  const navigate = useNavigate()
  const { interviewId } = useParams()
  useAuth('candidate')

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (interviewId) loadResult()
  }, [interviewId])

  const loadResult = async () => {
    setLoading(true)
    try {
      const r = await c2Result(interviewId)
      setResult(r?.data || r)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to load interview result')
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

  if (!result) {
    return (
      <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
        <PageHeader
          badge="Interview Result"
          title="Result Not Found"
          description="The interview result could not be loaded. It may not exist yet or the session has expired."
          icon={Trophy}
        />
        <EmptyState
          title="No Result Available"
          description="The interview result for this session was not found. Please complete an interview first."
          actionLabel="Back to Interviews"
          onAction={() => navigate('/candidate/interview')}
          icon={Trophy}
        />
      </div>
    )
  }

  const mcqScore = result.mcq_score || 0
  const descScore = result.descriptive_score || 0
  const codeScore = result.coding_score || 0
  const totalScore = result.total_score || result.interview_score || 0
  const timeTaken = result.time_taken || result.duration || 0
  const jobRole = result.job_role || result.role || 'Technical'
  const questions = result.questions || result.question_details || result.breakdown || []
  const passed = result.passed || totalScore >= 50

  const timeTakenFormatted = timeTaken > 0
    ? `${Math.floor(timeTaken / 60)}m ${timeTaken % 60}s`
    : 'N/A'

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
      <PageHeader
        badge="C2 AI Engine · Evaluation"
        title="Interview Result"
        description={`Detailed scorecard for your ${jobRole} technical assessment. Scores are recorded to your candidate profile.`}
        icon={Trophy}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/interview')}>
            <ArrowLeft size={14} /> Back to Interview
          </button>
        }
      />

      {/* Score Overview Cards */}
      <div className="dashboard-grid dashboard-grid-equal" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <StatCard
          label="MCQ Score"
          value={`${mcqScore.toFixed(1)}%`}
          icon={CheckCircle2}
          color="success"
          helperText="Deterministic key matching"
        />
        <StatCard
          label="Descriptive Score"
          value={`${descScore.toFixed(1)}%`}
          icon={FileText}
          color="info"
          helperText="Semantic cosine similarity"
        />
        <StatCard
          label="Coding Score"
          value={`${codeScore.toFixed(1)}%`}
          icon={Code}
          color="purple"
          helperText="Test case execution"
        />
        <StatCard
          label="Total Score"
          value={`${totalScore.toFixed(1)}%`}
          icon={BarChart3}
          color={passed ? 'success' : 'danger'}
          helperText={passed ? 'Passed assessment' : 'Below threshold'}
        />
      </div>

      {/* Total Score Banner */}
      <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', textAlign: 'center' }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--color-fg-muted)',
          marginBottom: 6
        }}>
          Blended Interview Score (P_int)
        </div>
        <div style={{
          fontSize: '3rem',
          fontWeight: 900,
          color: passed ? 'var(--color-success)' : 'var(--color-danger)',
          lineHeight: 1,
          fontFamily: 'var(--p-font-mono)',
          marginBottom: 8
        }}>
          {totalScore.toFixed(1)}%
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{
            fontSize: '12px',
            fontWeight: 700,
            padding: '3px 12px',
            borderRadius: 'var(--radius-full)',
            background: passed ? 'var(--color-success-muted)' : 'var(--color-danger-muted)',
            color: passed ? 'var(--color-success)' : 'var(--color-danger)',
            border: `1px solid ${passed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`
          }}>
            {passed ? 'Qualified' : 'Below Threshold'}
          </span>
          <span style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--color-fg-muted)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6
          }}>
            <Clock size={13} /> Time Taken: {timeTakenFormatted}
          </span>
        </div>

        {/* Score Breakdown Bars */}
        <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 560, margin: '24px auto 0' }}>
          {[
            { label: 'MCQ (P_mcq)', score: mcqScore, color: 'var(--color-success)' },
            { label: 'Descriptive (P_desc)', score: descScore, color: 'var(--color-info)' },
            { label: 'Coding (P_code)', score: codeScore, color: 'var(--color-purple)' },
          ].map((item) => (
            <div key={item.label} style={{ textAlign: 'left' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg-secondary)' }}>{item.label}</span>
                <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{item.score.toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: 8, background: 'var(--color-border-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{ width: `${item.score}%`, height: '100%', background: item.color, borderRadius: 'var(--radius-full)', transition: 'width 0.6s ease' }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Question-by-Question Review */}
      {questions.length > 0 && (
        <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={16} style={{ color: 'var(--color-primary)' }} /> Question-by-Question Review
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {questions.map((q, idx) => {
              const isCorrect = q.correct || q.is_correct || q.score > 0
              const qType = q.question_type || q.type || 'MCQ'
              const qText = q.question_text || q.question || `Question ${idx + 1}`
              const qScore = q.score != null ? q.score : null

              return (
                <div key={q.id || q.question_id || idx} style={{
                  padding: '12px 16px',
                  background: 'var(--color-bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: `4px solid ${isCorrect ? 'var(--color-success)' : 'var(--color-danger)'}`,
                  border: `1px solid ${isCorrect ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)'}`,
                  borderLeftWidth: 4,
                  borderLeftColor: isCorrect ? 'var(--color-success)' : 'var(--color-danger)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: 12
                }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: 'var(--radius-full)',
                        background: qType === 'MCQ' ? 'var(--color-success-muted)' : qType === 'Coding' ? 'var(--color-purple-muted)' : 'var(--color-info-muted)',
                        color: qType === 'MCQ' ? 'var(--color-success)' : qType === 'Coding' ? 'var(--color-purple)' : 'var(--color-info)',
                        border: '1px solid var(--color-border-subtle)'
                      }}>
                        {qType}
                      </span>
                      <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-fg-muted)' }}>
                        Q{idx + 1}
                      </span>
                    </div>
                    <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 600, color: 'var(--color-fg)', lineHeight: 1.5 }}>
                      {qText}
                    </div>
                    {q.your_answer != null && (
                      <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4 }}>
                        Your answer: <span style={{ fontWeight: 600, color: 'var(--color-fg-secondary)' }}>{String(q.your_answer)}</span>
                      </div>
                    )}
                    {q.correct_answer != null && !isCorrect && (
                      <div style={{ fontSize: '11px', color: 'var(--color-success)', marginTop: 2 }}>
                        Correct answer: <span style={{ fontWeight: 600 }}>{String(q.correct_answer)}</span>
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                    {qScore != null && (
                      <span style={{
                        fontSize: '12px',
                        fontWeight: 800,
                        fontFamily: 'var(--p-font-mono)',
                        color: isCorrect ? 'var(--color-success)' : 'var(--color-danger)'
                      }}>
                        {qScore.toFixed(0)}%
                      </span>
                    )}
                    {isCorrect ? (
                      <CheckCircle2 size={16} style={{ color: 'var(--color-success)' }} />
                    ) : (
                      <XCircle size={16} style={{ color: 'var(--color-danger)' }} />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Time Summary */}
      <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)', background: 'var(--color-bg-elevated)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <Clock size={18} style={{ color: 'var(--color-primary)' }} />
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700 }}>Time Summary</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Time</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2, fontFamily: 'var(--p-font-mono)' }}>{timeTakenFormatted}</div>
          </div>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Job Role</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{jobRole}</div>
          </div>
          <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Result</div>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: passed ? 'var(--color-success)' : 'var(--color-danger)', marginTop: 2 }}>{passed ? 'Passed' : 'Failed'}</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="card" style={{ padding: 'var(--p-space-5)', textAlign: 'center', background: 'var(--color-bg-elevated)' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
          What&apos;s Next?
        </h3>
        <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '0 0 16px 0' }}>
          Your scores have been saved. You can view your skill gap analysis or browse more opportunities.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={() => navigate('/candidate/interview')}>
            <ArrowLeft size={15} /> Back to Interview
          </button>
          <button className="btn btn-ghost" onClick={() => navigate('/candidate/skill-gap')}>
            <Target size={15} /> View Skill Gap
          </button>
          <button className="btn btn-ghost" onClick={() => navigate('/candidate/jobs')}>
            <Briefcase size={15} /> Browse Jobs
          </button>
        </div>
      </div>
    </div>
  )
}
