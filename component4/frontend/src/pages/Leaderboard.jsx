import { useEffect, useState } from 'react'
import { getLeaderboard } from '../api'
import { Trophy, Medal } from 'lucide-react'

const SEV_BADGE = { Low:'badge-success', Medium:'badge-warning', High:'badge-danger' }
const MEDAL_COLORS = ['#ffd700','#c0c0c0','#cd7f32']

export default function Leaderboard() {
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(()=>{
    getLeaderboard(20)
      .then(r=>setData(r.data.data))
      .catch(()=>{})
      .finally(()=>setLoading(false))
  },[])

  if(loading) return <div className="loading-wrap"><div className="spinner"/><p style={{color:'var(--text-muted)'}}>Loading…</p></div>

  return (
    <div>
      <div className="page-header">
        <h1>Candidate Leaderboard</h1>
        <p>Ranked by hire probability — Top candidates across all job roles</p>
      </div>

      {data.length === 0
        ? (
          <div className="empty-state">
            <Trophy size={48}/>
            <p>No candidates yet. Run an analysis to populate the leaderboard.</p>
          </div>
        )
        : (
          <>
            {/* Top 3 podium */}
            {data.length >= 3 && (
              <div className="grid-3" style={{marginBottom:24}}>
                {[data[1],data[0],data[2]].map((c,i)=>{
                  const rank = [2,1,3][i]
                  return (
                    <div key={c.candidate_id} className="card" style={{
                      textAlign:'center',
                      background: rank===1?'linear-gradient(135deg,rgba(108,99,255,.2),rgba(140,130,255,.08))':'var(--bg-card)',
                      border: rank===1?'1px solid var(--accent)':'1px solid var(--border)',
                      transform: rank===1?'scale(1.04)':'none',
                    }}>
                      <div style={{fontSize:28,marginBottom:8}}>
                        {rank===1?'🥇':rank===2?'🥈':'🥉'}
                      </div>
                      <p style={{fontSize:15,fontWeight:800,color:'var(--text-primary)'}}>{c.candidate_name}</p>
                      <p style={{fontSize:12,color:'var(--text-muted)',margin:'4px 0 10px'}}>{c.job_role}</p>
                      <div style={{fontSize:28,fontWeight:800,color:'#22c55e',marginBottom:8}}>
                        {c.hire_probability}%
                      </div>
                      <span className={`badge ${SEV_BADGE[c.gap_severity]}`}>{c.gap_severity} Gap</span>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Full table */}
            <div className="card">
              <p className="card-title"><Trophy size={15}/> Full Rankings</p>
              <div style={{overflowX:'auto'}}>
                <table style={{width:'100%',borderCollapse:'collapse',fontSize:13}}>
                  <thead>
                    <tr style={{borderBottom:'2px solid var(--border)'}}>
                      {['Rank','Candidate','ID','Job Role','Skill Match','Hire Probability','Gap Severity'].map(h=>(
                        <th key={h} style={{padding:'10px 12px',textAlign:'left',
                          fontSize:11,fontWeight:700,color:'var(--text-muted)',
                          textTransform:'uppercase',letterSpacing:'.6px'}}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((c,i)=>(
                      <tr key={c.candidate_id} style={{
                        borderBottom:'1px solid var(--border)',
                        transition:'background .15s',
                      }}
                        onMouseEnter={e=>e.currentTarget.style.background='var(--bg-card-hover)'}
                        onMouseLeave={e=>e.currentTarget.style.background='transparent'}>
                        <td style={{padding:'12px',fontWeight:800,color: i<3?MEDAL_COLORS[i]:'var(--text-muted)'}}>
                          {i<3?['🥇','🥈','🥉'][i]:`#${i+1}`}
                        </td>
                        <td style={{padding:'12px',fontWeight:600}}>{c.candidate_name}</td>
                        <td style={{padding:'12px',color:'var(--text-muted)',fontSize:12}}>{c.candidate_id}</td>
                        <td style={{padding:'12px'}}>{c.job_role}</td>
                        <td style={{padding:'12px'}}>
                          <div style={{display:'flex',alignItems:'center',gap:8}}>
                            <div className="progress-bar-wrap" style={{width:80,height:6}}>
                              <div className="progress-bar-fill" style={{width:`${c.skill_match_pct||0}%`}}/>
                            </div>
                            <span style={{fontSize:12,color:'var(--text-muted)'}}>{c.skill_match_pct||0}%</span>
                          </div>
                        </td>
                        <td style={{padding:'12px'}}>
                          <span style={{fontWeight:800,
                            color: c.hire_probability>=70?'#22c55e':c.hire_probability>=50?'#f59e0b':'#ef4444'}}>
                            {c.hire_probability}%
                          </span>
                        </td>
                        <td style={{padding:'12px'}}>
                          <span className={`badge ${SEV_BADGE[c.gap_severity]}`}>{c.gap_severity}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )
      }
    </div>
  )
}
