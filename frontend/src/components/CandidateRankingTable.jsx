import { useState, useMemo } from 'react'
import {
  Trophy, Award, Medal, Crown, Star, Shield, ShieldCheck,
  CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Download,
  Search, X, Copy, Check, Briefcase, GraduationCap, Code2,
  FileText, Sparkles, Filter, ArrowUpDown, ArrowUp, ArrowDown,
  User, CheckCircle, Info, Eye
} from 'lucide-react'
import toast from 'react-hot-toast'
import ScoreMeter, { getScoreRating } from './ScoreMeter'

/**
 * Normalizes and cleans candidate names.
 */
export const cleanCandidateName = (rawName, fallbackId) => {
  if (!rawName) return `Candidate ${(fallbackId || '01').slice(-4)}`
  let name = String(rawName).trim()
  name = name.replace(/\s*[\(\[]\s*CV\s*[\)\]]/gi, '')
  name = name.replace(/^(?:phone|email|name|profile|student)\s*:\s*/i, '')
  name = name.split(/\s*[\n\r·|:;•]\s*/)[0].trim()
  const words = name.split(/\s+/).filter(Boolean)
  if (words.length > 3) {
    name = words.slice(0, 3).join(' ')
  }
  return name || 'Candidate'
}

/**
 * Deterministically generates avatar colors based on candidate string.
 */
const getAvatarGradient = (str) => {
  const gradients = [
    'linear-gradient(135deg, #3b82f6, #1d4ed8)',
    'linear-gradient(135deg, #8b5cf6, #6d28d9)',
    'linear-gradient(135deg, #ec4899, #be185d)',
    'linear-gradient(135deg, #10b981, #047857)',
    'linear-gradient(135deg, #f59e0b, #b45309)',
    'linear-gradient(135deg, #06b6d4, #0e7490)',
    'linear-gradient(135deg, #6366f1, #4338ca)',
  ]
  let hash = 0
  const s = String(str || 'RecruitAI')
  for (let i = 0; i < s.length; i++) {
    hash = (hash << 5) - hash + s.charCodeAt(i)
    hash |= 0
  }
  return gradients[Math.abs(hash) % gradients.length]
}

/**
 * Extracts initials for avatar.
 */
const getInitials = (name) => {
  if (!name) return 'CA'
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return (parts[0] ? parts[0].slice(0, 2) : 'CA').toUpperCase()
}

/**
 * Calculates unified candidate metrics.
 */
export const calculateCandidateMetrics = (cand) => {
  const hasCV = cand.has_cv !== false && (cand.cv_score != null || cand.S_cv != null)
  const hasInt = Boolean(cand.interview_completed || cand.interview_score != null || cand.S_int != null)
  const isPassed = cand.passed_hard_filter !== false

  const sCvVal = hasCV ? (cand.cv_score ?? (cand.S_cv != null ? cand.S_cv * 100 : null)) : null
  const sSkillVal = hasCV ? (cand.skill_score ?? (cand.S_skill != null ? cand.S_skill * 100 : null)) : null
  const sExpVal = hasCV ? (cand.experience_score ?? (cand.S_exp != null ? cand.S_exp * 100 : null)) : null
  const sEduVal = hasCV ? (cand.education_score ?? (cand.S_edu != null ? cand.S_edu * 100 : null)) : null

  const sIntVal = hasInt ? (cand.interview_score ?? (cand.S_int != null ? cand.S_int * 100 : null)) : null
  const pMcqVal = hasInt ? (cand.mcq_score ?? (cand.P_mcq != null ? cand.P_mcq * 100 : null)) : null
  const pDescVal = hasInt ? (cand.descriptive_score ?? (cand.P_desc != null ? cand.P_desc * 100 : null)) : null
  const pCodeVal = hasInt ? (cand.coding_score ?? (cand.P_code != null ? cand.P_code * 100 : null)) : null

  let cssVal = null
  let scoreFormula = ''
  if (hasCV && hasInt && sCvVal != null && sIntVal != null) {
    cssVal = 0.40 * Number(sCvVal) + 0.60 * Number(sIntVal)
    scoreFormula = '40% CV + 60% Interview'
  } else if (hasCV && sCvVal != null) {
    cssVal = Number(sCvVal)
    scoreFormula = '100% CV Evaluation'
  } else if (hasInt && sIntVal != null) {
    cssVal = Number(sIntVal)
    scoreFormula = '100% AI Interview'
  } else {
    cssVal = cand.final_score ?? (cand.CSS != null ? (cand.CSS <= 1 ? cand.CSS * 100 : cand.CSS) : (cand.blended_score ?? cand.hire_probability ?? 0))
    scoreFormula = 'Composite Pipeline Fit'
  }

  const cleanName = cleanCandidateName(cand.candidate_name, cand.candidate_id)
  const isPrereqWarning = hasInt && (pCodeVal != null && Number(pCodeVal) < 25)

  return {
    hasCV,
    hasInt,
    isPassed,
    isComplete: hasCV && hasInt && isPassed,
    sCvVal: sCvVal != null ? Math.round(Number(sCvVal)) : null,
    sSkillVal: sSkillVal != null ? Math.round(Number(sSkillVal)) : null,
    sExpVal: sExpVal != null ? Math.round(Number(sExpVal)) : null,
    sEduVal: sEduVal != null ? Math.round(Number(sEduVal)) : null,
    sIntVal: sIntVal != null ? Math.round(Number(sIntVal)) : null,
    pMcqVal: pMcqVal != null ? Math.round(Number(pMcqVal)) : null,
    pDescVal: pDescVal != null ? Math.round(Number(pDescVal)) : null,
    pCodeVal: pCodeVal != null ? Math.round(Number(pCodeVal)) : null,
    integrityScore: cand.integrity_score != null ? Math.round(Number(cand.integrity_score)) : null,
    cssVal: cssVal != null ? Math.round(Number(cssVal)) : null,
    scoreFormula,
    cleanName,
    isPrereqWarning
  }
}

