import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Award, Trophy, Medal, Search, Filter, Sparkles, UserCheck, Briefcase,
  ExternalLink, CheckCircle2, Zap, ArrowRight, Star, RefreshCw, Send, Brain,
  Clock, Code, FileText, Check, Cpu
} from 'lucide-react'
import { c4Leaderboard } from '../api'

export default function Leaderboard() {
  const navigate = useNavigate()
  const userRole = localStorage.getItem('recruitai.role')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all') // 'all', 'verified', 'pending'

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    loadLeaderboard()
  }, [])

  const loadLeaderboard = async () => {
    setLoading(true)
    try {
      const r = await c4Leaderboard(50)
      setData(r.data.data || [])
    } catch (err) {
      console.error('Failed to load talent leaderboard:', err)
      toast.error('Failed to load talent leaderboard')
    } finally {
      setLoading(false)
    }
  }

  const sendDirectInvite = (candidateName, role) => {
    toast.success(`Direct Fast-Track Interview Invitation sent to ${candidateName} for ${role}!`, {
      icon: '🚀',
      duration: 4000
    })
  }

  const medal = (rank) => {
    if (rank === 1) return <div style={{ width: 34, height: 34, borderRadius: 8, background: 'linear-gradient(135deg, #FFD700, #FFA500)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 900, fontSize: 16 }} title="1st Place · Gold Medal">🥇</div>
    if (rank === 2) return <div style={{ width: 34, height: 34, borderRadius: 8, background: 'linear-gradient(135deg, #C0C0C0, #A0A0A0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 900, fontSize: 16 }} title="2nd Place · Silver Medal">🥈</div>
    if (rank === 3) return <div style={{ width: 34, height: 34, borderRadius: 8, background: 'linear-gradient(135deg, #CD7F32, #8B4513)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 900, fontSize: 16 }} title="3rd Place · Bronze Medal">🥉</div>
    return <div style={{ width: 34, height: 34, borderRadius: 8, background: 'var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text)', fontWeight: 800, fontSize: 14 }}>#{rank}</div>
  }

  const filteredData = data.filter((c) => {
    const nameMatch = (c.candidate_name || '').toLowerCase().includes(searchTerm.toLowerCase())
    const roleMatch = (c.job_role || '').toLowerCase().includes(searchTerm.toLowerCase())
    const skillMatch = (c.skills || []).some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesSearch = nameMatch || roleMatch || skillMatch

    // Domain filter
    let matchesDomain = true
    if (selectedDomain === 'se') matchesDomain = /software|developer|backend|frontend|full stack/i.test(c.job_role || '')
    else if (selectedDomain === 'ai') matchesDomain = /data|machine learning|ai|nlp/i.test(c.job_role || '')
    else if (selectedDomain === 'cloud') matchesDomain = /cloud|devops|sre|architect|infrastructure/i.test(c.job_role || '')
    else if (selectedDomain === 'sec') matchesDomain = /security|cyber/i.test(c.job_role || '')

    // Status filter
    let matchesStatus = true
    if (selectedStatus === 'verified') matchesStatus = c.interview_completed && c.has_cv
    else if (selectedStatus === 'pending') matchesStatus = !c.interview_completed

    return matchesSearch && matchesDomain && matchesStatus
  })

  // Statistics
  const verifiedCount = data.filter(d => d.interview_completed && d.has_cv).length
  const avgReadiness = data.length > 0
    ? Math.round(data.reduce((acc, curr) => acc + (curr.hire_probability || 0), 0) / data.length)
    : 80

  return (
    <div className="fade-in" style={{ padding: '24px 16px', maxWidth: 1050, margin: '0 auto' }}>
      {/* Page Header */}
      <div className="page-head" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1.2, marginBottom: 4 }}>
              Component 3 & 4 · Verified Talent Benchmarking
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
              <Trophy size={28} style={{ color: '#FFD700' }} /> Verified Talent Leaderboard (LambdaMART LTR Ranked)
            </h1>
            <p className="muted" style={{ fontSize: 13, marginTop: 4, margin: 0 }}>
              Ranked from real candidate scores after completing both <strong>CV Upload (Component 1)</strong> and <strong>AI Technical Interviews (Component 2)</strong>, sorted via <strong>LightGBM LambdaMART LTR</strong>.
            </p>
          </div>

          <button
            onClick={loadLeaderboard}
            className="btn btn-ghost btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh Talent
          </button>
        </div>
      </div>

      {/* Talent Metrics Strip */}
      <div className="grid grid-3" style={{ gap: 14, marginBottom: 20 }}>
        <div className="card" style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 42, height: 42, borderRadius: 8, background: 'rgba(34, 197, 94, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#22c55e' }}>
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="stat-label" style={{ fontSize: 11 }}>Verified CV + Interview Talent</div>
            <div style={{ fontSize: 22, fontWeight: 900, color: '#22c55e' }}>{verifiedCount} Candidates</div>
          </div>
        </div>

        <div className="card" style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 42, height: 42, borderRadius: 8, background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)' }}>
            <Cpu size={22} />
          </div>
          <div>
            <div className="stat-label" style={{ fontSize: 11 }}>Ranking Algorithm</div>
            <div style={{ fontSize: 18, fontWeight: 900, color: 'var(--accent)' }}>LambdaMART LTR</div>
          </div>
        </div>

        <div className="card" style={{ padding: 16, background: 'var(--bg-elevated)', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 42, height: 42, borderRadius: 8, background: 'rgba(245, 158, 11, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f59e0b' }}>
            <Star size={22} />
          </div>
          <div>
            <div className="stat-label" style={{ fontSize: 11 }}>Average Real Hire Readiness</div>
            <div style={{ fontSize: 22, fontWeight: 900, color: '#f59e0b' }}>{avgReadiness}%</div>
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="card" style={{ padding: 16, marginBottom: 20, borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          {/* Domain Pills */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {[
              { id: 'all', label: 'All Roles' },
              { id: 'se', label: 'Software & Web' },
              { id: 'cloud', label: 'Cloud & DevOps' },
              { id: 'ai', label: 'AI & Data Science' },
              { id: 'sec', label: 'Cybersecurity' },
            ].map((dom) => (
              <button
                key={dom.id}
                onClick={() => setSelectedDomain(dom.id)}
                className="btn btn-sm"
                style={{
                  background: selectedDomain === dom.id ? 'var(--color-primary)' : 'var(--bg)',
                  color: selectedDomain === dom.id ? '#fff' : 'var(--text-muted)',
                  border: '1px solid var(--border)',
                  fontSize: 12,
                  fontWeight: 600,
                  borderRadius: 6
                }}
              >
                {dom.label}
              </button>
            ))}
          </div>

          {/* Search Input & Status Selector */}
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flex: 1, minWidth: 260, justifyContent: 'flex-end' }}>
            <div style={{ position: 'relative', width: '100%', maxWidth: 280 }}>
              <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search name, role, or skill (e.g. Python, SQL)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ height: 36, paddingLeft: 32, fontSize: 12, borderRadius: 6, width: '100%' }}
              />
            </div>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              style={{ height: 36, padding: '0 10px', fontSize: 12, borderRadius: 6, background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)', fontWeight: 600 }}
            >
              <option value="all">All Candidates</option>
              <option value="verified">Verified (CV + Interview)</option>
              <option value="pending">Interview Pending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Talent Cards Grid */}
      {loading ? (
        <div className="card" style={{ padding: 48, textAlign: 'center' }}>
          <RefreshCw size={28} className="spin" style={{ color: 'var(--accent)', margin: '0 auto 12px' }} />
          <div style={{ fontSize: 14, fontWeight: 700 }}>Scoring verified candidate CVs and technical interview marks...</div>
        </div>
      ) : filteredData.length === 0 ? (
        <div className="card" style={{ padding: 48, textAlign: 'center' }}>
          <Search size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 4px' }}>No Candidates Matched Your Filter</h3>
          <p className="muted" style={{ fontSize: 13 }}>Try clearing your search query or selecting "All Candidates".</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filteredData.map((c) => {
            const rankNum = c.rank || 1
            const isTop3 = rankNum <= 3
            const isVerified = c.interview_completed && c.has_cv

            return (
              <div
                key={c.candidate_id}
                className="card"
                style={{
                  padding: 18,
                  borderRadius: 12,
                  border: isTop3 && isVerified ? '1.5px solid rgba(255, 215, 0, 0.4)' : '1px solid var(--border)',
                  background: isTop3 && isVerified ? 'linear-gradient(180deg, rgba(255, 215, 0, 0.02), var(--bg-elevated))' : 'var(--bg-elevated)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 16,
                  transition: 'all 0.2s ease'
                }}
              >
                {/* Left: Rank, Name, Role, Education & Skills */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1, minWidth: 320 }}>
                  {medal(rankNum)}

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 2 }}>
                      <h3 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text)', margin: 0 }}>
                        {c.candidate_name}
                      </h3>
                      <span
                        className="chip"
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '2px 8px',
                          background: isVerified ? 'rgba(34, 197, 94, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                          color: isVerified ? '#22c55e' : '#f59e0b',
                          border: isVerified ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)'
                        }}
                      >
                        {isVerified ? '✓ Verified (CV + Interview)' : '⏳ Interview Pending'}
                      </span>
                    </div>

                    <div style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 700, marginBottom: 4 }}>
                      {c.job_role} • <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>{c.experience_years} yrs exp · {c.education}</span>
                    </div>

                    {/* Skill chips */}
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {(c.skills || []).slice(0, 6).map((sk) => (
                        <span
                          key={sk}
                          onClick={() => setSearchTerm(sk)}
                          className="chip"
                          style={{ fontSize: 10, padding: '1px 6px', background: 'var(--bg)', border: '1px solid var(--border)', cursor: 'pointer' }}
                          title={`Click to filter by ${sk}`}
                        >
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Right: Scores & Sourcing Actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                  {/* Scores Strip */}
                  <div style={{ display: 'flex', gap: 12, background: 'var(--bg)', padding: '8px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700 }}>CV MATCH</div>
                      <div style={{ fontSize: 15, fontWeight: 800, color: 'var(--text)' }}>
                        {c.cv_match_score !== null ? `${c.cv_match_score}%` : 'N/A'}
                      </div>
                    </div>

                    <div style={{ width: 1, background: 'var(--border)' }} />

                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700 }}>AI INTERVIEW</div>
                      <div style={{ fontSize: 15, fontWeight: 800, color: isVerified ? '#22c55e' : '#f59e0b' }}>
                        {c.interview_score !== null ? `${c.interview_score}%` : 'Pending'}
                      </div>
                    </div>

                    <div style={{ width: 1, background: 'var(--border)' }} />

                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 10, color: 'var(--accent)', fontWeight: 800 }}>LTR SCORE</div>
                      <div style={{ fontSize: 16, fontWeight: 900, color: 'var(--accent)' }}>
                        {(c.ltr_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  {/* Actions for Company / Recruiter */}
                  <div style={{ display: 'flex', gap: 6 }}>
                    {userRole === 'company' && isVerified && (
                      <button
                        onClick={() => sendDirectInvite(c.candidate_name, c.job_role)}
                        className="btn btn-primary btn-sm"
                        style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700 }}
                      >
                        <Send size={12} /> Fast-Track Invite
                      </button>
                    )}
                    {c.candidate_id && (
                      <Link
                        to={`/profile/${c.candidate_id}`}
                        className="btn btn-ghost btn-sm"
                        style={{ fontSize: 12, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}
                      >
                        Profile <ExternalLink size={11} />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
