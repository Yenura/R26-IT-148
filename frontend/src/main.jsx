import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3500,
            style: {
              background: 'var(--color-bg-elevated)',
              color: 'var(--color-fg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              fontSize: '13px',
              fontWeight: 500,
              padding: '12px 16px',
            },
            success: {
              iconTheme: {
                primary: 'var(--color-success)',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: 'var(--color-danger)',
                secondary: '#fff',
              },
            },
          }}
        />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