/**
 * Top podium badge styling.
 */
const getPodiumRankBadge = (rankNum) => {
  if (rankNum === 1) {
    return {
      bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      color: '#ffffff',
      border: '1px solid rgba(251, 191, 36, 0.7)',
      boxShadow: '0 2px 10px rgba(245, 158, 11, 0.45)',
      icon: Crown,
      iconColor: '#ffffff',
      label: '1st'
    }
  }
  if (rankNum === 2) {
    return {
      bg: 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
      color: '#ffffff',
      border: '1px solid rgba(226, 232, 240, 0.6)',
      boxShadow: '0 2px 8px rgba(148, 163, 184, 0.35)',
      icon: Star,
      iconColor: '#ffffff',
      label: '2nd'
    }
  }
  if (rankNum === 3) {
    return {
      bg: 'linear-gradient(135deg, #d97706 0%, #92400e 100%)',
      color: '#ffffff',
      border: '1px solid rgba(245, 158, 11, 0.5)',
      boxShadow: '0 2px 8px rgba(217, 119, 6, 0.35)',
      icon: Medal,
      iconColor: '#ffffff',
      label: '3rd'
    }
  }
  return {
    bg: 'rgba(255, 255, 255, 0.05)',
    color: 'var(--color-fg)',
    border: '1px solid var(--color-border-subtle)',
    boxShadow: 'none',
    icon: null,
    iconColor: null,
    label: `#${rankNum < 10 ? `0${rankNum}` : rankNum}`
  }
}

