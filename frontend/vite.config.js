import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: true,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5174,
    },
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
            if (id.includes('recharts')) return 'vendor-charts'
            if (id.includes('lucide-react')) return 'vendor-icons'
            if (id.includes('axios')) return 'vendor-utils'
            return 'vendor'
          }
        }
      }
    }
  }
})
