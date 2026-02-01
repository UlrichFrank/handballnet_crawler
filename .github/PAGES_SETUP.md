# GitHub Pages Konfiguration

Diese Anwendung wird automatisch mit GitHub Pages deployt.

## Setup (manuell notwendig):

1. **Repository Settings** → **Pages**
   - Source: Deploy from a branch
   - Branch: `gh-pages` (wird von GitHub Actions erstellt)
   - Folder: `/ (root)`

2. **Actions Permissions**
   - Settings → Actions → General → Workflow permissions
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

3. **Trigger**
   - Täglich um 6:00 UTC (konfigurierbar in scrape-and-deploy.yml)
   - Oder manuell via: Actions → Scrape & Deploy to Pages → Run workflow

## Workflow

```
scrape-and-deploy.yml:
├─ Checkout code
├─ Setup Python + Node
├─ Install dependencies
├─ Run scraper.py
│   └─ Speichert Daten nach: frontend/public/data/{liga}/spieltag_N.json
│   └─ Aktualisiert: frontend/public/data/meta.json
├─ Build frontend (npm run build)
├─ Commit Datenänderungen
├─ Upload Pages artifact (frontend/dist)
└─ Deploy zu GitHub Pages
```

## Result

- 🌐 **URL**: https://ulrich-frank.github.io/hb_grabber/
- 📊 **Daten**: `https://ulrich-frank.github.io/hb_grabber/data/meta.json`
- 🎮 **App**: `https://ulrich-frank.github.io/hb_grabber/`

## Debugging

Fehlerhafte Läufe anschauen: Actions Tab → Scrape & Deploy to Pages → Failed Run
