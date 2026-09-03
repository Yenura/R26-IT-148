import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FileText, ArrowLeft, Loader2, Upload, Tag, Briefcase, GraduationCap,
  BarChart3, CheckCircle2, ChevronDown, Lightbulb
} from 'lucide-react'
import { c1AnalyzeFile, c1Roles } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'
import UploadZone from '../components/UploadZone'
import SkeletonLoader from '../components/SkeletonLoader'

export default function CVAnalyzeFile() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadRoles()
  }, [])

  const loadRoles = async () => {
    try {
      const res = await c1Roles()
      const rawRoles = res?.data?.roles || []
      const rolesList = Array.isArray(rawRoles)
        ? rawRoles.map((item) => (typeof item === 'string' ? item : item?.role || '')).filter(Boolean)
        : []
      setRoles(rolesList)
    } catch {
      setRoles([])
    }
  }

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setResult(null)
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setResult(null)
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      return toast.error('Please select a file first')
    }
    setUploading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (selectedRole) {
        formData.append('target_role', selectedRole)
      }
      const res = await c1AnalyzeFile(formData)
      setResult(res.data)
      toast.success('CV analyzed successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to analyze CV')
    } finally {
      setUploading(false)
    }
  }

  const skills = result?.skills || result?.extracted_skills || []
  const roleMatch = result?.target_role || result?.predicted_role || result?.job_role || 'N/A'
  const qualityScore = result?.quality_score || result?.overall_score || result?.cv_matching_score || 0
  const experienceYears = result?.experience_years ?? 'N/A'
  const education = result?.education || result?.education_analysis || 'N/A'

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <PageHeader
        badge="CV Analysis"
        title="Analyze CV File"
        description="Upload a candidate CV file for AI-powered analysis including skill extraction and role matching."
        icon={FileText}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/dashboard')}>
            <ArrowLeft size={15} /> Dashboard
          </button>
        }
      />

      {/* Upload Card */}
      <div className="card" style={{ marginBottom: 'var(--p-space-5)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Upload size={18} style={{ color: 'var(--color-primary)' }} /> Upload CV File
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            Supports PDF, DOCX, TXT (Max 10MB)
          </p>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          <UploadZone
            onFileSelect={handleFileSelect}
            uploading={uploading}
            selectedFile={selectedFile}
            onRemoveFile={handleRemoveFile}
          />

          {/* Role Selector */}
          {roles.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <label style={{ fontSize: '12px', marginBottom: 6, display: 'block', fontWeight: 600, color: 'var(--color-fg)' }}>
                Target Role (Optional)
              </label>
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  style={{ width: '100%', appearance: 'none', paddingRight: 36, fontSize: 'var(--p-text-sm)' }}
                >
                  <option value="">Auto-detect role</option>
                  {roles.map((role) => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
                <ChevronDown
                  size={16}
                  style={{
                    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                    pointerEvents: 'none', color: 'var(--color-fg-muted)'
                  }}
                />
              </div>
            </div>
          )}

          {/* Analyze Button */}
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={uploading || !selectedFile}
            >
              {uploading ? (
                <><Loader2 size={15} className="spin" /> Analyzing...</>
              ) : (
                <><FileText size={15} /> Analyze CV</>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-4)' }}>
          {/* Quality Score */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <BarChart3 size={18} style={{ color: 'var(--color-primary)' }} /> Quality Score
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)', display: 'flex', alignItems: 'center', gap: 20 }}>
              <div style={{
                width: 80, height: 80, borderRadius: 'var(--radius-full)',
                background: qualityScore >= 80 ? 'var(--color-success-muted)' : qualityScore >= 60 ? 'var(--color-warning-muted)' : 'var(--color-danger-muted)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: `3px solid ${qualityScore >= 80 ? 'var(--color-success)' : qualityScore >= 60 ? 'var(--color-warning)' : 'var(--color-danger)'}`,
                flexShrink: 0
              }}>
                <span style={{
                  fontSize: '1.3rem', fontWeight: 800,
                  color: qualityScore >= 80 ? 'var(--color-success)' : qualityScore >= 60 ? 'var(--color-warning)' : 'var(--color-danger)'
                }}>
                  {qualityScore.toFixed(0)}
                </span>
              </div>
              <div>
                <div style={{ fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-fg)' }}>
                  {qualityScore >= 80 ? 'Excellent Match' : qualityScore >= 60 ? 'Good Candidate' : 'Needs Improvement'}
                </div>
                <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                  Overall CV quality and role alignment score
                </div>
              </div>
            </div>
          </div>

          {/* Skills Extracted */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Tag size={18} style={{ color: 'var(--color-success)' }} /> Extracted Skills
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {skills.length > 0 ? skills.map((skill, i) => (
                  <span key={`${skill}-${i}`} className="chip" style={{ fontSize: '12px', margin: 0, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <CheckCircle2 size={12} style={{ color: 'var(--color-success)' }} /> {skill}
                  </span>
                )) : (
                  <span style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>No skills extracted</span>
                )}
              </div>
            </div>
          </div>

          {/* Role Match */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Lightbulb size={18} style={{ color: 'var(--color-warning)' }} /> Role Match
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-primary)' }}>
                  {roleMatch}
                </span>
              </div>
            </div>
          </div>

          {/* Experience & Education */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--p-space-4)' }}>
            <div className="card">
              <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-sm)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Briefcase size={16} style={{ color: 'var(--color-info)' }} /> Experience
                </h3>
              </div>
              <div style={{ padding: 'var(--p-space-5)' }}>
                <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', fontWeight: 600 }}>
                  {experienceYears} {experienceYears !== 'N/A' ? 'years' : ''}
                </p>
              </div>
            </div>

            <div className="card">
              <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <h3 style={{ margin: 0, fontSize: 'var(--p-text-sm)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <GraduationCap size={16} style={{ color: 'var(--color-purple)' }} /> Education
                </h3>
              </div>
              <div style={{ padding: 'var(--p-space-5)' }}>
                <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)', fontWeight: 600 }}>
                  {typeof education === 'string' ? education : education?.degree || education?.degree_field || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button className="btn btn-ghost" onClick={() => { setSelectedFile(null); setResult(null) }}>
              Analyze Another CV
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
