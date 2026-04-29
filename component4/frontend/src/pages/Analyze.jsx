import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeSkillGap } from '../api'
import toast from 'react-hot-toast'
import { Brain, Plus, X, ChevronRight, Loader } from 'lucide-react'

const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'Machine Learning Engineer',
  'DevOps Engineer', 'Cybersecurity Analyst', 'Cloud Solutions Architect',
  'Database Administrator', 'Frontend Developer', 'Backend Developer',
  'Mobile App Developer', 'Network Engineer', 'AI/NLP Engineer',
  'QA/Test Engineer', 'IT Project Manager', 'Embedded Systems Engineer'
]
const EDU_OPTIONS  = [
  'B.Sc (Computer Science / IT)',
  'B.Tech / B.E (Computer Science / IT)',
  'BCA',
  'M.Sc (Computer Science / IT)',
  'M.Tech / M.E (Computer Science / IT)',
  'MCA',
  'PhD (Computer Science / AI)',
  'Diploma in IT',
  'Bootcamp Graduate'
]
const CERT_OPTIONS = ['None','AWS Certified','Google ML','Deep Learning Specialization']
const ALL_SKILLS   = ['Python','Java','C++','SQL','React','Linux','TensorFlow','Pytorch',
                      'Machine Learning','Deep Learning','NLP','Cybersecurity','Networking','Ethical Hacking']
const PRESETS = {
  'Software Engineer':     ['Java','SQL','C++','React'],
  'Data Scientist':        ['Python','SQL','Machine Learning','Deep Learning'],
  'Machine Learning Engineer': ['Python','TensorFlow','Pytorch','Linux'],
  'DevOps Engineer':       ['Linux','Networking','Python'],
  'Cybersecurity Analyst': ['Cybersecurity','Networking','Linux','Ethical Hacking'],
  'Cloud Solutions Architect': ['Linux','Networking'],
  'Database Administrator':['SQL','Linux'],
  'Frontend Developer':    ['React'],
  'Backend Developer':     ['Java','SQL','Python'],
  'Mobile App Developer':  ['Java','React'],
  'Network Engineer':      ['Networking','Linux'],
  'AI/NLP Engineer':       ['Python','NLP','Machine Learning','Deep Learning'],
  'QA/Test Engineer':      ['Python','Java'],
  'IT Project Manager':    [],
  'Embedded Systems Engineer': ['C++','Linux']
}

const F = ({label,children}) => (
  <div className="form-group"><label>{label}</label>{children}</div>
)

