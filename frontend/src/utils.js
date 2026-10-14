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
