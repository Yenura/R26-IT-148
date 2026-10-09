import { useEffect, useState, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Network, RefreshCw, Info, X, ArrowRight, BookOpen, Search, Layers
} from 'lucide-react'
import { c4SkillGapGraph } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

const CATEGORY_COLORS = {
  frontend: { bg: '#dbeafe', fg: '#2563eb', border: '#93c5fd' },
  backend: { bg: '#dcfce7', fg: '#16a34a', border: '#86efac' },
  devops: { bg: '#fef3c7', fg: '#d97706', border: '#fcd34d' },
  database: { bg: '#f3e8ff', fg: '#9333ea', border: '#c4b5fd' },
  testing: { bg: '#ffe4e6', fg: '#e11d48', border: '#fda4af' },
  mobile: { bg: '#cffafe', fg: '#0891b2', border: '#67e8f9' },
  design: { bg: '#fce7f3', fg: '#db2777', border: '#f9a8d4' },
  aiml: { bg: '#ede9fe', fg: '#7c3aed', border: '#a78bfa' },
  ai_ml: { bg: '#ede9fe', fg: '#7c3aed', border: '#a78bfa' },
  security: { bg: '#fef2f2', fg: '#dc2626', border: '#fca5a5' },
  other: { bg: 'var(--color-bg-elevated)', fg: 'var(--color-fg-muted)', border: 'var(--color-border)' },
  default: { bg: 'var(--color-primary-muted)', fg: 'var(--color-primary)', border: 'var(--color-primary)' },
}

function getCategoryColor(category) {
  const cat = (category || '').toLowerCase().replace(/[\s-]/g, '_')
  return CATEGORY_COLORS[cat] || CATEGORY_COLORS.other
}

function nodeName(n) {
  if (typeof n === 'string') return n
  return n.label || n.skill || n.name || n.id || ''
}

function nodeCategory(n) {
  if (typeof n === 'object' && n) return (n.category || n.type || 'other').toLowerCase().replace(/[\s-]/g, '_')
  return 'other'
}

function nodeTier(n) {
  if (typeof n === 'object' && n) {
    if (n.tier) return n.tier
    const lvl = n.level ?? 0
    return lvl === 0 ? 'Foundational' : (lvl === 1 ? 'Intermediate' : 'Advanced')
  }
  return 'Foundational'
}

const TIERS = ['Foundational', 'Intermediate', 'Advanced']
const TIER_HINT = {
  Foundational: 'No prerequisites — start here',
  Intermediate: 'Builds on one foundation layer',
  Advanced: 'Requires deep prerequisite chains',
}

// Layered layout geometry
const COL_W = 250
const COL_GAP = 90
const PAD_X = 24
const HEADER_H = 44
const NODE_H = 46
const NODE_GAP = 10
const TOP_PAD = 16

