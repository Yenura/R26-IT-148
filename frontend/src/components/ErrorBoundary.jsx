import { Component } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('RecruitAI ErrorBoundary caught exception:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 60, textAlign: 'center', maxWidth: 480, margin: '80px auto' }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--color-danger-muted)', color: 'var(--color-danger)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
            <AlertCircle size={28} />
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-fg)', marginBottom: 8 }}>Something went wrong</h2>
          <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', marginBottom: 16, lineHeight: 1.5 }}>
            An unexpected error occurred. Please try refreshing the page.
          </p>
          {this.state.error && (
            <div style={{ textAlign: 'left', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 8, padding: 12, marginBottom: 20, fontSize: '12px', color: '#f87171', overflowX: 'auto', fontFamily: 'monospace' }}>
              <strong>Error:</strong> {String(this.state.error?.message || this.state.error)}
              {this.state.error?.stack && (
                <pre style={{ marginTop: 8, fontSize: '11px', whiteSpace: 'pre-wrap', maxHeight: 150, overflowY: 'auto' }}>
                  {this.state.error.stack}
                </pre>
              )}
            </div>
          )}
          <button
            className="btn btn-primary btn-sm"
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload() }}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
          >
            <RefreshCw size={14} /> Reload Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
