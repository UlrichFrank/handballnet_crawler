# 🏐 Handball Web Application - Setup & Usage

## 🎯 Was wurde implementiert

Eine moderne React-Webapplikation zur Visualisierung von Handball-Spieldaten, mit direkter Integration des Scrapers.

**Hauptmerkmale**:
- ✅ Liga-Auswahl (C-Jugend, D-Jugend, etc.)
- ✅ Team-Auswahl pro Liga
- ✅ Interaktive Spieltabelle mit Spieltag-basierter Datenstruktur
- ✅ 7 Statistik-Spalten pro Spiel
- ✅ Gesamt-Statistiken für jeden Spieler
- ✅ Professionelles Styling (XLS-Farben)
- ✅ Responsive Design mit Sticky Columns
- ✅ TypeScript + Tailwind CSS

## 🚀 Quick Start

### 1. Daten scrapen (erstmalig)
```bash
# Scrape Spieldaten für alle oder eine spezifische Liga
python3 scraper.py                    # Alle Ligen
# oder
python3 scraper.py mc-ol-3-bw_bwhv   # Nur C-Jugend
```

Daten werden direkt nach `frontend/public/data/<liga_id>/` gespeichert als `<spieltag_datum>.json`

### 2. Frontend starten
```bash
cd frontend
npm install                       # Falls noch nicht geschehen
npm run dev                       # Dev Server auf http://localhost:5173
```

### 3. Zum Handball-App navigieren
Öffne im Browser: **http://localhost:5173/hb_grabber**

## 📊 Datenfluss (NEU)

```
Handball4all Website
    ↓
scraper.py (alle Spieltage)
    ↓
frontend/public/data/
├── c_jugend/
│   ├── 20250920.json (Spieltag 1)
│   ├── 20250927.json (Spieltag 2)
│   └── ...
├── d_jugend/
│   ├── 20250920.json
│   └── ...
└── meta.json (Index aller Spieltage)
    ↓
React App (DataService lädt & cached)
    ↓
Interaktive Tabelle
```

## 📁 Dateistruktur

### Scraped Data Structure
```
frontend/public/data/
├── meta.json                          # Index: Ligen & Spieltag-Übersicht
├── c_jugend/
│   ├── 20250920.json                 # Spieltag als yyyymmdd.json
│   ├── 20250927.json
│   └── ...
└── d_jugend/
    ├── 20250920.json
    └── ...

# meta.json Struktur:
{
  "last_updated": "2026-02-02T...",
  "leagues": {
    "c_jugend": {
      "name": "C-Jugend (MC-OL 3)",
      "spieltage": ["20250920", "20250927", ...],
      "last_updated": "2026-02-02T..."
    },
    "d_jugend": { ... }
  }
}

# 20250920.json Struktur:
{
  "games": [
    {
      "game_id": "...",
      "order": 1,
      "date": "Sa, 20.09.",
      "final_score": "28:25",
      "home": {
        "team_name": "Team A",
        "players": [
          {
            "name": "Spieler 1",
            "goals": 5,
            "seven_meters": 2,
            "seven_meters_goals": 1,
            "two_min_penalties": 1,
            "yellow_cards": 0,
            "red_cards": 0,
            "blue_cards": 0
          }
        ]
      },
      "away": { ... },
      "officials": { ... }
    }
  ]
}
```

### Frontend Components
```
frontend/src/
├── services/
│   └── dataService.ts               # 🔑 Daten-Verwaltung & Loading
├── types/
│   └── handball.ts                  # TypeScript Types
├── components/handball/
│   ├── GameTable.tsx                # Haupt-Tabelle
│   ├── LeagueSelector.tsx           # Liga-Dropdown
│   ├── TeamSelector.tsx             # Team-Dropdown
│   ├── StandingsTable.tsx           # Standings (optional)
│   └── StatCell.tsx                 # Stat-Zelle Logik
└── pages/
    └── HandballPage.tsx             # Main Page
```

## 🎨 XLS-Farbschema (implementiert)

| Element | Farbe | Hex | Tailwind Class |
|---------|-------|-----|-----------------|
| Header | Blau | #4472C4 | `bg-hb-header` |
| Subheader | Hellblau | #D9E1F2 | `bg-hb-subheader` |
| Spieler (odd) | Weiß | #FFFFFF | `bg-white` |
| Spieler (even) | Grau | #F5F5F5 | `bg-hb-playerGray2` |
| Gesamt | Gelb | #FFF2CC | `bg-hb-gesamt` |

## 🛠️ Tech Stack

- **Frontend**: React 19, TypeScript 5.8
- **Styling**: Tailwind CSS 4.1
- **Build**: Vite 7.1
- **Backend**: Python 3.8+ (Scraper)
- **UI**: Radix UI, Lucide Icons
- **Router**: React Router 7

## 📋 Funktionalität