export default function CandidateRankingTable({
  candidates = [],
  jobTitle = '',
  showJobColumn = false,
  emptyMessage = 'No candidates match the current filters',
  onViewDetail = null
}) {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeFilter, setActiveFilter] = useState('all') // 'all', 'complete', 'pending_int', 'pending_cv', 'top'
  const [sortField, setSortField] = useState('rank') // 'rank', 'name', 'css', 'cv', 'int'
  const [sortOrder, setSortOrder] = useState('asc') // 'asc', 'desc'
  const [expandedId, setExpandedId] = useState(null)
  const [copiedId, setCopiedId] = useState(null)

  // Enrich candidates with computed metrics
  const enrichedCandidates = useMemo(() => {
    return candidates.map((cand, originalIdx) => {
      const metrics = calculateCandidateMetrics(cand)
      return {
        ...cand,
        originalRank: originalIdx + 1,
        metrics
      }
    })
  }, [candidates])

  // Filter candidates
  const filteredCandidates = useMemo(() => {
    return enrichedCandidates.filter((cand) => {
      const { cleanName, metrics } = cand
      const search = searchTerm.toLowerCase().trim()
      if (search) {
        const matchesName = cleanName.toLowerCase().includes(search)
        const matchesId = (cand.candidate_id || '').toLowerCase().includes(search)
        const matchesJob = (cand.job_title || cand.job_role || '').toLowerCase().includes(search)
        const matchesSkills = (cand.skills || []).some(s => String(s).toLowerCase().includes(search))
        if (!matchesName && !matchesId && !matchesJob && !matchesSkills) return false
      }

      if (activeFilter === 'complete') {
        return metrics.hasCV && metrics.hasInt
      }
      if (activeFilter === 'pending_int') {
        return metrics.hasCV && !metrics.hasInt
      }
      if (activeFilter === 'pending_cv') {
        return !metrics.hasCV && metrics.hasInt
      }
      if (activeFilter === 'top') {
        return (metrics.cssVal || 0) >= 75
      }

      return true
    })
  }, [enrichedCandidates, searchTerm, activeFilter])

  // Sort candidates
  const sortedCandidates = useMemo(() => {
    const list = [...filteredCandidates]

    list.sort((a, b) => {
      let comparison = 0
      if (sortField === 'rank') {
        comparison = a.originalRank - b.originalRank
      } else if (sortField === 'name') {
        comparison = a.metrics.cleanName.localeCompare(b.metrics.cleanName)
      } else if (sortField === 'css') {
        comparison = (b.metrics.cssVal || 0) - (a.metrics.cssVal || 0)
      } else if (sortField === 'cv') {
        comparison = (b.metrics.sCvVal || 0) - (a.metrics.sCvVal || 0)
      } else if (sortField === 'int') {
        comparison = (b.metrics.sIntVal || 0) - (a.metrics.sIntVal || 0)
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return list
  }, [filteredCandidates, sortField, sortOrder])

  // Count summaries for filter pills
  const counts = useMemo(() => {
    return {
      all: enrichedCandidates.length,
      complete: enrichedCandidates.filter(c => c.metrics.hasCV && c.metrics.hasInt).length,
      pending_int: enrichedCandidates.filter(c => c.metrics.hasCV && !c.metrics.hasInt).length,
      pending_cv: enrichedCandidates.filter(c => !c.metrics.hasCV && c.metrics.hasInt).length,
      top: enrichedCandidates.filter(c => (c.metrics.cssVal || 0) >= 75).length
    }
  }, [enrichedCandidates])

  // Stats calculation
  const stats = useMemo(() => {
    if (enrichedCandidates.length === 0) return null
    const scores = enrichedCandidates.map(c => c.metrics.cssVal).filter(s => s != null)
    const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
    const topScore = scores.length > 0 ? Math.max(...scores) : 0
    const topCandidate = enrichedCandidates.find(c => c.metrics.cssVal === topScore)

    return {
      avgScore,
      topScore,
      topCandidateName: topCandidate?.metrics.cleanName || '—'
    }
  }, [enrichedCandidates])

  // Handle header click to toggle sort
  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder(field === 'name' || field === 'rank' ? 'asc' : 'desc')
    }
  }

  // Toggle row expansion
  const toggleRow = (candId) => {
    setExpandedId(prev => prev === candId ? null : candId)
  }

  // Copy candidate summary
  const copySummary = (cand, e) => {
    e.stopPropagation()
    const { cleanName, metrics } = cand
    const summary = [
      `RecruitAI Candidate Evaluation Report`,
      `====================================`,
      `Candidate: ${cleanName}`,
      `Candidate ID: ${cand.candidate_id || 'N/A'}`,
      `Job Opening: ${cand.job_title || jobTitle || 'Engineering'}`,
      `Total Fit Score: ${metrics.cssVal != null ? `${metrics.cssVal}%` : 'N/A'} (${metrics.scoreFormula})`,
      `------------------------------------`,
      `CV Match Score: ${metrics.sCvVal != null ? `${metrics.sCvVal}%` : 'Pending'}`,
      `  • Skills Match: ${metrics.sSkillVal != null ? `${metrics.sSkillVal}%` : 'N/A'}`,
      `  • Experience Match: ${metrics.sExpVal != null ? `${metrics.sExpVal}%` : 'N/A'}`,
      `  • Education Match: ${metrics.sEduVal != null ? `${metrics.sEduVal}%` : 'N/A'}`,
      `------------------------------------`,
      `Technical Interview: ${metrics.sIntVal != null ? `${metrics.sIntVal}%` : 'Pending'}`,
      `  • MCQ Score: ${metrics.pMcqVal != null ? `${metrics.pMcqVal}%` : 'N/A'}`,
      `  • Descriptive Score: ${metrics.pDescVal != null ? `${metrics.pDescVal}%` : 'N/A'}`,
      `  • Live Coding Score: ${metrics.pCodeVal != null ? `${metrics.pCodeVal}%` : 'N/A'}`,
      `  • Proctor Integrity: ${metrics.integrityScore != null ? `${metrics.integrityScore}%` : 'Verified'}`,
      `Status: ${metrics.isComplete ? 'Fully Evaluated' : 'Pending Stage completion'}`
    ].join('\n')

    navigator.clipboard.writeText(summary)
    setCopiedId(cand.candidate_id)
    toast.success(`Copied evaluation summary for ${cleanName}`)
    setTimeout(() => setCopiedId(null), 2000)
  }

  // Export CSV
  const exportToCSV = () => {
    if (enrichedCandidates.length === 0) {
      toast.error('No candidate data to export')
      return
    }

    const headers = [
      'Rank',
      'Candidate Name',
      'Candidate ID',
      'Job Title',
      'Total Fit Score (%)',
      'Formula / Stage',
      'CV Score (%)',
      'Skills Score (%)',
      'Experience Score (%)',
      'Education Score (%)',
      'Interview Score (%)',
      'MCQ Score (%)',
      'Descriptive Score (%)',
      'Coding Score (%)',
      'Proctor Integrity (%)',
      'Evaluation Status'
    ]

    const rows = enrichedCandidates.map(c => [
      c.originalRank,
      `"${c.metrics.cleanName.replace(/"/g, '""')}"`,
      `"${(c.candidate_id || '').replace(/"/g, '""')}"`,
      `"${(c.job_title || jobTitle || '').replace(/"/g, '""')}"`,
      c.metrics.cssVal ?? '',
      `"${c.metrics.scoreFormula}"`,
      c.metrics.sCvVal ?? '',
      c.metrics.sSkillVal ?? '',
      c.metrics.sExpVal ?? '',
      c.metrics.sEduVal ?? '',
      c.metrics.sIntVal ?? '',
      c.metrics.pMcqVal ?? '',
      c.metrics.pDescVal ?? '',
      c.metrics.pCodeVal ?? '',
      c.metrics.integrityScore ?? '',
      c.metrics.isComplete ? 'Full Assessment Complete' : (c.metrics.hasCV ? 'Pending Interview' : 'Pending CV')
    ])

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `candidate_ranking_leaderboard_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Downloaded candidate rankings CSV')
  }

  const renderSortArrow = (field) => {
    if (sortField !== field) {
      return <ArrowUpDown size={12} style={{ opacity: 0.4, marginLeft: 4 }} />
    }
    return sortOrder === 'asc' ? (
      <ArrowUp size={12} style={{ color: 'var(--color-primary)', marginLeft: 4 }} />
    ) : (
      <ArrowDown size={12} style={{ color: 'var(--color-primary)', marginLeft: 4 }} />
    )
  }

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* ── Summary Stats Strip ── */}
      {stats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 12
        }}>
          <div style={{
            background: 'var(--color-surface, rgba(255, 255, 255, 0.03))',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, #f59e0b20, #f59e0b40)',
              color: '#f59e0b',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Trophy size={18} />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Top Performing Candidate
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-fg)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span>{stats.topCandidateName}</span>
                <span style={{ fontSize: '11px', color: '#f59e0b', fontFamily: 'var(--p-font-mono)' }}>({stats.topScore}%)</span>
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--color-surface, rgba(255, 255, 255, 0.03))',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(10, 132, 255, 0.15)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Award size={18} />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Cohort Average Score
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-fg)', fontFamily: 'var(--p-font-mono)' }}>
                {stats.avgScore}% Composite Fit
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--color-surface, rgba(255, 255, 255, 0.03))',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(48, 209, 88, 0.15)',
              color: 'var(--color-success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <CheckCircle2 size={18} />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-fg-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Full Evaluations
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--color-fg)' }}>
                {counts.complete} of {counts.all} Applicants ({counts.all > 0 ? Math.round((counts.complete / counts.all) * 100) : 0}%)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Toolbar: Search, Filter Tabs & Export ── */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 12,
        padding: '12px 16px',
        background: 'var(--color-surface, rgba(255, 255, 255, 0.02))',
        border: '1px solid var(--color-border-subtle)',
        borderRadius: 'var(--radius-md)'
      }}>
        {/* Search */}
        <div style={{ position: 'relative', width: 280, maxWidth: '100%' }}>
          <Search size={14} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-fg-muted)' }} />
          <input
            type="text"
            placeholder="Search candidate, ID, skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              paddingLeft: 34,
              paddingRight: searchTerm ? 30 : 12,
              height: 36,
              fontSize: '12.5px',
              width: '100%',
              borderRadius: 'var(--radius-sm)'
            }}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              style={{
                position: 'absolute',
                right: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--color-fg-muted)',
                cursor: 'pointer',
                padding: 4,
                display: 'flex',
                alignItems: 'center'
              }}
              title="Clear search"
            >
              <X size={13} />
            </button>
          )}
        </div>

        {/* Filter Segment Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {[
            { id: 'all', label: 'All', count: counts.all },
            { id: 'complete', label: 'Full Assessment', count: counts.complete },
            { id: 'pending_int', label: 'Pending Interview', count: counts.pending_int },
            { id: 'pending_cv', label: 'Pending CV', count: counts.pending_cv },
            { id: 'top', label: 'Top Fit (≥75%)', count: counts.top }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              className={`btn btn-sm ${activeFilter === tab.id ? 'btn-primary' : 'btn-ghost'}`}
              style={{
                fontSize: '11.5px',
                padding: '5px 10px',
                height: 32,
                borderRadius: 'var(--radius-full)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5
              }}
            >
              <span>{tab.label}</span>
              <span style={{
                fontSize: '10px',
                fontWeight: 800,
                padding: '1px 6px',
                borderRadius: '9999px',
                background: activeFilter === tab.id ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.08)',
                color: activeFilter === tab.id ? '#ffffff' : 'var(--color-fg-muted)'
              }}>
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Export CSV Button */}
        <button
          onClick={exportToCSV}
          className="btn btn-ghost btn-sm"
          style={{
            fontSize: '12px',
            height: 34,
            padding: '0 12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6
          }}
          title="Download rankings as CSV spreadsheet"
        >
          <Download size={14} /> Export CSV
        </button>
      </div>

      {/* ── Table Card Container ── */}
      <div className="card glass-card" style={{ padding: 0, overflow: 'hidden', border: '1px solid var(--color-border-subtle)' }}>
        <div style={{ overflowX: 'auto', width: '100%' }}>
          <table className="table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--color-surface-hover, rgba(255, 255, 255, 0.035))', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <th
                  onClick={() => handleSort('rank')}
                  style={{
                    width: 72,
                    textAlign: 'center',
                    padding: '12px 10px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--color-fg-muted)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  title="Click to sort by rank"
                >
                  <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                    Rank {renderSortArrow('rank')}
                  </div>
                </th>

                <th
                  onClick={() => handleSort('name')}
                  style={{
                    minWidth: 220,
                    padding: '12px 14px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--color-fg-muted)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  title="Click to sort by candidate name"
                >
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    Candidate {renderSortArrow('name')}
                  </div>
                </th>

                <th
                  onClick={() => handleSort('css')}
                  style={{
                    width: 140,
                    padding: '12px 14px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--color-fg-muted)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  title="Click to sort by composite fit score"
                >
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    Composite Fit {renderSortArrow('css')}
                  </div>
                </th>

                <th
                  onClick={() => handleSort('cv')}
                  style={{
                    minWidth: 190,
                    padding: '12px 14px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--color-fg-muted)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  title="Click to sort by CV qualifications score"
                >
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    CV Score & Qualifications {renderSortArrow('cv')}
                  </div>
                </th>

                <th
                  onClick={() => handleSort('int')}
                  style={{
                    minWidth: 240,
                    padding: '12px 14px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                    color: 'var(--color-fg-muted)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  title="Click to sort by AI technical interview score"
                >
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    AI Interview & Proctoring {renderSortArrow('int')}
                  </div>
                </th>

                <th style={{
                  width: 90,
                  textAlign: 'center',
                  padding: '12px 10px',
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: 'var(--color-fg-muted)'
                }}>
                  Scorecard
                </th>
              </tr>
            </thead>

            <tbody>
              {sortedCandidates.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '48px 16px', color: 'var(--color-fg-muted)' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                      <Filter size={28} style={{ opacity: 0.4 }} />
                      <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--color-fg)' }}>
                        {emptyMessage}
                      </div>
                      <p style={{ margin: 0, fontSize: '12px' }}>
                        Try clearing your search query or switching filter tabs.
                      </p>
                      {(searchTerm || activeFilter !== 'all') && (
                        <button
                          className="btn btn-primary btn-sm"
                          style={{ marginTop: 6 }}
                          onClick={() => { setSearchTerm(''); setActiveFilter('all') }}
                        >
                          Reset Filters
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                sortedCandidates.map((cand) => {
                  const { metrics, originalRank } = cand
                  const rankNum = originalRank
                  const podium = getPodiumRankBadge(rankNum)
                  const PodiumIcon = podium.icon
                  const isExpanded = expandedId === cand.candidate_id
                  const rating = getScoreRating(metrics.cssVal || 0)

                  return (
                    <tr
                      key={`${cand.candidate_id || originalRank}_${cand.job_id || ''}`}
                      onClick={() => toggleRow(cand.candidate_id)}
                      style={{
                        borderBottom: '1px solid var(--color-border-subtle)',
                        background: isExpanded ? 'rgba(10, 132, 255, 0.04)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.15s ease'
                      }}
                      className="table-row-hoverable"
                    >
                      {/* Rank Column with Podium Badging */}
                      <td style={{ textAlign: 'center', padding: '12px 10px', verticalAlign: 'middle' }}>
                        <div
                          style={{
                            width: 38,
                            height: 32,
                            borderRadius: '8px',
                            background: podium.bg,
                            color: podium.color,
                            border: podium.border,
                            boxShadow: podium.boxShadow,
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 3,
                            fontWeight: 800,
                            fontSize: '12px',
                            fontFamily: 'var(--p-font-mono)',
                            margin: '0 auto'
                          }}
                          title={`Leaderboard Rank #${rankNum}`}
                        >
                          {PodiumIcon && <PodiumIcon size={12} color={podium.iconColor} />}
                          <span>{podium.label}</span>
                        </div>
                      </td>

                      {/* Candidate Column */}
                      <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div
                            style={{
                              width: 36,
                              height: 36,
                              borderRadius: 'var(--radius-full)',
                              background: getAvatarGradient(metrics.cleanName || cand.candidate_id),
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#ffffff',
                              fontWeight: 800,
                              fontSize: '12px',
                              letterSpacing: '0.04em',
                              flexShrink: 0,
                              boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)'
                            }}
                          >
                            {getInitials(metrics.cleanName)}
                          </div>

                          <div style={{ minWidth: 0, display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                              <span
                                style={{
                                  fontWeight: 700,
                                  color: 'var(--color-fg)',
                                  fontSize: '13.5px',
                                  whiteSpace: 'nowrap',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  maxWidth: 240
                                }}
                                title={metrics.cleanName}
                              >
                                {metrics.cleanName}
                              </span>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                              <span style={{ fontFamily: 'var(--p-font-mono)' }}>
                                ID: {cand.candidate_id?.slice(0, 10) || 'Applicant'}
                              </span>
                              {(showJobColumn || cand.job_title) && (
                                <>
                                  <span>·</span>
                                  <span style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={cand.job_title}>
                                    {cand.job_title}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Composite Fit Score Column */}
                      <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                          <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                            <span style={{
                              fontSize: '16px',
                              fontWeight: 900,
                              color: rating.color,
                              fontFamily: 'var(--p-font-mono)',
                              letterSpacing: '-0.02em'
                            }}>
                              {metrics.cssVal != null ? `${metrics.cssVal}%` : '—'}
                            </span>
                            {metrics.cssVal != null && (
                              <span style={{
                                fontSize: '9.5px',
                                fontWeight: 700,
                                color: rating.color,
                                textTransform: 'uppercase',
                                letterSpacing: '0.04em'
                              }}>
                                {rating.label.split(' ')[0]}
                              </span>
                            )}
                          </div>

                          {/* Mini visual score progress bar */}
                          {metrics.cssVal != null && (
                            <div style={{
                              width: '100%',
                              maxWidth: 100,
                              height: 4,
                              background: 'var(--color-border-subtle)',
                              borderRadius: '9999px',
                              overflow: 'hidden'
                            }}>
                              <div
                                style={{
                                  width: `${Math.min(100, Math.max(0, metrics.cssVal))}%`,
                                  height: '100%',
                                  background: rating.color,
                                  borderRadius: '9999px'
                                }}
                              />
                            </div>
                          )}
                        </div>
                      </td>

                      {/* CV Score & Breakdown Column */}
                      <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>
                        {metrics.hasCV && metrics.sCvVal != null ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                              <span style={{
                                fontSize: '13px',
                                fontWeight: 800,
                                color: 'var(--color-fg)',
                                fontFamily: 'var(--p-font-mono)'
                              }}>
                                {metrics.sCvVal}% Match
                              </span>
                            </div>

                            {/* Subscores: Skills, Exp, Edu */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
                              <span
                                title={`Verified Skills Match: ${metrics.sSkillVal ?? 0}%`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: 'rgba(10, 132, 255, 0.1)',
                                  color: 'var(--color-primary)',
                                  border: '1px solid rgba(10, 132, 255, 0.22)',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                Skill: {metrics.sSkillVal ?? 0}%
                              </span>
                              <span
                                title={`Experience Relevance: ${metrics.sExpVal ?? 0}%`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: 'rgba(48, 209, 88, 0.1)',
                                  color: 'var(--color-success)',
                                  border: '1px solid rgba(48, 209, 88, 0.22)',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                Exp: {metrics.sExpVal ?? 0}%
                              </span>
                              <span
                                title={`Education Alignment: ${metrics.sEduVal ?? 0}%`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: 'rgba(168, 85, 247, 0.1)',
                                  color: 'var(--color-purple)',
                                  border: '1px solid rgba(168, 85, 247, 0.22)',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                Edu: {metrics.sEduVal ?? 0}%
                              </span>
                            </div>
                          </div>
                        ) : (
                          <span style={{
                            fontSize: '11px',
                            fontWeight: 600,
                            color: 'var(--color-warning)',
                            background: 'var(--color-warning-muted)',
                            padding: '3px 8px',
                            borderRadius: 'var(--radius-sm)'
                          }}>
                            Pending CV Match
                          </span>
                        )}
                      </td>

                      {/* Technical Interview & Proctoring Column */}
                      <td style={{ padding: '12px 14px', verticalAlign: 'middle' }}>
                        {metrics.hasInt && metrics.sIntVal != null ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span style={{
                                fontSize: '13px',
                                fontWeight: 800,
                                color: '#c084fc',
                                fontFamily: 'var(--p-font-mono)'
                              }}>
                                {metrics.sIntVal}% Tech Fit
                              </span>

                              {metrics.integrityScore != null && (
                                <span
                                  title={`Proctored integrity score: ${metrics.integrityScore}%`}
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: 3,
                                    fontSize: '10px',
                                    fontWeight: 700,
                                    color: 'var(--color-fg-muted)',
                                    background: 'var(--color-surface, rgba(255, 255, 255, 0.05))',
                                    padding: '1px 6px',
                                    borderRadius: '4px',
                                    border: '1px solid var(--color-border-subtle)',
                                    whiteSpace: 'nowrap'
                                  }}
                                >
                                  <Shield size={10} color="var(--color-success)" /> {metrics.integrityScore}% Integrity
                                </span>
                              )}
                            </div>

                            {/* Subscores: MCQ, Theory, Coding */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
                              <span
                                title={`Technical MCQ Score: ${metrics.pMcqVal ?? 0}%`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: 'rgba(59, 130, 246, 0.1)',
                                  color: '#3b82f6',
                                  border: '1px solid rgba(59, 130, 246, 0.22)',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                MCQ: {metrics.pMcqVal ?? 0}%
                              </span>

                              <span
                                title={`Descriptive/Theoretical Score: ${metrics.pDescVal ?? 0}%`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: 'rgba(14, 165, 233, 0.1)',
                                  color: '#38bdf8',
                                  border: '1px solid rgba(14, 165, 233, 0.22)',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                Desc: {metrics.pDescVal ?? 0}%
                              </span>

                              <span
                                title={`Live Coding Score: ${metrics.pCodeVal ?? 0}%${metrics.isPrereqWarning ? ' (Below 25% prerequisite threshold)' : ''}`}
                                style={{
                                  fontSize: '10px',
                                  fontWeight: 700,
                                  fontFamily: 'var(--p-font-mono)',
                                  padding: '1px 5px',
                                  borderRadius: '4px',
                                  background: metrics.isPrereqWarning ? 'rgba(239, 68, 68, 0.14)' : 'rgba(168, 85, 247, 0.1)',
                                  color: metrics.isPrereqWarning ? '#ef4444' : '#c084fc',
                                  border: `1px solid ${metrics.isPrereqWarning ? 'rgba(239, 68, 68, 0.35)' : 'rgba(168, 85, 247, 0.22)'}`,
                                  whiteSpace: 'nowrap',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: 3
                                }}
                              >
                                {metrics.isPrereqWarning && <AlertTriangle size={9} />}
                                Code: {metrics.pCodeVal ?? 0}%
                              </span>
                            </div>
                          </div>
                        ) : (
                          <span style={{
                            fontSize: '11px',
                            fontWeight: 600,
                            color: 'var(--color-warning)',
                            background: 'var(--color-warning-muted)',
                            padding: '3px 8px',
                            borderRadius: 'var(--radius-sm)'
                          }}>
                            Pending AI Interview
                          </span>
                        )}
                      </td>

                      {/* Expand / Actions Column */}
                      <td style={{ textAlign: 'center', padding: '12px 10px', verticalAlign: 'middle' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          <button
                            onClick={(e) => copySummary(cand, e)}
                            className="btn-ghost btn-sm"
                            style={{
                              width: 28,
                              height: 28,
                              padding: 0,
                              borderRadius: '6px',
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: copiedId === cand.candidate_id ? 'var(--color-success)' : 'var(--color-fg-muted)'
                            }}
                            title="Copy candidate evaluation scorecard"
                          >
                            {copiedId === cand.candidate_id ? <Check size={13} /> : <Copy size={13} />}
                          </button>

                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleRow(cand.candidate_id)
                            }}
                            className="btn-ghost btn-sm"
                            style={{
                              width: 28,
                              height: 28,
                              padding: 0,
                              borderRadius: '6px',
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: isExpanded ? 'var(--color-primary)' : 'var(--color-fg-muted)'
                            }}
                            title={isExpanded ? 'Collapse scorecard' : 'Expand full scorecard'}
                          >
                            {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* ── Expanded Scorecard Drawer (when a candidate row is clicked) ── */}
        {expandedId && (() => {
          const cand = enrichedCandidates.find(c => c.candidate_id === expandedId)
          if (!cand) return null
          const { metrics, originalRank } = cand
          const podium = getPodiumRankBadge(originalRank)
          const rating = getScoreRating(metrics.cssVal || 0)

          return (
            <div style={{
              background: 'var(--color-surface, rgba(16, 16, 22, 0.95))',
              borderTop: '2px solid var(--color-primary)',
              padding: '20px 24px',
              animation: 'fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <div style={{
                      width: 24,
                      height: 24,
                      borderRadius: '6px',
                      background: podium.bg,
                      color: podium.color,
                      fontSize: '11px',
                      fontWeight: 800,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontFamily: 'var(--p-font-mono)'
                    }}>
                      #{originalRank}
                    </div>
                    <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 800, color: 'var(--color-fg)' }}>
                      {metrics.cleanName}
                    </h4>
                    <span style={{
                      fontSize: '10.5px',
                      fontWeight: 700,
                      color: rating.color,
                      background: rating.bg,
                      border: `1px solid ${rating.border}`,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)'
                    }}>
                      {rating.label}
                    </span>
                  </div>

                  <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-fg-muted)' }}>
                    Candidate ID: <code style={{ fontFamily: 'var(--p-font-mono)' }}>{cand.candidate_id}</code>
                    {cand.job_title && ` · Position: ${cand.job_title}`}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {onViewDetail && (
                    <button
                      onClick={() => onViewDetail(cand.candidate_id)}
                      className="btn btn-primary btn-sm"
                      style={{ fontSize: '11.5px', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                    >
                      <Eye size={13} /> View Full Assessment
                    </button>
                  )}

                  <button
                    onClick={(e) => copySummary(cand, e)}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '11.5px', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    {copiedId === cand.candidate_id ? <Check size={13} /> : <Copy size={13} />}
                    {copiedId === cand.candidate_id ? 'Copied' : 'Copy Scorecard'}
                  </button>

                  <button
                    onClick={() => setExpandedId(null)}
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '11.5px' }}
                  >
                    Close
                  </button>
                </div>
              </div>

              {/* Score breakdown grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 16
              }}>
                {/* Composite Fit Formula Card */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: 16
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <Sparkles size={15} style={{ color: 'var(--color-primary)' }} />
                    <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-fg)' }}>
                      Composite Scoring Engine
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 8 }}>
                    <span style={{ fontSize: '28px', fontWeight: 900, fontFamily: 'var(--p-font-mono)', color: rating.color }}>
                      {metrics.cssVal != null ? `${metrics.cssVal}%` : '—'}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--color-fg-muted)', fontWeight: 600 }}>
                      Final Composite Score
                    </span>
                  </div>

                  <div style={{
                    fontSize: '11.5px',
                    color: 'var(--color-fg-secondary)',
                    background: 'var(--color-surface-hover, rgba(255, 255, 255, 0.04))',
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border-subtle)',
                    lineHeight: 1.45
                  }}>
                    <strong>Scoring Formula:</strong><br />
                    <code>CSS = 0.40 × S_cv + 0.60 × S_int</code><br />
                    Combines verified CV background qualifications (40%) with real-time multi-dimensional AI technical interview results (60%).
                  </div>
                </div>

                {/* CV Qualifications Card */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: 16
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
                    <FileText size={15} style={{ color: 'var(--color-primary)' }} />
                    <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-fg)' }}>
                      CV Evaluation Breakdown ({metrics.sCvVal != null ? `${metrics.sCvVal}%` : 'Pending'})
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <ScoreMeter
                      score={metrics.sSkillVal || 0}
                      label="Key Technical Skills Match"
                      size="sm"
                    />
                    <ScoreMeter
                      score={metrics.sExpVal || 0}
                      label="Years & Domain Experience Fit"
                      size="sm"
                    />
                    <ScoreMeter
                      score={metrics.sEduVal || 0}
                      label="Educational Degree Alignment"
                      size="sm"
                    />
                  </div>
                </div>

                {/* Technical Interview & Proctoring Card */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: 16
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Code2 size={15} style={{ color: '#c084fc' }} />
                      <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-fg)' }}>
                        AI Interview Performance
                      </span>
                    </div>

                    {metrics.integrityScore != null && (
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 3,
                        fontSize: '10.5px',
                        fontWeight: 700,
                        color: 'var(--color-success)',
                        background: 'var(--color-success-muted)',
                        padding: '1px 6px',
                        borderRadius: 'var(--radius-full)'
                      }}>
                        <ShieldCheck size={11} /> {metrics.integrityScore}% Proctor Score
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <ScoreMeter
                      score={metrics.pMcqVal || 0}
                      label="MCQ Knowledge Assessment"
                      size="sm"
                    />
                    <ScoreMeter
                      score={metrics.pDescVal || 0}
                      label="Descriptive / Theoretical Answers"
                      size="sm"
                    />
                    <ScoreMeter
                      score={metrics.pCodeVal || 0}
                      label="Live Interactive Coding Challenge"
                      size="sm"
                    />
                  </div>

                  {metrics.isPrereqWarning && (
                    <div style={{
                      marginTop: 10,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      fontSize: '11px',
                      color: 'var(--color-danger)',
                      background: 'var(--color-danger-muted)',
                      padding: '6px 8px',
                      borderRadius: 'var(--radius-sm)'
                    }}>
                      <AlertTriangle size={13} flexShrink={0} />
                      <span>Coding score is below the 25% minimum technical prerequisite threshold.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })()}
      </div>
    </div>
  )
}
