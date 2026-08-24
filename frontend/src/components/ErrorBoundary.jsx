import { Component } from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends Component {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 60, textAlign: 'center', maxWidth: 480, margin: '80px auto' }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--color-danger-muted)', color: 'var(--color-danger)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
            <AlertCircle size={28} />
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-fg)', marginBottom: 8 }}>Something went wrong</h2>
          <p style={{ fontSize: 'var(--p-text-sm)', color: 'var(--color-fg-muted)', marginBottom: 24, lineHeight: 1.5 }}>
            An unexpected error occurred. Please try refreshing the page.
          </p>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => { this.setState({ hasError: false }); window.location.reload() }}
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