### Scraper
- Automatisches Scraping aller Spieltage
- Inkrementelles Scraping (nur neue Spiele)
- Korrekte Jahr-Behandlung (Sep 2025 - Mai 2026 Saison)
- Gruppierung nach Spieltag (yyyymmdd)
- Meta-Index Auto-Update

### LeagueSelector
- Dropdown mit allen verfügbaren Ligen aus meta.json
- Lädt Teams wenn Liga gewechselt wird

### TeamSelector
- Dropdown mit Teams der gewählten Liga
- Sortiert alphabetisch

### GameTable
- **Header**: Spiel-Info (Datum, Score, Home/Away Icon)
- **Subheader**: Stat-Labels (Tore, 7m, etc.)
- **Spieler-Zeilen**:
  - Spielername (sticky left)
  - Pro Spiel: 7 Statistiken
  - Summary: Saison-Totals
  - Alternating Row Colors
- **GESAMT-Zeile**: Team-Summen (gelber Hintergrund)

### Anzeigelogik (XLS-kompatibel)
```
Tore:              Immer anzeigen (auch 0)
7m Versuche:       "-" wenn 0
7m Tore:           "-" wenn keine Versuche OR wenn 0
2-Min Penalties:   "-" wenn 0
Gelb/Rot/Blau:     "-" wenn 0
```

## 🔍 API / Services

### DataService Methoden
```typescript
// Liga-Management
await dataService.getLeagues()                    // Alle Ligen
await dataService.getTeamsForLeague(outName)     // Teams einer Liga
await dataService.getGameData(outName, spieltag) // Spieltag-Daten laden

// Spiel-Daten
dataService.getTeamGames(gameData, teamName)     // Team's Spiele (Home+Away)
dataService.getTeamPlayers(teamGames)            // Alle Spieler des Teams

// Statistiken
dataService.getPlayerGameStats(game, playerName)       // Einzelspiel-Stats
dataService.getPlayerTotalStats(teamGames, playerName) // Gesamt-Stats
dataService.getGameTotals(game)                        // Team-Summen pro Spiel
```

## 🚀 Build & Deploy

### Production Build
```bash
cd frontend
npm run build                  # → dist/ Ordner (mit Daten)
npm run preview                # Lokales Preview
```

### Deployment
Die `dist/` Datei kann auf jeden Static Host deployed werden:
- Netlify, Vercel, GitHub Pages
- Apache/Nginx
- S3 + CloudFront

**Wichtig**: Stelle sicher, dass `dist/data/` mit den neuesten Spieltag-Dateien aktualisiert wird!

## ⚠️ Troubleshooting

### "Keine Daten sichtbar"
1. Prüfe ob Scraper gelaufen ist:
   ```bash
   ls -la frontend/public/data/c_jugend/
   ```
2. Prüfe ob meta.json aktualisiert wurde:
   ```bash
   cat frontend/public/data/meta.json
   ```
3. Browser-Cache leeren (Hard Refresh)

### "Daten werden nicht geladen"
- Öffne Browser DevTools (F12) → Network Tab
- Suche nach `meta.json` Request - sollte 200 Status haben
- Prüfe ob `/hb_grabber/data/` Path korrekt ist

### "Styling sieht seltsam aus"
- Cache leeren: Hard Refresh (Cmd+Shift+R oder Ctrl+Shift+R)
- Tailwind rebuild: `npm run build`

### "Teams nicht vorhanden"
- Sicherstelle, dass Scraper tatsächlich Teams gefunden hat
- Prüfe Scraper-Output nach Fehlern

### "Falsches Spieltag-Datum"
- Der Scraper parst Daten wie "Sa, 20.09." und bestimmt das Jahr automatisch
- Bei Saisonwechsel (Sep → Jan) wird das Jahr korrekt angepasst
- Falls Problem: Prüfe ob `meta.json` korrekte yyyymmdd-Keys hat

## 🔄 Scraper-Optionen

```bash
# Alle Ligen scrapen
python3 scraper.py

# Einzelne Liga scrapen
python3 scraper.py mc-ol-3-bw_bwhv
python3 scraper.py gd-bol-srm_srm

# Config prüfen
cat config/config.json
```

## 📞 Weitere Entwicklung

### Aktuelle Phase
- ✅ Datenstruktur optimiert (pro Spieltag)
- ✅ Jahr-Handling für Saisonübergang
- ✅ Meta-Index Auto-Update
- ✅ Frontend-Integration

### Nächste Schritte
- [ ] Spieltag-Selector (Dropdown für verschiedene Spieltage)
- [ ] Performance-Optimierung für viele Spieltage
- [ ] A11y Audit (WCAG 2.1)
- [ ] Mobile UI verbessern

---

**Status**: ✅ Phase 3 aktualisiert - neue Datenstruktur  
**Version**: 1.1.0  
**Last Updated**: 2026-02-02
