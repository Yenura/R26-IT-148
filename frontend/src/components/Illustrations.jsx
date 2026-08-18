import { useEffect, useRef } from 'react'

export function HeroIllustration() {
  const svgRef = useRef(null)

  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return
    // Animate the pipeline dots
    const dots = svg.querySelectorAll('.pipeline-dot')
    dots.forEach((dot, i) => {
      dot.style.animationDelay = `${i * 0.3}s`
    })
  }, [])

  return (
    <svg
      ref={svgRef}
      viewBox="0 0 400 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%' }}
    >
      {/* Background grid pattern */}
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(59,130,246,0.06)" strokeWidth="1"/>
        </pattern>
        <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8"/>
          <stop offset="50%" stopColor="#10b981" stopOpacity="0.8"/>
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.8"/>
        </linearGradient>
        <linearGradient id="docGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#1e293b"/>
          <stop offset="100%" stopColor="#0f172a"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <rect width="400" height="400" fill="url(#grid)" rx="16"/>

      {/* Animated pipeline path */}
      <path
        d="M 60 120 C 120 120, 140 200, 200 200 C 260 200, 280 120, 340 120"
        stroke="url(#flowGrad)"
        strokeWidth="2"
        strokeDasharray="8 4"
        fill="none"
        opacity="0.5"
      >
        <animate
          attributeName="stroke-dashoffset"
          from="0"
          to="-24"
          dur="2s"
          repeatCount="indefinite"
        />
      </path>

      {/* Resume document */}
      <g className="pipeline-dot" style={{ animation: 'float 3s ease-in-out infinite' }}>
        <rect x="30" y="80" width="60" height="80" rx="6" fill="url(#docGrad)" stroke="rgba(59,130,246,0.3)" strokeWidth="1"/>
        <rect x="42" y="95" width="36" height="3" rx="1.5" fill="rgba(59,130,246,0.5)"/>
        <rect x="42" y="104" width="28" height="3" rx="1.5" fill="rgba(59,130,246,0.3)"/>
        <rect x="42" y="113" width="32" height="3" rx="1.5" fill="rgba(59,130,246,0.3)"/>
        <rect x="42" y="122" width="20" height="3" rx="1.5" fill="rgba(59,130,246,0.2)"/>
        <rect x="42" y="131" width="24" height="3" rx="1.5" fill="rgba(59,130,246,0.2)"/>
        <text x="60" y="72" textAnchor="middle" fill="rgba(59,130,246,0.7)" fontSize="10" fontWeight="600">Resume</text>
      </g>

      {/* AI Brain node */}
      <g className="pipeline-dot" style={{ animation: 'float 3s ease-in-out infinite 0.5s' }}>
        <circle cx="200" cy="200" r="40" fill="rgba(16,185,129,0.08)" stroke="rgba(16,185,129,0.3)" strokeWidth="1.5">
          <animate attributeName="r" values="38;42;38" dur="3s" repeatCount="indefinite"/>
        </circle>
        <circle cx="200" cy="200" r="24" fill="rgba(16,185,129,0.12)" stroke="rgba(16,185,129,0.4)" strokeWidth="1"/>
        {/* Brain icon */}
        <path d="M192 192 C192 188, 196 184, 200 184 C204 184, 208 188, 208 192 C212 192, 216 196, 216 200 C216 204, 212 208, 208 208 C208 212, 204 216, 200 216 C196 216, 192 212, 192 208 C188 208, 184 204, 184 200 C184 196, 188 192, 192 192Z" fill="rgba(16,185,129,0.6)" stroke="rgba(16,185,129,0.8)" strokeWidth="1"/>
        <text x="200" y="256" textAnchor="middle" fill="rgba(16,185,129,0.7)" fontSize="10" fontWeight="600">AI Analysis</text>
      </g>

      {/* Interview node */}
      <g className="pipeline-dot" style={{ animation: 'float 3s ease-in-out infinite 1s' }}>
        <rect x="300" y="80" width="70" height="80" rx="8" fill="url(#docGrad)" stroke="rgba(139,92,246,0.3)" strokeWidth="1.5"/>
        {/* Chat bubbles */}
        <rect x="312" y="95" width="30" height="12" rx="6" fill="rgba(139,92,246,0.2)" stroke="rgba(139,92,246,0.3)" strokeWidth="0.5"/>
        <rect x="328" y="112" width="30" height="12" rx="6" fill="rgba(59,130,246,0.2)" stroke="rgba(59,130,246,0.3)" strokeWidth="0.5"/>
        <rect x="312" y="129" width="24" height="12" rx="6" fill="rgba(139,92,246,0.2)" stroke="rgba(139,92,246,0.3)" strokeWidth="0.5"/>
        <text x="335" y="72" textAnchor="middle" fill="rgba(139,92,246,0.7)" fontSize="10" fontWeight="600">Interview</text>
      </g>

      {/* Rank result */}
      <g className="pipeline-dot" style={{ animation: 'float 3s ease-in-out infinite 1.5s' }}>
        <rect x="160" y="300" width="80" height="60" rx="8" fill="url(#docGrad)" stroke="rgba(249,115,22,0.3)" strokeWidth="1.5"/>
        {/* Bar chart */}
        <rect x="172" y="340" width="8" height="12" rx="2" fill="rgba(249,115,22,0.5)"/>
        <rect x="184" y="332" width="8" height="20" rx="2" fill="rgba(249,115,22,0.6)"/>
        <rect x="196" y="324" width="8" height="28" rx="2" fill="rgba(249,115,22,0.7)"/>
        <rect x="208" y="328" width="8" height="24" rx="2" fill="rgba(249,115,22,0.6)"/>
        <rect x="220" y="336" width="8" height="16" rx="2" fill="rgba(249,115,22,0.5)"/>
        <text x="200" y="292" textAnchor="middle" fill="rgba(249,115,22,0.7)" fontSize="10" fontWeight="600">Ranking</text>
      </g>

      {/* Connecting lines with animation */}
      <line x1="90" y1="120" x2="160" y2="200" stroke="rgba(59,130,246,0.2)" strokeWidth="1" strokeDasharray="4 4">
        <animate attributeName="stroke-dashoffset" from="0" to="-8" dur="1.5s" repeatCount="indefinite"/>
      </line>
      <line x1="240" y1="200" x2="300" y2="120" stroke="rgba(16,185,129,0.2)" strokeWidth="1" strokeDasharray="4 4">
        <animate attributeName="stroke-dashoffset" from="0" to="-8" dur="1.5s" repeatCount="indefinite"/>
      </line>
      <line x1="200" y1="240" x2="200" y2="300" stroke="rgba(139,92,246,0.2)" strokeWidth="1" strokeDasharray="4 4">
        <animate attributeName="stroke-dashoffset" from="0" to="-8" dur="1.5s" repeatCount="indefinite"/>
      </line>

      {/* Floating particles */}
      {[
        { cx: 130, cy: 160, r: 2, delay: 0 },
        { cx: 270, cy: 160, r: 1.5, delay: 0.5 },
        { cx: 200, cy: 140, r: 2, delay: 1 },
        { cx: 150, cy: 260, r: 1.5, delay: 1.5 },
        { cx: 250, cy: 260, r: 2, delay: 2 },
      ].map((p, i) => (
        <circle key={i} cx={p.cx} cy={p.cy} r={p.r} fill="rgba(59,130,246,0.4)">
          <animate
            attributeName="cy"
            values={`${p.cy};${p.cy - 10};${p.cy}`}
            dur="3s"
            begin={`${p.delay}s`}
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.4;0.8;0.4"
            dur="3s"
            begin={`${p.delay}s`}
            repeatCount="indefinite"
          />
        </circle>
      ))}

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
      `}</style>
    </svg>
  )
}

export function ResumeScanIllustration() {
  return (
    <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: 'auto' }}>
      <defs>
        <linearGradient id="scanLine" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity="0"/>
          <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.8"/>
          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0"/>
        </linearGradient>
      </defs>
      {/* Document */}
      <rect x="50" y="20" width="100" height="120" rx="6" fill="#1e293b" stroke="rgba(59,130,246,0.2)" strokeWidth="1"/>
      {/* Text lines */}
      <rect x="64" y="36" width="60" height="4" rx="2" fill="rgba(59,130,246,0.3)"/>
      <rect x="64" y="48" width="48" height="3" rx="1.5" fill="rgba(59,130,246,0.2)"/>
      <rect x="64" y="58" width="56" height="3" rx="1.5" fill="rgba(59,130,246,0.2)"/>
      <rect x="64" y="68" width="40" height="3" rx="1.5" fill="rgba(59,130,246,0.15)"/>
      <rect x="64" y="78" width="52" height="3" rx="1.5" fill="rgba(59,130,246,0.15)"/>
      <rect x="64" y="88" width="44" height="3" rx="1.5" fill="rgba(59,130,246,0.15)"/>
      <rect x="64" y="98" width="60" height="3" rx="1.5" fill="rgba(59,130,246,0.2)"/>
      <rect x="64" y="108" width="36" height="3" rx="1.5" fill="rgba(59,130,246,0.15)"/>
      {/* Skills badges */}
      <rect x="64" y="120" width="24" height="10" rx="5" fill="rgba(16,185,129,0.2)" stroke="rgba(16,185,129,0.3)" strokeWidth="0.5"/>
      <rect x="92" y="120" width="28" height="10" rx="5" fill="rgba(59,130,246,0.2)" stroke="rgba(59,130,246,0.3)" strokeWidth="0.5"/>
      <rect x="124" y="120" width="20" height="10" rx="5" fill="rgba(139,92,246,0.2)" stroke="rgba(139,92,246,0.3)" strokeWidth="0.5"/>
      {/* Scan line */}
      <rect x="50" y="0" width="100" height="2" fill="url(#scanLine)">
        <animate attributeName="y" values="20;140;20" dur="2.5s" repeatCount="indefinite"/>
      </rect>
      {/* Highlighted sections */}
      <rect x="62" y="34" width="64" height="8" rx="2" fill="rgba(16,185,129,0.1)" stroke="rgba(16,185,129,0.2)" strokeWidth="0.5">
        <animate attributeName="opacity" values="0;1;0" dur="2.5s" repeatCount="indefinite"/>
      </rect>
      <rect x="62" y="96" width="64" height="8" rx="2" fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.2)" strokeWidth="0.5">
        <animate attributeName="opacity" values="0;1;0" dur="2.5s" begin="0.8s" repeatCount="indefinite"/>
      </rect>
    </svg>
  )
}

export function InterviewIllustration() {
  return (
    <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: 'auto' }}>
      {/* Screen */}
      <rect x="30" y="10" width="140" height="100" rx="8" fill="#1e293b" stroke="rgba(139,92,246,0.2)" strokeWidth="1"/>
      {/* Code bracket */}
      <text x="100" y="50" textAnchor="middle" fill="rgba(139,92,246,0.6)" fontSize="24" fontFamily="monospace">{'{ }'}</text>
      {/* Question text */}
      <rect x="50" y="65" width="80" height="4" rx="2" fill="rgba(139,92,246,0.3)"/>
      <rect x="60" y="75" width="60" height="3" rx="1.5" fill="rgba(139,92,246,0.2)"/>
      {/* Answer options */}
      <rect x="50" y="90" width="100" height="12" rx="4" fill="rgba(16,185,129,0.1)" stroke="rgba(16,185,129,0.3)" strokeWidth="0.5">
        <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
      </rect>
      <rect x="50" y="108" width="100" height="12" rx="4" fill="rgba(59,130,246,0.08)" stroke="rgba(59,130,246,0.2)" strokeWidth="0.5"/>
      {/* Timer */}
      <circle cx="160" cy="25" r="12" fill="rgba(249,115,22,0.15)" stroke="rgba(249,115,22,0.4)" strokeWidth="1"/>
      <text x="160" y="29" textAnchor="middle" fill="rgba(249,115,22,0.8)" fontSize="9" fontWeight="600">2:30</text>
      {/* Progress dots */}
      {[0,1,2,3,4].map(i => (
        <circle key={i} cx={60 + i * 16} cy="140" r="4" fill={i < 3 ? 'rgba(16,185,129,0.6)' : 'rgba(59,130,246,0.2)'}>
          {i === 2 && <animate attributeName="r" values="4;5;4" dur="1s" repeatCount="indefinite"/>}
        </circle>
      ))}
    </svg>
  )
}

export function RankingIllustration() {
  return (
    <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: 'auto' }}>
      {/* Candidate bars */}
      {[
        { x: 30, h: 80, color: 'rgba(16,185,129,0.6)', label: '92%' },
        { x: 60, h: 65, color: 'rgba(59,130,246,0.5)', label: '78%' },
        { x: 90, h: 55, color: 'rgba(139,92,246,0.5)', label: '71%' },
        { x: 120, h: 45, color: 'rgba(249,115,22,0.4)', label: '62%' },
        { x: 150, h: 35, color: 'rgba(244,63,94,0.4)', label: '48%' },
      ].map((bar, i) => (
        <g key={i}>
          <rect x={bar.x} y={120 - bar.h} width="20" height={bar.h} rx="4" fill={bar.color}>
            <animate attributeName="height" values={`0;${bar.h}`} dur="0.8s" begin={`${i * 0.15}s`} fill="freeze"/>
            <animate attributeName="y" values={`120;${120 - bar.h}`} dur="0.8s" begin={`${i * 0.15}s`} fill="freeze"/>
          </rect>
          <text x={bar.x + 10} y={115 - bar.h} textAnchor="middle" fill="rgba(255,255,255,0.7)" fontSize="8" fontWeight="600">
            {bar.label}
          </text>
        </g>
      ))}
      {/* Trophy */}
      <text x="100" y="25" textAnchor="middle" fontSize="28" style={{ animation: 'float 2s ease-in-out infinite' }}>🏆</text>
      {/* Rank #1 label */}
      <rect x="20" y="130" width="40" height="14" rx="7" fill="rgba(16,185,129,0.2)" stroke="rgba(16,185,129,0.4)" strokeWidth="0.5"/>
      <text x="40" y="140" textAnchor="middle" fill="rgba(16,185,129,0.9)" fontSize="7" fontWeight="700">#1</text>
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
      `}</style>
    </svg>
  )
}

