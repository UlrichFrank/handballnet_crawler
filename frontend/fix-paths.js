import fs from 'fs'
import path from 'path'

// Hardcode the base path (must match vite.config.ts)
const basePath = '/handballnet_crawler/'

const indexPath = path.resolve('dist', 'index.html')
let html = fs.readFileSync(indexPath, 'utf-8')

// Replace absolute asset paths with basePath-prefixed paths in HTML
html = html
  .replace(/src="\/assets\//g, `src="${basePath}assets/`)
  .replace(/href="\/assets\//g, `href="${basePath}assets/`)
  .replace(/href="\/vite\.svg"/g, `href="${basePath}vite.svg"`)
  .replace(/href="\/team-logo\.svg"/g, `href="${basePath}team-logo.svg"`)
  .replace(/src="\/team-logo\.svg"/g, `src="${basePath}team-logo.svg"`)

fs.writeFileSync(indexPath, html)
console.log(`✅ Fixed asset paths in index.html with base path: ${basePath}`)

// Also fix paths in JS bundle
const assetsDir = path.resolve('dist', 'assets')
if (fs.existsSync(assetsDir)) {
  const jsFiles = fs.readdirSync(assetsDir).filter(f => f.endsWith('.js'))
  
  for (const jsFile of jsFiles) {
    const jsPath = path.join(assetsDir, jsFile)
    let js = fs.readFileSync(jsPath, 'utf-8')
    
    // Replace /team-logo.svg with base path
    js = js.replace(/\/team-logo\.svg/g, basePath + 'team-logo.svg')
    
    fs.writeFileSync(jsPath, js)
  }
  
  if (jsFiles.length > 0) {
    console.log(`✅ Fixed asset paths in ${jsFiles.length} JS file(s)`)
  }
}

