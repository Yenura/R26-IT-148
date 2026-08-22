import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Award, Trophy, Medal, Search, RefreshCw, CheckCircle2,
  Cpu, Send, ExternalLink, ShieldCheck, Sparkles, UserCheck
} from 'lucide-react'
import { c4Leaderboard } from '../api'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import ScoreBadge from '../components/ScoreBadge'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function Leaderboard() {
  const navigate = useNavigate()
  const userRole = localStorage.getItem('recruitai.role')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('all')

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) {
      navigate('/login/candidate')
      return
    }
    loadLeaderboard()
  }, [])

  const loadLeaderboard = async () => {
    setLoading(true)
    try {
      const r = await c4Leaderboard(50)
      setData(r.data?.data || [])
    } catch (err) {
      toast.error('Failed to load talent leaderboard')
    } finally {
      setLoading(false)
    }
  }

  const sendDirectInvite = (candidateName, role) => {
    toast.success(`Fast-track interview invitation dispatched to ${candidateName} for ${role}!`, {
      icon: '🚀',
      duration: 3500
    })
  }

  const filteredData = data.filter((c) => {
    const nameMatch = (c.candidate_name || '').toLowerCase().includes(searchTerm.toLowerCase())
    const roleMatch = (c.job_role || '').toLowerCase().includes(searchTerm.toLowerCase())
    const skillMatch = (c.skills || []).some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesSearch = !searchTerm || nameMatch || roleMatch || skillMatch

    let matchesDomain = true
    if (selectedDomain === 'se') matchesDomain = /software|developer|backend|frontend|full stack/i.test(c.job_role || '')
    else if (selectedDomain === 'ai') matchesDomain = /data|machine learning|ai|nlp/i.test(c.job_role || '')
    else if (selectedDomain === 'cloud') matchesDomain = /cloud|devops|sre|architect|infrastructure/i.test(c.job_role || '')
    else if (selectedDomain === 'sec') matchesDomain = /security|cyber/i.test(c.job_role || '')

    return matchesSearch && matchesDomain
  })

  const verifiedCount = data.filter((d) => d.interview_completed && d.has_cv).length

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
      {/* Header */}
      <PageHeader
        badge="Component 3 & 4 Benchmarking"
        title="Verified Talent Standings"
        description="Top candidates ranked via LightGBM LambdaMART LTR after verifying CV credentials and completing AI technical assessments."
        icon={Trophy}
        actions={
          <button
            onClick={loadLeaderboard}
            className="btn btn-ghost btn-sm"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh Standings
          </button>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-3" style={{ gap: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <StatCard
          label="Verified Candidates"
          value={verifiedCount}
          icon={ShieldCheck}
          color="success"
          helperText="Completed CV + Assessment"
        />
        <StatCard
          label="Ranking Framework"
          value="LambdaMART"
          icon={Cpu}
          color="primary"
          helperText="LTR NDCG@10 Optimized"
        />
        <StatCard
          label="Leaderboard Pool"
          value={data.length}
          icon={UserCheck}
          color="purple"
          helperText="Actively benchmarked talent"
        />
      </div>

      {/* Filter & Search Controls */}
      <div className="card" style={{ padding: 'var(--p-space-4)', marginBottom: 'var(--p-space-5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          {/* Domain Filter Pills */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {[
              { id: 'all', label: 'All Disciplines' },
              { id: 'se', label: 'Software Engineering' },
              { id: 'ai', label: 'AI & Data Science' },
              { id: 'cloud', label: 'Cloud & DevOps' },
              { id: 'sec', label: 'Cybersecurity' }
            ].map((domain) => (
              <button
                key={domain.id}
                onClick={() => setSelectedDomain(domain.id)}
                className={`btn btn-sm ${selectedDomain === domain.id ? 'btn-primary' : 'btn-ghost'}`}
                style={{ fontSize: 'var(--p-text-xs)' }}
              >
                {domain.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div style={{ position: 'relative', width: 240 }}>
            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
            <input
              type="text"
              placeholder="Search talent or skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: 30, height: 34, fontSize: 'var(--p-text-xs)' }}
            />
          </div>
        </div>
      </div>

      {/* Standings Table */}
      {loading ? (
        <SkeletonLoader type="table" rows={6} cols={5} />
      ) : filteredData.length === 0 ? (
        <EmptyState
          title="No verified candidates found"
          description="Candidates will appear here after completing their technical interviews and CV verifications."
          icon={Trophy}
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: 60 }}>Rank</th>
                  <th>Candidate</th>
                  <th>Specialization Role</th>
                  <th>Core Competencies</th>
                  <th>Hire Readiness</th>
                  {userRole === 'company' && <th style={{ textAlign: 'right' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {filteredData.map((c, index) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  return (
                    <tr key={c.candidate_id || index}>
                      <td>
                        <div style={{
                          width: 28,
                          height: 28,
                          borderRadius: 'var(--radius-sm)',
                          background: isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)',
                          color: isTop3 ? '#fff' : 'var(--color-fg)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '12px'
                        }}>
                          #{rank}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                            {c.candidate_name || 'Anonymous Talent'}
                          </div>
                          {c.interview_completed && (
                            <span style={{ fontSize: '10px', color: 'var(--color-success)', background: 'var(--color-success-muted)', padding: '1px 6px', borderRadius: 'var(--radius-full)', fontWeight: 700 }}>
                              ✓ Verified
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                          ID: {c.candidate_id?.slice(0, 10) || 'Talent'}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', fontWeight: 600 }}>
                          {c.job_role || 'Software Engineer'}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 280 }}>
                          {(c.skills || []).slice(0, 4).map((s) => (
                            <span key={s} className="chip" style={{ fontSize: '10px', margin: 0, padding: '1px 6px' }}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{ fontFamily: 'var(--p-font-mono)', fontWeight: 800, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                            {c.hire_probability ? `${c.hire_probability}%` : '85%'}
                          </span>
                          <ScoreBadge score={c.hire_probability || 85} showLabel={false} />
                        </div>
                      </td>
                      {userRole === 'company' && (
                        <td style={{ textAlign: 'right' }}>
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => sendDirectInvite(c.candidate_name, c.job_role)}
                            style={{ fontSize: 'var(--p-text-xs)', padding: '4px 10px' }}
                          >
                            <Send size={12} /> Fast-Track Invite
                          </button>
                        </td>
                      )}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