export function SkillGapIllustration() {
  return (
    <svg viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: 'auto' }}>
      {/* Skill bars with gaps */}
      {[
        { y: 25, current: 70, required: 90, label: 'React' },
        { y: 50, current: 45, required: 80, label: 'Node.js' },
        { y: 75, current: 85, required: 85, label: 'Python' },
        { y: 100, current: 30, required: 70, label: 'SQL' },
        { y: 125, current: 60, required: 75, label: 'Docker' },
      ].map((skill, i) => (
        <g key={i}>
          <text x="28" y={skill.y + 9} textAnchor="end" fill="rgba(255,255,255,0.5)" fontSize="8">{skill.label}</text>
          {/* Required (background) */}
          <rect x="32" y={skill.y} width={skill.required * 1.2} height="12" rx="6" fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.2)" strokeWidth="0.5"/>
          {/* Current (filled) */}
          <rect x="32" y={skill.y} width={skill.current * 1.2} height="12" rx="6" fill={skill.current >= skill.required ? 'rgba(16,185,129,0.5)' : 'rgba(249,115,22,0.4)'}>
            <animate attributeName="width" values={`0;${skill.current * 1.2}`} dur="0.6s" begin={`${i * 0.1}s`} fill="freeze"/>
          </rect>
          {/* Gap indicator */}
          {skill.current < skill.required && (
            <line
              x1={32 + skill.current * 1.2}
              y1={skill.y}
              x2={32 + skill.required * 1.2}
              y2={skill.y}
              stroke="rgba(244,63,94,0.5)"
              strokeWidth="2"
              strokeDasharray="2 2"
            >
              <animate attributeName="stroke-dashoffset" from="0" to="-4" dur="1s" repeatCount="indefinite"/>
            </line>
          )}
        </g>
      ))}
      {/* Legend */}
      <circle cx="40" cy="148" r="4" fill="rgba(16,185,129,0.5)"/>
      <text x="48" y="151" fill="rgba(255,255,255,0.5)" fontSize="7">Current</text>
      <circle cx="100" cy="148" r="4" fill="rgba(59,130,246,0.2)" stroke="rgba(59,130,246,0.3)" strokeWidth="0.5"/>
      <text x="108" y="151" fill="rgba(255,255,255,0.5)" fontSize="7">Required</text>
    </svg>
  )
}