export default function Analyze() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('basic')
  const [form, setForm] = useState({
    candidate_id:'', candidate_name:'', job_role:'Software Engineer',
    experience_years:2, education:'B.Tech / B.E (Computer Science / IT)', certifications:'None',
    cv_matching_score:'', interview_score:'', mcq_score:'',
    descriptive_score:'', coding_score:'',
    skills:[], weak_topics:[], failed_mcq_topics:[],
  })
  const [si, setSi] = useState('')
  const [wi, setWi] = useState('')
  const [mi, setMi] = useState('')

  const set = (k,v) => setForm(f=>({...f,[k]:v}))
  const toggle = s => set('skills', form.skills.includes(s)
    ? form.skills.filter(x=>x!==s) : [...form.skills, s])
  const addCustom = () => { if(si.trim()&&!form.skills.includes(si.trim())) set('skills',[...form.skills,si.trim()]); setSi('') }
  const addTag = (f,v,clr) => { if(v.trim()&&!form[f].includes(v.trim())) set(f,[...form[f],v.trim()]); clr('') }
  const rmTag = (f,i) => set(f,form[f].filter((_,j)=>j!==i))

  const handleSubmit = async e => {
    e.preventDefault()
    if(!form.candidate_id) return toast.error('Candidate ID required')
    if(!form.candidate_name) return toast.error('Name required')
    if(!form.skills.length) return toast.error('Add at least one skill')
    const payload = {
      ...form,
      candidate_id: form.candidate_id.trim(),
      candidate_name: form.candidate_name.trim(),
      experience_years: Number(form.experience_years),
      cv_matching_score: form.cv_matching_score!=='' ? Number(form.cv_matching_score) : null,
      interview_score:   form.interview_score!==''   ? Number(form.interview_score)   : null,
      mcq_score:         form.mcq_score!==''         ? Number(form.mcq_score)         : null,
      descriptive_score: form.descriptive_score!=='' ? Number(form.descriptive_score) : null,
      coding_score:      form.coding_score!==''      ? Number(form.coding_score)      : null,
    }
    setLoading(true)
    try {
      await analyzeSkillGap(payload)
      toast.success('Analysis complete!')
      navigate(`/report/${form.candidate_id}`)
    } catch(err) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
    } finally { setLoading(false) }
  }



  return (
    <div>
      <div className="page-header">
        <h1>Analyse Candidate CV</h1>
        <p>Enter candidate details to generate a personalised Skill Gap Report & Career Plan</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="tabs">
          {[['basic','Candidate Info'],['scores','Interview Scores'],['topics','Weak Topics']].map(([k,l])=>(
            <button key={k} type="button" className={`tab-btn${tab===k?' active':''}`} onClick={()=>setTab(k)}>{l}</button>
          ))}
        </div>

        {tab==='basic' && (
          <div className="grid-2" style={{gap:20}}>
            <div className="card">
              <p className="card-title"><Brain size={15}/> Candidate Details</p>
              <F label="CANDIDATE ID *"><input className="form-control" placeholder="CAND-001" value={form.candidate_id} onChange={e=>set('candidate_id',e.target.value)} style={{width:'100%'}}/></F>
              <F label="FULL NAME *"><input className="form-control" placeholder="Jane Smith" value={form.candidate_name} onChange={e=>set('candidate_name',e.target.value)} style={{width:'100%'}}/></F>
              <F label="JOB ROLE">
                <select className="form-control" value={form.job_role} onChange={e=>set('job_role',e.target.value)}>
                  {JOB_ROLES.map(r=><option key={r}>{r}</option>)}
                </select>
              </F>
              <F label="EXPERIENCE (YRS)"><input className="form-control" type="number" min={0} max={30} value={form.experience_years} onChange={e=>set('experience_years',e.target.value)}/></F>
              <F label="EDUCATION">
                <select className="form-control" value={form.education} onChange={e=>set('education',e.target.value)}>
                  {EDU_OPTIONS.map(o=><option key={o}>{o}</option>)}
                </select>
              </F>
              <F label="CERTIFICATION">
                <select className="form-control" value={form.certifications} onChange={e=>set('certifications',e.target.value)}>
                  {CERT_OPTIONS.map(o=><option key={o}>{o}</option>)}
                </select>
              </F>
            </div>
            <div className="card">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:14}}>
                <p className="card-title" style={{margin:0}}>Skills *</p>
                <button type="button" className="btn btn-ghost" style={{fontSize:11,padding:'5px 10px'}}
                  onClick={()=>set('skills',[...new Set([...form.skills,...(PRESETS[form.job_role]||[])])])}>
                  <Plus size={12}/> Preset
                </button>
              </div>
              <div style={{display:'flex',flexWrap:'wrap',gap:6,marginBottom:14}}>
                {ALL_SKILLS.map(s=>(
                  <button key={s} type="button" onClick={()=>toggle(s)} style={{
                    padding:'4px 10px',borderRadius:999,fontSize:11,fontWeight:600,cursor:'pointer',transition:'all .2s',
                    border:'1px solid var(--border)',
                    background: form.skills.includes(s)?'var(--accent-glow)':'var(--bg-primary)',
                    color: form.skills.includes(s)?'var(--accent-light)':'var(--text-muted)',
                  }}>{s}</button>
                ))}
              </div>
              <div style={{display:'flex',gap:8,marginBottom:12}}>
                <input className="form-control" placeholder="Custom skill…" value={si}
                  onChange={e=>setSi(e.target.value)}
                  onKeyDown={e=>e.key==='Enter'&&(e.preventDefault(),addCustom())}/>
                <button type="button" className="btn btn-primary" style={{flexShrink:0}} onClick={addCustom}><Plus size={14}/></button>
              </div>
              <div>
                {!form.skills.length
                  ? <p style={{color:'var(--text-muted)',fontSize:12}}>No skills selected</p>
                  : form.skills.map((s,i)=>(
                    <span key={i} className="skill-chip chip-has">{s}
                      <X size={11} style={{cursor:'pointer',marginLeft:4}} onClick={()=>rmTag('skills',i)}/>
                    </span>
                  ))
                }
              </div>
            </div>
          </div>
        )}

        {tab==='scores' && (
          <div className="card">
            <p className="card-title">Component 1 & 2 Scores</p>
            <div className="alert alert-info">Scores from CV Matching (C1) and AI Interview (C2). Leave blank if unavailable.</div>
            <div className="grid-2">
              {[
                ['cv_matching_score','CV MATCHING SCORE (C1, 0–100)'],
                ['interview_score','INTERVIEW SCORE (C2, 0–100)'],
                ['mcq_score','MCQ SCORE (0–100)'],
                ['descriptive_score','DESCRIPTIVE SCORE (0–100)'],
                ['coding_score','CODING SCORE (0–100)'],
              ].map(([k,l])=>(
                <F key={k} label={l}>
                  <input className="form-control" type="number" min={0} max={100} placeholder="e.g. 72"
                    value={form[k]} onChange={e=>set(k,e.target.value)}/>
                </F>
              ))}
            </div>
          </div>
        )}

        {tab==='topics' && (
          <div className="grid-2" style={{gap:20}}>
            {[
              {label:'WEAK TOPICS (descriptive)', field:'weak_topics', val:wi, setVal:setWi},
              {label:'FAILED MCQ TOPICS',         field:'failed_mcq_topics', val:mi, setVal:setMi},
            ].map(({label,field,val,setVal})=>(
              <div key={field} className="card">
                <p className="card-title" style={{fontSize:13}}>{label}</p>
                <div style={{display:'flex',gap:8,marginBottom:12}}>
                  <input className="form-control" placeholder="Topic name…" value={val}
                    onChange={e=>setVal(e.target.value)}
                    onKeyDown={e=>e.key==='Enter'&&(e.preventDefault(),addTag(field,val,setVal))}/>
                  <button type="button" className="btn btn-primary" style={{flexShrink:0}}
                    onClick={()=>addTag(field,val,setVal)}><Plus size={14}/></button>
                </div>
                <div>
                  {!form[field].length
                    ? <p style={{color:'var(--text-muted)',fontSize:12}}>None added</p>
                    : form[field].map((t,i)=>(
                      <span key={i} className="skill-chip chip-required">{t}
                        <X size={11} style={{cursor:'pointer',marginLeft:4}} onClick={()=>rmTag(field,i)}/>
                      </span>
                    ))
                  }
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{marginTop:24,display:'flex',gap:12}}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading
              ? <><span style={{display:'inline-block',width:14,height:14,border:'2px solid #ffffff55',borderTopColor:'#fff',borderRadius:'50%',animation:'spin .8s linear infinite'}}/> Analysing…</>
              : <><ChevronRight size={14}/> Run Analysis</>
            }
          </button>
          <button type="button" className="btn btn-ghost"
            onClick={()=>setForm(f=>({...f,skills:[],cv_matching_score:'',interview_score:'',mcq_score:'',descriptive_score:'',coding_score:'',weak_topics:[],failed_mcq_topics:[]}))}>
            Reset
          </button>
        </div>
      </form>
    </div>
  )
}
