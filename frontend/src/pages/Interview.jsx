import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Play, CheckCircle, Code, FileText, Settings } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { getChartTheme } from '../chartTheme'
import { c2Start, c2Submit, c2Jobs, c2RunCode } from '../api'
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
  const [confirm, setConfirm] = useState({ open: false, title: '', message: '', action: null })

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'candidate') { navigate('/login/candidate'); return }
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
    } catch { toast.error('Failed to load roles') }
  }

  const startInterview = async () => {
    if (!selectedRole) return toast.error('Select a role')
    setBusy(true)
    try {
      const skills = jobRole && jobSkills
        ? jobSkills.split(',').filter(Boolean)
        : (Object.keys(roles).length > 0 ? (roles[selectedRole] || []).slice(0, 5) : [])
      const r = await c2Start({
        candidate_id: localStorage.getItem('recruitai.user_id'),
        job_role: selectedRole,
        required_skills: skills,
        num_questions: numQuestions,
      })
      setSession(r.data)
      setCurrentQ(0)
      setAnswers({})
      setStep('quiz')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to start')
    } finally { setBusy(false) }
  }

  const answerQuestion = (questionId, value) => {
    setAnswers((a) => ({ ...a, [questionId]: value }))
    setRunResults(null)
  }

  const runCode = async () => {
    if (!q || q.question_type !== 'Coding') return
    const code = answers[q.id] || ''
    if (!code.trim()) return toast.error('Write some code first')
    setRunning(true)
    setRunResults(null)
    try {
      const r = await c2RunCode({ code_text: code, test_cases: q.test_cases || [] })
      setRunResults(r.data)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Run failed')
    } finally { setRunning(false) }
  }

  const submitInterview = async () => {
    setConfirm({
      open: true,
      title: 'Submit interview?',
      message: 'You cannot change answers after submission.',
      action: async () => {
        setBusy(true)
        try {
          const questions = session.questions || []
          const payload = {
            candidate_id: localStorage.getItem('recruitai.user_id'),
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
          toast.success('Interview complete!')
        } catch (err) {
          toast.error(err?.response?.data?.detail || 'Submit failed')
        } finally { setBusy(false) }
      }
    })
  }

  const questions = session?.questions || []
  const q = questions[currentQ]
  const progress = questions.length > 0 ? ((currentQ + 1) / questions.length) * 100 : 0

  const typeIcon = (t) => t === 'MCQ' ? <CheckCircle size={14} /> : t === 'Coding' ? <Code size={14} /> : <FileText size={14} />

  // SETUP
  if (step === 'setup') {
    return (
      <div className="fade-in" style={{ padding: 28, maxWidth: 700, margin: '0 auto' }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>
          {isPracticeMode ? 'Practice Interview' : `Interview — ${jobRole}`}
        </h1>
        <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>
          {isPracticeMode
            ? 'AI-powered interview with MCQ, Descriptive, and Coding questions'
            : `Answer questions for the ${jobRole} position`
          }
        </p>

        <div className="card" style={{ padding: 24 }}>
          {isPracticeMode && (
            <>
              <h3 style={{ marginBottom: 16 }}>Select Role</h3>
              <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)} style={{ width: '100%', padding: '10px 12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, marginBottom: 16 }}>
                <option value="">Choose a role...</option>
                {Object.keys(roles).sort().map((r) => <option key={r} value={r}>{r}</option>)}
              </select>

              {selectedRole && roles[selectedRole] && (
                <div style={{ marginBottom: 16 }}>
                  <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>Skills tested:</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {roles[selectedRole].slice(0, 8).map((s) => <span key={s} className="chip" style={{ fontSize: 11 }}>{s}</span>)}
                  </div>
                </div>
              )}
            </>
          )}

          {!isPracticeMode && jobSkills && (
            <div style={{ marginBottom: 16 }}>
              <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>Skills tested:</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {jobSkills.split(',').filter(Boolean).map((s) => <span key={s} className="chip" style={{ fontSize: 11 }}>{s}</span>)}
              </div>
            </div>
          )}

          <div style={{ marginBottom: 16 }}>
            <label className="muted" style={{ fontSize: 12, display: 'block', marginBottom: 6 }}>
              <Settings size={12} style={{ verticalAlign: -1, marginRight: 4 }} />
              Number of Questions
            </label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {[5, 10, 15, 20].map(n => (
                <button key={n} className={`btn btn-sm ${numQuestions === n ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setNumQuestions(n)} type="button">
                  {n}
                </button>
              ))}
              <input type="number" min={3} max={30} value={numQuestions}
                onChange={e => setNumQuestions(Math.max(3, Math.min(30, Number(e.target.value) || 10)))}
                style={{ width: 60, padding: '6px 8px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: 13, textAlign: 'center' }}
              />
            </div>
          </div>

          <button className="btn" onClick={startInterview} disabled={busy || (!isPracticeMode ? !selectedRole : !selectedRole)} style={{ width: '100%' }}>
            <Play size={16} /> {busy ? 'Starting...' : 'Start Interview'}
          </button>
        </div>
      </div>
    )
  }

  // QUIZ
  if (step === 'quiz' && q) {
    return (
      <div className="fade-in" style={{ padding: 28, maxWidth: 700, margin: '0 auto' }}>
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>{selectedRole} Interview</span>
            <span className="muted" style={{ fontSize: 13 }}>Question {currentQ + 1} of {questions.length}</span>
          </div>
          <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${progress}%`, background: 'var(--accent)', borderRadius: 2, transition: 'width 0.3s' }} />
          </div>
        </div>

        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
            <span className="chip" style={{ fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}>
              {typeIcon(q.question_type)} {q.question_type}
            </span>
            {q.difficulty && <span className="chip" style={{ fontSize: 11 }}>{q.difficulty}</span>}
          </div>

          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20, lineHeight: 1.5 }}>{q.question_text}</h3>

          {q.question_type === 'MCQ' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {(q.options || []).map((opt, i) => (
                <label key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', background: answers[q.id] === String(i) ? 'var(--accent)15' : 'var(--input-bg)', border: `1px solid ${answers[q.id] === String(i) ? 'var(--accent)' : 'var(--border)'}`, borderRadius: 8, cursor: 'pointer', transition: 'all 0.15s' }}>
                  <input type="radio" name={q.id} value={i} checked={answers[q.id] === String(i)} onChange={() => answerQuestion(q.id, String(i))} style={{ accentColor: 'var(--accent)' }} />
                  <span style={{ fontSize: 14 }}>{opt.text || opt}</span>
                </label>
              ))}
            </div>
          )}

          {q.question_type === 'Descriptive' && (
            <textarea
              value={answers[q.id] || ''}
              onChange={(e) => answerQuestion(q.id, e.target.value)}
              placeholder="Write your answer..."
              rows={6}
              style={{ width: '100%', padding: '12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 14, resize: 'vertical' }}
            />
          )}

          {q.question_type === 'Coding' && (
            <>
              <textarea
                value={answers[q.id] || ''}
                onChange={(e) => answerQuestion(q.id, e.target.value)}
                placeholder="Write your code..."
                rows={8}
                style={{ width: '100%', padding: '12px', background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: 13, fontFamily: 'monospace', resize: 'vertical' }}
              />
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <button className="btn btn-ghost btn-sm" onClick={runCode} disabled={running} type="button">
                  {running ? 'Running...' : 'Run Code'}
                </button>
              </div>
              {runResults && (
                <div style={{ marginTop: 12, padding: 12, background: 'var(--input-bg)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 13 }}>
                  {!runResults.syntax_valid && (
                    <div style={{ color: 'var(--danger)', fontWeight: 600, marginBottom: 6 }}>Syntax Error</div>
                  )}
                  {runResults.results?.length === 0 && runResults.syntax_valid && (
                    <div className="muted">No testable cases for this question.</div>
                  )}
                  {runResults.results?.map((r, i) => (
                    <div key={i} style={{ marginBottom: 8, padding: '8px 10px', background: r.passed ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)', border: `1px solid ${r.passed ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`, borderRadius: 6 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600 }}>Test {i + 1}</span>
                        <span style={{ color: r.passed ? 'var(--accent-2)' : 'var(--danger)', fontWeight: 600 }}>{r.passed ? 'PASS' : 'FAIL'}</span>
                      </div>
                      <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-muted)' }}>Input: {JSON.stringify(r.input)}</div>
                      <div style={{ fontFamily: 'monospace', fontSize: 12 }}>Expected: {r.expected}</div>
                      <div style={{ fontFamily: 'monospace', fontSize: 12 }}>Got: {r.output || '(no output)'}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
            <button className="btn btn-ghost" onClick={() => setCurrentQ((c) => Math.max(0, c - 1))} disabled={currentQ === 0}>Previous</button>
            {currentQ < questions.length - 1 ? (
              <button className="btn" onClick={() => setCurrentQ((c) => c + 1)}>Next</button>
            ) : (
              <button className="btn btn-success" onClick={submitInterview} disabled={busy}>{busy ? 'Submitting...' : 'Submit Interview'}</button>
            )}
          </div>
          <ConfirmDialog
            open={confirm.open}
            title={confirm.title}
            message={confirm.message}
            onConfirm={async () => { await confirm.action(); setConfirm({ ...confirm, open: false }) }}
            onCancel={() => setConfirm({ ...confirm, open: false })}
          />
        </div>
      </div>
    )
  }

  // RESULT
  if (step === 'result' && result) {
    const chartData = [
      { name: 'MCQ', value: result.mcq_score || 0, fill: 'var(--accent)' },
      { name: 'Descriptive', value: result.descriptive_score || 0, fill: 'var(--accent-2)' },
      { name: 'Coding', value: result.coding_score || 0, fill: 'var(--warn)' },
    ]

    return (
      <div className="fade-in" style={{ padding: 28, maxWidth: 700, margin: '0 auto' }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>Interview Results</h1>
        <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>{selectedRole} — {result.grade}</p>

        <div className="grid grid-3" style={{ marginBottom: 20 }}>
          <div className="stat">
            <div className="stat-label">Overall Score</div>
            <div className="stat-value" style={{ color: 'var(--accent)' }}>{result.interview_score?.toFixed(1)}%</div>
          </div>
          <div className="stat">
            <div className="stat-label">Grade</div>
            <div className="stat-value" style={{ color: result.interview_score >= 60 ? 'var(--accent-2)' : 'var(--danger)' }}>{result.grade}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Questions</div>
            <div className="stat-value">{(result.mcq_total || 0) + (result.descriptive_total || 0) + (result.coding_total || 0)}</div>
          </div>
        </div>

        <div className="card" style={{ padding: 20, marginBottom: 20 }}>
          <h3 style={{ marginBottom: 12 }}>Score Breakdown</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ ...ct.axisTick }} axisLine={false} tickLine={false} />
              <YAxis tick={{ ...ct.axisTickLg }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={ct.tooltip} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={40}>
                {chartData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {result.weak_topics && result.weak_topics.length > 0 && (
          <div className="card" style={{ padding: 20, marginBottom: 20 }}>
            <h3 style={{ marginBottom: 8 }}>Weak Areas</h3>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {result.weak_topics.map((t, i) => <span key={i} className="chip" style={{ fontSize: 11, borderColor: 'var(--danger)', color: 'var(--danger)' }}>{t}</span>)}
            </div>
          </div>
        )}

        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn" onClick={() => { setStep('setup'); setResult(null); setSession(null); }}>Practice Again</button>
          {jobRole && <button className="btn btn-ghost" onClick={() => navigate(-1)}>Back to Job</button>}
        </div>
      </div>
    )
  }

  return null
}
