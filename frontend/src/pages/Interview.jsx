import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Play, CheckCircle2, Code, FileText, Settings, Sparkles,
  ArrowRight, ArrowLeft, RefreshCw, Check, X, Terminal, Trophy
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { getChartTheme } from '../chartTheme'
import { c2Start, c2Submit, c2Jobs, c2RunCode } from '../api'
import PageHeader from '../components/PageHeader'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import ConfirmDialog from '../components/ConfirmDialog'

export default function Interview() {
  const ct = getChartTheme()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const jobRole = searchParams.get('role') || ''
  const jobSkills = searchParams.get('skills') || ''
  const isPracticeMode = !jobRole

  const [step, setStep] = useState('setup')
  const [roles, setRoles] = useState({})
  const [selectedRole, setSelectedRole] = useState(jobRole)
  const [numQuestions, setNumQuestions] = useState(10)
  const [session, setSession] = useState(null)
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [runResults, setRunResults] = useState(null)
  const [running, setRunning] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') {
      navigate('/login/candidate')
      return
    }
    loadRoles()
  }, [])

  useEffect(() => {
    if (jobRole) setSelectedRole(jobRole)
  }, [jobRole])

  useEffect(() => {
    setRunResults(null)
  }, [currentQ])

  const loadRoles = async () => {
    try {
      const r = await c2Jobs()
      setRoles(r?.data?.jobs || {})
    } catch {
      toast.error('Failed to load roles')
    }
  }

  const startInterview = async () => {
    if (!selectedRole) return toast.error('Please select a target role')
    setBusy(true)
    try {
      const skills = jobRole && jobSkills
        ? jobSkills.split(',').filter(Boolean)
        : (Object.keys(roles).length > 0 ? (roles[selectedRole] || []).slice(0, 5) : [])
      const r = await c2Start({
        candidate_id: localStorage.getItem('recruitai.user_id') || 'candidate-user',
        job_role: selectedRole,
        required_skills: skills,
        num_questions: numQuestions,
      })
      setSession(r.data)
      setCurrentQ(0)
      setAnswers({})
      setStep('quiz')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to start interview')
    } finally {
      setBusy(false)
    }
  }

  const answerQuestion = (questionId, value) => {
    setAnswers((a) => ({ ...a, [questionId]: value }))
    setRunResults(null)
  }

  const runCode = async () => {
    if (!q || q.question_type !== 'Coding') return
    const code = answers[q.id] || ''
    if (!code.trim()) return toast.error('Write some code before running tests')
    setRunning(true)
    setRunResults(null)
    try {
      const r = await c2RunCode({ code_text: code, test_cases: q.test_cases || [] })
      setRunResults(r.data)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Execution failed')
    } finally {
      setRunning(false)
    }
  }

  const submitInterview = async () => {
    setConfirm({
      open: true,
      title: 'Submit technical interview?',
      message: 'Your answers will be evaluated and combined with your CV qualifications to update your ranking scores.',
      action: async () => {
        setBusy(true)
        try {
          const questions = session.questions || []
          const payload = {
            candidate_id: localStorage.getItem('recruitai.user_id') || 'candidate-user',
            session_id: session.session_id,
            job_role: selectedRole,
            answers: questions.map((q) => {
              const a = answers[q.id]
              if (q.question_type === 'MCQ') return { question_id: q.id, selected_option: a != null ? parseInt(a) : null }
              if (q.question_type === 'Descriptive') return { question_id: q.id, answer_text: a || '' }
              if (q.question_type === 'Coding') return { question_id: q.id, code_text: a || '', language: 'Python' }
              return { question_id: q.id, answer_text: a || '' }
            }),
          }
          const r = await c2Submit(payload)
          setResult(r.data)
          setStep('result')
          toast.success('Interview evaluation complete!')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Submission failed')
        } finally {
          setBusy(false)
        }
      }
    })
  }

  const questions = session?.questions || []
  const q = questions[currentQ]
  const progressPct = questions.length > 0 ? (((currentQ + 1) / questions.length) * 100).toFixed(0) : 0

  const typeIcon = (t) => {
    if (t === 'MCQ') return <CheckCircle2 size={14} />
    if (t === 'Coding') return <Code size={14} />
    return <FileText size={14} />
  }

  // ─────────────────────────────────────────────────────────────
  // SETUP STAGE
  // ─────────────────────────────────────────────────────────────
  if (step === 'setup') {
    return (
      <div className="fade-in" style={{ maxWidth: 760, margin: '0 auto' }}>
        <PageHeader
          badge="Component 2 AI Engine"
          title={isPracticeMode ? 'AI Technical Interview Sandbox' : `Technical Assessment · ${jobRole}`}
          description="Simulate real-world technical evaluations with automated MCQs, semantic theory scoring, and live Python test execution."
          icon={Code}
        />

        <div className="card" style={{ padding: 'var(--p-space-6)' }}>
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Target Technical Role *</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
            >
              <option value="">Select target role...</option>
              {Object.keys(roles).map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 24 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Question Volume</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {[5, 10, 15].map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => setNumQuestions(count)}
                  className={`btn ${numQuestions === count ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ flex: 1 }}
                >
                  {count} Questions
                </button>
              ))}
            </div>
          </div>

          {/* Assessment Protocol Summary */}
          <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 24 }}>
            <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 8, color: 'var(--color-fg)' }}>
              Assessment Evaluation Format
            </div>
            <ul style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-secondary)', margin: 0, paddingLeft: 18, lineHeight: 1.6 }}>
              <li><strong>Deterministic MCQs:</strong> Automated algorithmic key matching.</li>
              <li><strong>Descriptive Theory:</strong> Semantic cosine vector similarity evaluation.</li>
              <li><strong>Coding Sandbox:</strong> Automated Python syntax AST verification & test cases runner.</li>
            </ul>
          </div>

          <button
            className="btn btn-primary"
            onClick={startInterview}
            disabled={busy || !selectedRole}
            style={{ width: '100%', padding: '12px 20px', fontSize: 'var(--p-text-base)', fontWeight: 700 }}
          >
            <Play size={18} /> {busy ? 'Generating Assessment...' : 'Start Assessment Now'}
          </button>
        </div>
      </div>
    )
  }

  // ─────────────────────────────────────────────────────────────
  // QUIZ STAGE
  // ─────────────────────────────────────────────────────────────
  if (step === 'quiz' && q) {
    const isAnswered = answers[q.id] !== undefined && answers[q.id] !== ''
    const isLast = currentQ === questions.length - 1

    return (
      <div className="fade-in" style={{ maxWidth: 880, margin: '0 auto' }}>
        {/* Progress Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-primary)' }}>
              {selectedRole} Assessment
            </div>
            <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)' }}>
              Question {currentQ + 1} of {questions.length}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              background: q.question_type === 'Coding' ? 'var(--color-purple-muted)' : 'var(--color-primary-muted)',
              color: q.question_type === 'Coding' ? 'var(--color-purple)' : 'var(--color-primary)',
              border: '1px solid var(--color-border-subtle)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4
            }}>
              {typeIcon(q.question_type)} {q.question_type}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: 6, background: 'var(--color-border-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden', marginBottom: 24 }}>
          <div style={{ width: `${progressPct}%`, height: '100%', background: 'var(--color-primary)', transition: 'width 0.3s ease' }} />
        </div>

        {/* Question Card */}
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, lineHeight: 1.4, color: 'var(--color-fg)', margin: '0 0 20px 0' }}>
            {q.question_text || q.question}
          </h2>

          {/* MCQ Mode */}
          {q.question_type === 'MCQ' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {(q.options || []).map((opt, idx) => {
                const isSelected = answers[q.id] === idx
                return (
                  <div
                    key={idx}
                    onClick={() => answerQuestion(q.id, idx)}
                    style={{
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-md)',
                      border: `1.5px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border-subtle)'}`,
                      background: isSelected ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      border: `2px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--color-primary)',
                      fontSize: '12px',
                      fontWeight: 800,
                      flexShrink: 0
                    }}>
                      {String.fromCharCode(65 + idx)}
                    </div>
                    <span style={{ fontSize: 'var(--p-text-base)', color: 'var(--color-fg)' }}>
                      {opt}
                    </span>
                  </div>
                )
              })}
            </div>
          )}

          {/* Descriptive Mode */}
          {q.question_type === 'Descriptive' && (
            <div>
              <textarea
                placeholder="Type your technical explanation here with architectural or algorithmic details..."
                value={answers[q.id] || ''}
                onChange={(e) => answerQuestion(q.id, e.target.value)}
                rows={6}
                style={{ fontFamily: 'inherit', fontSize: 'var(--p-text-base)', lineHeight: 1.6 }}
              />
            </div>
          )}

          {/* Coding Sandbox Mode */}
          {q.question_type === 'Coding' && (
            <div>
              <div style={{ marginBottom: 12 }}>
                <textarea
                  placeholder="# Write your Python solution here...&#10;def solution():&#10;    pass"
                  value={answers[q.id] || ''}
                  onChange={(e) => answerQuestion(q.id, e.target.value)}
                  rows={10}
                  style={{
                    fontFamily: 'var(--p-font-mono)',
                    fontSize: '13px',
                    lineHeight: 1.5,
                    background: 'var(--color-bg)',
                    color: 'var(--color-fg)'
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={runCode}
                  disabled={running}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
                >
                  <Terminal size={14} /> {running ? 'Running Tests...' : 'Run Unit Tests'}
                </button>
              </div>

              {/* Console Output */}
              {runResults && (
                <div style={{
                  padding: 14,
                  background: 'var(--color-bg)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border-subtle)',
                  fontFamily: 'var(--p-font-mono)',
                  fontSize: '12px'
                }}>
                  <div style={{
                    fontWeight: 700,
                    marginBottom: 6,
                    color: runResults.all_passed ? 'var(--color-success)' : 'var(--color-danger)'
                  }}>
                    {runResults.all_passed ? '✓ All Test Cases Passed' : '✗ Some Test Cases Failed'}
                  </div>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: 'var(--color-fg-secondary)' }}>
                    {runResults.output || JSON.stringify(runResults, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setCurrentQ((c) => Math.max(0, c - 1))}
            disabled={currentQ === 0}
          >
            <ArrowLeft size={14} /> Previous
          </button>

          {isLast ? (
            <button
              className="btn btn-primary"
              onClick={submitInterview}
              disabled={busy}
            >
              <Trophy size={16} /> Submit Assessment
            </button>
          ) : (
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setCurrentQ((c) => Math.min(questions.length - 1, c + 1))}
            >
              Next Question <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* Confirmation Dialog */}
        <ConfirmDialog
          open={confirm.open}
          title={confirm.title}
          message={confirm.message}
          confirmLabel="Submit Assessment"
          onConfirm={async () => {
            await confirm.action()
            setConfirm({ ...confirm, open: false })
          }}
          onCancel={() => setConfirm({ ...confirm, open: false })}
        />
      </div>
    )
  }

  // ─────────────────────────────────────────────────────────────
  // RESULT STAGE
  // ─────────────────────────────────────────────────────────────
  if (step === 'result' && result) {
    const mcqScore = result.mcq_score || 0
    const descScore = result.descriptive_score || 0
    const codeScore = result.code_score || 0
    const overallScore = result.overall_score || (mcqScore * 0.2 + descScore * 0.3 + codeScore * 0.5)

    const chartData = [
      { name: 'MCQ Test', score: mcqScore },
      { name: 'Theory Exam', score: descScore },
      { name: 'Code Sandbox', score: codeScore },
    ]

    return (
      <div className="fade-in" style={{ maxWidth: 880, margin: '0 auto' }}>
        <PageHeader
          badge="Evaluation Summary"
          title="Technical Assessment Scorecard"
          description={`Comprehensive AI evaluation breakdown for ${selectedRole}. Scores are recorded to your candidate profile.`}
          icon={Trophy}
          actions={
            <button className="btn btn-ghost btn-sm" onClick={() => setStep('setup')}>
              <RefreshCw size={14} /> Retake Assessment
            </button>
          }
        />

        {/* Top Overall Score Card */}
        <div className="card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', letterSpacing: '0.08em', marginBottom: 6 }}>
            Blended Interview Score (P_int)
          </div>
          <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--color-primary)', lineHeight: 1, fontFamily: 'var(--p-font-mono)', marginBottom: 8 }}>
            {overallScore.toFixed(1)}%
          </div>
          <div style={{ display: 'inline-flex', marginBottom: 20 }}>
            <ScoreBadge score={overallScore} />
          </div>

          <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', textAlign: 'left' }}>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <ScoreMeter score={mcqScore} label="MCQ Accuracy (P_mcq)" size="sm" />
            </div>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <ScoreMeter score={descScore} label="Theory Cosine (P_desc)" size="sm" />
            </div>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <ScoreMeter score={codeScore} label="Coding Sandbox (P_code)" size="sm" />
            </div>
          </div>
        </div>

        {/* Section Comparison Chart */}
        <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
            Section Score Breakdown
          </h3>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <XAxis dataKey="name" stroke={ct.axis} tick={{ fill: ct.text, fontSize: 12 }} />
                <YAxis domain={[0, 100]} stroke={ct.axis} tick={{ fill: ct.text, fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: ct.tooltipBg, border: `1px solid ${ct.tooltipBorder}`, borderRadius: 8 }}
                  formatter={(val) => [`${Number(val).toFixed(1)}%`, 'Score']}
                />
                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? 'var(--color-primary)' : index === 1 ? 'var(--color-info)' : 'var(--color-purple)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Navigation CTAs */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <Link to="/candidate/jobs" className="btn btn-ghost">
            Browse Jobs
          </Link>
          <Link to="/candidate/dashboard" className="btn btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return null
}
