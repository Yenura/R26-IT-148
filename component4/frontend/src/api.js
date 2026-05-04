import axios from 'axios'

const API = axios.create({ baseURL: 'http://127.0.0.1:8000/api/v1' })

export const analyzeSkillGap    = (data)       => API.post('/skill-gap/analyze', data)
export const getReport           = (id)         => API.get(`/skill-gap/report/${id}`)
export const listReports         = (skip=0,limit=50) => API.get(`/skill-gap/reports?skip=${skip}&limit=${limit}`)
export const deleteReport        = (id)         => API.delete(`/skill-gap/report/${id}`)
export const getRoles            = ()           => API.get('/skill-gap/roles')

export const generateCareerPath  = (data)       => API.post('/career/path', data)
export const getCareerResources  = (role)       => API.get(`/career/resources/${encodeURIComponent(role)}`)
export const getCareerRoles      = ()           => API.get('/career/roles')
export const getRoadmap          = (id)         => API.get(`/career/roadmap/${id}`)

export const updateProgress      = (data)       => API.post('/progress/update', data)
export const getProgress         = (id)         => API.get(`/progress/${id}`)
export const resetProgress       = (id)         => API.delete(`/progress/${id}`)

export const getAnalyticsSummary = ()           => API.get('/analytics/summary')
export const getLeaderboard      = (limit=10)   => API.get(`/analytics/leaderboard?limit=${limit}`)
export const getRoleInsights     = (role)       => API.get(`/analytics/role-insights/${encodeURIComponent(role)}`)
