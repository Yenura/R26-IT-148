import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FileText, ArrowLeft, Send, Loader2, Tag, GraduationCap, Briefcase,
  Lightbulb, CheckCircle
} from 'lucide-react'
import { uResumeParse } from '../api'
import { useAuth } from '../hooks/useAuth'
import PageHeader from '../components/PageHeader'

export default function ResumeParse() {
  const navigate = useNavigate()
  useAuth('candidate')

  const [text, setText] = useState('')
  const [parsing, setParsing] = useState(false)
  const [result, setResult] = useState(null)

  const handleParse = async () => {
    if (!text.trim()) {
      return toast.error('Please paste your resume text first')
    }
    setParsing(true)
    setResult(null)
    try {
      const res = await uResumeParse({ text: text.trim() })
      setResult(res.data)
      toast.success('Resume parsed successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to parse resume')
    } finally {
      setParsing(false)
    }
  }

  return (
    <div className="fade-in" style={{ maxWidth: 800, margin: '0 auto' }}>
      <PageHeader
        badge="Resume Parser"
        title="Parse Resume Text"
        description="Paste your resume content below to extract skills, experience, and education using AI."
        icon={FileText}
        actions={
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/candidate/dashboard')}>
            <ArrowLeft size={15} /> Dashboard
          </button>
        }
      />

      {/* Input Card */}
      <div className="card" style={{ marginBottom: 'var(--p-space-5)' }}>
        <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileText size={18} style={{ color: 'var(--color-primary)' }} /> Resume Content
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
            Copy and paste the full text of your resume below
          </p>
        </div>
        <div style={{ padding: 'var(--p-space-5)' }}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`Paste your resume text here...\n\nExample:\nJohn Doe\nSoftware Engineer\n\nEducation:\nBSc Computer Science, University of Technology, 2022\n\nExperience:\nJunior Developer at TechCorp (2022-Present)\n- Built REST APIs with Python and FastAPI\n- Developed React frontend components\n\nSkills:\nPython, JavaScript, React, Docker, SQL, Git`}
            rows={12}
            style={{ fontSize: 'var(--p-text-sm)', width: '100%', resize: 'vertical' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 }}>
            <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
              {text.length} characters
            </span>
            <button
              className="btn btn-primary"
              onClick={handleParse}
              disabled={parsing || !text.trim()}
            >
              {parsing ? (
                <><Loader2 size={15} className="spin" /> Parsing...</>
              ) : (
                <><Send size={15} /> Parse Resume</>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Parsing Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--p-space-4)' }}>
          {/* Skills */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Tag size={18} style={{ color: 'var(--color-success)' }} /> Extracted Skills
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {(result.skills || []).length > 0 ? result.skills.map((skill, i) => (
                  <span key={`${skill}-${i}`} className="chip" style={{ fontSize: '12px', margin: 0, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <CheckCircle size={12} style={{ color: 'var(--color-success)' }} /> {skill}
                  </span>
                )) : (
                  <span style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)' }}>No skills extracted</span>
                )}
              </div>
            </div>
          </div>

          {/* Experience */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Briefcase size={18} style={{ color: 'var(--color-info)' }} /> Experience
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                {result.experience_years !== undefined
                  ? `${result.experience_years} years of experience`
                  : result.experience || 'No experience information extracted'}
              </p>
            </div>
          </div>

          {/* Education */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <GraduationCap size={18} style={{ color: 'var(--color-purple)' }} /> Education
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', color: 'var(--color-fg)' }}>
                {result.education || 'No education information extracted'}
              </p>
            </div>
          </div>

          {/* Suggested Role */}
          <div className="card">
            <div style={{ padding: 'var(--p-space-5)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--p-text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Lightbulb size={18} style={{ color: 'var(--color-warning)' }} /> Suggested Role
              </h3>
            </div>
            <div style={{ padding: 'var(--p-space-5)' }}>
              <p style={{ margin: 0, fontSize: 'var(--p-text-sm)', fontWeight: 700, color: 'var(--color-primary)' }}>
                {result.suggested_role || result.predicted_role || 'Unable to determine role'}
              </p>
              {result.role_confidence && (
                <p style={{ margin: '6px 0 0', fontSize: '11px', color: 'var(--color-fg-muted)' }}>
                  Confidence: {(result.role_confidence * 100).toFixed(0)}%
                </p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button className="btn btn-ghost" onClick={() => { setText(''); setResult(null) }}>
              Clear & Parse Another
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/candidate/resume/predict-role')}>
              Predict Role from Resume
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
