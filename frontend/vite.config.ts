import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import * as fs from 'node:fs'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Read .env.local if it exists
const envLocalPath = path.resolve(__dirname, '.env.local')
let basePath = '/hb_grabber/'

if (fs.existsSync(envLocalPath)) {
  const envContent = fs.readFileSync(envLocalPath, 'utf-8')
  const envMatch = envContent.match(/VITE_BASE_PATH=(.+)/)
  if (envMatch) {
    basePath = envMatch[1].trim()
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: basePath,
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          // Keep image files and XML files in root directory instead of assets folder
          const info = assetInfo.name?.split('.') || [];
          const extType = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico|xml/i.test(extType)) {
            return `[name].[ext]`;
          }
          return `assets/[name]-[hash].[ext]`;
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})