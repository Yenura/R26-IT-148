/**
 * api.js — Axios client for Component 4 backend
 *
 * Fixes applied (code review):
 *   M5: Added response error interceptor with structured logging
 *   M5: Base URL reads from VITE_API_URL env var (no hardcoded localhost)
 *   M5: Request timeout set to 15 s
 */

import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor — centralised error logging
API.interceptors.response.use(
  (res) => res,
  (err) => {
    const status  = err?.response?.status
    const detail  = err?.response?.data?.detail || err.message || 'Unknown error'
    const url     = err?.config?.url || ''
    console.error(`[API] ${status ?? 'ERR'} ${url} —`, detail)
    return Promise.reject(err)
  }
)

// ── Skill Gap Analysis ─────────────────────────────────────────────────────────
/** Submit a candidate for skill gap analysis */
export const analyzeCandidate = (payload)     => API.post('/skill-gap/analyze', payload)

/** List all skill gap report summaries */
export const listReports      = ()            => API.get('/skill-gap/reports')

/** Get full skill gap report for one candidate */
export const getReport        = (candidateId) => API.get(`/skill-gap/report/${candidateId}`)

/** Delete a candidate's report */
export const deleteReport     = (candidateId) => API.delete(`/skill-gap/report/${candidateId}`)

/** Get the list of supported job roles */
export const getRoles         = ()            => API.get('/skill-gap/roles')

// ── Career Path ───────────────────────────────────────────────────────────────
/** Generate a career progression path for a candidate */
export const getCareerPath    = (payload)     => API.post('/career/path', payload)

/** Get learning resources for a specific job role */
export const getResources     = (role)        => API.get(`/career/resources/${encodeURIComponent(role)}`)

// ── Progress Tracking ─────────────────────────────────────────────────────────
/** Get the learning progress for a candidate */
export const getProgress      = (candidateId) => API.get(`/progress/${candidateId}`)

/** Update a skill's status for a candidate */
export const updateProgress   = (payload)     => API.post('/progress/update', payload)

/** Reset all progress entries for a candidate */
export const resetProgress    = (candidateId) => API.delete(`/progress/${candidateId}`)

// ── Analytics ─────────────────────────────────────────────────────────────────
/** Get aggregate analytics summary for the dashboard */
export const getAnalyticsSummary = ()               => API.get('/analytics/summary')

/** Get top candidates ranked by hire probability */
export const getLeaderboard      = (limit = 10)     => API.get(`/analytics/leaderboard?limit=${limit}`)

/** Get analytics breakdown for a specific job role */
export const getRoleInsights     = (role)           => API.get(`/analytics/role-insights/${encodeURIComponent(role)}`)

export default API
