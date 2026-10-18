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
        // Only split packages the app actually imports (verified by grep:
        // three/fiber/drei/framer-motion/gsap/remotion have zero imports
        // in src). Listing unimported packages here forces Rollup to emit
        // dead ~180KB+ chunks, so they stay out.
        manualChunks: {
          'vendor-icons': ['lucide-react'],
          'vendor-charts': ['recharts'],
          'vendor-utils': ['axios'],
        }
      }
    }
  }
})