export default function SkillDependencyGraph() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')
  const [activeTier, setActiveTier] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadGraph()
  }, [])

  const loadGraph = async () => {
    setLoading(true)
    try {
      const r = await c4SkillGapGraph()
      setGraphData(r?.data?.data || r?.data || null)
    } catch {
      toast.error('Failed to load skill dependency graph')
    } finally {
      setLoading(false)
    }
  }

  const nodes = useMemo(() => graphData?.nodes || graphData?.skills || [], [graphData])
  const edges = useMemo(() => graphData?.edges || graphData?.dependencies || graphData?.connections || [], [graphData])

  const getConnectedSkills = useCallback((skillName) => {
    const connected = new Set()
    edges.forEach((edge) => {
      const src = edge.source || edge.from
      const tgt = edge.target || edge.to
      if (src === skillName) connected.add(tgt)
      if (tgt === skillName) connected.add(src)
    })
    return connected
  }, [edges])

  const highlightedNodes = useMemo(() => {
    if (!selectedNode) return new Set()
    const s = getConnectedSkills(selectedNode)
    s.add(selectedNode)
    return s
  }, [selectedNode, getConnectedSkills])

  // Per-node stats + grouping
  const nodeStats = useMemo(() => {
    const stats = {}
    nodes.forEach((n) => {
      const name = nodeName(n)
      stats[name] = { requires: 0, unlocks: 0 }
    })
    edges.forEach((e) => {
      const src = e.source || e.from
      const tgt = e.target || e.to
      if (stats[src]) stats[src].unlocks += 1
      if (stats[tgt]) stats[tgt].requires += 1
    })
    return stats
  }, [nodes, edges])

  const categories = useMemo(() => {
    const map = {}
    nodes.forEach((n) => {
      const c = nodeCategory(n)
      map[c] = (map[c] || 0) + 1
    })
    return Object.entries(map).sort((a, b) => b[1] - a[1])
  }, [nodes])

  const matchesFilter = useCallback((name, data) => {
    if (activeCategory !== 'all' && nodeCategory(data) !== activeCategory) return false
    if (activeTier !== 'all' && nodeTier(data) !== activeTier) return false
    if (search && !name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  }, [activeCategory, activeTier, search])

  // Layered positions: one column per tier, stacked rows
  const layout = useMemo(() => {
    const byTier = { Foundational: [], Intermediate: [], Advanced: [] }
    nodes.forEach((n) => {
      const name = nodeName(n)
      const tier = TIERS.includes(nodeTier(n)) ? nodeTier(n) : 'Foundational'
      byTier[tier].push({ name, data: n })
    })
    // Most-connected first so hub skills sit near the top of each column
    Object.values(byTier).forEach((arr) => arr.sort((a, b) => {
      const sa = (nodeStats[a.name]?.requires || 0) + (nodeStats[a.name]?.unlocks || 0)
      const sb = (nodeStats[b.name]?.requires || 0) + (nodeStats[b.name]?.unlocks || 0)
      return sb - sa
    }))
    const pos = {}
    let maxRows = 0
    TIERS.forEach((tier, col) => {
      byTier[tier].forEach((item, row) => {
        pos[item.name] = {
          ...item,
          col,
          row,
          x: PAD_X + col * (COL_W + COL_GAP),
          y: TOP_PAD + HEADER_H + row * (NODE_H + NODE_GAP),
        }
      })
      maxRows = Math.max(maxRows, byTier[tier].length)
    })
    const height = TOP_PAD + HEADER_H + maxRows * (NODE_H + NODE_GAP) + 24
    const width = PAD_X * 2 + COL_W * 3 + COL_GAP * 2
    return { pos, byTier, width, height }
  }, [nodes, nodeStats])

  const edgePath = (a, b) => {
    const x1 = a.x + COL_W
    const y1 = a.y + NODE_H / 2
    const x2 = b.x
    const y2 = b.y + NODE_H / 2
    const mx = (x1 + x2) / 2
    return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2 - 2} ${y2}`
  }

  const selectedNodeData = nodes.find((n) => nodeName(n) === selectedNode)
  const selectedEdges = selectedNode
    ? edges.filter((e) => (e.source || e.from) === selectedNode || (e.target || e.to) === selectedNode)
    : []
  const prerequisites = selectedEdges
    .filter((e) => (e.target || e.to) === selectedNode)
    .map((e) => e.source || e.from)
  const unlocks = selectedEdges
    .filter((e) => (e.source || e.from) === selectedNode)
    .map((e) => e.target || e.to)

  const categoryCount = categories.length
  const hasFilter = activeCategory !== 'all' || activeTier !== 'all' || search

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto' }}>
      <PageHeader
        badge="Skill Dependencies"
        title="Skill Dependency Graph"
        description="Follow the learning ladder left to right: master foundational skills to unlock intermediate tools, then advanced specializations."
        icon={Network}
        actions={
          <button onClick={loadGraph} className="btn btn-ghost btn-sm">
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        }
      />

      {loading ? (
        <SkeletonLoader type="card" count={3} />
      ) : !nodes.length ? (
        <EmptyState
          title="No Skill Dependency Data"
          description="Complete a skill gap analysis to generate your personalized skill dependency map."
          actionLabel="Run Skill Gap Analysis"
          onAction={() => navigate('/candidate/skill-gap')}
          icon={Network}
        />
      ) : (
        <div>
          {/* Filter toolbar */}
          <div className="card" style={{
            padding: '12px 16px', marginBottom: 16,
            display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap',
          }}>
            <div style={{ position: 'relative', width: 220 }}>
              <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
              <input
                type="text"
                placeholder="Search skills..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ paddingLeft: 30, height: 34, fontSize: 'var(--p-text-xs)', width: '100%' }}
              />
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {['all', ...TIERS].map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveTier(t)}
                  className={`btn btn-sm ${activeTier === t ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 'var(--p-text-xs)' }}
                >
                  {t === 'all' ? 'All tiers' : t}
                </button>
              ))}
            </div>
            {hasFilter && (
              <button
                onClick={() => { setActiveCategory('all'); setActiveTier('all'); setSearch('') }}
                className="btn btn-ghost btn-sm"
                style={{ fontSize: 'var(--p-text-xs)', marginLeft: 'auto' }}
              >
                <X size={13} /> Clear filters
              </button>
            )}
          </div>

          <div style={{ display: 'flex', gap: 20, alignItems: 'flex-start' }}>
            {/* Graph Canvas */}
            <div className="card" style={{ flex: 1, minWidth: 0, padding: 0, overflow: 'hidden' }}>
              {/* Legend (click to isolate a category) */}
              <div style={{
                padding: '12px 16px', borderBottom: '1px solid var(--color-border-subtle)',
                display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap',
              }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>
                  Categories:
                </span>
                <button
                  onClick={() => setActiveCategory('all')}
                  className={`btn btn-sm ${activeCategory === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: '10px', padding: '2px 10px' }}
                >
                  All
                </button>
                {categories.map(([cat, count]) => {
                  const colors = getCategoryColor(cat)
                  const active = activeCategory === cat
                  return (
                    <button
                      key={cat}
                      onClick={() => setActiveCategory(active ? 'all' : cat)}
                      title={`${count} skills`}
                      style={{
                        display: 'inline-flex', alignItems: 'center', gap: 5,
                        fontSize: '10px', fontWeight: 700, cursor: 'pointer',
                        color: active ? '#fff' : colors.fg,
                        background: active ? colors.fg : colors.bg,
                        border: `1px solid ${colors.border}`,
                        borderRadius: 'var(--radius-full)', padding: '3px 10px',
                      }}
                    >
                      <span style={{ width: 8, height: 8, borderRadius: 'var(--radius-full)', background: active ? '#fff' : colors.fg, display: 'inline-block' }} />
                      {cat.replace(/_/g, ' ')} · {count}
                    </button>
                  )
                })}
              </div>

              <div style={{ overflowX: 'auto' }}>
                <svg
                  width="100%" viewBox={`0 0 ${layout.width} ${layout.height}`}
                  style={{ display: 'block', minWidth: 640, height: 'auto', maxHeight: 640 }}
                >
                  <defs>
                    <marker id="dep-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                      <path d="M 0 1 L 9 5 L 0 9" fill="none" stroke="var(--color-fg-muted)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                    </marker>
                    <marker id="dep-arrow-hot" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                      <path d="M 0 1 L 9 5 L 0 9" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </marker>
                  </defs>

                  {/* Tier column headers + backdrop */}
                  {TIERS.map((tier, col) => {
                    const x = PAD_X + col * (COL_W + COL_GAP)
                    return (
                      <g key={tier}>
                        <rect
                          x={x - 12} y={TOP_PAD} width={COL_W + 24} height={layout.height - TOP_PAD - 12}
                          rx={12} fill="var(--color-bg)" opacity={0.55}
                        />
                        <text x={x + COL_W / 2} y={TOP_PAD + 18} textAnchor="middle" fontSize="11" fontWeight="800"
                          fill="var(--color-fg-muted)" style={{ textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                          {tier} · {layout.byTier[tier].length}
                        </text>
                        <text x={x + COL_W / 2} y={TOP_PAD + 32} textAnchor="middle" fontSize="9" fill="var(--color-fg-muted)" opacity={0.8}>
                          {TIER_HINT[tier]}
                        </text>
                      </g>
                    )
                  })}

                  {/* Edges */}
                  {edges.map((edge, idx) => {
                    const srcName = edge.source || edge.from
                    const tgtName = edge.target || edge.to
                    const a = layout.pos[srcName]
                    const b = layout.pos[tgtName]
                    if (!a || !b) return null
                    const hot = selectedNode && (srcName === selectedNode || tgtName === selectedNode)
                    const dim = selectedNode ? !hot : false
                    const filtered = !matchesFilter(srcName, a.data) || !matchesFilter(tgtName, b.data)
                    return (
                      <path
                        key={`edge-${idx}`}
                        d={edgePath(a, b)}
                        fill="none"
                        stroke={hot ? 'var(--color-primary)' : 'var(--color-fg-muted)'}
                        strokeWidth={hot ? 2.4 : 1.4}
                        opacity={dim ? 0.08 : (filtered ? 0.06 : 0.45)}
                        markerEnd={hot ? 'url(#dep-arrow-hot)' : 'url(#dep-arrow)'}
                        style={{ transition: 'opacity 0.2s ease' }}
                      />
                    )
                  })}

                  {/* Nodes */}
                  {Object.values(layout.pos).map((p) => {
                    const colors = getCategoryColor(nodeCategory(p.data))
                    const isSelected = selectedNode === p.name
                    const connected = selectedNode && highlightedNodes.has(p.name)
                    const dimmed = (selectedNode && !connected) || !matchesFilter(p.name, p.data)
                    const st = nodeStats[p.name] || { requires: 0, unlocks: 0 }
                    const hovered = hoveredNode === p.name
                    return (
                      <g
                        key={`node-${p.name}`}
                        onClick={() => setSelectedNode(isSelected ? null : p.name)}
                        onMouseEnter={() => setHoveredNode(p.name)}
                        onMouseLeave={() => setHoveredNode(null)}
                        style={{ cursor: 'pointer' }}
                        opacity={dimmed ? 0.22 : 1}
                      >
                        <rect
                          x={p.x} y={p.y} width={COL_W} height={NODE_H} rx={10}
                          fill={isSelected ? colors.fg : colors.bg}
                          stroke={isSelected ? colors.fg : (hovered || connected ? colors.fg : colors.border)}
                          strokeWidth={isSelected ? 2.5 : (hovered || connected ? 2 : 1.2)}
                          style={{ transition: 'all 0.15s ease' }}
                        />
                        <rect x={p.x} y={p.y} width={5} height={NODE_H} rx={2.5} fill={isSelected ? '#ffffff88' : colors.fg} />
                        <text
                          x={p.x + 16} y={p.y + (st.requires + st.unlocks > 0 ? 19 : NODE_H / 2)}
                          fontSize="12.5" fontWeight="700"
                          fill={isSelected ? '#fff' : colors.fg}
                          style={{ pointerEvents: 'none', userSelect: 'none' }}
                        >
                          {p.name}
                        </text>
                        {(st.requires + st.unlocks > 0) && (
                          <text
                            x={p.x + 16} y={p.y + 34}
                            fontSize="9.5" fontWeight="600"
                            fill={isSelected ? '#ffffffcc' : 'var(--color-fg-muted)'}
                            style={{ pointerEvents: 'none', userSelect: 'none' }}
                          >
                            {st.requires > 0 ? `needs ${st.requires}` : 'no prerequisites'}{st.unlocks > 0 ? ` · unlocks ${st.unlocks}` : ''}
                          </text>
                        )}
                        <text
                          x={p.x + COL_W - 10} y={p.y + NODE_H / 2}
                          textAnchor="end" dominantBaseline="central"
                          fontSize="13" fontWeight="800"
                          fill={isSelected ? '#fff' : colors.fg} opacity={isSelected ? 0.9 : 0.55}
                          style={{ pointerEvents: 'none', userSelect: 'none' }}
                        >
                          {(st.requires || 0) + (st.unlocks || 0)}
                        </text>
                      </g>
                    )
                  })}
                </svg>
              </div>
            </div>

            {/* Side Detail Panel */}
            <div style={{ width: 320, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="card" style={{ padding: 'var(--p-space-4)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <Info size={14} style={{ color: 'var(--color-primary)' }} />
                  <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)' }}>How to Use</span>
                </div>
                <p style={{ fontSize: '11px', color: 'var(--color-fg-muted)', margin: 0, lineHeight: 1.6 }}>
                  Skills flow left to right along prerequisite arrows. Click a skill to highlight its
                  prerequisites and everything it unlocks. Use the legend to isolate one category.
                </p>
              </div>

              {selectedNode ? (
                <div className="card" style={{ padding: 'var(--p-space-5)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <h3 style={{ margin: 0, fontSize: 'var(--p-text-sm)', fontWeight: 800, color: 'var(--color-fg)' }}>
                      {selectedNode}
                    </h3>
                    <button onClick={() => setSelectedNode(null)} className="btn btn-ghost btn-sm" style={{ padding: 4 }}>
                      <X size={14} />
                    </button>
                  </div>

                  {(() => {
                    const colors = getCategoryColor(selectedNodeData ? nodeCategory(selectedNodeData) : 'other')
                    return (
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 14 }}>
                        <span style={{
                          fontSize: '10px', fontWeight: 800, padding: '3px 10px',
                          borderRadius: 'var(--radius-full)', textTransform: 'uppercase', letterSpacing: '0.04em',
                          background: colors.bg, color: colors.fg, border: `1px solid ${colors.border}`,
                        }}>
                          {(selectedNodeData && nodeCategory(selectedNodeData)) || 'other'}
                        </span>
                        <span style={{
                          fontSize: '10px', fontWeight: 800, padding: '3px 10px',
                          borderRadius: 'var(--radius-full)', textTransform: 'uppercase', letterSpacing: '0.04em',
                          background: 'var(--color-bg-elevated)', color: 'var(--color-fg-secondary)',
                          border: '1px solid var(--color-border)',
                        }}>
                          <Layers size={10} style={{ verticalAlign: '-1px', marginRight: 4 }} />
                          {(selectedNodeData && nodeTier(selectedNodeData)) || 'Foundational'}
                        </span>
                      </div>
                    )
                  })()}

                  {selectedNodeData && typeof selectedNodeData === 'object' && selectedNodeData.description && (
                    <p style={{ fontSize: '11px', color: 'var(--color-fg-secondary)', lineHeight: 1.5, margin: '0 0 14px 0' }}>
                      {selectedNodeData.description}
                    </p>
                  )}

                  {prerequisites.length > 0 && (
                    <div style={{ marginBottom: 12 }}>
                      <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                        Learn first ({prerequisites.length})
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {prerequisites.map((name) => (
                          <SkillRow key={`pre-${name}`} name={name} hint="prerequisite" onPick={setSelectedNode} />
                        ))}
                      </div>
                    </div>
                  )}

                  {unlocks.length > 0 && (
                    <div>
                      <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                        Unlocks next ({unlocks.length})
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {unlocks.map((name) => (
                          <SkillRow key={`un-${name}`} name={name} hint="unlockable" onPick={setSelectedNode} />
                        ))}
                      </div>
                    </div>
                  )}

                  {prerequisites.length === 0 && unlocks.length === 0 && (
                    <p style={{ fontSize: '11px', color: 'var(--color-fg-muted)', margin: 0 }}>
                      No recorded dependencies for this skill.
                    </p>
                  )}
                </div>
              ) : (
                <div className="card" style={{ padding: 'var(--p-space-5)', textAlign: 'center' }}>
                  <Network size={32} style={{ color: 'var(--color-border)', margin: '0 auto 12px' }} />
                  <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                    Select a skill on the graph to see its prerequisites and what it unlocks.
                  </p>
                </div>
              )}

              {/* Quick Stats */}
              <div className="card" style={{ padding: 'var(--p-space-4)' }}>
                <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 10 }}>
                  Graph Summary
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--color-fg-secondary)' }}>Total Skills</span>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{nodes.length}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--color-fg-secondary)' }}>Dependencies</span>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{edges.length}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--color-fg-secondary)' }}>Categories</span>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{categoryCount}</span>
                  </div>
                  {TIERS.map((t) => (
                    <div key={t} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', color: 'var(--color-fg-secondary)' }}>{t}</span>
                      <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>{layout.byTier[t].length}</span>
                    </div>
                  ))}
                  <button
                    onClick={() => navigate('/candidate/skill-gap')}
                    className="btn btn-ghost btn-sm"
                    style={{ marginTop: 4, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
                  >
                    <BookOpen size={13} /> Find my gaps
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function SkillRow({ name, hint, onPick }) {
  const isPre = hint === 'prerequisite'
  return (
    <div
      style={{
        padding: '8px 10px', background: 'var(--color-bg-elevated)',
        borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer',
      }}
      onClick={() => onPick(name)}
    >
      <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg)' }}>{name}</span>
      <span style={{
        fontSize: '10px', color: isPre ? 'var(--color-warning)' : 'var(--color-success)',
        fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4,
      }}>
        {isPre ? '← learn first' : 'unlocks →'}
        <ArrowRight size={10} style={{ transform: isPre ? 'rotate(180deg)' : 'none' }} />
      </span>
    </div>
  )
}
