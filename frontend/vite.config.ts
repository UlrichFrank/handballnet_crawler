import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// GitHub Pages serves project repos at /reponame/, so set base accordingly
let basePath = '/handballnet_crawler/'

// Read .env.local if it exists (for local development)
const envLocalPath = path.resolve(__dirname, '.env.local')
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
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})