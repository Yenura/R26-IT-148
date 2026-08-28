import axios from 'axios'

const inFlightGetRequests = new Map()
const responseCache = new Map()
const CACHE_TTL_MS = 60000 // 60s cache
const REVALIDATE_AFTER_MS = 5000 // Background refresh after 5s

export const clearApiCache = () => {
  responseCache.clear()
}

const mk = (url) => {
  const instance = axios.create({
    baseURL: `${url}/api/v1`,
    timeout: 120_000,
  })
  // Attach JWT token from localStorage if present
  instance.interceptors.request.use((cfg) => {
    const token = localStorage.getItem('recruitai.token')
    if (token) cfg.headers.Authorization = `Bearer ${token}`
    return cfg
  })

  // Invalidate cache on mutations
  const originalPost = instance.post.bind(instance)
  const originalPut = instance.put.bind(instance)
  const originalDelete = instance.delete.bind(instance)

  instance.post = (...args) => {
    responseCache.clear()
    return originalPost(...args)
  }
  instance.put = (...args) => {
    responseCache.clear()
    return originalPut(...args)
  }
  instance.delete = (...args) => {
    responseCache.clear()
    return originalDelete(...args)
  }

  // Fast Cached GET with SWR background revalidation
  const originalGet = instance.get.bind(instance)
  instance.get = (requestUrl, config = {}) => {
    const key = `${url}:${requestUrl}:${JSON.stringify(config.params || {})}`
    const now = Date.now()

    // 1. Check if cached response is present
    if (responseCache.has(key)) {
      const entry = responseCache.get(key)
      const age = now - entry.timestamp
      if (age < CACHE_TTL_MS) {
        // If data is slightly aged, trigger non-blocking background revalidation
        if (age > REVALIDATE_AFTER_MS && !inFlightGetRequests.has(key)) {
          originalGet(requestUrl, config)
            .then((freshRes) => {
              responseCache.set(key, { timestamp: Date.now(), data: freshRes })
            })
            .catch(() => {})
        }
        return Promise.resolve(entry.data)
      }
      responseCache.delete(key)
    }

    // 2. Return in-flight promise to prevent duplicate concurrent requests
    if (inFlightGetRequests.has(key)) {
      return inFlightGetRequests.get(key)
    }

    const promise = originalGet(requestUrl, config)
      .then((res) => {
        responseCache.set(key, { timestamp: Date.now(), data: res })
        return res
      })
      .finally(() => {
        inFlightGetRequests.delete(key)
      })

    inFlightGetRequests.set(key, promise)
    return promise
  }

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
export const C3 = mk(
  import.meta.env.VITE_C3_URL
    ? (import.meta.env.VITE_C3_URL.endsWith('/api/v1') ? import.meta.env.VITE_C3_URL : `${import.meta.env.VITE_C3_URL}/api/v1`)
    : 'http://127.0.0.1:8003/api/v1'
)
export const C4 = mk(
  import.meta.env.VITE_C4_URL
    ? (import.meta.env.VITE_C4_URL.endsWith('/api/v1') ? import.meta.env.VITE_C4_URL : `${import.meta.env.VITE_C4_URL}/api/v1`)
    : 'http://127.0.0.1:8004/api/v1'
)

// ── Unified: Auth ─────────────────────────────────────────────
export const authGetProfile         = ()        => C0.get('/auth/profile')
export const authUpdateProfile      = (payload) => C0.put('/auth/profile', payload)
export const authChangePassword     = (payload) => C0.put('/auth/password', payload)
export const authUploadAvatar       = (formData) => C0.post('/auth/avatar', formData)

// ── Unified: Jobs ─────────────────────────────────────────────
export const c0JobsAll          = ()              => C0.get('/jobs/all')
export const uJobsPublic       = (id)            => C0.get(`/jobs/public/${id}`)
export const uJobsGet          = (id)            => C0.get(`/jobs/${id}`)
export const uJobsMy           = ()              => C0.get('/jobs')
export const uJobsCreate       = (payload)       => C0.post('/jobs', payload)
export const uJobsUpdate       = (id, payload)   => C0.patch(`/jobs/${id}`, payload)
export const uJobsDelete       = (id)            => C0.delete(`/jobs/${id}`)
export const uJobsApply        = (id, payload)   => C0.post(`/jobs/${id}/apply`, payload)
export const uJobsWithdraw     = (id)             => C0.delete(`/jobs/${id}/apply`)
export const uJobsApplicants   = (id)            => C0.get(`/jobs/${id}/applicants`)
export const uJobsApplicantCounts = ()            => C0.get('/jobs/applicant-counts')

// ── Unified: Resume ───────────────────────────────────────────
export const uResumeUpload     = (formData)      => C0.post('/resume/upload', formData)
export const uResumeList       = ()              => C0.get('/resume/')
export const uResumeUpdate     = (id, payload)   => C0.put(`/resume/${id}`, payload)
export const uResumeDelete     = (id)            => C0.delete(`/resume/${id}`)
export const uInterviewDetail  = (candidateId)   => C0.get(`/resume/interview-detail/${candidateId}`)
export const c0Predictions     = ()              => C0.get('/resume/predictions')
export const c0Applications    = ()              => C0.get('/jobs/applications')
export const c0InterviewScores = (candidateId)   => C0.get(`/resume/interview-scores/${candidateId}`)
export const c0ResumeMatch     = (resumeId, params = {}) => {
  const qs = new URLSearchParams({ resume_id: resumeId, ...params }).toString()
  return C0.get(`/resume/match?${qs}`)
}

// ── Unified: Export ──────────────────────────────────────────
export const c0ExportCSV  = (type = 'predictions') => C0.get(`/export/csv?type=${type}`, { responseType: 'blob' })
export const c0ExportExcel= (type = 'predictions') => C0.get(`/export/excel?type=${type}`, { responseType: 'blob' })
export const c0ExportPDF  = (type = 'predictions') => C0.get(`/export/pdf?type=${type}`, { responseType: 'blob' })

// ── Component 1: CV Analysis ──────────────────────────────────
export const c1Analyze         = (payload)       => C1.post('/cv/analyze', payload)
export const c1Roles           = ()              => C1.get('/roles')
export const c1Classify        = (payload)       => C1.post('/cv/classify', payload)
export const c1AnalyzeFile     = (formData)      => C1.post('/cv/analyze-file', formData)

// ── Component 2: AI Interview ─────────────────────────────────
export const c2Start       = (payload)      => C2.post('/interview/start', payload)
export const c2Submit      = (payload)      => C2.post('/interview/submit', payload)
export const c2Jobs        = ()             => C2.get('/interview/jobs')
export const c2RunCode     = (payload)      => C2.post('/interview/code/run', payload)

// ── Component 3: Candidate Ranking ────────────────────────────
export const c3Roles       = ()             => C3.get('/rank/jobs')
export const c3Rank        = (payload)      => C3.post('/rank/compute', payload)
export const c3Pipeline    = (jobId)        => C3.get(`/rank/pipeline/${jobId}`)
export const c3Explain     = (candidateId)  => C3.get(`/rank/explain/${candidateId}`)
export const c3Results     = (jobId)        => C3.get(`/rank/results/${jobId}`)

// ── Component 4: Skill Gap & Career Development ───────────────
export const c4Leaderboard     = (limit = 10) => C4.get(`/analytics/leaderboard?limit=${limit}`)
export const c4SkillGap        = (payload)    => C4.post('/skill-gap', payload)
export const c4SkillGapRoles   = ()           => C4.get('/skill-gap/roles')
export const c4SkillGapAnalyze = (payload)    => C4.post('/skill-gap/analyze', payload)
export const c4SkillGapApplied = (candidateId)=> C4.get(`/skill-gap/applied-jobs/${candidateId}`)
export const c4SkillGapSimulate= (payload)    => C4.post('/skill-gap/simulate', payload)
export const c4SkillGapGraph   = ()           => C4.get('/skill-gap/graph')
export const c4SkillGapReport  = (candidateId)=> C4.get(`/skill-gap/report/${candidateId}`)
export const c4SkillGapReports = (skip = 0, limit = 50) => C4.get(`/skill-gap/reports?skip=${skip}&limit=${limit}`)
export const c4SkillGapDeleteReport = (candidateId) => C4.delete(`/skill-gap/report/${candidateId}`)
export const c4CareerRec       = (payload)    => C4.post('/career/recommendation', payload)
export const c4CareerRoles     = ()           => C4.get('/career/roles')
export const c4CareerPath      = (payload)    => C4.post('/career/path', payload)
export const c4LearningPath    = (payload)    => C4.post('/career/learning-path', payload)
export const c4Progress        = (candidateId)=> C4.get(`/progress/${candidateId}`)
export const c4ProgressPopulate= (payload)    => C4.post('/progress/populate', payload)
export const c4ProgressSync    = (candidateId)=> C4.post(`/progress/sync-from-applied-interviews/${candidateId}`)
export const c4ProgressUpdate  = (payload)    => C4.post('/progress/update', payload)
export const c4ProgressDelete  = (candidateId)=> C4.delete(`/progress/${candidateId}`)
export const c4ProgressDeleteSkill = (candidateId, skill) => C4.delete(`/progress/${candidateId}/${encodeURIComponent(skill)}`)
