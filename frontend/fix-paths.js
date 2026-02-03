import fs from 'fs'
import path from 'path'

// Hardcode the base path (must match vite.config.ts)
const basePath = '/handballnet_crawler/'

const indexPath = path.resolve('dist', 'index.html')
let html = fs.readFileSync(indexPath, 'utf-8')

// Replace absolute asset paths with basePath-prefixed paths
html = html
  .replace(/src="\/assets\//g, `src="${basePath}assets/`)
  .replace(/href="\/assets\//g, `href="${basePath}assets/`)
  .replace(/href="\/vite\.svg"/g, `href="${basePath}vite.svg"`)

fs.writeFileSync(indexPath, html)
console.log(`✅ Fixed asset paths in index.html with base path: ${basePath}`)

