import React, { useEffect, useState } from 'react'
import { Sparkles, Brain, CheckCircle2, Circle, Loader2 } from 'lucide-react'

const DEFAULT_STAGES = [
  'Parsing document layout & multi-column OCR streams...',
  'Extracting technical skill entities & education credentials...',
  'Computing calendar tenure & employment timeline deduplication...',
  'Evaluating 20 canonical IT role taxonomy classifications...',
  'Running dense Sentence-BERT semantic cosine matching...',
  'Synthesizing 3-pillar intelligence & 4-milestone roadmap...'
]

export default function LoadingState({
  title = "Analyzing Candidate with AI...",
  subtitle = "Our multi-pillar intelligence engine is evaluating resume fit and technical readiness.",
  stages = DEFAULT_STAGES,
  stageDurationMs = 600,
  className = '',
  style = {}
}) {
  const [stageIdx, setStageIdx] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIdx((prev) => (prev < stages.length - 1 ? prev + 1 : prev))
    }, stageDurationMs)
    return () => clearInterval(timer)
  }, [stageDurationMs, stages.length])

  return (
    <div
      className={`card ${className}`}
      style={{
        padding: '36px 32px',
        textAlign: 'center',
        background: 'var(--color-bg-elevated)',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--color-border)',
        margin: '20px 0',
        boxShadow: 'var(--shadow-md)',
        maxWidth: 620,
        marginLeft: 'auto',
        marginRight: 'auto',
        ...style
      }}
    >
      {/* Animated Center Icon */}
      <div style={{
        width: 60,
        height: 60,
        borderRadius: 'var(--radius-full)',
        background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(124, 58, 237, 0.15))',
        color: 'var(--color-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 16px',
        border: '1px solid rgba(37, 99, 235, 0.3)',
        boxShadow: '0 0 24px rgba(37, 99, 235, 0.2)'
      }}>
        <Brain size={30} style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }} />
      </div>

      <h3 style={{
        fontSize: 'var(--p-text-lg)',
        fontWeight: 800,
        color: 'var(--color-fg)',
        marginBottom: 6,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8
      }}>
        <Sparkles size={18} style={{ color: 'var(--color-primary)' }} /> {title}
      </h3>
      <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '0 auto 24px', maxWidth: 440, lineHeight: 1.5 }}>
        {subtitle}
      </p>

      {/* Structured Pipeline Stage Stepper */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        textAlign: 'left',
        background: 'var(--color-bg-soft)',
        padding: '16px 20px',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border-subtle)'
      }}>
        {stages.map((stageText, idx) => {
          const isDone = idx < stageIdx
          const isCurrent = idx === stageIdx
          const isPending = idx > stageIdx

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                fontSize: '12px',
                color: isDone
                  ? 'var(--color-success)'
                  : isCurrent
                  ? 'var(--color-primary)'
                  : 'var(--color-fg-muted)',
                fontWeight: isCurrent ? 700 : 500,
                opacity: isPending ? 0.45 : 1,
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{ width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                {isDone && <CheckCircle2 size={16} style={{ color: 'var(--color-success)' }} />}
                {isCurrent && <Loader2 size={15} style={{ color: 'var(--color-primary)', animation: 'spin 1s linear infinite' }} />}
                {isPending && <Circle size={14} style={{ color: 'var(--color-fg-muted)' }} />}
              </div>
              <span style={{ flex: 1 }}>{stageText}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
