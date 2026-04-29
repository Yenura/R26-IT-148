import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAnalyticsSummary } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { Users, AlertTriangle, TrendingUp, Award, ChevronRight, BookOpen } from 'lucide-react'

const COLORS = ['#22c55e', '#f59e0b', '#ef4444', '#6c63ff', '#3b82f6']

const SEV_COLOR = { Low: '#22c55e', Medium: '#f59e0b', High: '#ef4444' }

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAnalyticsSummary()
      .then(s => setSummary(s.data.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="loading-wrap">
      <div className="spinner" />
      <p style={{ color: 'var(--text-muted)' }}>Loading dashboard…</p>
    </div>
  )

  const d = summary || {}
  const avgs = d.averages || {}

  /* Severity pie data */
  const sevData = Object.entries(d.gap_severity || {}).map(([name, value]) => ({ name, value }))

  /* Missing skills bar data */
  const missData = (d.top_missing_skills || []).map(x => ({ skill: x.skill, count: x.count }))

  /* Role bar data */
  const roleData = Object.entries(d.role_distribution || {}).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="page-header">
        <h1>Skill Gap Dashboard</h1>
        <p>Analytics overview — Component 4: Skill Gap Analysis & Career Development</p>
      </div>

      {/* ── KPI tiles ── */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        <div className="stat-tile">
          <span className="label">Total Reports</span>
          <span className="value">{d.total_reports ?? 0}</span>
          <span className="sub">candidates analysed</span>
        </div>
        <div className="stat-tile">
          <span className="label">Avg Skill Match</span>
          <span className="value" style={{ color: '#6c63ff' }}>
            {avgs.skill_match_pct ?? 0}%
          </span>
          <span className="sub">across all roles</span>
        </div>
        <div className="stat-tile">
          <span className="label">Avg Hire Prob.</span>
          <span className="value" style={{ color: '#22c55e' }}>
            {avgs.hire_probability ?? 0}%
          </span>
          <span className="sub">model prediction</span>
        </div>
        <div className="stat-tile">
          <span className="label">Skills In Progress</span>
          <span className="value" style={{ color: '#f59e0b' }}>
            {d.progress_tracking?.in_progress ?? 0}
          </span>
          <span className="sub">learning underway</span>
        </div>
      </div>

      {/* ── Charts row ── */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Severity pie */}
        <div className="card">
          <p className="card-title"><AlertTriangle size={16} /> Gap Severity Distribution</p>
          {sevData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={sevData} cx="50%" cy="50%" outerRadius={80}
                     dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                     labelLine={false}>
                  {sevData.map((e, i) => (
                    <Cell key={i} fill={SEV_COLOR[e.name] || COLORS[i]} />
                  ))}
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
                <XAxis dataKey="name" tick={{ fill: '#7c81a8', fontSize: 11 }}
                       tickFormatter={v => v.split(' ')[0]} />
                <YAxis tick={{ fill: '#7c81a8', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }} />
                <Bar dataKey="value" fill="#6c63ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="empty-state"><p>No data yet</p></div>}
        </div>
      </div>

      {/* ── Missing skills + Top Candidates ── */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Top missing skills */}
        <div className="card">
          <p className="card-title"><BookOpen size={16} /> Most Common Skill Gaps</p>
          {missData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={missData} layout="vertical"
                        margin={{ top: 0, right: 16, left: 60, bottom: 0 }}>
                <XAxis type="number" tick={{ fill: '#7c81a8', fontSize: 11 }} />
                <YAxis type="category" dataKey="skill" tick={{ fill: '#e8eaf6', fontSize: 12 }} width={60} />
                <Tooltip contentStyle={{ background: '#20243a', border: '1px solid #6c63ff44', borderRadius: 8 }} />
                <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>Run analyses to see skill gap trends</p></div>
          )}
        </div>

        {/* Top Candidates from analytics */}
        <div className="card">
          <p className="card-title"><Award size={16} /> Top Missing Skills Summary</p>
          {d.top_missing_skills?.length ? (
            <div>
              {d.top_missing_skills.map((item, i) => (
                <div key={item.skill} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '10px 0',
                  borderBottom: i < d.top_missing_skills.length - 1 ? '1px solid var(--border)' : 'none'
                }}>
                  <span style={{
                    width: 28, height: 28, borderRadius: 6,
                    background: 'rgba(239,68,68,.12)', border: '1px solid rgba(239,68,68,.25)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11, fontWeight: 800, color: '#ef4444', flexShrink: 0
                  }}>{i + 1}</span>
                  <span style={{ flex: 1, fontSize: 13, fontWeight: 600 }}>{item.skill}</span>
                  <div style={{ width: 80 }}>
                    <div className="progress-bar-wrap">
                      <div className="progress-bar-fill"
                        style={{ width: `${Math.min(item.count * 10, 100)}%`,
                                 background: 'linear-gradient(90deg,#ef4444,#f97316)' }}/>
                    </div>
                  </div>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', flexShrink: 0 }}>
                    {item.count} candidate{item.count !== 1 ? 's' : ''}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state"><p>No skill gap data yet</p></div>
          )}
        </div>
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
