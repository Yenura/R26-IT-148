import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FileSearch, MessagesSquare, Trophy, Search,
  ArrowRight, Activity, Zap, Users, CheckCircle2, Circle, MapPin
} from 'lucide-react'
import { HEALTH } from '../api'

const PIPELINE_STAGES = [
  { to: '/cv-match',  icon: FileSearch,    title: 'CV Match',       desc: 'Upload CVs and match to roles', comp: 'Component 1', color: '#3b82f6' },
  { to: '/interview', icon: MessagesSquare, title: 'AI Interview',  desc: 'QG-powered interview questions', comp: 'Component 2', color: '#60a5fa' },
  { to: '/ranking',   icon: Trophy,         title: 'Ranking',        desc: 'CSS + LambdaMART candidate ranking', comp: 'Component 3', color: '#f59e0b' },
  { to: '/skill-gap', icon: Search,         title: 'Hire Decision',  desc: 'Skill gap, hire probability & learning plan', comp: 'Component 4', color: '#10b981' },
]

const COMP_DEFS = [
  { key: 'c1', name: 'CV Intelligence', port: 8001 },
  { key: 'c2', name: 'AI Interview', port: 8002 },
  { key: 'c3', name: 'Ranking Engine', port: 8003 },
  { key: 'c4', name: 'Skill Analytics', port: 8004 },
]

export default function Dashboard() {
  const [health, setHealth] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    const check = async () => {
      const out = {}
      await Promise.all(COMP_DEFS.map(async ({ key }) => {
        try {
          const r = await fetch(HEALTH[key], { signal: AbortSignal.timeout(5000) })
          out[key] = { ok: r.status === 200, status: r.status }
        } catch {
          out[key] = { ok: false, status: 0 }
        }
      }))
      if (alive) { setHealth(out); setLoading(false) }
    }
    check()
    const t = setInterval(check, 15000)
    return () => { alive = false; clearInterval(t) }
  }, [])

  const upCount = COMP_DEFS.filter(({ key }) => health[key]?.ok).length

  return (
    <div className="fade-in">
      <div className="page-head">
        <span className="section-tag">Welcome back</span>
        <h1>RecruitAI Dashboard</h1>
        <p>Your end-to-end AI recruitment platform — from CV to hire decision.</p>
      </div>

      {/* Health + Stats Row */}
      <div className="grid grid-4" style={{ marginBottom: 24 }}>
        <div className="stat stat-highlight">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={16} style={{ color: upCount === 4 ? 'var(--accent-2)' : 'var(--accent-warn)' }} />
            <span className="stat-label">System Health</span>
          </div>
          <div className="stat-value" style={{ color: upCount === 4 ? 'var(--accent-2)' : 'var(--accent-warn)' }}>
            {loading ? '—' : `${upCount}/4`}
          </div>
          <div className="stat-sub">{loading ? 'Checking services…' : upCount === 4 ? 'All systems operational' : 'Some services offline'}</div>
        </div>
        {[
          { label: 'Total Candidates', value: '—', sub: 'Across all pipelines', icon: Users },
          { label: 'Pipeline Stages', value: '4', sub: 'CV → Interview → Rank → Hire', icon: Zap },
          { label: 'Quick Actions', value: '8', sub: 'Available features', icon: CheckCircle2 },
        ].map(({ label, value, sub, icon: Icon }) => (
          <div className="stat" key={label}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon size={14} style={{ color: 'var(--text-muted)' }} />
              <span className="stat-label">{label}</span>
            </div>
            <div className="stat-value" style={{ fontSize: 24 }}>{value}</div>
            <div className="stat-sub">{sub}</div>
          </div>
        ))}
      </div>

      {/* Service Health */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3>
          <Activity size={16} style={{ color: 'var(--accent)' }} />
          Service Health
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          {COMP_DEFS.map(({ key, name, port }) => (
            <div key={key} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px',
              background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)',
              border: `1px solid ${health[key]?.ok ? 'rgba(0,228,184,.2)' : 'var(--border)'}`
            }}>
              <span className={`status-dot ${health[key]?.ok ? 'up' : 'down'}`} />
              <div style={{ minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{name}</div>
                <div className="muted" style={{ fontSize: 11 }}>:{port}</div>
              </div>
              <span className="spacer" />
              <span className={`badge badge-${health[key]?.ok ? 'green' : 'red'}`}>
                {health[key]?.ok ? 'online' : 'offline'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Flow */}
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: 16, fontWeight: 700 }}>Recruitment Pipeline</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {PIPELINE_STAGES.map(({ to, icon: Icon, title, desc, comp, color }, i) => (
            <div key={to} style={{ position: 'relative' }}>
              <Link to={to} className="card card-interactive" style={{ textDecoration: 'none', display: 'block', height: '100%' }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: `${color}18`, display: 'flex',
                  alignItems: 'center', justifyContent: 'center', marginBottom: 14
                }}>
                  <Icon size={22} style={{ color }} />
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 4 }}>
                  Stage {i + 1}
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{title}</div>
                <p className="muted" style={{ fontSize: 12, margin: 0, lineHeight: 1.5 }}>{desc}</p>
                <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--accent)', fontSize: 13, fontWeight: 600 }}>
                  Open <ArrowRight size={14} />
                </div>
              </Link>
              {i < 3 && (
                <div style={{
                  position: 'absolute', top: '50%', right: -20,
                  transform: 'translateY(-50%)', color: 'var(--text-muted)',
                  fontSize: 18, zIndex: 1
                }}>→</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-2">
        <Link to="/leaderboard" className="card card-interactive" style={{ textDecoration: 'none' }}>
          <h3 style={{ margin: 0 }}>
            <Trophy size={16} style={{ color: 'var(--accent-warn)' }} />
            Leaderboard
          </h3>
          <p className="muted" style={{ margin: '8px 0 0', fontSize: 13 }}>View top candidates and analytics</p>
        </Link>
        <Link to="/career" className="card card-interactive" style={{ textDecoration: 'none' }}>
          <h3 style={{ margin: 0 }}>
            <MapPin size={16} style={{ color: 'var(--accent-2)' }} />
            Career Paths
          </h3>
          <p className="muted" style={{ margin: '8px 0 0', fontSize: 13 }}>Explore role progressions and resources</p>
        </Link>
      </div>
    </div>
  )
}
