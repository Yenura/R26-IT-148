import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: true,
  },
  build: {
    target: 'esnext',
    cssCodeSplit: true,
    cssMinify: true,
    minify: 'esbuild',
    reportCompressedSize: false,
    assetsInlineLimit: 4096,
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react-dom') || id.includes('react-router')) return 'vendor-react'
            if (id.includes('lucide-react')) return 'vendor-icons'
            if (id.includes('recharts')) return 'vendor-charts'
            if (id.includes('axios') || id.includes('canvas-confetti')) return 'vendor-utils'
            return 'vendor'
          }
        }
      }
    }
  }
})
