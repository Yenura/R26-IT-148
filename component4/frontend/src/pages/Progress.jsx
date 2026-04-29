import { useEffect, useState } from 'react'
import { getProgress, updateProgress, listReports } from '../api'
import toast from 'react-hot-toast'
import { TrendingUp, CheckCircle, Clock, Circle } from 'lucide-react'

const STATUS_META = {
  not_started: { label:'Not Started', color:'var(--text-muted)', icon: Circle,        badge:'badge-info'    },
  in_progress:  { label:'In Progress', color:'var(--warning)',   icon: Clock,          badge:'badge-warning' },
  completed:    { label:'Completed',   color:'var(--success)',   icon: CheckCircle,    badge:'badge-success' },
}

function ProgressRing({ pct }) {
  const r = 38, circ = 2 * Math.PI * r
  const offset = circ - (pct / 100) * circ
  return (
    <svg width={90} height={90}>
      <circle cx={45} cy={45} r={r} fill="none" stroke="rgba(108,99,255,.15)" strokeWidth={7}/>
      <circle cx={45} cy={45} r={r} fill="none" stroke="#6c63ff" strokeWidth={7}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" transform="rotate(-90 45 45)"
        style={{transition:'stroke-dashoffset .6s ease'}}/>
      <text x={45} y={50} textAnchor="middle" fontSize={15} fontWeight={800} fill="#e8eaf6">{pct}%</text>
    </svg>
  )
}

export default function Progress() {
  const [reports,  setReports]  = useState([])
  const [selId,    setSelId]    = useState('')
  const [progress, setProgress] = useState(null)
  const [loading,  setLoading]  = useState(false)

  useEffect(()=>{
    listReports().then(r=>setReports(r.data.data)).catch(()=>{})
  },[])

  const load = (id) => {
    if(!id) return
    setLoading(true)
    getProgress(id).then(r=>setProgress(r.data)).catch(()=>setProgress(null)).finally(()=>setLoading(false))
  }

  useEffect(()=>{ load(selId) },[selId])

  const changeStatus = async (skill, status) => {
    try {
      await updateProgress({ candidate_id: selId, skill, status, notes:'' })
      toast.success(`${skill} → ${status}`)
      load(selId)
    } catch(e) { toast.error('Update failed') }
  }

  const stats = progress?.stats || {}
  const skills = progress?.skills || []

  return (
    <div>
      <div className="page-header">
        <h1>Progress Tracking</h1>
        <p>Track your learning journey skill by skill</p>
      </div>

      <div className="card" style={{marginBottom:24}}>
        <div className="form-group" style={{margin:0}}>
          <label>SELECT CANDIDATE</label>
          <select className="form-control" style={{maxWidth:360}} value={selId}
            onChange={e=>setSelId(e.target.value)}>
            <option value="">— Pick a candidate —</option>
            {reports.map(r=>(
              <option key={r.candidate_id} value={r.candidate_id}>
                {r.candidate_name} — {r.job_role}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <div className="loading-wrap"><div className="spinner"/></div>}

      {!loading && selId && !progress && (
        <div className="alert alert-info">No progress data yet. Run an analysis first.</div>
      )}

      {!loading && progress && (
        <>
          {/* Stats */}
          <div className="grid-4" style={{marginBottom:24}}>
            <div className="stat-tile" style={{alignItems:'center'}}>
              <ProgressRing pct={stats.completion_pct||0}/>
              <span className="label">Completion</span>
            </div>
            <div className="stat-tile">
              <span className="label">Total Skills</span>
              <span className="value">{stats.total||0}</span>
            </div>
            <div className="stat-tile">
              <span className="label">In Progress</span>
              <span className="value" style={{color:'var(--warning)'}}>{stats.in_progress||0}</span>
            </div>
            <div className="stat-tile">
              <span className="label">Completed</span>
              <span className="value" style={{color:'var(--success)'}}>{stats.completed||0}</span>
            </div>
          </div>

          {/* Overall bar */}
          <div className="card" style={{marginBottom:24}}>
            <p className="card-title"><TrendingUp size={15}/> Overall Progress</p>
            <div style={{display:'flex',gap:20,marginBottom:12}}>
              {Object.entries(STATUS_META).map(([k,{label,color,badge}])=>(
                <div key={k} style={{display:'flex',alignItems:'center',gap:6}}>
                  <span className={`badge ${badge}`}>{stats[k]||0}</span>
                  <span style={{fontSize:12,color:'var(--text-muted)'}}>{label}</span>
                </div>
              ))}
            </div>
            <div className="progress-bar-wrap" style={{height:14}}>
              <div className="progress-bar-fill" style={{width:`${stats.completion_pct||0}%`}}/>
            </div>
          </div>

          {/* Skill list */}
          <div className="card">
            <p className="card-title">Skill Progress</p>
            {skills.length === 0
              ? <div className="empty-state"><p>No skills tracked yet</p></div>
              : skills.map((s,i)=>{
                  const m = STATUS_META[s.status] || STATUS_META.not_started
                  const Icon = m.icon
                  return (
                    <div key={i} style={{
                      display:'flex',alignItems:'center',gap:16,padding:'12px 0',
                      borderBottom: i<skills.length-1?'1px solid var(--border)':'none',
                    }}>
                      <Icon size={18} style={{color:m.color,flexShrink:0}}/>
                      <span style={{flex:1,fontSize:13,fontWeight:600}}>{s.skill}</span>
                      <span style={{fontSize:11,color:'var(--text-muted)',flex:1}}>{s.notes||''}</span>
                      <select
                        value={s.status}
                        onChange={e=>changeStatus(s.skill, e.target.value)}
                        style={{
                          background:'var(--bg-secondary)',border:'1px solid var(--border)',
                          color:'var(--text-primary)',borderRadius:'var(--radius)',
                          padding:'5px 10px',fontSize:12,cursor:'pointer',
                        }}>
                        <option value="not_started">Not Started</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  )
                })
            }
          </div>
        </>
      )}

      {!loading && !selId && (
        <div className="empty-state">
          <TrendingUp size={48}/>
          <p>Select a candidate to view and update their learning progress</p>
        </div>
      )}
    </div>
  )
}
