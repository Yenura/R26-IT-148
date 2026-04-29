import { useEffect, useState } from 'react'
import { listReports, generateCareerPath, getRoleResources } from '../api'
import { MapPin, ArrowRight, BookOpen, ChevronRight } from 'lucide-react'

const ROLES = ['Data Scientist','AI Researcher','Software Engineer','Cybersecurity Analyst']

export default function CareerPath() {
  const [reports,   setReports]   = useState([])
  const [selId,     setSelId]     = useState('')
  const [selRole,   setSelRole]   = useState('Data Scientist')
  const [pathData,  setPathData]  = useState(null)
  const [resources, setResources] = useState([])
  const [loading,   setLoading]   = useState(false)
  const [resLoading,setResLoading]= useState(false)

  useEffect(()=>{
    listReports().then(r=>setReports(r.data.data)).catch(()=>{})
  },[])

  useEffect(()=>{
    setResLoading(true)
    getRoleResources(selRole).then(r=>setResources(r.data.resources)).catch(()=>setResources([])).finally(()=>setResLoading(false))
  },[selRole])

  const handleGenerate = async () => {
    if(!selId) return
    const rep = reports.find(r=>r.candidate_id===selId)
    if(!rep) return
    setLoading(true)
    try {
      const r = await generateCareerPath({
        candidate_id: rep.candidate_id,
        current_role: rep.job_role,
        skills: rep.present_skills||[],
        experience_years: 3,
      })
      setPathData(r.data.data)
      setSelRole(rep.job_role)
    } catch(e) {
      console.error(e)
    } finally { setLoading(false) }
  }

  const PRI_COLOR = { Required:'var(--accent)', Optional:'var(--warning)' }

  return (
    <div>
      <div className="page-header">
        <h1>Career Path & Learning Resources</h1>
        <p>Visualise your growth track and access curated learning resources per job role</p>
      </div>

      {/* Controls */}
      <div className="card" style={{marginBottom:24}}>
        <div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'flex-end'}}>
          <div className="form-group" style={{margin:0,flex:1,minWidth:200}}>
            <label>SELECT CANDIDATE</label>
            <select className="form-control" value={selId} onChange={e=>setSelId(e.target.value)}>
              <option value="">— Pick a candidate —</option>
              {reports.map(r=>(
                <option key={r.candidate_id} value={r.candidate_id}>
                  {r.candidate_name} — {r.job_role}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{margin:0,flex:1,minWidth:200}}>
            <label>JOB ROLE (for resources)</label>
            <select className="form-control" value={selRole} onChange={e=>setSelRole(e.target.value)}>
              {ROLES.map(r=><option key={r}>{r}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={!selId||loading}>
            {loading?'Generating…':<><MapPin size={14}/> Generate Path</>}
          </button>
        </div>
      </div>

      {/* Career milestones */}
      {pathData && (
        <div className="card" style={{marginBottom:24}}>
          <p className="card-title"><MapPin size={15}/> Career Milestone Track — {pathData.current_role}</p>
          <div style={{display:'flex',alignItems:'center',gap:0,overflowX:'auto',paddingBottom:8}}>
            {pathData.path_nodes.map((node,i)=>(
              <div key={i} style={{display:'flex',alignItems:'center',flexShrink:0}}>
                <div style={{
                  display:'flex',flexDirection:'column',alignItems:'center',gap:8,padding:'0 6px',
                }}>
                  <div style={{
                    width:14,height:14,borderRadius:'50%',flexShrink:0,
                    background: node.current?'var(--accent)':'var(--border)',
                    boxShadow: node.current?'0 0 12px var(--accent-glow)':'none',
                    border: node.current?'3px solid var(--accent-light)':'3px solid var(--bg-card)',
                  }}/>
                  <div style={{
                    padding:'6px 12px',borderRadius:'var(--radius)',fontSize:12,fontWeight:600,
                    background: node.current?'var(--accent-glow)':'var(--bg-secondary)',
                    color: node.current?'var(--accent-light)':'var(--text-muted)',
                    border: `1px solid ${node.current?'var(--accent)':'var(--border)'}`,
                    whiteSpace:'nowrap',
                  }}>{node.title}</div>
                </div>
                {i < pathData.path_nodes.length-1 && (
                  <ChevronRight size={16} style={{color:'var(--border)',flexShrink:0}}/>
                )}
              </div>
            ))}
          </div>

          <hr className="divider"/>
          <div className="grid-2">
            <div>
              <p style={{fontSize:12,fontWeight:700,color:'var(--text-muted)',marginBottom:8}}>CURRENT LEVEL</p>
              <span className="badge badge-accent" style={{fontSize:14,padding:'6px 16px'}}>{pathData.current_level}</span>
            </div>
            <div>
              <p style={{fontSize:12,fontWeight:700,color:'var(--text-muted)',marginBottom:8}}>LATERAL OPTIONS</p>
              <div style={{display:'flex',gap:6,flexWrap:'wrap'}}>
                {pathData.lateral_options.length
                  ? pathData.lateral_options.map((o,i)=><span key={i} className="badge badge-info">{o}</span>)
                  : <span style={{color:'var(--text-muted)',fontSize:12}}>None identified</span>}
              </div>
            </div>
          </div>

          {pathData.missing_for_next_level.length > 0 && (
            <div className="alert alert-warning" style={{marginTop:16}}>
              <strong>Skills needed for next level:</strong> {pathData.missing_for_next_level.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Resources */}
      <div className="card">
        <p className="card-title"><BookOpen size={15}/> Learning Resources — {selRole}</p>
        {resLoading
          ? <div className="loading-wrap" style={{minHeight:120}}><div className="spinner"/></div>
          : resources.length === 0
            ? <div className="empty-state"><p>No resources found</p></div>
            : (
              <div style={{display:'grid',gap:14}}>
                {resources.map((r,i)=>(
                  <div key={i} style={{
                    display:'flex',alignItems:'center',gap:16,padding:'14px 16px',
                    background:'var(--bg-secondary)',borderRadius:'var(--radius)',
                    border:'1px solid var(--border)',transition:'border-color .2s',
                  }}
                    onMouseEnter={e=>e.currentTarget.style.borderColor='var(--accent)'}
                    onMouseLeave={e=>e.currentTarget.style.borderColor='var(--border)'}>
                    <div style={{
                      width:36,height:36,borderRadius:'var(--radius)',flexShrink:0,
                      background: r.priority==='Required'?'rgba(108,99,255,.15)':'rgba(245,158,11,.12)',
                      display:'flex',alignItems:'center',justifyContent:'center',
                      fontSize:11,fontWeight:800,color:PRI_COLOR[r.priority],
                    }}>{i+1}</div>
                    <div style={{flex:1,minWidth:0}}>
                      <p style={{fontSize:13,fontWeight:700,marginBottom:3}}>{r.skill}</p>
                      <p style={{fontSize:12,color:'var(--text-muted)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{r.course}</p>
                      <p style={{fontSize:11,color:'var(--text-muted)',marginTop:2}}>{r.duration} · {r.level}</p>
                    </div>
                    <span className={`badge badge-${r.priority==='Required'?'accent':'warning'}`}>{r.priority}</span>
                    <a href={r.url} target="_blank" rel="noreferrer" className="btn btn-ghost"
                      style={{fontSize:11,padding:'5px 12px',flexShrink:0}}>
                      Open <ArrowRight size={11}/>
                    </a>
                  </div>
                ))}
              </div>
            )
        }
      </div>
    </div>
  )
}
