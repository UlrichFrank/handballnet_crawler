# Handball Web Application

Eine moderne React-basierte Webapplikation zur Visualisierung von Handball-Spieldaten und Spielerstatistiken, orientiert am Excel-Report-Layout.

## 🚀 Features

- **Liga-Auswahl**: Wähle zwischen verschiedenen Ligen (C-Jugend, D-Jugend, etc.)
- **Team-Auswahl**: Filtern nach Teams innerhalb einer Liga
- **Interaktive Spieltabelle**:
  - Spieler-Übersicht (sortiert alphabetisch)
  - Pro Spiel: 7 Statistik-Spalten (Tore, 7m Versuche, 7m Tore, 2-Min, Gelb, Rot, Blau)
  - Summary-Spalten mit Gesamt-Statistiken
  - GESAMT-Zeile mit Team-Summen
  - Alternating Row Colors für bessere Lesbarkeit
- **Professionelles Design**:
  - XLS-Farbschema (Blau-Header, Gelbe Gesamt-Zeile)
  - Responsive Layout mit horizontalem Scrollen
  - Sticky Player-Spalte (bleibt beim Scrollen fixiert)
  - Desktop & Mobile optimiert

## 🏗️ Architektur

### Daten-Layer
```
config/config.json (Ligen-Konfiguration)
    ↓
output/spiele_*.json (Spieldaten pro Liga)
    ↓
frontend/public/data/ (Web-verfügbar)
```

### Component-Struktur
```
HandballPage (Main Page)
├── LeagueSelector (Liga-Dropdown)
├── TeamSelector (Team-Dropdown)
└── GameTable (Haupt-Komponente)
    └── StatCell (Einzelne Statistik-Zelle)
```

### Services
- **dataService.ts**: Daten laden, parsen, aggregieren
  - `loadConfig()`: Ligen-Konfiguration laden
  - `getLeagues()`: Verfügbare Ligen abrufen
  - `getGameData(outName)`: Spieldaten laden & cachen
  - `getTeamsForLeague()`: Teams einer Liga
  - `getTeamGames()`: Alle Spiele eines Teams
  - `getPlayerGameStats()`: Spielerstatistiken pro Spiel
  - `getPlayerTotalStats()`: Aggregierte Spielerstatistiken
  - `getGameTotals()`: Team-Summen pro Spiel

## 📊 Daten-Logik (XLS-kompatibel)

Die Tabellendarstellung folgt exakt dem Excel-Report:

### Stat-Anzeige-Regeln
| Stat | 0-Wert Anzeige | Spezial |
|------|-----------------|---------|
| **Tore** | `0` | Immer anzeigen |
| **7m Versuche** | `-` | Nur wenn 0 |
| **7m Tore** | `-` | Nur wenn keine 7m Versuche |
| **2-Min** | `-` | Nur wenn 0 |
| **Gelb/Rot/Blau** | `-` | Nur wenn 0 |

### GESAMT-Zeile
- Summiert alle Spielerstatistiken pro Spiel
- Gelber Hintergrund (#FFF2CC) wie XLS
- Gleiche Anzeigelogik wie Spielerstatistiken

## 🛠️ Technologie-Stack

- **Frontend**: React 19 + TypeScript
- **Styling**: Tailwind CSS 4.1 + PostCSS
- **Build**: Vite 7.x
- **UI Components**: Radix UI, Lucide Icons
- **Routing**: React Router 7

## 📁 Dateistruktur

```
frontend/
├── public/
│   ├── config.json          # Ligen-Konfiguration
│   └── data/
│       ├── spiele_c_jugend.json
│       └── spiele_d_jugend.json
├── src/
│   ├── components/
│   │   └── handball/
│   │       ├── GameTable.tsx        # Haupt-Tabelle
│   │       ├── LeagueSelector.tsx   # Liga-Auswahl
│   │       ├── TeamSelector.tsx     # Team-Auswahl
│   │       └── StatCell.tsx         # Statistik-Zelle
│   ├── services/
│   │   └── dataService.ts           # Daten-Management
│   ├── types/
│   │   └── handball.ts              # TypeScript Types
│   └── pages/
│       └── HandballPage.tsx         # Main Page
├── tailwind.config.js               # Tailwind mit HB-Farben
└── package.json

```

## 🎨 Tailwind Colors (XLS-Palette)

```javascript
colors: {
  hb: {
    header: "#4472C4",      // Header Blau
    subheader: "#D9E1F2",   // Light Blue
    playerGray1: "#E7E6E6", // Dunkel Grau (Player Rows)
    playerGray2: "#F5F5F5", // Hell Grau (Alternating)
    gesamt: "#FFF2CC",      // Yellow (Totals)
    white: "#FFFFFF",
  }
}
```

## 🚀 Quick Start

### Development
```bash
cd frontend
npm install
npm run dev
```
Dann öffne http://localhost:5173/handball

### Production Build
```bash
npm run build
npm run preview
```

## 📋 Roadmap (Phase 4 & 5)

### Phase 4: Features & Polish
- [x] Build erfolgreich
- [ ] Error Handling verbessern
- [ ] Loading States optimieren
- [ ] Accessibility (a11y) prüfen
- [ ] Performance für große Datenmengen

### Phase 5: Optionale Features
- [ ] Spieler-Suchfunktion
- [ ] Filter & Sorting
- [ ] Grafiken einbinden
- [ ] Export (CSV/PDF)
- [ ] Mobile-spezifische UI

## 🐛 Debugging

### Häufige Probleme

**Daten werden nicht geladen?**
- Sicherstellen, dass `config.json` und `*.json` Dateien in `frontend/public/` sind
- Browser DevTools → Network Tab → Requests zu `/config.json` und `/data/` prüfen

**Styling sieht falsch aus?**
- Tailwind Build neu starten: `npm run build`
- Browser Cache leeren (Hard Refresh: Cmd+Shift+R)

**TypeScript Fehler?**
- `npm run lint` zur Überprüfung
- TSConfig in `tsconfig.json` prüfen

## 📝 Notizen für Entwickler

- DataService ist ein Singleton (cacht Daten automatisch)
- Alle Player/Team-Namen werden alphabetisch sortiert
- Spiele werden nach `order` Field sortiert (aus JSON)
- StatCell regelt automatisch die "-" Anzeigelogik
- Die Tabelle scrollt horizontal, Player-Spalte bleibt sticky

## 🔄 Integration mit bestehenden Scripts

Die WebApp nutzt die gleichen JSON-Dateien wie der Python-Report-Generator:
```bash
# Daten generieren
python generate_excel_report.py

# Kopiere zu Web
cp output/spiele_*.json frontend/public/data/
cp config/config.json frontend/public/config.json
```

---

**Version**: 1.0.0  
**Status**: Production Ready (Phase 3 abgeschlossen, Phase 4 in Arbeit)
