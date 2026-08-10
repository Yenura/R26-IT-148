import axios from 'axios'

const mk = (url) => {
  const instance = axios.create({
    baseURL: `${url}/api/v1`,
    timeout: 120_000,
    headers: { 'Content-Type': 'application/json' },
  })
  // Attach JWT token from localStorage if present
  instance.interceptors.request.use((cfg) => {
    const token = localStorage.getItem('recruitai.token')
    if (token) cfg.headers.Authorization = `Bearer ${token}`
    return cfg
  })
  return instance
}

const mkHealth = (url) => `${url}/health`

// ── Unified backend (auth, resume, jobs, export) ──────────────
const _C0 = mk(import.meta.env.VITE_C0_URL || 'http://127.0.0.1:8000')

// Response interceptor: redirect to login on 401
_C0.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/auth/')) {
      localStorage.removeItem('recruitai.token')
      localStorage.removeItem('recruitai.role')
      window.location.href = '/'
    }
    return Promise.reject(err)
  }
)

export const C0 = _C0

// ── Component backends ────────────────────────────────────────
export const C1 = mk(import.meta.env.VITE_C1_URL || 'http://127.0.0.1:8001')
export const C2 = mk(import.meta.env.VITE_C2_URL || 'http://127.0.0.1:8002')
export const C3 = mk(import.meta.env.VITE_C3_URL || 'http://127.0.0.1:8003')
export const C4 = mk(import.meta.env.VITE_C4_URL || 'http://127.0.0.1:8004')

export const HEALTH = {
  c0: mkHealth(import.meta.env.VITE_C0_URL || 'http://127.0.0.1:8000'),
  c1: mkHealth(import.meta.env.VITE_C1_URL || 'http://127.0.0.1:8001'),
  c2: mkHealth(import.meta.env.VITE_C2_URL || 'http://127.0.0.1:8002'),
  c3: mkHealth(import.meta.env.VITE_C3_URL || 'http://127.0.0.1:8003'),
  c4: mkHealth(import.meta.env.VITE_C4_URL || 'http://127.0.0.1:8004'),
}

// ── Unified: Auth ─────────────────────────────────────────────
export const authRegisterCompany    = (payload) => C0.post('/auth/register/company', payload)
export const authLoginCompany       = (payload) => C0.post('/auth/login/company', payload)
export const authRegisterCandidate  = (payload) => C0.post('/auth/register/candidate', payload)
export const authLoginCandidate     = (payload) => C0.post('/auth/login/candidate', payload)
export const authMe                 = ()        => C0.get('/auth/me')
export const authGetProfile         = ()        => C0.get('/auth/profile')
export const authUpdateProfile      = (payload) => C0.put('/auth/profile', payload)
export const authChangePassword     = (payload) => C0.put('/auth/password', payload)
export const authUploadAvatar       = (formData) => C0.post('/auth/avatar', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})

// ── Unified: Jobs ─────────────────────────────────────────────
export const uJobsList         = ()              => C0.get('/jobs')
export const uJobsAll          = ()              => C0.get('/jobs/all')
export const c0JobsAll         = ()              => C0.get('/jobs/all')
export const uJobsPublic       = (id)            => C0.get(`/jobs/public/${id}`)
export const uJobsCreate       = (payload)       => C0.post('/jobs', payload)
export const uJobsGet          = (id)            => C0.get(`/jobs/${id}`)
export const uJobsUpdate       = (id, payload)   => C0.patch(`/jobs/${id}`, payload)
export const uJobsDelete       = (id)            => C0.delete(`/jobs/${id}`)
export const uJobsApply        = (id, payload)   => C0.post(`/jobs/${id}/apply`, payload)
export const uJobsWithdraw     = (id)             => C0.delete(`/jobs/${id}/apply`)
export const uJobsApplicants   = (id)            => C0.get(`/jobs/${id}/applicants`)

