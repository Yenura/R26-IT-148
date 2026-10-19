import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Play, CheckCircle2, Code, FileText, Settings, Sparkles,
  ArrowRight, ArrowLeft, RefreshCw, Check, X, Terminal, Trophy, Briefcase
} from 'lucide-react'
import { getChartTheme, CHART_COLORS } from '../chartTheme'
import { c2Start, c2Submit, c2Jobs, c2RunCode } from '../api'
import { useAuth } from '../hooks/useAuth'
import useProctoring from '../hooks/useProctoring'
import PageHeader from '../components/PageHeader'
import ScoreMeter from '../components/ScoreMeter'
import ScoreBadge from '../components/ScoreBadge'
import ConfirmDialog from '../components/ConfirmDialog'

/* Mirrors backend `services/role_profiles.py`; used only as a fallback when
   GET /interview/jobs is unavailable. The backend is the source of truth and
   also tells us which languages the sandbox can actually execute. */
const ROLE_LANGUAGES = {
  "Software Engineer": ["Python","Java","C#","C++","JavaScript","Go"],
  "Backend Developer": ["Python","Java","C#","Node.js","Go","JavaScript"],
  "Frontend Developer": ["JavaScript","TypeScript"],
  "Full Stack Developer": ["JavaScript","TypeScript","Python","Java"],
  "Mobile App Developer": ["Kotlin","Swift","Dart","Java"],
  "Data Scientist": ["Python","R"],
  "Machine Learning Engineer": ["Python"],
  "Data Engineer": ["Python","SQL","Scala"],
  "DevOps Engineer": ["Python","Bash","Go"],
  "Database Administrator": ["SQL","Python"],
  "Blockchain Developer": ["Solidity","Rust","Go","Python"],
  "AI/NLP Engineer": ["Python"],
  "Embedded Systems Engineer": ["C","C++"],
  "QA/Test Automation Engineer": ["Python","Java","JavaScript"],
  "Site Reliability Engineer": ["Python","Go","Bash"],
}
const NON_CODING_ROLES = ["Business/Systems Analyst","Cloud Solutions Architect","Cybersecurity Analyst","Network Engineer","UI/UX Designer"]

/* Languages the interview can ask in: Python is executable in the sandbox,
   the rest are assessed with the non-executed formats below (predict-the-
   output / find-the-bug / complete-the-function), which is why a Frontend
   Developer is no longer asked Python.  Mirrors role_profiles.py. */
const FALLBACK_SUPPORTED = ["Python","Java","C++","JavaScript","Go","Rust"]

/* Only these are actually executed by the sandbox. */
const EXECUTABLE_LANGUAGES = ["Python"]

/* Coding formats graded WITHOUT executing the candidate's code. */
const NON_EXEC_FORMATS = ['Predict Output', 'Find the Bug', 'Complete Function']

