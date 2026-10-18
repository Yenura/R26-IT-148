/**
 * Normalize API response into an array.
 * Handles: direct arrays, {data: [...]}, {data: {data: [...]}},
 * and named collections like {resumes: [...]}, {jobs: [...]}.
 */
export const toArr = (r) => {
  const d = r?.data
  if (Array.isArray(d)) return d
  if (Array.isArray(d?.data)) return d.data
  if (Array.isArray(d?.resumes)) return d.resumes
  if (Array.isArray(d?.applications)) return d.applications
  if (Array.isArray(d?.predictions)) return d.predictions
  if (Array.isArray(d?.jobs)) return d.jobs
  return []
}

const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/

/**
 * Shared email check, mirroring the server validator
 * (recruit-ai/backend/schemas.py: check_email_format).
 * Format-only on purpose: deliverability (MX/disposable) is
 * enforced server-side at registration.
 */
export const isValidEmail = (v = '') => {
  const s = String(v).trim()
  if (!s || s.length > 254) return false
  if (!EMAIL_RE.test(s)) return false
  const [local, domain] = s.toLowerCase().split('@')
  if (!local || local.startsWith('.') || local.endsWith('.') || local.includes('..')) return false
  if (!domain || domain.includes('..') || /^[.-]/.test(domain) || /[.-]$/.test(domain)) return false
  return true
}

const C0_ORIGIN = (import.meta.env.VITE_C0_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

/**
 * Resolve a backend avatar path to an absolute URL.
 * The API returns app-relative paths (e.g. /api/v1/auth/avatar/<id>)
 * which would otherwise resolve against the frontend origin and 404.
 * Only http(s) and backend-relative paths are allowed through.
 */
export const avatarSrc = (url = '') => {
  const s = String(url || '').trim()
  if (!s) return ''
  if (/^https?:\/\//i.test(s)) return s
  if (s.startsWith('/')) return `${C0_ORIGIN}${s}`
  return ''
}
