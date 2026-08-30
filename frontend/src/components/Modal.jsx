import React, { useEffect, useRef } from 'react'
import { X } from 'lucide-react'

export default function Modal({
  open,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 600,
  icon: Icon
}) {
  const dialogRef = useRef(null)
  const previousFocusRef = useRef(null)
  const onCloseRef = useRef(onClose)

  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  useEffect(() => {
    if (!open) return

    previousFocusRef.current = document.activeElement
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (onCloseRef.current) onCloseRef.current()
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

    // Auto-focus only once on open: focus first interactive input or first focusable
    const timer = setTimeout(() => {
      if (dialogRef.current) {
        // Do not steal focus if user has already focused an element inside the dialog
        if (dialogRef.current.contains(document.activeElement) && document.activeElement !== document.body) {
          return
        }
        const firstInput = dialogRef.current.querySelector(
          'input:not([disabled]), select:not([disabled]), textarea:not([disabled])'
        )
        if (firstInput) {
          firstInput.focus()
        } else {
          const firstFocusable = dialogRef.current.querySelector(
            'button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'
          )
          if (firstFocusable) firstFocusable.focus()
        }
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
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 'var(--p-z-modal, 400)',
        background: 'var(--modal-overlay)',
        backdropFilter: 'blur(4px)',
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
        role="dialog"
        aria-modal="true"
        aria-label={title}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          width: '100%',
          maxWidth: maxWidth,
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'var(--shadow-xl)',
          overflow: 'hidden'
        }}
      >
        {/* Modal Header */}
        <div style={{
          padding: 'var(--p-space-4) var(--p-space-5)',
          borderBottom: '1px solid var(--color-border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {Icon && (
              <div style={{
                width: 34,
                height: 34,
                borderRadius: 'var(--radius-md)',
                background: 'var(--color-primary-muted)',
                color: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Icon size={18} />
              </div>
            )}
            <div>
              <h3 style={{ fontSize: 'var(--p-text-lg)', fontWeight: 700, color: 'var(--color-fg)', margin: 0 }}>
                {title}
              </h3>
              {subtitle && (
                <p style={{ fontSize: 'var(--p-text-xs)', color: 'var(--color-fg-muted)', margin: '2px 0 0 0' }}>
                  {subtitle}
                </p>
              )}
            </div>
          </div>

            <button
            onClick={onClose}
            className="btn-ghost btn-sm"
            style={{ padding: 6, borderRadius: 'var(--radius-sm)', color: 'var(--color-fg-muted)' }}
            aria-label="Close modal"
            title="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{
          padding: 'var(--p-space-5)',
          overflowY: 'auto',
          flex: 1
        }}>
          {children}
        </div>
      </div>
    </div>
  )
}