export default function Interview() {
  useAuth('candidate')
  const ct = getChartTheme()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const jobRole = searchParams.get('role') || ''
  const jobSkills = searchParams.get('skills') || ''
  const numParam = (key, fallback) => {
    // parseInt can return NaN (missing) — but an explicit 0 is a valid
    // choice (e.g. zero coding questions) and must not fall to default.
    const v = parseInt(searchParams.get(key), 10)
    return Number.isNaN(v) ? fallback : v
  }

  /* ─────────────────────────────────────────────────────────────
     Bug fix #1 — Deduplicate repeated phrases in MCQ option text.
     Backend question generation sometimes emits options with the same
     phrase repeated 2-3 times. Strip consecutive duplicate n-grams so
     options render cleanly.
     ───────────────────────────────────────────────────────────── */
  const dedupeText = (text) => {
    if (!text) return text
    // Split into words, then collapse runs of 3+ identical consecutive words
    const words = text.split(/\s+/)
    const cleaned = []
    for (let i = 0; i < words.length; i++) {
      // If this word matches the previous 2 words, skip it (triple+ repeat)
      if (i >= 2 && words[i] === words[i - 1] && words[i] === words[i - 2]) continue
      // Also skip if it matches the word 3 back forming a 4-word repeat
      if (i >= 3 && words[i] === words[i - 3] && words[i - 1] === words[i - 2] && words[i - 2] === words[i - 3]) continue
      cleaned.push(words[i])
    }
    return cleaned.join(' ')
  }

  /* ─────────────────────────────────────────────────────────────
     Bug fix #3 — Track whether any coding answer was actually submitted.
     If no code was written for coding questions, force codeScore to 0
     regardless of what the backend returns.
     ───────────────────────────────────────────────────────────── */
  const anyCodingSubmitted = () => {
    const codingQuestions = session?.questions?.filter((q) => q.question_type === 'Coding') || []
    return codingQuestions.some((q) => {
      const a = answers[q.id]
      return a != null && String(a).trim().length > 0
    })
  }
  const jobCount = numParam('count', 10)
  const jobMcqCount = numParam('mcqCount', 4)
  const jobDescCount = numParam('descCount', 3)
  const jobLevel = searchParams.get('level') || 'Mid-Level'
  const jobMcqTime = parseInt(searchParams.get('mcqTime'), 10) || 60
  const jobDescTime = parseInt(searchParams.get('descTime'), 10) || 300
  const jobCodingTime = parseInt(searchParams.get('codingTime'), 10) || 600
  const jobTotalTime = parseInt(searchParams.get('totalTime'), 10) || 60
  const jobDescription = searchParams.get('description') || ''
  const jobId = searchParams.get('jobId') || ''
  const isPracticeMode = !jobRole

  const [step, setStep] = useState('setup')
  const [roles, setRoles] = useState({})
  const [roleProfiles, setRoleProfiles] = useState({})
  const [selectedRole, setSelectedRole] = useState(jobRole)

  /* Coding capability + offerable languages come from the backend, which knows
     what we can actually ask in (executed, or via a non-executed format).
     Fall back to the local mirror if the request failed. */
  const languagesFor = (role) => {
    const fromServer = roleProfiles[role]?.languages
    if (Array.isArray(fromServer) && fromServer.length) return fromServer
    const declared = (ROLE_LANGUAGES[role] || []).filter((l) => FALLBACK_SUPPORTED.includes(l))
    return declared
  }
  const isCodingRole = (role) => {
    if (roleProfiles[role]) return !!roleProfiles[role].is_coding
    return !!ROLE_LANGUAGES[role] && !NON_CODING_ROLES.includes(role)
  }
  const defaultLanguage = (role) => languagesFor(role)[0] || 'Python'

  const isNonCodingRole = !isCodingRole(selectedRole)
  const effectiveCodingCount = isNonCodingRole ? 0 : numParam('codingCount', 3)
  const [selectedLevel, setSelectedLevel] = useState(jobLevel)
  const [selectedLanguage, setSelectedLanguage] = useState('Auto')
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

  // Proctoring: only active for job interviews (not practice mode)
  const proctoringActive = !isPracticeMode && step === 'quiz'
  const proctoring = useProctoring(proctoringActive)

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

  // Start proctoring when entering quiz stage (job interviews only)
  useEffect(() => {
    if (proctoringActive) {
      proctoring.start()
    }
    return () => {
      if (!proctoringActive) proctoring.stop()
    }
  }, [proctoringActive])

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
          toast.error('Time is up! Moving to next question...')
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

  // Auto-advance when timer hits 0
  useEffect(() => {
    if (step !== 'quiz' || !session || timeLeft !== 0) return
    const timer = setTimeout(() => {
      if (currentQ < session.questions.length - 1) {
        setCurrentQ((q) => q + 1)
      } else {
        handleSubmit()
      }
    }, 1500)
    return () => clearTimeout(timer)
  }, [timeLeft, step, currentQ, session])

  const loadRoles = async () => {
    try {
      const r = await c2Jobs()
      setRoles(r?.data?.jobs || {})
      setRoleProfiles(r?.data?.role_profiles || {})
    } catch {
      toast.error('Failed to load roles')
    }
  }

  const startInterview = async () => {
    if (!selectedRole) return toast.error('Please select a target role')
    setBusy(true)
    try {
      let skills = jobRole && jobSkills
        ? jobSkills.split(',').filter(Boolean)
        : (Object.keys(roles).length > 0 ? (roles[selectedRole] || []).slice(0, 5) : [])
      // If practice mode and user chose a language for coding role, prioritize it
      if (isPracticeMode && selectedLanguage !== 'Auto' && isCodingRole(selectedRole)) {
        skills = [selectedLanguage, ...skills.filter((s) => s.toLowerCase() !== selectedLanguage.toLowerCase())]
      }
      const codingLanguage = selectedLanguage === 'Auto' ? defaultLanguage(selectedRole) : selectedLanguage
      const r = await c2Start({
        candidate_id: localStorage.getItem('recruitai.user_id') || 'candidate-user',
        job_role: selectedRole,
        job_level: selectedLevel,
        required_skills: skills,
        num_questions: numQuestions,
        mcq_count: jobMcqCount,
        desc_count: jobDescCount,
        coding_count: effectiveCodingCount,
        coding_language: codingLanguage,
        mcq_time: jobMcqTime,
        desc_time: jobDescTime,
        coding_time: jobCodingTime,
        total_time: jobTotalTime,
        job_description: jobDescription,
        job_id: jobId,
        is_practice: isPracticeMode,
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
      const r = await c2RunCode({ code_text: code, test_cases: q.test_cases || [], language: q.language || defaultLanguage(selectedRole) })
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
            job_id: jobId || session.job_id || '',
            answers: questions.map((q) => {
              const a = answers[q.id]
              if (q.question_type === 'MCQ') return { question_id: q.id, selected_option: a != null ? parseInt(a) : null }
              if (q.question_type === 'Descriptive') return { question_id: q.id, answer_text: a || '' }
              if (q.question_type === 'Coding') {
                // Non-executed formats carry a text answer or an option, never code.
                if (q.format === 'Find the Bug') return { question_id: q.id, selected_option: a != null ? parseInt(a) : null }
                if (q.format === 'Predict Output' || q.format === 'Complete Function') return { question_id: q.id, answer_text: a || '' }
                return { question_id: q.id, code_text: a || '', language: q.language || defaultLanguage(selectedRole) }
              }
              return { question_id: q.id, answer_text: a || '' }
            }),
          }
          // Attach proctoring data for job interviews
          if (!isPracticeMode) {
            proctoring.stop()
            payload.proctoring = proctoring.getProctoringData()
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
  if (step === 'interview' && !q) {
    return (
      <div style={{ padding: 60, textAlign: 'center' }}>
        <p>Loading question...</p>
      </div>
    )
  }
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
    // JOB INTERVIEW: Locked settings from company — candidate confirms and starts
    if (!isPracticeMode) {
      return (
        <div className="fade-in" style={{ maxWidth: 760, margin: '0 auto' }}>
          <PageHeader
            badge="Company-Assigned Assessment"
            title={`Technical Assessment · ${jobRole}`}
            description="This interview is configured by the employer. Settings below are locked and cannot be changed."
            icon={Code}
          />

          <div className="card glass-card" style={{ padding: 'var(--p-space-6)' }}>
            {/* Locked company settings summary */}
            <div style={{ padding: 16, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)', marginBottom: 20 }}>
              <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, marginBottom: 12, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Settings size={16} style={{ color: 'var(--color-primary)' }} /> Employer Interview Configuration
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Target Role</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{selectedRole}</div>
                </div>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Job Level</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{selectedLevel}</div>
                </div>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Questions</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{numQuestions}</div>
                </div>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Duration</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)', marginTop: 2 }}>{jobTotalTime} minutes</div>
                </div>
              </div>

              {/* Per-type breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginTop: 12 }}>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>MCQ</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-primary)', marginTop: 2 }}>{jobMcqCount} questions</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>{jobMcqTime}s each</div>
                </div>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Descriptive</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-info)', marginTop: 2 }}>{jobDescCount} questions</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>{jobDescTime}s each</div>
                </div>
                <div style={{ padding: '8px 12px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Coding</div>
                  <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: isNonCodingRole ? 'var(--color-fg-muted)' : 'var(--color-purple)', marginTop: 2 }}>{effectiveCodingCount} questions</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                  {isNonCodingRole ? 'N/A for this role' : jobCodingTime + 's each'}
                </div>
                </div>
              </div>
            </div>

            {/* Skills required */}
            {jobSkills && (
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6 }}>Required Skills</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                   {[...new Set(jobSkills.split(',').filter(Boolean))].map((s, i) => (
                     <span key={`${s}-${i}`} className="chip" style={{ fontSize: '11px', padding: '2px 8px' }}>{s.trim()}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Proctoring notice */}
            <div style={{ padding: 12, background: 'var(--color-purple-muted)', border: '1px solid var(--color-purple-muted)', borderRadius: 'var(--radius-sm)', marginBottom: 20 }}>
              <div style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-purple)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Settings size={13} /> Live Proctoring Active
              </div>
              <p style={{ fontSize: '11px', color: 'var(--color-fg-secondary)', margin: '4px 0 0 0' }}>
                This interview is monitored for integrity. Your webcam, browser activity, and typing patterns are tracked. Do not switch tabs or leave the screen.
              </p>
            </div>

            <button
              className="btn btn-primary"
              onClick={startInterview}
              disabled={busy || !selectedRole}
              style={{ width: '100%', padding: '12px 20px', fontSize: 'var(--p-text-base)', fontWeight: 700 }}
            >
              <Play size={18} /> {busy ? 'Generating Assessment...' : 'Start Technical Interview'}
            </button>
          </div>
        </div>
      )
    }

    // PRACTICE INTERVIEW: Full editable setup
    return (
      <div className="fade-in" style={{ maxWidth: 760, margin: '0 auto' }}>
        <PageHeader
          badge="Component 2 AI Engine"
          title={isPracticeMode ? 'AI Technical Interview Sandbox' : `Technical Assessment · ${jobRole}`}
          description="Simulate real-world technical evaluations with automated MCQs, semantic theory scoring, and live Python test execution."
          icon={Code}
        />

        <div className="card glass-card" style={{ padding: 'var(--p-space-6)' }}>
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '12px', marginTop: 0 }}>Target Technical Role *</label>
            <select
              value={selectedRole}
              onChange={(e) => { setSelectedRole(e.target.value); setSelectedLanguage('Auto'); }}
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

          {selectedRole && isCodingRole(selectedRole) && (
            <div style={{ marginBottom: 20 }}>
              {languagesFor(selectedRole).length === 0 ? (
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                  This role has no coding section: we have no questions in a language it
                  declares, so that weight goes to the written questions instead.
                </div>
              ) : languagesFor(selectedRole).length > 1 ? (
                <>
                  <label style={{ fontSize: '12px', marginTop: 0 }}>Programming Language (for coding questions)</label>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    style={{ fontSize: 'var(--p-text-base)', padding: '10px 12px' }}
                  >
                    <option value="Auto">Auto (from role)</option>
                    {languagesFor(selectedRole).map((lang) => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                  <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', marginTop: 4 }}>
                    {(() => {
                      const lang = selectedLanguage === 'Auto' ? defaultLanguage(selectedRole) : selectedLanguage
                      return EXECUTABLE_LANGUAGES.includes(lang)
                        ? `Coding questions in ${lang} are run and auto-graded.`
                        : `Coding questions in ${lang} are auto-graded without running code.`
                    })()}
                  </div>
                </>
              ) : (
                <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                  Coding questions are in <strong>{defaultLanguage(selectedRole)}</strong>
                  {EXECUTABLE_LANGUAGES.includes(defaultLanguage(selectedRole))
                    ? ' and are run and auto-graded.'
                    : ' and are auto-graded without running code.'}
                </div>
              )}
            </div>
          )}

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
              border: `1px solid ${timeLeft <= 30 ? 'var(--color-danger-muted)' : 'var(--color-border-subtle)'}`,
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
        <div className="card glass-card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)' }}>
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
                      {typeof opt === 'string' ? dedupeText(opt) : dedupeText(opt.text)}
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

          {/* Coding, non-executed formats: no Run button, graded from an answer
              key (find-the-bug by option, the others by text). */}
          {q.question_type === 'Coding' && NON_EXEC_FORMATS.includes(q.format) && (
            <div>
              <div style={{
                marginBottom: 14, padding: 14, background: 'var(--color-bg)',
                borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)',
                fontFamily: 'var(--p-font-mono)', fontSize: '12.5px', lineHeight: 1.6,
                whiteSpace: 'pre', overflowX: 'auto', color: 'var(--color-fg)'
              }}>
                {q.code || ''}
              </div>

              {q.format === 'Find the Bug' ? (
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
                          fontFamily: 'var(--p-font-mono)'
                        }}
                      >
                        <div style={{
                          width: 24, height: 24, borderRadius: '50%',
                          border: `2px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          color: 'var(--color-primary)', fontSize: '12px', fontWeight: 800, flexShrink: 0
                        }}>
                          {String.fromCharCode(65 + idx)}
                        </div>
                        <span style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', whiteSpace: 'pre' }}>
                          {typeof opt === 'string' ? opt : opt.text}
                        </span>
                      </button>
                    )
                  })}
                </div>
              ) : (
                <input
                  type="text"
                  placeholder={q.format === 'Complete Function' ? 'Type the missing line...' : 'What does this code print?'}
                  value={answers[q.id] || ''}
                  onChange={(e) => answerQuestion(q.id, e.target.value)}
                  spellCheck={false}
                  autoComplete="off"
                  style={{ width: '100%', fontFamily: 'var(--p-font-mono)', fontSize: 13 }}
                />
              )}

              <div style={{ marginTop: 10, fontSize: 12, color: 'var(--color-fg-muted)' }}>
                Graded without running code.
              </div>
            </div>
          )}

          {/* Coding Sandbox Mode */}
          {q.question_type === 'Coding' && !NON_EXEC_FORMATS.includes(q.format) && (
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
                  placeholder={`# Write your ${q.language || defaultLanguage(selectedRole)} solution here...\ndef solution():\n    pass`}
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
                  border: `1px solid ${runResults.syntax_valid === false ? 'var(--color-danger-muted)' : 'var(--color-border-subtle)'}`,
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
                          border: `1px solid ${r.passed ? 'var(--color-success-muted)' : 'var(--color-danger-muted)'}`,
                          background: r.passed ? 'var(--color-success-muted)' : 'var(--color-danger-muted)'
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
    let codeScore = result.coding_score || 0
    // Bug fix #3: if no coding answer was submitted, force code score to 0
    if (!anyCodingSubmitted()) codeScore = 0
    // Recalculate overall score locally so backend's incorrect baseline doesn't leak through
    const overallScore = mcqScore * 0.25 + descScore * 0.35 + codeScore * 0.40

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
        <div className="card glass-card" style={{ padding: 'var(--p-space-6)', marginBottom: 'var(--p-space-5)', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-fg-muted)', letterSpacing: '0.08em', marginBottom: 6 }}>
            Blended Interview Score (P_int)
          </div>
          <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--color-primary)', lineHeight: 1, fontFamily: 'var(--p-font-mono)', marginBottom: 8 }}>
            {overallScore.toFixed(1)}%
          </div>
          <div style={{ display: 'inline-flex', marginBottom: 16 }}>
            <ScoreBadge score={overallScore} />
          </div>

          {result?.weights_used && (
            <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)', marginBottom: 18, fontFamily: 'var(--p-font-mono)' }}>
              Weighting Formula: {((result.weights_used.mcq || 0) * 100).toFixed(0)}% MCQ + {((result.weights_used.descriptive || 0) * 100).toFixed(0)}% Theory + {((result.weights_used.coding || 0) * 100).toFixed(0)}% Coding
            </div>
          )}

          <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', textAlign: 'left' }}>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>Weight: {((result?.weights_used?.mcq ?? 0.25) * 100).toFixed(0)}%</span>
                <span className="badge badge-subtle" style={{ fontSize: '10px' }}>MCQ</span>
              </div>
              <ScoreMeter score={mcqScore} label="MCQ Accuracy (P_mcq)" size="sm" />
            </div>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>Weight: {((result?.weights_used?.descriptive ?? 0.35) * 100).toFixed(0)}%</span>
                <span className="badge badge-subtle" style={{ fontSize: '10px' }}>Theory</span>
              </div>
              <ScoreMeter score={descScore} label="Theory Cosine (P_desc)" size="sm" />
            </div>
            <div style={{ padding: 14, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>Weight: {((result?.weights_used?.coding ?? 0.40) * 100).toFixed(0)}%</span>
                <span className="badge badge-subtle" style={{ fontSize: '10px' }}>Code</span>
              </div>
              <ScoreMeter score={codeScore} label="Coding Sandbox (P_code)" size="sm" />
            </div>
          </div>
        </div>

        {/* Section Score Breakdown — Horizontal Bars (Apple-style) */}
        <div className="card glass-card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
            Section Score Breakdown
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {chartData.map((entry, index) => {
              const color = index === 0 ? CHART_COLORS.accent : index === 1 ? CHART_COLORS.info : CHART_COLORS.purple
              return (
                <div key={entry.name} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 600, color: 'var(--color-fg)' }}>{entry.name}</span>
                    <span style={{ fontSize: 'var(--p-text-sm)', fontWeight: 800, color: color }}>{entry.score.toFixed(0)}%</span>
                  </div>
                  <div style={{ width: '100%', height: 8, background: 'var(--color-border-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${Math.max(entry.score, 0)}%`,
                        height: '100%',
                        background: `linear-gradient(90deg, ${color}, ${color})`,
                        borderRadius: 'var(--radius-full)',
                        transition: 'width 0.6s ease-out',
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Next Step Action Hub */}
        <div className="card glass-card" style={{ padding: 'var(--p-space-5)', textAlign: 'center', background: 'var(--color-bg-elevated)' }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: 'var(--p-text-base)', fontWeight: 700 }}>
            Next Steps in Your Application Process
          </h3>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '0 0 16px 0' }}>
            Your 3 category interview marks have been pushed to the company recruiter pipeline and saved to your profile.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/candidate/skill-gap${jobId ? `?jobId=${jobId}` : ''}`)}
            >
              <Sparkles size={15} /> View Skill Gap & Composite Mark
            </button>
            {jobId ? (
              <button
                className="btn btn-ghost"
                onClick={() => navigate(`/candidate/jobs/${jobId}`)}
              >
                <Briefcase size={15} /> Return to Job Posting
              </button>
            ) : (
              <button
                className="btn btn-ghost"
                onClick={() => navigate('/candidate/jobs')}
              >
                <Briefcase size={15} /> Browse Open Jobs
              </button>
            )}
            <button
              className="btn btn-ghost"
              onClick={() => navigate(`/pipeline/cv-match${jobId ? `?jobId=${jobId}` : ''}`)}
            >
              <FileText size={15} /> Run Role CV Match
            </button>
          </div>
        </div>
      </div>
    )
  }

  return null
}
