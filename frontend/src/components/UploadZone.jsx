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
          style={{
            border: `2px dashed ${dragOver ? 'var(--color-primary)' : 'var(--border)'}`,
            background: dragOver ? 'var(--color-primary-muted)' : 'var(--bg-elevated)',
            borderRadius: 14,
            padding: '36px 24px',
            textAlign: 'center',
            transition: 'all 0.2s ease',
            cursor: 'pointer'
          }}
          onClick={() => document.getElementById('resume-file-input')?.click()}
        >
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--color-primary-muted)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <Upload size={26} />
          </div>
          <h4 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)', marginBottom: 6 }}>
            Drop candidate resume here or <span style={{ color: 'var(--color-primary)', textDecoration: 'underline' }}>Browse Files</span>
          </h4>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
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
        <div style={{ padding: 18, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 42, height: 42, borderRadius: 10, background: 'rgba(59, 130, 246, 0.1)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileText size={22} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>{selectedFile.name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                {(selectedFile.size / 1024).toFixed(1)} KB · {uploading ? 'Processing File...' : 'Ready for AI Screening'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {uploading ? (
              <span className="chip" style={{ fontSize: 12, background: 'var(--color-primary-muted)', color: 'var(--color-primary)', border: '1px solid var(--color-primary)' }}>
                Uploading...
              </span>
            ) : (
              <span className="chip" style={{ fontSize: 12, background: 'rgba(34, 197, 94, 0.1)', color: 'var(--color-success)', border: '1px solid rgba(34, 197, 94, 0.3)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <CheckCircle2 size={13} /> Uploaded
              </span>
            )}
            {onRemoveFile && (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={onRemoveFile}
                style={{ padding: 6, color: 'var(--danger)' }}
                title="Remove file"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      )}

      {fileError && (
        <div style={{ marginTop: 10, fontSize: 13, color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <AlertCircle size={15} /> {fileError}
        </div>
      )}
    </div>
  )
}
