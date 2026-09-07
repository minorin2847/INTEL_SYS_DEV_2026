import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, calls to /api/* are proxied to the FastAPI service so the browser
// makes same-origin requests. Override the target with DIABETES_API_URL.
// For a production build, set VITE_API_BASE to the API's public URL.
const apiTarget = process.env.DIABETES_API_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
})
