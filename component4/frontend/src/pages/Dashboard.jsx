import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAnalyticsSummary, getLeaderboard } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  Users, AlertTriangle, TrendingUp, Award, ChevronRight,
  BookOpen, Target, Briefcase, Monitor,
} from 'lucide-react'

const SEV_COLOR = { Low: '#22c55e', Medium: '#f59e0b', High: '#ef4444' }
const ROLE_COLORS = [
  '#6c63ff','#3b82f6','#06b6d4','#8b5cf6','#f59e0b',
  '#22c55e','#ef4444','#ec4899','#14b8a6','#f97316',
]

export default function Dashboard() {
  const [summary,     setSummary]     = useState(null)
  const [leaderboard, setLeaderboard] = useState([])
  const [loading,     setLoading]     = useState(true)

  useEffect(() => {
    Promise.all([
      getAnalyticsSummary().then(r => setSummary(r.data.data)),
      getLeaderboard(5).then(r => setLeaderboard(r.data.data)),
    ]).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="loading-wrap">
      <div className="spinner" />
      <p style={{ color: 'var(--text-muted)' }}>Loading dashboard…</p>
    </div>
  )

  const d    = summary || {}
  const avgs = d.averages || {}

  const sevData  = Object.entries(d.gap_severity      || {}).map(([name, value]) => ({ name, value }))
  const roleData = Object.entries(d.role_distribution || {}).map(([name, value]) => ({ name: name.split(' ')[0], fullName: name, value }))
  const missData = (d.top_missing_skills || []).slice(0, 8)
  const levelData = Object.entries(d.level_distribution || {}).map(([name, value]) => ({ name, value }))

  const hireTrue  = d.hire_predictions?.['true']  || d.hire_predictions?.['True']  || 0
  const hireFalse = d.hire_predictions?.['false'] || d.hire_predictions?.['False'] || 0

  return (
    <div>
      <div className="page-header">
        <h1>Skill Gap Dashboard</h1>
        <p>Component 4 — AI-Driven Recruitment Ecosystem (10 000-record dataset)</p>
      </div>

      {/* ── KPI Row ── */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {[
          { label: 'Total Reports',      value: d.total_reports ?? 0,          sub: 'candidates analysed',  color: undefined },
          { label: 'Avg Skill Match',    value: `${avgs.skill_match_pct ?? 0}%`, sub: 'across all roles',   color: '#6c63ff' },
          { label: 'Avg Hire Prob.',     value: `${avgs.hire_probability ?? 0}%`, sub: 'ML prediction',     color: '#22c55e' },
          { label: 'Skills In Progress', value: d.progress_tracking?.in_progress ?? 0, sub: 'learning underway', color: '#f59e0b' },
        ].map(({ label, value, sub, color }) => (
          <div key={label} className="stat-tile">
            <span className="label">{label}</span>
            <span className="value" style={color ? { color } : {}}>{value}</span>
            <span className="sub">{sub}</span>
          </div>
        ))}
      </div>

      {/* ── Secondary KPIs ── */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {[
          { label: 'Avg Projects',     value: avgs.projects_count   ?? 0, color: '#06b6d4' },
          { label: 'Avg Certs',        value: avgs.certifications   ?? 0, color: '#8b5cf6' },
          { label: 'Hire Predicted',   value: hireTrue,                    color: '#22c55e' },
          { label: 'Not Recommended',  value: hireFalse,                   color: '#ef4444' },
        ].map(({ label, value, color }) => (
          <div key={label} className="stat-tile">
            <span className="label">{label}</span>
            <span className="value" style={{ color, fontSize: 24 }}>{value}</span>
          </div>
        ))}
      </div>

      {/* ── Charts Row 1 ── */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Severity pie */}
        <div className="card">
          <p className="card-title"><AlertTriangle size={16} /> Gap Severity Distribution</p>
          {sevData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={sevData} cx="50%" cy="50%" outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}>
                  {sevData.map((e, i) => <Cell key={i} fill={SEV_COLOR[e.name] || '#6c63ff'} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="empty-state"><p>No data yet</p></div>}
        </div>

        {/* Role distribution */}
        <div className="card">
          <p className="card-title"><Users size={16} /> Candidates by Job Role</p>
          {roleData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={roleData} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fill: '#7c81a8', fontSize: 10 }} />
                <YAxis tick={{ fill: '#7c81a8', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }}
                  formatter={(val, name, props) => [val, props.payload.fullName || name]}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {roleData.map((_, i) => <Cell key={i} fill={ROLE_COLORS[i % ROLE_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-state"><p>No data yet</p></div>}
        </div>
      </div>

      {/* ── Charts Row 2 ── */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Missing skills */}
        <div className="card">
          <p className="card-title"><BookOpen size={16} /> Most Common Skill Gaps</p>
          {missData.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={missData} layout="vertical"
                margin={{ top: 0, right: 16, left: 80, bottom: 0 }}>
                <XAxis type="number" tick={{ fill: '#7c81a8', fontSize: 11 }} />
                <YAxis type="category" dataKey="skill" tick={{ fill: '#e8eaf6', fontSize: 11 }} width={80} />
                <Tooltip contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }} />
                <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-state"><p>Run analyses to see skill gap trends</p></div>}
        </div>

        {/* Job Level distribution */}
        <div className="card">
          <p className="card-title"><Briefcase size={16} /> Candidates by Job Level</p>
          {levelData.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={levelData} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fill: '#7c81a8', fontSize: 10 }} />
                <YAxis tick={{ fill: '#7c81a8', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }} />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-state"><p>No level data yet</p></div>}
        </div>
      </div>

      {/* ── Leaderboard ── */}
      <div className="card" style={{ marginBottom: 24 }}>
        <p className="card-title"><Award size={16} /> Top Candidates Leaderboard</p>
        {leaderboard.length ? (
          <div>
            {leaderboard.map((c, i) => (
              <div key={c.candidate_id || i} style={{
                display: 'flex', alignItems: 'center', gap: 14,
                padding: '12px 0', borderBottom: i < leaderboard.length - 1 ? '1px solid var(--border)' : 'none',
              }}>
                <span style={{
                  width: 30, height: 30, borderRadius: 8, flexShrink: 0,
                  background: i === 0 ? 'rgba(251,191,36,.15)' : 'rgba(108,99,255,.12)',
                  border: `1px solid ${i === 0 ? 'rgba(251,191,36,.3)' : 'rgba(108,99,255,.2)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, fontWeight: 800,
                  color: i === 0 ? '#fbbf24' : 'var(--accent-light)',
                }}>#{i + 1}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 700, fontSize: 13 }}>{c.candidate_name}</p>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {c.job_role} {c.job_level ? `· ${c.job_level}` : ''} {c.work_mode ? `· ${c.work_mode}` : ''}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span className={`badge ${c.gap_severity === 'Low' ? 'badge-success' : c.gap_severity === 'Medium' ? 'badge-warning' : 'badge-danger'}`}>
                    {c.gap_severity}
                  </span>
                  <span style={{ fontWeight: 800, fontSize: 15, color: '#22c55e' }}>{c.hire_probability}%</span>
                </div>
              </div>
            ))}
          </div>
        ) : <div className="empty-state"><p>No candidates yet</p></div>}
      </div>

      {/* ── Quick actions ── */}
      <div className="card">
        <p className="card-title"><TrendingUp size={16} /> Quick Actions</p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Link to="/analyze"  className="btn btn-primary"><ChevronRight size={14} /> Analyse New CV</Link>
          <Link to="/report"   className="btn btn-ghost"><ChevronRight size={14} /> View Reports</Link>
          <Link to="/career"   className="btn btn-ghost"><ChevronRight size={14} /> Career Path</Link>
          <Link to="/progress" className="btn btn-ghost"><ChevronRight size={14} /> Track Progress</Link>
        </div>
      </div>
    </div>
  )
}
