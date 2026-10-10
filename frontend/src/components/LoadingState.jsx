import { useEffect, useState } from 'react'
import { Sparkles, Brain, Loader2 } from 'lucide-react'

const STAGES = [
  'Reading resume document...',
  'Extracting technical skills & education...',
  'Analyzing work experience timeline...',
  'Classifying 20 canonical IT job roles...',
  'Calculating multi-criteria screening score...',
  'Evaluating skill gap priorities & career paths...'
]

export default function LoadingState({ title = "Analyzing Resume with AI...", stageDurationMs = 700 }) {
  const [stageIdx, setStageIdx] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIdx((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev))
    }, stageDurationMs)
    return () => clearInterval(timer)
  }, [stageDurationMs])

  return (
    <div style={{ padding: 48, textAlign: 'center', background: 'var(--color-bg-elevated)', borderRadius: 14, border: '1px solid var(--color-border)', margin: '20px 0' }}>
      <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'var(--color-primary-muted)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
        <Brain size={32} className="spin" />
      </div>
      <h3 style={{ fontSize: 18, fontWeight: 800, color: 'var(--color-fg)', marginBottom: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
        <Sparkles size={18} style={{ color: 'var(--color-primary)' }} /> {title}
      </h3>
      <div style={{ fontSize: 14, color: 'var(--color-primary)', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
        <Loader2 size={16} className="spin" /> {STAGES[stageIdx]}
      </div>
    </div>
  )
}
