import React, { useState } from 'react'
import { Sparkles, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, ArrowRight, ShieldCheck } from 'lucide-react'

/**
 * AIInsightCard
 * Standardized, human-centered AI explainability component.
 * Displays: Match Score, Confidence, Key Strengths, Identified Gaps, Detailed Evidence, and Recommended Action.
 */
export default function AIInsightCard({
  title = 'AI Candidate Intelligence',
  score = 0,
  scoreLabel = 'Match Score',
  confidence = 'High',
  strengths = [],
  gaps = [],
  evidence = null,
  recommendedAction = 'Proceed with Interview Screening',
  onActionClick = null,
  actionText = 'Take Recommended Action',
  badgeText = 'AI Analyzed',
  variant = 'default'
}) {
  const [showEvidence, setShowEvidence] = useState(false)

  const numScore = Math.round(score)
  const isHigh = numScore >= 75
  const isMed = numScore >= 50 && numScore < 75

  const scoreColor = isHigh ? 'var(--color-success)' : isMed ? 'var(--color-warning)' : 'var(--color-danger)'
  const scoreBg = isHigh ? 'var(--color-success-muted)' : isMed ? 'var(--color-warning-muted)' : 'var(--color-danger-muted)'
  const scoreBorder = isHigh ? 'rgba(5, 150, 105, 0.3)' : isMed ? 'rgba(217, 119, 6, 0.3)' : 'rgba(225, 29, 72, 0.3)'

  return (
    <div
      className="card"
      style={{
        padding: '20px 24px',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)',
        background: 'var(--color-bg-elevated)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        boxShadow: 'var(--shadow-sm)',
        transition: 'all var(--duration-normal) var(--ease)'
      }}
    >
      {/* Card Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(124, 58, 237, 0.15))',
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(37, 99, 235, 0.25)'
          }}>
            <Sparkles size={18} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '15px', color: 'var(--color-fg)' }}>
              {title}
            </div>
            <div style={{ fontSize: '11.5px', color: 'var(--color-fg-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <ShieldCheck size={12} style={{ color: 'var(--color-success)' }} />
              Confidence: <strong style={{ color: 'var(--color-fg)' }}>{confidence}</strong>
              <span>•</span>
              <span style={{ fontSize: '10.5px', padding: '1px 6px', borderRadius: 'var(--radius-full)', background: 'var(--chip-bg)', color: 'var(--color-fg-secondary)' }}>
                {badgeText}
              </span>
            </div>
          </div>
        </div>

        {/* Score Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '6px 14px',
          borderRadius: 'var(--radius-full)',
          background: scoreBg,
          border: `1px solid ${scoreBorder}`
        }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '9.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-fg-muted)', letterSpacing: '0.04em' }}>
              {scoreLabel}
            </div>
            <div style={{ fontSize: '18px', fontWeight: 900, color: scoreColor, lineHeight: 1 }}>
              {numScore}%
            </div>
          </div>
        </div>
      </div>

      {/* Strengths & Gaps Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: 14,
        padding: '14px',
        borderRadius: 'var(--radius-md)',
        background: 'var(--color-bg-soft)',
        border: '1px solid var(--color-border-subtle)'
      }}>
        {/* Strengths */}
        <div>
          <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-success)', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <CheckCircle2 size={13} /> Key Strengths
          </div>
          {strengths.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: '12px', color: 'var(--color-fg-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {strengths.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)' }}>Solid foundational background verified.</div>
          )}
        </div>

        {/* Gaps */}
        <div>
          <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--color-warning)', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <AlertTriangle size={13} /> Opportunities to Develop
          </div>
          {gaps.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: '12px', color: 'var(--color-fg-secondary)', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {gaps.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)' }}>No critical skill or experience gaps detected.</div>
          )}
        </div>
      </div>

      {/* Expandable Evidence */}
      {evidence && (
        <div>
          <button
            type="button"
            onClick={() => setShowEvidence(!showEvidence)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-primary)',
              fontSize: '11.5px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: 0
            }}
          >
            {showEvidence ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showEvidence ? 'Hide Supporting Evidence' : 'View Supporting Evidence & Data Points'}
          </button>

          {showEvidence && (
            <div style={{
              marginTop: 10,
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-border-subtle)',
              fontSize: '12px',
              color: 'var(--color-fg-secondary)',
              lineHeight: 1.6
            }}>
              {evidence}
            </div>
          )}
        </div>
      )}

      {/* Recommended Next Action */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 10,
        paddingTop: 12,
        borderTop: '1px solid var(--color-border-subtle)'
      }}>
        <div style={{ fontSize: '12px', color: 'var(--color-fg-muted)' }}>
          <strong style={{ color: 'var(--color-fg)' }}>Next Action:</strong> {recommendedAction}
        </div>
        {onActionClick && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onActionClick}
            style={{ fontSize: '11.5px', padding: '6px 14px', fontWeight: 700 }}
          >
            {actionText} <ArrowRight size={13} />
          </button>
        )}
      </div>
    </div>
  )
}
