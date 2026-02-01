# 🏐 Handball Web Application - Setup & Usage

## 🎯 Was wurde implementiert

Eine moderne React-Webapplikation zur Visualisierung von Handball-Spieldaten, basierend auf dem bestehenden Excel-Report-Layout.

**Hauptmerkmale**:
- ✅ Liga-Auswahl (C-Jugend, D-Jugend, etc.)
- ✅ Team-Auswahl pro Liga
- ✅ Interaktive Spieltabelle mit XLS-Layout
- ✅ 7 Statistik-Spalten pro Spiel
- ✅ Gesamt-Statistiken für jeden Spieler
- ✅ Professionelles Styling (XLS-Farben)
- ✅ Responsive Design mit Sticky Columns
- ✅ TypeScript + Tailwind CSS

## 🚀 Quick Start

### 1. Daten vorbereiten
```bash
# Stelle sicher, dass die JSON-Dateien existieren
ls output/spiele_*.json           # Spieldaten
ls config/config.json             # Ligen-Konfiguration

# Kopiere zu Frontend Public
cp config/config.json frontend/public/config.json
cp output/spiele_*.json frontend/public/data/
```

### 2. Frontend starten
```bash
cd frontend
npm install                       # Falls noch nicht geschehen
npm run dev                       # Dev Server auf http://localhost:5173
```

### 3. Zum Handball-App navigieren
Öffne im Browser: **http://localhost:5173/handball**

## 📊 Datenfluss

```
config/config.json (Ligen)
    ↓
output/spiele_*.json (Spieldaten)
    ↓
frontend/public/{config.json, data/*.json}
    ↓
React App (DataService lädt & cached)
    ↓
Interaktive Tabelle
```

## 📁 Neue Dateien

### Frontend Components
```
frontend/src/
├── services/
│   └── dataService.ts               # 🔑 Daten-Verwaltung
├── types/
│   └── handball.ts                  # TypeScript Types
├── components/handball/
│   ├── GameTable.tsx                # Haupt-Tabelle
│   ├── LeagueSelector.tsx           # Liga-Dropdown
│   ├── TeamSelector.tsx             # Team-Dropdown
│   └── StatCell.tsx                 # Stat-Zelle Logik
└── pages/
    └── HandballPage.tsx             # Main Page
```

### Public Data
```
frontend/public/
├── config.json                      # ← Kopiere von config/config.json
└── data/
    ├── spiele_c_jugend.json         # ← Kopiere von output/
    └── spiele_d_jugend.json         # ← Kopiere von output/
```

### Dokumentation
```
frontend/HANDBALL_APP.md             # Ausführliche Dokumentation
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
- **UI**: Radix UI, Lucide Icons
- **Router**: React Router 7

## 📋 Funktionalität

### LeagueSelector
- Dropdown mit allen verfügbaren Ligen
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
await dataService.getGameData(outName)           // Spieldaten laden

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
npm run build                  # → dist/ Ordner
npm run preview                # Lokales Preview
```

### Deployment
Die `dist/` Datei kann auf jeden Static Host deployed werden:
- Netlify, Vercel, GitHub Pages
- Apache/Nginx
- S3 + CloudFront

## ⚠️ Troubleshooting

### "Daten werden nicht geladen"
- Sicherstelle, dass `frontend/public/config.json` existiert
- Sicherstelle, dass `frontend/public/data/spiele_*.json` existiert
- Browser DevTools → Network → Requests prüfen

### "Styling sieht seltsam aus"
- Cache leeren: Hard Refresh (Cmd+Shift+R oder Ctrl+Shift+R)
- Tailwind rebuild: `npm run build`

### "Teams nicht vorhanden"
- Sicherstelle, dass `config.json` gültig ist
- Prüfe ob `output_name` in config mit JSON-Dateiname übereinstimmt

## 📞 Weitere Entwicklung

### Phase 4 (Nächste Schritte)
- [ ] Performance-Optimierung für 50+ Spieler
- [ ] A11y Audit (WCAG 2.1)
- [ ] Mobile UI verbessern

### Phase 5 (Optional)
- [ ] Spieler-Suche/Filter
- [ ] Sortierbare Spalten
- [ ] CSV/PDF Export
- [ ] Grafiken aus JSON einbinden

## 📖 Vollständige Doku

Siehe `frontend/HANDBALL_APP.md` für:
- Detaillierte Komponenten-Architektur
- Daten-Struktur & Logik
- Integration mit Python-Generator
- Entwickler-Notizen

---

**Status**: ✅ Phase 3 abgeschlossen - Produktionsreif  
**Version**: 1.0.0  
**Last Updated**: 2026-02-01