// ── Unified: Resume ───────────────────────────────────────────
export const uResumeUpload     = (formData)      => C0.post('/resume/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const uResumeList       = ()              => C0.get('/resume/')
export const uResumeGet        = (id)            => C0.get(`/resume/${id}`)
export const uResumeParse      = (text)          => C0.post(`/resume/parse?text=${encodeURIComponent(text)}`)
export const uResumeMatch      = (payload)       => C0.get('/resume/match', { params: payload })
export const uResumePredictRole= ()              => C0.get('/resume/predict-role')
export const uResumeUpdate     = (id, payload)   => C0.put(`/resume/${id}`, payload)
export const uResumeDelete     = (id)            => C0.delete(`/resume/${id}`)

// ── Unified: Export ───────────────────────────────────────────
export const uExportCsv        = (type = 'predictions') => C0.get(`/export/csv?type=${type}`, { responseType: 'blob' })
export const uExportExcel      = (type = 'predictions') => C0.get(`/export/excel?type=${type}`, { responseType: 'blob' })
export const uExportPdf        = (type = 'predictions') => C0.get(`/export/pdf?type=${type}`, { responseType: 'blob' })

// ── Component 1: Job & CV Intelligence ────────────────────────
export const c1Jobs        = ()              => C1.get('/jobs')
export const c1CreateJob   = (payload)      => C1.post('/jobs', payload)
export const c1MatchCv     = (payload)      => C1.post('/match/cv', payload)
export const c1Report      = (id)           => C1.get(`/match/report/${id}`)

// ── Component 2: AI Interview ─────────────────────────────────
export const c2Start       = (payload)      => C2.post('/interview/start', payload)
export const c2Submit      = (payload)      => C2.post('/interview/submit', payload)
export const c2Result      = (id)           => C2.get(`/interview/result/${id}`)
export const c2Session     = (id)           => C2.get(`/interview/session/${id}`)
export const c2Questions   = (role)         => C2.get(`/interview/questions/${encodeURIComponent(role)}`)
export const c2Jobs        = ()             => C2.get('/interview/jobs')

// ── Component 3: Candidate Ranking ────────────────────────────
export const c3Roles       = ()             => C3.get('/rank/jobs')
export const c3Rank        = (payload)      => C3.post('/rank/compute', payload)
export const c3Pipeline    = (jobId)        => C3.get(`/rank/pipeline/${jobId}`)
export const c3Results     = (jobId)        => C3.get(`/rank/results/${jobId}`)
export const c3Explain     = (candidateId)  => C3.get(`/rank/explain/${candidateId}`)
export const c3SetWeights  = (payload)      => C3.post('/rank/weights', payload)

// ── Component 4: Skill Gap & Career Development ───────────────
export const c4Roles           = ()           => C4.get('/skill-gap/roles')
export const c4Analyze         = (payload)    => C4.post('/skill-gap/analyze', payload)
export const c4Report          = (candidateId)=> C4.get(`/skill-gap/report/${candidateId}`)
export const c4Reports         = ()           => C4.get('/skill-gap/reports')
export const c4DeleteReport    = (candidateId)=> C4.delete(`/skill-gap/report/${candidateId}`)
export const c4CareerPath      = (payload)    => C4.post('/career/path', payload)
export const c4CareerRoles     = ()           => C4.get('/career/roles')
export const c4Resources       = (role)       => C4.get(`/career/resources/${encodeURIComponent(role)}`)
export const c4Roadmap         = (candidateId)=> C4.get(`/career/roadmap/${candidateId}`)
export const c4Progress        = (candidateId)=> C4.get(`/progress/${candidateId}`)
export const c4UpdateProgress  = (payload)    => C4.post('/progress/update', payload)
export const c4ResetProgress   = (candidateId)=> C4.delete(`/progress/${candidateId}`)
export const c4Summary         = ()           => C4.get('/analytics/summary')
export const c4Leaderboard     = (limit = 10) => C4.get(`/analytics/leaderboard?limit=${limit}`)
export const c4RoleInsights    = (role)       => C4.get(`/analytics/role-insights/${encodeURIComponent(role)}`)
