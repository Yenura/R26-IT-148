import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Skill Gap ──────────────────────────────────────────────────────────────
export const analyzeSkillGap   = (payload)       => api.post('/skill-gap/analyze', payload)
export const getSkillGapReport = (candidateId)   => api.get(`/skill-gap/report/${candidateId}`)
export const listReports       = (skip=0,limit=20) => api.get('/skill-gap/reports', { params: { skip, limit } })
export const deleteReport      = (candidateId)   => api.delete(`/skill-gap/report/${candidateId}`)

// ── Career ─────────────────────────────────────────────────────────────────
export const generateCareerPath = (payload)   => api.post('/career/path', payload)
export const getRoleResources   = (jobRole)   => api.get(`/career/resources/${encodeURIComponent(jobRole)}`)
export const getCandidateRoadmap = (id)       => api.get(`/career/roadmap/${id}`)

// ── Progress ───────────────────────────────────────────────────────────────
export const updateProgress   = (payload)     => api.post('/progress/update', payload)
export const getProgress      = (candidateId) => api.get(`/progress/${candidateId}`)
export const resetProgress    = (candidateId) => api.delete(`/progress/${candidateId}`)

// ── Analytics ──────────────────────────────────────────────────────────────
export const getAnalyticsSummary = () => api.get('/analytics/summary')
export const getLeaderboard      = (limit=10) => api.get('/analytics/leaderboard', { params: { limit } })

export default api
