import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Play, CheckCircle2, Code, FileText, Settings, Sparkles,
  ArrowRight, ArrowLeft, RefreshCw, Check, X, Terminal, Trophy
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { getChartTheme } from '../chartTheme'
import { c2Start, c2Submit, c2Jobs, c2RunCode } from '../api'
import { useAuth } from '../hooks/useAuth'
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
  const jobCount = parseInt(searchParams.get('count'), 10) || 10
  const jobLevel = searchParams.get('level') || 'Mid-Level'
  const jobMcqTime = parseInt(searchParams.get('mcqTime'), 10) || 60
  const jobDescTime = parseInt(searchParams.get('descTime'), 10) || 300
  const jobCodingTime = parseInt(searchParams.get('codingTime'), 10) || 600
  const jobTotalTime = parseInt(searchParams.get('totalTime'), 10) || 60
  const isPracticeMode = !jobRole

  const [step, setStep] = useState('setup')
  const [roles, setRoles] = useState({})
  const [selectedRole, setSelectedRole] = useState(jobRole)
  const [selectedLevel, setSelectedLevel] = useState(jobLevel)
  const [numQuestions, setNumQuestions] = useState(jobCount)
  const [session, setSession] = useState(null)
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [runResults, setRunResults] = useState(null)
  const [running, setRunning] = useState(false)
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', danger: false, action: null })
  const [timeLeft, setTimeLeft] = useState(jobTotalTime * 60)
  const timerRef = useRef(null)

  useEffect(() => { loadRoles() }, [])

  useEffect(() => {
    if (jobRole) {
      const canonicalRoles = Object.keys(roles)
      const match = canonicalRoles.find((r) => r.toLowerCase() === jobRole.toLowerCase())
        || canonicalRoles.find((r) => r.toLowerCase().includes(jobRole.toLowerCase()) || jobRole.toLowerCase().includes(r.toLowerCase()))
      setSelectedRole(match || jobRole)
    }
  }, [jobRole, roles])

  useEffect(() => {
    setRunResults(null)
  }, [currentQ])

  const getPerQuestionTime = useCallback(() => {
    if (!session) return jobMcqTime
    const q = session.questions?.[currentQ]
    if (!q) return jobMcqTime
    if (q.question_type === 'MCQ') return jobMcqTime
    if (q.question_type === 'Descriptive') return jobDescTime
    if (q.question_type === 'Coding') return jobCodingTime
    return jobMcqTime
  }, [session, currentQ, jobMcqTime, jobDescTime, jobCodingTime])

  useEffect(() => {
    if (step !== 'quiz' || !session) return
    setTimeLeft(getPerQuestionTime())
  }, [currentQ, step, session, getPerQuestionTime])

  useEffect(() => {
    if (step !== 'quiz' || timeLeft <= 0) return
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current)
          toast.error('Time is up for this question!')
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => clearInterval(timerRef.current)
  }, [step, currentQ])

  useEffect(() => {
    if (result) clearInterval(timerRef.current)
  }, [result])

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
        job_level: selectedLevel,
        required_skills: skills,
        num_questions: numQuestions,
        mcq_time: jobMcqTime,
        desc_time: jobDescTime,
        coding_time: jobCodingTime,
        total_time: jobTotalTime,
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
              {selectedRole && !Object.keys(roles).includes(selectedRole) && (
                <option key={selectedRole} value={selectedRole}>{selectedRole}</option>
              )}
            </select>
          </div>

          <div style={{ marginBottom: 24 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Job Level</label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
            >
              {['Intern', 'Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal / Staff'].map((lvl) => (
                <option key={lvl} value={lvl}>{lvl}</option>
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
              fontSize: '13px',
              fontWeight: 700,
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              background: timeLeft <= 30 ? 'var(--color-danger-muted)' : 'var(--color-bg-elevated)',
              color: timeLeft <= 30 ? 'var(--color-danger)' : 'var(--color-fg)',
              border: `1px solid ${timeLeft <= 30 ? 'rgba(239,68,68,0.3)' : 'var(--color-border-subtle)'}`,
              fontVariantNumeric: 'tabular-nums'
            }}>
              {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
            </span>
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
          <div style={{ maxHeight: 400, overflowY: 'auto', paddingRight: 8, marginBottom: 20 }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, lineHeight: 1.6, color: 'var(--color-fg)', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {q.question_text || q.question}
            </h2>
          </div>

          {/* MCQ Mode */}
          {q.question_type === 'MCQ' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {(q.options || []).map((opt, idx) => {
                const isSelected = answers[q.id] === idx
                return (
                  <button
                    key={String.fromCharCode(65 + idx)}
                    type="button"
                    onClick={() => answerQuestion(q.id, idx)}
                    aria-pressed={isSelected}
                    style={{
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-md)',
                      border: `1.5px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border-subtle)'}`,
                      background: isSelected ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      transition: 'all 0.15s ease',
                      textAlign: 'left',
                      width: '100%',
                      fontSize: 'inherit',
                      fontFamily: 'inherit',
                      animation: isSelected ? 'option-select-bounce 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'none'
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
                      {typeof opt === 'string' ? opt : opt.text}
                    </span>
                  </button>
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
              {/* Test Cases / Examples */}
              {q.test_cases?.length > 0 && (
                <div style={{ marginBottom: 16, padding: 14, background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 10, letterSpacing: '0.05em' }}>
                    Examples / Test Cases
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {q.test_cases.filter(tc => {
                      const exp = String(tc.expected_output || '').trim().toLowerCase()
                      return exp && exp !== 'see answer' && exp !== 'result'
                    }).map((tc, i) => (
                      <div key={i} style={{ fontSize: '12px', fontFamily: 'var(--p-font-mono)', lineHeight: 1.6 }}>
                        <div style={{ color: 'var(--color-fg-muted)' }}>
                          <span style={{ fontWeight: 700 }}>Input:</span>{' '}
                          {Object.entries(tc.input || {}).map(([k, v]) => `${k} = ${JSON.stringify(v)}`).join(', ')}
                        </div>
                        <div style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
                          Expected Output: {JSON.stringify(tc.expected_output)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ marginBottom: 12 }}>
                <textarea
                  placeholder="# Write your Python solution here...&#10;def solution():&#10;    pass"
                  value={answers[q.id] || ''}
                  onChange={(e) => answerQuestion(q.id, e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Tab') {
                      e.preventDefault()
                      const ta = e.target
                      const start = ta.selectionStart
                      const end = ta.selectionEnd
                      const val = ta.value
                      if (e.shiftKey) {
                        const lineStart = val.lastIndexOf('\n', start - 1) + 1
                        const lineText = val.substring(lineStart, start)
                        const spaces = lineText.match(/^ {1,4}/)
                        if (spaces) {
                          const removeLen = spaces[0].length
                          answerQuestion(q.id, val.substring(0, lineStart) + val.substring(lineStart + removeLen))
                          setTimeout(() => { ta.selectionStart = ta.selectionEnd = start - removeLen }, 0)
                        }
                      } else {
                        const newVal = val.substring(0, start) + '    ' + val.substring(end)
                        answerQuestion(q.id, newVal)
                        setTimeout(() => { ta.selectionStart = ta.selectionEnd = start + 4 }, 0)
                      }
                    } else if (e.key === 'Enter') {
                      e.preventDefault()
                      const ta = e.target
                      const start = ta.selectionStart
                      const val = ta.value
                      const lineStart = val.lastIndexOf('\n', start - 1) + 1
                      const lineText = val.substring(lineStart, start)
                      const indent = lineText.match(/^(\s*)/)[1]
                      const extra = lineText.trimEnd().endsWith(':') ? '    ' : ''
                      const newVal = val.substring(0, start) + '\n' + indent + extra + val.substring(ta.selectionEnd)
                      answerQuestion(q.id, newVal)
                      setTimeout(() => { ta.selectionStart = ta.selectionEnd = start + 1 + indent.length + extra.length }, 0)
                    }
                  }}
                  rows={10}
                  spellCheck={false}
                  style={{
                    fontFamily: 'var(--p-font-mono)',
                    fontSize: '13px',
                    lineHeight: 1.5,
                    background: 'var(--color-bg)',
                    color: 'var(--color-fg)',
                    tabSize: 4
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
                  border: `1px solid ${runResults.syntax_valid === false ? 'rgba(244,63,94,0.4)' : 'var(--color-border-subtle)'}`,
                  fontFamily: 'var(--p-font-mono)',
                  fontSize: '12px'
                }}>
                  {/* Syntax error */}
                  {runResults.syntax_valid === false && (
                    <div style={{ padding: '8px 12px', marginBottom: 10, borderRadius: 'var(--radius-sm)', background: 'var(--color-danger-muted)', color: 'var(--color-danger)', fontWeight: 700 }}>
                      ✗ Syntax Error — your code won&apos;t run. Fix the error and try again.
                    </div>
                  )}

                  {/* Per-test-case results */}
                  {runResults.results?.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {runResults.results.map((r, i) => (
                        <div key={i} style={{
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          border: `1px solid ${r.passed ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}`,
                          background: r.passed ? 'rgba(16,185,129,0.06)' : 'rgba(244,63,94,0.06)'
                        }}>
                          <div style={{ fontWeight: 700, marginBottom: 4, color: r.passed ? 'var(--color-success)' : 'var(--color-danger)' }}>
                            {r.passed ? '✓' : '✗'} Test Case {i + 1}
                          </div>
                          <div style={{ color: 'var(--color-fg-muted)' }}>
                            <span style={{ fontWeight: 600 }}>Input:</span>{' '}
                            {Object.entries(r.input || {}).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ')}
                          </div>
                          <div>
                            <span style={{ color: 'var(--color-fg-muted)', fontWeight: 600 }}>Expected:</span>{' '}
                            <span style={{ color: 'var(--color-success)' }}>{r.expected}</span>
                          </div>
                          <div>
                            <span style={{ color: 'var(--color-fg-muted)', fontWeight: 600 }}>Your Output:</span>{' '}
                            <span style={{ color: r.passed ? 'var(--color-success)' : 'var(--color-danger)' }}>{r.output || '(no output)'}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: 'var(--color-fg-muted)' }}>No test cases were executed.</div>
                  )}
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
    const codeScore = result.coding_score || 0
    const overallScore = result.interview_score || (mcqScore * 0.2 + descScore * 0.3 + codeScore * 0.5)

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
      </div>
    )
  }

  return null
}
