import { useState } from 'react'
import toast from 'react-hot-toast'
import {
  Upload, ClipboardPaste, Send, Loader2, Tag, GraduationCap,
  Briefcase, Lightbulb, CheckCircle
} from 'lucide-react'
import { uResumeUpload, uResumeParse } from '../api'
import UploadZone from './UploadZone'

/**
 * Shared CV ingestion: file upload + paste-text tabs in one place.
 * Merges the former ResumeParse / CVAnalyzeFile / RolePredict flows —
 * role prediction is covered by CV Match auto-classification downstream.
 *
 * Props:
 *   onIngested({ kind: 'upload'|'paste', data }) — host refresh hook
 *   onDone()      — fired after a successful ingest (e.g. collapse container)
 *   uploadToast   — override success message for file uploads
 */
export default function CVIngest({ onIngested, onDone, uploadToast }) {
  const [tab, setTab] = useState('upload')
  const [uploading, setUploading] = useState(false)
  const [text, setText] = useState('')
  const [parsing, setParsing] = useState(false)
  const [parseResult, setParseResult] = useState(null)

  const handleFile = async (file) => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    try {
      const res = await uResumeUpload(formData)
      toast.success(uploadToast || 'Resume uploaded & parsed!')
      onIngested?.({ kind: 'upload', data: res.data })
      onDone?.()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleParse = async () => {
    if (!text.trim()) {
      return toast.error('Please paste your resume text first')
    }
    setParsing(true)
    setParseResult(null)
    try {
      const res = await uResumeParse({ text: text.trim() })
      setParseResult(res.data)
      toast.success('Resume parsed successfully!')
      onIngested?.({ kind: 'paste', data: res.data })
      // NOTE: no onDone() here — the container must stay open so the
      // extraction preview remains visible (uploads collapse via onDone).
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to parse resume')
    } finally {
      setParsing(false)
    }
  }

  const tabBtn = (key, icon, label) => (
    <button
      key={key}
      type="button"
      onClick={() => setTab(key)}
      className={`btn btn-sm ${tab === key ? 'btn-primary' : 'btn-ghost'}`}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
    >
      {icon} {label}
    </button>
  )

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {tabBtn('upload', <Upload size={14} />, 'Upload File')}
        {tabBtn('paste', <ClipboardPaste size={14} />, 'Paste Text')}
      </div>

      {tab === 'upload' ? (
        <UploadZone
          onFileSelect={handleFile}
          uploading={uploading}
        />
      ) : (
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={'Paste your resume text here...\n\nExample:\nJohn Doe\nSoftware Engineer\n\nSkills:\nPython, JavaScript, React, Docker, SQL, Git'}
            rows={8}
            style={{ fontSize: 'var(--p-text-sm)', width: '100%', resize: 'vertical' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
            <span style={{ fontSize: '11px', color: 'var(--color-fg-muted)' }}>
              {text.length} characters
            </span>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleParse}
              disabled={parsing || !text.trim()}
            >
              {parsing ? (
                <><Loader2 size={14} className="spin" /> Parsing...</>
              ) : (
                <><Send size={14} /> Parse Resume</>
              )}
            </button>
          </div>

          {parseResult && (
            <div className="card" style={{ marginTop: 12, padding: 'var(--p-space-4)' }}>
              {(parseResult.skills || []).length > 0 && (
                <div style={{ marginBottom: 10 }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <Tag size={13} /> Extracted Skills
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {parseResult.skills.map((skill, i) => (
                      <span key={`${skill}-${i}`} className="chip" style={{ fontSize: '11px', margin: 0, display: 'flex', alignItems: 'center', gap: 4 }}>
                        <CheckCircle size={11} style={{ color: 'var(--color-success)' }} /> {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)' }}>
                {(parseResult.experience_years !== undefined || parseResult.experience) && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Briefcase size={12} /> {parseResult.experience_years !== undefined ? `${parseResult.experience_years} yrs` : parseResult.experience}
                  </span>
                )}
                {parseResult.education && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <GraduationCap size={12} /> {parseResult.education}
                  </span>
                )}
                {(parseResult.suggested_role || parseResult.predicted_role) && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--color-primary)', fontWeight: 700 }}>
                    <Lightbulb size={12} /> {parseResult.suggested_role || parseResult.predicted_role}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
