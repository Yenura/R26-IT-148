import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  Trophy, ArrowLeft, Users, Award, Brain, CheckCircle2,
  ChevronRight, Eye, BarChart3, Target, Briefcase
} from 'lucide-react'
import { c3Results, c3Pipeline, c3Explain } from '../api'
import PageHeader from '../components/PageHeader'
import EmptyState from '../components/EmptyState'
import SkeletonLoader from '../components/SkeletonLoader'

export default function RankingResults() {
  const navigate = useNavigate()
  const { jobId } = useParams()
  const [results, setResults] = useState([])
  const [job, setJob] = useState(null)
  const [busy, setBusy] = useState(true)
  const [selectedCandidate, setSelectedCandidate] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [explainBusy, setExplainBusy] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    if (!token || role !== 'company') {
      navigate('/login/company')
      return
    }
    loadResults()
  }, [jobId])

  const loadResults = async () => {
    setBusy(true)
    try {
      let data = []
      try {
        const res = await c3Results(jobId)
        data = res?.data?.data || res?.data?.rankings || res?.data || []
        if (Array.isArray(data) && data.length > 0) {
          setResults(data)
          setBusy(false)
          return
        }
      } catch {}

      const fallback = await c3Pipeline(jobId)
      data = fallback?.data?.data || fallback?.data?.rankings || []
      setResults(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error('loadResults error:', err)
      toast.error('Failed to load ranking results')
    } finally {
      setBusy(false)
    }
  }

  const openExplanation = async (candidateId) => {
    if (selectedCandidate === candidateId) {
      setSelectedCandidate(null)
      setExplanation(null)
      return
    }
    setSelectedCandidate(candidateId)
    setExplainBusy(true)
    try {
      const res = await c3Explain(candidateId)
      const explanations = res?.data?.explanations
      setExplanation(explanations?.[0] || null)
    } catch {
      setExplanation(null)
    } finally {
      setExplainBusy(false)
    }
  }

  const sortedResults = [...results].sort((a, b) => (a.rank || 999) - (b.rank || 999))

  return (
    <div className="fade-in" style={{ maxWidth: 1140, margin: '0 auto' }}>
      <button
        className="btn btn-ghost btn-sm"
        onClick={() => navigate('/company/dashboard')}
        style={{ marginBottom: 'var(--p-space-4)' }}
      >
        <ArrowLeft size={14} /> Back to Dashboard
      </button>

      <PageHeader
        badge="Ranking Results"
        title="Candidate Ranking Results"
        description="Ranked candidates with detailed score breakdowns for the selected job opening."
        icon={Trophy}
        actions={
          <Link to="/company/ranking/weights" className="btn btn-ghost btn-sm">
            <BarChart3 size={14} /> Adjust Weights
          </Link>
        }
      />

      {busy ? (
        <SkeletonLoader type="table" rows={5} cols={7} />
      ) : sortedResults.length === 0 ? (
        <EmptyState
          title="No ranking results available"
          description="Run the ranking pipeline for this job to generate candidate evaluation scores."
          actionLabel="Back to Ranking"
          onAction={() => navigate('/pipeline/ranking')}
          icon={Trophy}
        />
      ) : (
        <>
          <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 'var(--p-space-5)' }}>
            <div style={{ padding: 'var(--p-space-4) var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Trophy size={18} style={{ color: 'var(--color-primary)' }} />
                  Ranked Candidates
                </h3>
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0 0' }}>
                  Sorted by overall fit score. Top 3 candidates are highlighted.
                </p>
              </div>
              <span style={{ fontSize: 'var(--p-text-xs)', fontWeight: 700, color: 'var(--color-primary)', background: 'var(--color-primary-muted)', padding: '3px 10px', borderRadius: 'var(--radius-full)' }}>
                {sortedResults.length} Candidate{sortedResults.length > 1 ? 's' : ''}
              </span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 60 }}>Rank</th>
                    <th>Candidate</th>
                    <th>Overall Score</th>
                    <th>Skills</th>
                    <th>Experience</th>
                    <th>Education</th>
                    <th>Interview</th>
                    <th>MCQ</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedResults.map((cand, idx) => {
                    const rank = cand.rank || idx + 1
                    const isTop3 = rank <= 3 && cand.passed_hard_filter
                    return (
                      <tr
                        key={cand.candidate_id || idx}
                        style={{ opacity: cand.passed_hard_filter ? 1 : 0.6 }}
                      >
                        <td>
                          <div style={{
                            width: 28,
                            height: 28,
                            borderRadius: 'var(--radius-sm)',
                            background: cand.passed_hard_filter
                              ? (isTop3 ? 'var(--color-primary)' : 'var(--color-border-subtle)')
                              : 'var(--color-danger-muted)',
                            color: cand.passed_hard_filter
                              ? (isTop3 ? '#fff' : 'var(--color-fg)')
                              : 'var(--color-danger)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 800,
                            fontSize: '12px'
                          }}>
                            {cand.passed_hard_filter ? `#${rank}` : '✗'}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontWeight: 700, color: 'var(--color-fg)', fontSize: 'var(--p-text-sm)' }}>
                            {cand.candidate_name || 'Candidate'}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                            ID: {cand.candidate_id?.slice(0, 10) || '—'}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                            {(cand.final_score || cand.blended_score || 0).toFixed(1)}%
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                            {(cand.skill_score || cand.s_skill || 0).toFixed(0)}%
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                            {(cand.experience_score || cand.s_exp || 0).toFixed(0)}%
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', fontFamily: 'var(--p-font-mono)' }}>
                            {(cand.education_score || cand.s_edu || 100).toFixed(0)}%
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-purple)', fontFamily: 'var(--p-font-mono)', fontWeight: 600 }}>
                            {(cand.interview_score || cand.p_int || 0).toFixed(0)}%
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-info)', fontFamily: 'var(--p-font-mono)' }}>
                            {(cand.mcq_score || 0).toFixed(0)}%
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: 4 }}>
                            {cand.passed_hard_filter && (
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => openExplanation(cand.candidate_id)}
                                style={{ fontSize: '12px', padding: '4px 10px' }}
                              >
                                <Eye size={13} /> {selectedCandidate === cand.candidate_id ? 'Hide' : 'Explain'}
                              </button>
                            )}
                            {!cand.passed_hard_filter && (
                              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-danger)', background: 'var(--color-danger-muted)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                                {cand.filter_fail_reason || 'Disqualified'}
                              </span>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Score Breakdown Detail */}
          {selectedCandidate && (
            <div className="card" style={{ padding: 'var(--p-space-5)', marginBottom: 'var(--p-space-5)' }}>
              <h3 style={{ margin: '0 0 12px', fontSize: 'var(--p-text-base)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Target size={16} style={{ color: 'var(--color-primary)' }} />
                Score Breakdown — {sortedResults.find(c => c.candidate_id === selectedCandidate)?.candidate_name || 'Candidate'}
              </h3>

              {explainBusy ? (
                <div style={{ display: 'flex', gap: 8 }}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="skeleton" style={{ height: 60, flex: 1, borderRadius: 'var(--radius-md)' }} />
                  ))}
                </div>
              ) : explanation ? (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10, marginBottom: 14 }}>
                    {[
                      { label: 'Skills', value: explanation.contributions?.find(c => c.feature?.includes('skill'))?.value || 0 },
                      { label: 'Experience', value: explanation.contributions?.find(c => c.feature?.includes('exp'))?.value || 0 },
                      { label: 'Education', value: explanation.contributions?.find(c => c.feature?.includes('edu'))?.value || 0 },
                      { label: 'Interview', value: explanation.contributions?.find(c => c.feature?.includes('int'))?.value || 0 },
                      { label: 'MCQ', value: explanation.contributions?.find(c => c.feature?.includes('mcq'))?.value || 0 },
                    ].map((item) => (
                      <div key={item.label} style={{ padding: 10, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)', textAlign: 'center' }}>
                        <div style={{ fontSize: '10px', color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 4 }}>{item.label}</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--p-font-mono)', color: 'var(--color-fg)' }}>
                          {typeof item.value === 'number' ? (item.value * 100).toFixed(0) + '%' : '—'}
                        </div>
                      </div>
                    ))}
                  </div>

                  {explanation.top_drivers?.length > 0 && (
                    <div style={{ padding: 12, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-subtle)' }}>
                      <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-fg-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Top Ranking Drivers</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {explanation.top_drivers.map((d, i) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: 'var(--color-bg)', borderRadius: 'var(--radius-sm)', fontSize: '11px' }}>
                            <span style={{ color: 'var(--color-fg)', fontWeight: 600 }}>{d.feature}</span>
                            <span style={{ fontFamily: 'var(--p-font-mono)', color: 'var(--color-primary)', fontWeight: 700 }}>
                              {(d.value * 100).toFixed(0)}% × {d.weight.toFixed(3)} = {(d.contribution * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', margin: 0 }}>
                  No detailed explanation available for this candidate.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
