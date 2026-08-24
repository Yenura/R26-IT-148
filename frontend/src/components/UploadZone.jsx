import { useState } from 'react'
import { Upload, FileText, X, CheckCircle2, AlertCircle } from 'lucide-react'

export default function UploadZone({ onFileSelect, uploading, selectedFile, onRemoveFile }) {
  const [dragOver, setDragOver] = useState(false)
  const [fileError, setFileError] = useState('')

  const validateAndPass = (file) => {
    setFileError('')
    if (!file) return
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
      setFileError('Unsupported file format. Please upload PDF, DOCX, or TXT.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setFileError('File size exceeds 10MB limit.')
      return
    }
    onFileSelect(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndPass(e.dataTransfer.files[0])
    }
  }

  return (
    <div style={{ width: '100%' }}>
      {!selectedFile ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById('resume-file-input')?.click()}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); document.getElementById('resume-file-input')?.click() } }}
          tabIndex={0}
          role="button"
          aria-label="Upload resume file"
          style={{
            border: `2px dashed ${dragOver ? 'var(--color-primary)' : 'var(--color-border)'}`,
            background: dragOver ? 'var(--color-primary-muted)' : 'var(--color-bg-elevated)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--p-space-8) var(--p-space-6)',
            textAlign: 'center',
            transition: 'all var(--duration-normal) var(--ease)',
            cursor: 'pointer',
            boxShadow: dragOver ? '0 0 24px rgba(99, 102, 241, 0.2)' : 'var(--shadow-sm)'
          }}
          onClick={() => document.getElementById('resume-file-input')?.click()}
        >
          <div style={{
            width: 58,
            height: 58,
            borderRadius: 'var(--radius-full)',
            background: 'var(--color-primary-muted)',
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto var(--p-space-4)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            boxShadow: '0 4px 16px rgba(99, 102, 241, 0.2)'
          }}>
            <Upload size={26} />
          </div>
          <h4 style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)', marginBottom: 6 }}>
            Drop candidate resume here or <span style={{ color: 'var(--color-primary)', textDecoration: 'underline' }}>Browse Files</span>
          </h4>
          <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: 0 }}>
            Supports PDF, DOCX, TXT (Maximum file size: 10MB)
          </p>
          <input
            id="resume-file-input"
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={(e) => validateAndPass(e.target.files[0])}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        <div style={{
          padding: 'var(--p-space-4) var(--p-space-5)',
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary-muted)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(99, 102, 241, 0.25)'
            }}>
              <FileText size={22} />
            </div>
            <div>
              <div style={{ fontSize: 'var(--p-text-base)', fontWeight: 700, color: 'var(--color-fg)' }}>
                {selectedFile.name}
              </div>
              <div style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', marginTop: 2 }}>
                {(selectedFile.size / 1024).toFixed(1)} KB · {uploading ? 'Processing AI feature vectors...' : 'Ready for AI Screening'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {uploading ? (
              <span className="chip" style={{ fontSize: '11px', background: 'var(--color-primary-muted)', color: 'var(--color-primary)', border: '1px solid var(--color-primary)' }}>
                Parsing & Extracting...
              </span>
            ) : (
              <span className="chip" style={{ fontSize: '11px', background: 'var(--color-success-muted)', color: 'var(--color-success)', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <CheckCircle2 size={13} /> Uploaded
              </span>
            )}
            {onRemoveFile && (
              <button
                type="button"
                className="btn-ghost btn-sm"
                onClick={onRemoveFile}
                aria-label="Remove file"
                style={{ padding: 6, color: 'var(--color-danger)', borderRadius: 'var(--radius-sm)' }}
                title="Remove file"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      )}

      {fileError && (
        <div style={{ marginTop: 10, fontSize: 'var(--p-text-xs)', color: 'var(--color-danger)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <AlertCircle size={14} /> {fileError}
        </div>
      )}
    </div>
  )
}
