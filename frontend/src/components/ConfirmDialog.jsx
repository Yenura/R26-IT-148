import React, { useEffect, useRef } from 'react'
import { AlertTriangle, Trash2, X } from 'lucide-react'

export default function ConfirmDialog({
  open,
  title = 'Are you sure?',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null)
  const previousFocusRef = useRef(null)
  const onCancelRef = useRef(onCancel)

  useEffect(() => {
    onCancelRef.current = onCancel
  }, [onCancel])

  useEffect(() => {
    if (!open) return

    previousFocusRef.current = document.activeElement
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (onCancelRef.current) onCancelRef.current()
        return
      }

      // Focus trap
      if (e.key === 'Tab' && dialogRef.current) {
        const focusable = Array.from(
          dialogRef.current.querySelectorAll(
            'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
          )
        ).filter((el) => el.offsetParent !== null)

        if (focusable.length === 0) return
        const first = focusable[0]
        const last = focusable[focusable.length - 1]

        if (e.shiftKey) {
          if (document.activeElement === first || !dialogRef.current.contains(document.activeElement)) {
            e.preventDefault()
            last.focus()
          }
        } else {
          if (document.activeElement === last || !dialogRef.current.contains(document.activeElement)) {
            e.preventDefault()
            first.focus()
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    // Auto-focus the confirm button
    const timer = setTimeout(() => {
      if (dialogRef.current) {
        const confirmBtn = dialogRef.current.querySelector('.btn-primary, .btn-danger')
        if (confirmBtn) confirmBtn.focus()
      }
    }, 50)

    return () => {
      clearTimeout(timer)
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = originalOverflow || 'unset'
      if (previousFocusRef.current && previousFocusRef.current.focus) {
        try {
          previousFocusRef.current.focus()
        } catch {
          // Ignore
        }
      }
    }
  }, [open])

  if (!open) return null

  return (
    <div
      onClick={onCancel}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 'var(--p-z-modal, 9999)',
        background: 'var(--modal-overlay)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--p-space-4)',
        animation: 'fadeIn 0.15s ease'
      }}
    >
      <div
        ref={dialogRef}
        onClick={(e) => e.stopPropagation()}
        role="alertdialog"
        aria-modal="true"
        aria-label={title}
        style={{
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border-strong)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--p-space-6)',
          maxWidth: 420,
          width: '100%',
          boxShadow: 'var(--shadow-xl)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 'var(--p-space-5)' }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 'var(--radius-md)',
            flexShrink: 0,
            background: danger ? 'var(--color-danger-muted)' : 'var(--color-primary-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: `1px solid ${danger ? 'rgba(244, 63, 94, 0.25)' : 'rgba(99, 102, 241, 0.25)'}`
          }}>
            {danger
              ? <Trash2 size={20} style={{ color: 'var(--color-danger)' }} />
              : <AlertTriangle size={20} style={{ color: 'var(--color-primary)' }} />}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, color: 'var(--color-fg)', margin: '0 0 6px 0', letterSpacing: '-0.01em' }}>
              {title}
            </h3>
            <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-secondary)', lineHeight: 1.55, margin: 0 }}>
              {message}
            </p>
          </div>
          <button
            onClick={onCancel}
            className="btn-ghost btn-sm"
            aria-label="Cancel"
            style={{ padding: 4, borderRadius: 'var(--radius-sm)', color: 'var(--color-fg-muted)' }}
            title="Cancel"
          >
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <button className="btn btn-ghost btn-sm" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            className={`btn btn-sm ${danger ? 'btn-danger' : 'btn-primary'}`}
            onClick={onConfirm}
            style={danger ? { background: 'var(--color-danger)', color: 'var(--color-on-danger)', border: 'none' } : {}}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
