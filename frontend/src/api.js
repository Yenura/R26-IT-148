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

// ── Unified: Auth ─────────────────────────────────────────────
export const authGetProfile         = ()        => C0.get('/auth/profile')
export const authUpdateProfile      = (payload) => C0.put('/auth/profile', payload)
export const authChangePassword     = (payload) => C0.put('/auth/password', payload)
export const authUploadAvatar       = (formData) => C0.post('/auth/avatar', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})

// ── Unified: Jobs ─────────────────────────────────────────────
export const c0JobsAll          = ()              => C0.get('/jobs/all')
export const uJobsPublic       = (id)            => C0.get(`/jobs/public/${id}`)
export const uJobsGet          = (id)            => C0.get(`/jobs/${id}`)
export const uJobsApply        = (id, payload)   => C0.post(`/jobs/${id}/apply`, payload)
export const uJobsWithdraw     = (id)             => C0.delete(`/jobs/${id}/apply`)
export const uJobsApplicants   = (id)            => C0.get(`/jobs/${id}/applicants`)

// ── Unified: Resume ───────────────────────────────────────────
export const uResumeUpload     = (formData)      => C0.post('/resume/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const uResumeList       = ()              => C0.get('/resume/')
export const uResumeUpdate     = (id, payload)   => C0.put(`/resume/${id}`, payload)
export const uResumeDelete     = (id)            => C0.delete(`/resume/${id}`)
export const uInterviewDetail  = (candidateId)   => C0.get(`/resume/interview-detail/${candidateId}`)

// ── Component 2: AI Interview ─────────────────────────────────
export const c2Start       = (payload)      => C2.post('/interview/start', payload)
export const c2Submit      = (payload)      => C2.post('/interview/submit', payload)
export const c2Jobs        = ()             => C2.get('/interview/jobs')
export const c2RunCode     = (payload)      => C2.post('/interview/code/run', payload)

// ── Component 3: Candidate Ranking ────────────────────────────
export const c3Roles       = ()             => C3.get('/rank/jobs')
export const c3Rank        = (payload)      => C3.post('/rank/compute', payload)
export const c3Pipeline    = (jobId)        => C3.get(`/rank/pipeline/${jobId}`)

// ── Component 4: Skill Gap & Career Development ───────────────
export const c4Leaderboard     = (limit = 10) => C4.get(`/analytics/leaderboard?limit=${limit}`)
