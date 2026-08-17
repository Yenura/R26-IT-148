import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Award, Trophy, Medal } from 'lucide-react'
import { c4Leaderboard } from '../api'

export default function Leaderboard() {
  const navigate = useNavigate()
  const [data, setData] = useState([])

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    if (!token) { navigate('/'); return }
    c4Leaderboard(10).then((r) => setData(r.data.data || [])).catch(() => {})
  }, [])

  const medal = (i) => i === 0 ? <Trophy size={20} style={{ color: '#FFD700' }} /> : i === 1 ? <Medal size={20} style={{ color: '#C0C0C0' }} /> : i === 2 ? <Medal size={20} style={{ color: '#CD7F32' }} /> : <span style={{ width: 20, textAlign: 'center', fontSize: 14, fontWeight: 700, color: 'var(--text-muted)' }}>{i + 1}</span>
  const bg = (i) => i === 0 ? 'linear-gradient(135deg, #FFD70210, #FFD70205)' : i === 1 ? 'linear-gradient(135deg, #C0C0C010, #C0C0C005)' : i === 2 ? 'linear-gradient(135deg, #CD7F3210, #CD7F3205)' : 'transparent'

  return (
    <div className="fade-in" style={{ padding: 28, maxWidth: 700, margin: '0 auto' }}>
      <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 4 }}>Leaderboard</h1>
      <p className="muted" style={{ fontSize: 13, marginBottom: 24 }}>Top candidates by hire probability</p>

      {data.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <Award size={32} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
          <div style={{ fontSize: 16, fontWeight: 600 }}>No data yet</div>
          <div className="muted" style={{ fontSize: 13 }}>Complete skill gap analyses to appear here.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {data.map((c, i) => (
            <div
              key={c.candidate_id || i}
              className="card"
              style={{
                padding: 16, background: bg(i), display: 'flex', alignItems: 'center', gap: 12,
              }}
            >
              {medal(i)}
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{c.candidate_name}</div>
                <div className="muted" style={{ fontSize: 12 }}>{c.job_role || 'General'}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--accent)' }}>{c.hire_probability?.toFixed(0) || 0}%</div>
                <div className="muted" style={{ fontSize: 11 }}>hire prob.</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
