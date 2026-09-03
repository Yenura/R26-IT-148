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

/**
 * Extract a user-friendly error message from an API error response.
 */
export const getErrorMessage = (err) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.msg ? d.msg.replace(/^Value error,\s*/i, '') : JSON.stringify(d))).join(', ')
  }
  if (typeof detail === 'object' && detail !== null) {
    return Object.values(detail).join(', ')
  }
  return err?.message || 'Invalid email or password'
}

/**
 * Clean candidate name extracted from CV/resume text.
 */
export const cleanCandidateName = (rawName, fallbackFilename) => {
  if (!rawName) return (fallbackFilename || 'Candidate').replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ')
  let name = String(rawName).trim()
  name = name.replace(/\s*[\(\[]\s*CV\s*[\)\]]/gi, '')
  name = name.replace(/^(?:phone|email|name|profile|student)\s*:\s*/i, '')
  name = name.split(/\s*[\n\r·|:;•]\s*/)[0].trim()
  const words = name.split(/\s+/).filter(Boolean)
  if (words.length > 3) {
    name = words.slice(0, 3).join(' ')
  }
  return name || 'Candidate Profile'
}

/**
 * Normalize company name for consistent display.
 */
export const cleanCompanyName = (name) => {
  if (!name) return 'General Tech'
  let c = String(name).trim()
  c = c.replace(/\s*\d{6,}\b/g, '')
  if (/^techcorp\b/i.test(c)) return 'TechCorp'
  if (c.toLowerCase() === 'slt') return 'SLT Mobitel'
  if (c.toLowerCase() === 'virtusa') return 'Virtusa'
  if (c.toLowerCase() === 'syscolabs' || c.toLowerCase() === 'sysco labs') return 'Sysco LABS'
  if (c.toLowerCase() === 'ifs') return 'IFS'
  if (c.toLowerCase() === 'wso2') return 'WSO2'
  if (c.toLowerCase() === '99x') return '99x'
  if (c.toLowerCase() === 'codegen') return 'CodeGen'
  if (c.toLowerCase() === 'tech corp' || c.toLowerCase() === 'techcorp') return 'TechCorp Global'
  return c.split(' ').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}
