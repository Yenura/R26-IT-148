import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const KEY = 'recruitai.pipeline.v1'
const PipelineContext = createContext(null)

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || []
  } catch {
    return []
  }
}

export function PipelineProvider({ children }) {
  const [candidates, setCandidates] = useState(load)

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(candidates))
  }, [candidates])

  const addCandidate = (c) =>
    setCandidates((prev) => {
      const exists = prev.some((p) => p.id === c.id)
      return exists ? prev : [...prev, c]
    })

  const setCv = (id, cv) =>
    setCandidates((prev) =>
      prev.map((p) => (p.id === id ? { ...p, cv } : p)))

  const setInterview = (id, interview) =>
    setCandidates((prev) =>
      prev.map((p) => (p.id === id ? { ...p, interview } : p)))

  const removeCandidate = (id) =>
    setCandidates((prev) => prev.filter((p) => p.id !== id))

  const clear = () => setCandidates([])

  const value = useMemo(
    () => ({
      candidates,
      addCandidate,
      setCv,
      setInterview,
      removeCandidate,
      clear,
    }),
    [candidates]
  )

  return <PipelineContext.Provider value={value}>{children}</PipelineContext.Provider>
}

export function usePipeline() {
  return useContext(PipelineContext)
}
