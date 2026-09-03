import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Network, RefreshCw, Info, X, ArrowRight, BookOpen
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
  ai_ml: { bg: '#ede9fe', fg: '#7c3aed', border: '#a78bfa' },
  security: { bg: '#fef2f2', fg: '#dc2626', border: '#fca5a5' },
  default: { bg: 'var(--color-primary-muted)', fg: 'var(--color-primary)', border: 'var(--color-primary)' },
}

function getCategoryColor(category) {
  const cat = (category || '').toLowerCase().replace(/[\s-]/g, '_')
  return CATEGORY_COLORS[cat] || CATEGORY_COLORS.default
}

export default function SkillDependencyGraph() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoveredNode, setHoveredNode] = useState(null)

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

  const nodes = graphData?.nodes || graphData?.skills || []
  const edges = graphData?.edges || graphData?.dependencies || graphData?.connections || []

  // Build adjacency for determining highlighted connections
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

  const highlightedNodes = selectedNode ? getConnectedSkills(selectedNode) : new Set()
  highlightedNodes.add(selectedNode)

  // Compute node positions in a circular layout
  const getNodePosition = (idx, total) => {
    const radius = 220
    const cx = 300
    const cy = 260
    const angle = (2 * Math.PI * idx) / total - Math.PI / 2
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    }
  }

  const nodePositions = nodes.map((n, idx) => {
    const name = typeof n === 'string' ? n : n.skill || n.name || n.id
    const pos = getNodePosition(idx, nodes.length)
    return { ...pos, name, data: n }
  })

  // Map skill name to position for drawing edges
  const posMap = {}
  nodePositions.forEach((p) => { posMap[p.name] = p })

  // Find the data for the selected node
  const selectedNodeData = nodes.find((n) => {
    const name = typeof n === 'string' ? n : n.skill || n.name || n.id
    return name === selectedNode
  })

  return (
    <div className="fade-in" style={{ maxWidth: 1100, margin: '0 auto' }}>
      <PageHeader
        badge="Skill Dependencies"
        title="Skill Dependency Graph"
        description="Visualize how skills relate to each other. Skills with dependencies are connected — mastering foundational skills unlocks advanced ones."
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
        <div style={{ display: 'flex', gap: 20 }}>
          {/* Graph Canvas */}
          <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', minHeight: 560, position: 'relative' }}>
            {/* Legend */}
            <div style={{
              padding: '12px 16px', borderBottom: '1px solid var(--color-border-subtle)',
              display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap'
            }}>
              <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase' }}>
                Categories:
              </span>
              {Object.entries(CATEGORY_COLORS).filter(([k]) => k !== 'default').map(([cat, colors]) => (
                <span key={cat} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: '10px', color: colors.fg, fontWeight: 600 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 'var(--radius-full)', background: colors.fg, display: 'inline-block' }} />
                  {cat.replace(/_/g, ' ')}
                </span>
              ))}
            </div>

            <svg width="100%" height="520" viewBox="0 0 600 520" style={{ display: 'block' }}>
              {/* Edges */}
              {edges.map((edge, idx) => {
                const srcName = edge.source || edge.from
                const tgtName = edge.target || edge.to
                const srcPos = posMap[srcName]
                const tgtPos = posMap[tgtName]
                if (!srcPos || !tgtPos) return null

                const isHighlighted = selectedNode && (srcName === selectedNode || tgtName === selectedNode)

                return (
                  <line
                    key={`edge-${idx}`}
                    x1={srcPos.x} y1={srcPos.y}
                    x2={tgtPos.x} y2={tgtPos.y}
                    stroke={isHighlighted ? 'var(--color-primary)' : 'var(--color-border)'}
                    strokeWidth={isHighlighted ? 2.5 : 1.5}
                    strokeDasharray={isHighlighted ? 'none' : '6 4'}
                    opacity={selectedNode ? (isHighlighted ? 1 : 0.15) : 0.4}
                    style={{ transition: 'all 0.2s ease' }}
                  />
                )
              })}

              {/* Nodes */}
              {nodePositions.map((nodePos, idx) => {
                const cat = typeof nodePos.data === 'object' ? (nodePos.data.category || nodePos.data.type) : ''
                const colors = getCategoryColor(cat)
                const isSelected = selectedNode === nodePos.name
                const isConnected = highlightedNodes.has(nodePos.name) && selectedNode
                const isOther = selectedNode && !isConnected
                const radius = isSelected ? 28 : isConnected ? 24 : 22

                return (
                  <g
                    key={`node-${idx}`}
                    onClick={() => setSelectedNode(isSelected ? null : nodePos.name)}
                    onMouseEnter={() => setHoveredNode(nodePos.name)}
                    onMouseLeave={() => setHoveredNode(null)}
                    style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
                  >
                    <circle
                      cx={nodePos.x} cy={nodePos.y} r={radius}
                      fill={isSelected ? colors.fg : colors.bg}
                      stroke={colors.fg}
                      strokeWidth={isSelected ? 3 : isConnected ? 2 : 1.5}
                      opacity={isOther ? 0.2 : 1}
                      style={{ transition: 'all 0.2s ease' }}
                    />
                    <text
                      x={nodePos.x} y={nodePos.y + 1}
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize="10"
                      fontWeight="700"
                      fill={isSelected ? '#fff' : colors.fg}
                      opacity={isOther ? 0.2 : 1}
                      style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                      {nodePos.name.length > 12 ? nodePos.name.slice(0, 11) + '…' : nodePos.name}
                    </text>
                  </g>
                )
              })}

              {/* Tooltip on hover */}
              {hoveredNode && !selectedNode && (
                <g>
                  {(() => {
                    const n = nodePositions.find((p) => p.name === hoveredNode)
                    if (!n) return null
                    const text = n.name
                    const tx = Math.min(Math.max(n.x, 60), 540)
                    const ty = n.y - 38
                    return (
                      <>
                        <rect x={tx - 50} y={ty - 12} width={100} height={22} rx={6} fill="var(--color-bg-elevated)" stroke="var(--color-border)" strokeWidth="1" />
                        <text x={tx} y={ty + 2} textAnchor="middle" fontSize="11" fontWeight="700" fill="var(--color-fg)" style={{ pointerEvents: 'none' }}>
                          {text}
                        </text>
                      </>
                    )
                  })()}
                </g>
              )}
            </svg>
          </div>

          {/* Side Detail Panel */}
          <div style={{ width: 320, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Instructions */}
            <div className="card" style={{ padding: 'var(--p-space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <Info size={14} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-fg)' }}>How to Use</span>
              </div>
              <p style={{ fontSize: '11px', color: 'var(--color-fg-muted)', margin: 0, lineHeight: 1.6 }}>
                Click a skill node to see its dependencies and connected skills. Connected nodes are highlighted in the graph. Click again to deselect.
              </p>
            </div>

            {/* Selected Node Details */}
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

                {selectedNodeData && typeof selectedNodeData === 'object' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16 }}>
                    {selectedNodeData.category && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', minWidth: 70 }}>Category</span>
                        <span className="chip" style={{ fontSize: '10px' }}>
                          {selectedNodeData.category}
                        </span>
                      </div>
                    )}
                    {selectedNodeData.level && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', minWidth: 70 }}>Level</span>
                        <span style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg)' }}>{selectedNodeData.level}</span>
                      </div>
                    )}
                    {selectedNodeData.description && (
                      <div style={{ display: 'flex', gap: 8 }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', minWidth: 70, marginTop: 2 }}>Details</span>
                        <span style={{ fontSize: '11px', color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>{selectedNodeData.description}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Connected Skills */}
                {edges.filter((e) => (e.source || e.from) === selectedNode || (e.target || e.to) === selectedNode).length > 0 && (
                  <div>
                    <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                      Connected Skills
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {edges
                        .filter((e) => (e.source || e.from) === selectedNode || (e.target || e.to) === selectedNode)
                        .map((edge, idx) => {
                          const other = (edge.source || edge.from) === selectedNode
                            ? (edge.target || edge.to)
                            : (edge.source || edge.from)
                          const isDependency = (edge.target || edge.to) === selectedNode
                          return (
                            <div key={idx} style={{
                              padding: '8px 10px', background: 'var(--color-bg-elevated)',
                              borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)',
                              display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer'
                            }} onClick={() => setSelectedNode(other)}>
                              <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-fg)' }}>{other}</span>
                              <span style={{
                                fontSize: '10px', color: isDependency ? 'var(--color-warning)' : 'var(--color-success)',
                                fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4
                              }}>
                                {isDependency ? '← prerequisite' : 'unlockable →'}
                                <ArrowRight size={10} style={{ transform: isDependency ? 'rotate(180deg)' : 'none' }} />
                              </span>
                            </div>
                          )
                        })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="card" style={{ padding: 'var(--p-space-5)', textAlign: 'center' }}>
                <Network size={32} style={{ color: 'var(--color-border)', margin: '0 auto 12px' }} />
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  Select a skill node on the graph to see its details and connected skills.
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
                  <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                    {new Set(nodes.map((n) => typeof n === 'object' ? (n.category || n.type) : '').filter(Boolean)).size}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
