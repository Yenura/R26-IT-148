import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getSkillGapReport, listReports } from '../api'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from 'recharts'
import { FileText, AlertCircle, CheckCircle, BookOpen, ArrowRight } from 'lucide-react'

const SEV = { Low:'badge-success', Medium:'badge-warning', High:'badge-danger' }
const SCORE_COLOR = v => v>=70?'#22c55e':v>=50?'#f59e0b':'#ef4444'

function ScoreBox({ label, value }) {
  const c = value!=null ? SCORE_COLOR(value) : 'var(--text-muted)'
  return (
    <div style={{textAlign:'center',padding:'16px 20px',background:'var(--bg-secondary)',
                 borderRadius:'var(--radius)',border:'1px solid var(--border)'}}>
      <div style={{fontSize:11,fontWeight:700,color:'var(--text-muted)',textTransform:'uppercase',marginBottom:6}}>{label}</div>
      <div style={{fontSize:26,fontWeight:800,color:c}}>{value!=null?`${value}`:'-'}</div>
    </div>
  )
}

export default function Report() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [report,  setReport]  = useState(null)
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [selId,   setSelId]   = useState(id||'')

  useEffect(()=>{ listReports().then(r=>setReports(r.data.data)).catch(()=>{}) },[])

  useEffect(()=>{
    if(!selId){ setLoading(false); return }
    setLoading(true)
    getSkillGapReport(selId).then(r=>setReport(r.data.data)).catch(()=>setReport(null)).finally(()=>setLoading(false))
  },[selId])

  if(loading) return <div className="loading-wrap"><div className="spinner"/><p style={{color:'var(--text-muted)'}}>Loading report…</p></div>

  const radarData = report ? [
    {metric:'Skill Match', value: report.skill_match_pct},
    {metric:'Gap Score',   value: Math.round(report.gap_score*100)},
    {metric:'Hire Prob',   value: report.hire_probability},
    {metric:'CV Score',    value: report.cv_matching_score??0},
    {metric:'Interview',   value: report.interview_score??0},
  ] : []

  const missingData = [
    ...(report?.missing_required||[]).map(s=>({skill:s,type:'Required',count:1})),
    ...(report?.missing_optional||[]).map(s=>({skill:s,type:'Optional',count:1})),
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Skill Gap Report</h1>
        <p>Detailed breakdown of skill gaps, learning plan and career suggestions</p>
      </div>

      {/* Candidate selector */}
      <div className="card" style={{marginBottom:24}}>
        <div style={{display:'flex',gap:12,alignItems:'center',flexWrap:'wrap'}}>
          <select className="form-control" style={{maxWidth:280}}
            value={selId} onChange={e=>{setSelId(e.target.value); navigate(`/report/${e.target.value}`)}}>
            <option value="">— Select a candidate —</option>
            {reports.map(r=>(
              <option key={r.candidate_id} value={r.candidate_id}>
                {r.candidate_name} ({r.candidate_id}) — {r.job_role}
              </option>
            ))}
          </select>
          <Link to="/analyze" className="btn btn-primary"><ArrowRight size={14}/> New Analysis</Link>
        </div>
      </div>

      {!report ? (
        <div className="empty-state">
          <FileText size={48}/>
          <p>Select a candidate or <Link to="/analyze" style={{color:'var(--accent-light)'}}>run a new analysis</Link></p>
        </div>
      ) : (
        <>
          {/* Header band */}
          <div className="card" style={{marginBottom:20,background:'linear-gradient(135deg,#1a1d2788,#20243a)'}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:16}}>
              <div>
                <h2 style={{fontSize:20,fontWeight:800,color:'var(--text-primary)'}}>{report.candidate_name}</h2>
                <p style={{color:'var(--text-muted)',fontSize:13,marginTop:4}}>{report.candidate_id} · {report.job_role}</p>
                <div style={{marginTop:10,display:'flex',gap:8,flexWrap:'wrap'}}>
                  <span className={`badge ${SEV[report.gap_severity]}`}>Gap: {report.gap_severity}</span>
                  <span className={`badge ${report.predicted_hire?'badge-success':'badge-danger'}`}>
                    {report.predicted_hire?'Hire Predicted':'Not Recommended'}
                  </span>
                </div>
              </div>
              <div style={{display:'flex',gap:12,flexWrap:'wrap'}}>
                <ScoreBox label="Skill Match"  value={report.skill_match_pct+'%'}/>
                <ScoreBox label="Hire Prob"    value={report.hire_probability+'%'}/>
                <ScoreBox label="CV Score"     value={report.cv_matching_score}/>
                <ScoreBox label="Interview"    value={report.interview_score}/>
              </div>
            </div>
          </div>

          <div className="grid-2" style={{marginBottom:20}}>
            {/* Radar */}
            <div className="card">
              <p className="card-title">Performance Radar</p>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(108,99,255,.2)"/>
                  <PolarAngleAxis dataKey="metric" tick={{fill:'#7c81a8',fontSize:11}}/>
                  <Radar dataKey="value" stroke="#6c63ff" fill="#6c63ff" fillOpacity={0.25}/>
                  <Tooltip contentStyle={{background:'#20243a',border:'1px solid #6c63ff44',borderRadius:8}}/>
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Skills snapshot */}
            <div className="card">
              <p className="card-title">Skill Snapshot</p>
              <div style={{marginBottom:12}}>
                <p style={{fontSize:12,color:'var(--text-muted)',marginBottom:6}}>Present Skills</p>
                {report.present_skills.map((s,i)=><span key={i} className="skill-chip chip-has">{s}</span>)}
              </div>
              <hr className="divider"/>
              <div style={{marginBottom:12}}>
                <p style={{fontSize:12,color:'var(--danger)',marginBottom:6}}>Missing Required</p>
                {report.missing_required.length
                  ? report.missing_required.map((s,i)=><span key={i} className="skill-chip chip-required">{s}</span>)
                  : <span style={{fontSize:12,color:'var(--success)'}}>None — all required skills present!</span>}
              </div>
              <div>
                <p style={{fontSize:12,color:'var(--warning)',marginBottom:6}}>Missing Optional</p>
                {report.missing_optional.length
                  ? report.missing_optional.map((s,i)=><span key={i} className="skill-chip chip-optional">{s}</span>)
                  : <span style={{fontSize:12,color:'var(--text-muted)'}}>None</span>}
              </div>
            </div>
          </div>

          {/* Gap categories */}
          <div className="grid-2" style={{marginBottom:20}}>
            {[
              {title:'Technical Gaps',      data:report.technical_gaps,       color:'#3b82f6'},
              {title:'ML / AI Gaps',        data:report.ml_ai_gaps,           color:'#8b5cf6'},
              {title:'Security Gaps',       data:report.security_gaps,        color:'#ef4444'},
              {title:'Knowledge Gaps',      data:report.knowledge_gaps,       color:'#f59e0b'},
            ].map(({title,data,color})=>(
              <div key={title} className="card">
                <p className="card-title" style={{color}}><AlertCircle size={14}/> {title}</p>
                {data.length
                  ? data.map((s,i)=>(
                    <div key={i} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',
                      borderBottom:'1px solid var(--border)'}}>
                      <div style={{width:8,height:8,borderRadius:'50%',background:color,flexShrink:0}}/>
                      <span style={{fontSize:13}}>{s}</span>
                    </div>
                  ))
                  : <p style={{color:'var(--success)',fontSize:13}}><CheckCircle size={13}/> No gaps here</p>}
              </div>
            ))}
          </div>

          {/* Learning plan */}
          <div className="card" style={{marginBottom:20}}>
            <p className="card-title"><BookOpen size={15}/> Learning Plan</p>
            <div className="timeline">
              {report.learning_plan.map((phase,i)=>(
                <div key={i} className="timeline-item">
                  <div className="timeline-dot"/>
                  <div style={{background:'var(--bg-secondary)',padding:'14px 16px',borderRadius:'var(--radius)',border:'1px solid var(--border)'}}>
                    <p style={{fontWeight:700,fontSize:13,marginBottom:8,color:'var(--accent-light)'}}>{phase.title}</p>
                    <p style={{fontSize:12,color:'var(--text-muted)',marginBottom:10}}>
                      Skills: <strong style={{color:'var(--text-primary)'}}>{phase.skills.join(', ')}</strong>
                    </p>
                    {phase.resources.map((r,j)=>(
                      <div key={j} style={{display:'flex',alignItems:'center',gap:10,padding:'8px 0',borderTop:'1px solid var(--border)'}}>
                        <span className={`badge badge-${r.priority==='Critical'?'danger':r.priority==='High'?'warning':'info'}`} style={{flexShrink:0}}>{r.priority}</span>
                        <div style={{flex:1}}>
                          <p style={{fontSize:12,fontWeight:600}}>{r.course}</p>
                          <p style={{fontSize:11,color:'var(--text-muted)'}}>{r.duration} · {r.level}</p>
                        </div>
                        <a href={r.url} target="_blank" rel="noreferrer"
                          style={{fontSize:11,color:'var(--accent-light)',textDecoration:'none'}}>
                          Open ↗
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Suggestions */}
          <div className="grid-2" style={{marginBottom:20}}>
            <div className="card">
              <p className="card-title">Improvement Suggestions</p>
              {report.improvement_suggestions.length
                ? report.improvement_suggestions.map((s,i)=>(
                  <div key={i} className="alert alert-warning" style={{marginBottom:8}}>{s}</div>
                ))
                : <div className="alert alert-success">Great profile — no major suggestions!</div>}
            </div>
            <div className="card">
              <p className="card-title">Career Path Suggestions</p>
              {report.career_path_suggestions.map((s,i)=>(
                <div key={i} className="alert alert-info" style={{marginBottom:8}}>{s}</div>
              ))}
              <div style={{marginTop:12}}>
                <Link to="/career" className="btn btn-primary" style={{fontSize:12}}>
                  <ArrowRight size={13}/> Full Career Path
                </Link>
              </div>
            </div>
          </div>

          {/* Roadmap */}
          <div className="card">
            <p className="card-title">Skill Roadmap</p>
            <div style={{display:'flex',gap:12,fontSize:11,marginBottom:12}}>
              {[['#22c55e','Has Skill'],['#ef4444','Required (Missing)'],['#f59e0b','Optional (Missing)']].map(([c,l])=>(
                <span key={l} style={{display:'flex',alignItems:'center',gap:5}}>
                  <span style={{width:10,height:10,borderRadius:'50%',background:c,display:'inline-block'}}/>
                  {l}
                </span>
              ))}
            </div>
            <div className="roadmap-grid">
              {report.roadmap_nodes.map(n=>(
                <div key={n.id} className={`roadmap-node node-${n.status==='has'?'has':n.status==='missing_required'?'required':'optional'}`}>
                  {n.label}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
