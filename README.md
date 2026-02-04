# 🏐 Handball Spiele Scraper & WebApp

Ein vollständiges System zur Erfassung, Analyse und Visualisierung von Handball-Spieldaten mit Web-UI, interaktiven Grafiken und Excel-Reports.

## ✨ Features

### 📊 Datenerfassung (Scraper)
- **Mehrere Ligen**: Unbegrenzte Anzahl von Ligen konfigurierbar
- **Vollständige Spielerdaten**: Tore, 7-Meter, Strafen, Karten
- **Inkrementelle Updates**: Speichert Spieltag-weise lokal
- **Tor-Timeline**: Extrakt exakte Zeitpunkte aus PDF-Berichten
- **Automatisierte Aktualisierung**: GitHub Actions (täglich 21:00 CET)

### 🎨 Visualisierung & WebApp
- **Interactive Grafiken**: Canvas-basierte Spiel-Ablauf-Visualisierung
- **Interaktive Timeline**: Hover-Tooltips mit Spielerinfos
- **Responsive Design**: Desktop & Mobile optimiert
- **6 Statistik-Rankings**:
  - 🥅 Torschützen (Top Scorer)
  - 🎯 7-Meter-Schützen (mit Trefferquote)
  - ⚔️ Bestes Torverhältnis (Goal Differential)
  - 🔥 Bester Angriff (Offensive)
  - 🛡️ Beste Verteidigung (Defensive)
  - ⚖️ Fair Play (Gewichtete Strafen-Statistik)

### 📋 Berichte
- **Excel-Export**: Pro Liga eine Datei mit allen Spieldaten
- **Team-Detailansichten**: Spieler-Statistiken pro Team
- **Automatisierte Generierung**: Bei jedem Scraper-Lauf

### 🌐 Deployment
- **GitHub Pages**: Automatisches Deployment nach jedem Scraper-Lauf
- **CI/CD Pipeline**: GitHub Actions mit täglichem Schedule + manueller Trigger
- **Live unter**: https://ulrichfrank.github.io/handballnet_crawler/

---

## 🚀 Quick Start

### 1. Installation

**Anforderungen:**
- Python 3.10+
- Node.js 18+
- Chrome/Chromium (für Selenium)
- Git

**Setup:**
```bash
# Clone Repository
git clone https://github.com/UlrichFrank/handballnet_crawler.git
cd handballnet_crawler

# Python Dependencies
pip install -r requirements.txt

# Node Dependencies
npm install
cd frontend && npm install && cd ..
```

### 2. Konfiguration

**Config-Datei**: `config/config.json`

```json
{
  "ref": {
    "base_url": "https://www.handball.net"
  },
  "ssl": {
    "verify_ssl": true,
    "cert_path": "~/root-ca.crt"
  },
  "crawler": {
    "timeout": 30,
    "retry_attempts": 3,
    "delay_between_requests": 1,
    "date_from": "2025-09-13",
    "date_to": "2026-05-10"
  },
  "leagues": [
    {
      "name": "mc-ol-3-bw_bwhv",
      "display_name": "Handball4all Baden-Württemberg MC-OL 3",
      "half_duration": 25
    },
    {
      "name": "gd-bol-srm_srm",
      "display_name": "Handball4all Baden-Württemberg MD-BOL",
      "half_duration": 20
    }
  ]
}
```

**Konfigurationsfelder pro Liga:**
| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `name` | Eindeutige Liga-ID (URL-safe) | `mc-ol-3-bw_bwhv` |
| `display_name` | Anzeigename in der UI | `Handball4all Baden-Württemberg MC-OL 3` |
| `half_duration` | Spieldauer einer Halbzeit (Minuten) | `25` |

**Standard-Halbzeit-Dauer nach Altersgruppe:**
- A-Jugend (17-18 Jahre): **2 × 30 Minuten**
- B-Jugend (15-16 Jahre): **2 × 25 Minuten**
- C-Jugend (13-14 Jahre): **2 × 25 Minuten**
- D-Jugend (11-12 Jahre): **2 × 20 Minuten**

### 3. Scraper ausführen

```bash
# Neue Daten von handball.net scrapen
python scraper.py

# Output:
# ✓ Speichert Spieltag-JSON pro Tag: frontend/public/data/{liga_name}/{yyyymmdd}.json
# ✓ Aktualisiert meta.json mit Spieltag-Index
```

### 4. Grafiken & Reports generieren

```bash
# Tor-Timeline-Grafiken zeichnen
python generate_graphics_from_json.py

# Excel-Reports erstellen
python generate_excel_report.py

# Output:
# ✓ output/{liga_name}.xlsx (pro Liga eine Excel-Datei)
```

### 5. WebApp starten

```bash
# Development
npm run dev
# → http://localhost:5173

# Production Build
npm run build
# → frontend/dist/

# Preview
npm run preview
```

---

## 📁 Projekt-Struktur

```
handballnet_crawler/
├── config/
│   ├── config.json              # Hauptkonfiguration (Ligas, Date Range)
│   ├── config.example.json      # Beispiel mit mehr Ligen
│   └── config.gh.json          # GitHub Actions Config
├── frontend/
│   ├── public/
│   │   ├── config.json         # Frontend-Konfiguration
│   │   ├── data/              # Spieltag-JSON-Dateien (per Scraper generiert)
│   │   │   ├── meta.json
│   │   │   ├── mc-ol-3-bw_bwhv/
│   │   │   │   ├── 20250920.json
│   │   │   │   ├── 20250927.json
│   │   │   │   └── ...
│   │   │   └── gd-bol-srm_srm/
│   │   │       └── ...
│   │   └── index.html
│   ├── src/
│   │   ├── pages/              # React Pages (Spiele, Tabelle, Statistik, etc.)
│   │   ├── components/
│   │   │   ├── handball/       # Game, Team, League Components
│   │   │   ├── statistics/     # 6 Rankings-Tabellen
│   │   │   └── ui/            # Dialog, Button, etc.
│   │   ├── services/
│   │   │   └── dataService.ts  # API zum Laden der JSON-Daten
│   │   ├── types/
│   │   │   └── handball.ts     # TypeScript Interfaces
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── hb_crawler/
│   ├── pdf_parser.py           # Extrakt Goals aus PDF-Reports
│   └── ...
├── scraper.py                  # Hauptscript: Scraper der Spielplan & Spielerdaten
├── generate_graphics_from_json.py  # Tor-Timeline-Grafiken
├── generate_excel_report.py    # Excel-Report Generator
├── generate_goal_graphic.py    # Grafik-Rendering Utilities
├── requirements.txt            # Python Dependencies
├── output/                     # Generated (Excel, Graphics) - im .gitignore
├── .github/
│   └── workflows/
│       └── daily-update-deploy.yml  # GitHub Actions Workflow
└── README.md
```

---

## 🔄 Datenfluss

### 1. Scraper-Phase
```
handball.net
    ↓
scraper.py (Selenium)
    ├→ Spielplan laden
    ├→ Spieler-Daten extrahieren
    ├→ PDF-Report-Analyse (Goal Timeline)
    └→ Speichern pro Spieltag
         ↓
frontend/public/data/{liga_name}/{yyyymmdd}.json
```

**Datenformat (Spieltag-JSON):**
```json
{
  "games": [
    {
      "game_id": "...",
      "date": "2025-09-20",
      "order": 1,
      "home": {
        "team_name": "Team A",
        "players": [
          {
            "name": "Max Müller",
            "goals": 5,
            "seven_meters": 1,
            "seven_meters_goals": 0,
            "two_min_penalties": 1,
            "yellow_cards": 0,
            "red_cards": 0,
            "blue_cards": 0
          }
        ]
      },
      "away": { /* same structure */ },
      "final_score": "26:24",
      "half_duration": 25,
      "goals_timeline": [
        { "minute": 5, "second": 30, "scorer": "Max Müller", "team": "home", "seven_meter": false },
        { "minute": 6, "second": 15, "scorer": "Opponent", "team": "away", "seven_meter": false }
      ],
      "officials": { /* referee data */ }
    }
  ]
}
```

### 2. Frontend-Phase
```
Frontend lädt:
  ├→ config.json (Liga-Konfiguration)
  ├→ meta.json (Spieltag-Index)
  └→ {liga_name}/{yyyymmdd}.json (Spiel-Daten)
         ↓
     Aggregation & Rendering
         ↓
  ├→ Spieltabelle (Game Table)
  ├→ Spielleitung (Officials)
  ├→ Interaktive Timeline-Grafiken (Canvas)
  └→ 6 Statistik-Rankings

```

### 3. Reports-Phase
```
generate_graphics_from_json.py
  ├→ Liest alle {yyyymmdd}.json
  └→ Erstellt PNG-Grafiken pro Spiel
         ↓
output/{liga_name}_graphics/

generate_excel_report.py
  ├→ Aggregiert Daten across all Spieltage
  ├→ Gruppiert by Team
  └→ Erstellt Excel-Report
         ↓
output/{liga_name}.xlsx
```

---

## 🎯 Verwendung

### WebApp-Pages

#### 1. **Spiele** (Game Table)
- Listet alle Spiele der Liga auf
- Spalten: Datum, Teams, Endstand, Spieler-Statistiken (To, 7m, 2min, Karten)
- Click → Interaktive Timeline-Grafik öffnet sich

#### 2. **Tabelle** (Standings)
- Tabelle mit Platzierung (Punkte, Spiele, Tore, Differenz)
- Click auf Team → Lädt Team-Details in "Spiele"-Tab

#### 3. **Spielleitung** (Officials)
- Liste von Schiedsrichtern und Einsätze
- Gruppiert nach Rolle (Hauptschiri, Feldschiri)
- Click auf Spiel → Springt zu Spiel in "Spiele"-Tab

#### 4. **Statistik** (Rankings)
- **Torschützen**: Spieler sortiert nach Toren (absteigend)
- **7-Meter-Schützen**: Trefferquote, Versuche vs. Treffer
- **Torverhältnis**: Teams nach Goal Differential
- **Bester Angriff**: Teams nach meisten Toren
- **Beste Verteidigung**: Teams nach wenigsten Toren
- **Fair Play**: Teams nach Strafen-Gewichtung (Blau=4, Rot=3, 2min=2, Gelb=1)

### Interaktive Grafiken

**Timeline für jedes Spiel:**
- Canvas-Rendering der Tor-Events
- Y-Achse: Spielstand (+/- Differenz)
- X-Achse: Spielzeit (in Minuten)
- Kreise: Tore (Heim=Blau, Gast=Rot)
- Hover-Tooltip:
  - Torschütze
  - Zeitstempel (MM:SS)
  - Tor-Art (Spiel vs. 7-Meter)
  - Neuer Spielstand
  - Overlapping Goals: Mehrere Events anzeigen (chronologische Reihenfolge)

---

## 🌐 Deployment

### Local Testing
```bash
npm run dev
# Dann: http://localhost:5173
```

### GitHub Pages (Automatisch)

**Automatisierter Workflow:**
1. Täglich um **21:00 CET** (20:00 UTC)
2. Oder manuell auslösbar: GitHub → Actions → "Daily Update & Deploy" → "Run workflow"

**Workflow-Schritte:**
1. Scraper ausführen (`python scraper.py`)
2. Grafiken generieren (`python generate_graphics_from_json.py`)
3. Excel-Report erstellen (`python generate_excel_report.py`)
4. Frontend builden (`npm run build`)
5. Deploy zu GitHub Pages (`gh-pages` Branch)

**Verfügbar unter:**
- https://ulrichfrank.github.io/handballnet_crawler/

### Workflow-Konfiguration
- **Schedule**: `0 20 * * *` (UTC, automatisch DST-angepasst)
- **Manual Trigger**: `workflow_dispatch`
- **Datei**: `.github/workflows/daily-update-deploy.yml`

---

## 🔧 Development

### Frontend Development

```bash
cd frontend
npm run dev          # Start Vite dev server
npm run build        # Production build
npm run lint         # ESLint check
npm run preview      # Preview production build
```

**Tech Stack:**
- React 19 + TypeScript 5.8
- Vite 7 (Fast bundler)
- Tailwind CSS 4 + Radix UI
- React Router 7

### Backend Development

```bash
# Test Scraper
python scraper.py --help

# Test Graphics Generation
python generate_graphics_from_json.py

# Test Excel Generation
python generate_excel_report.py
```

**For Local Data Sync with Git (Incremental Updates):**

The project uses a dual-branch strategy to maintain incremental data updates:
- **`main` branch**: Source code (data is git-ignored)
- **`data` branch**: Only game data files (versioned separately)

**Workflow for local scraping:**
```bash
# 1. Load existing data from data branch (before scraping)
./load_data_branch.sh

# 2. Run scraper (uses existing data for incremental updates)
python scraper.py

# 3. Sync new data back to data branch (after scraping)
./sync_data_branch.sh
```

**Tech Stack:**
- Python 3.10+
- Selenium (Browser Automation)
- BeautifulSoup4 (HTML Parsing)
- pdfplumber (PDF Parsing)
- openpyxl (Excel Generation)
- matplotlib (Graphics)

### Adding New Leagues

1. **Edit `config/config.json`:**
   ```json
   {
     "name": "ma-ol-1-bw_bwhv",
     "display_name": "Männliche A-Jugend Oberliga",
     "half_duration": 30
   }
   ```

2. **Run Scraper:**
   ```bash
   ./load_data_branch.sh
   python scraper.py
   ./sync_data_branch.sh
   ```

3. **App automatically loads new league** (no code changes needed)

---

## 📊 Statistics Details

### 1. Torschützen (Top Scorers)
- Sortiert nach Anzahl Tore (absteigend)
- Zeigt: Spieler, Team, Tore total

### 2. 7-Meter-Schützen (7m Success Rate)
- Sortiert nach Anzahl 7m-Tore (absteigend)
- Zeigt: Spieler, Tore, Versuche, Trefferquote
- Nur Spieler mit mind. 1 Versuch

### 3. Torverhältnis (Goal Differential)
- Sortiert nach Torverhältnis (absteigend)
- Formel: `goals_for - goals_against`
- Zeigt: Team, Tore pro, Tore contra, Differenz

### 4. Bester Angriff (Best Offense)
- Sortiert nach meisten Toren (absteigend)
- Zeigt: Team, Tore total, Spiele, Tore/Spiel

### 5. Beste Verteidigung (Best Defense)
- Sortiert nach wenigsten Toren (aufsteigend)
- Zeigt: Team, Tore bekommen, Spiele, Tore/Spiel

### 6. Fair Play
- Sortiert nach Strafen-Punkten (aufsteigend, niedrig = besser)
- Gewichtung: Blau=4 Pkt, Rot=3 Pkt, 2-Min=2 Pkt, Gelb=1 Pkt
- Zeigt: Team, Total-Punkte, Blau, Rot, 2-Min, Gelb

---

## 🐛 Troubleshooting

### Scraper findet keine Daten
- Prüfe: `config/config.json` - Sind Liga-IDs korrekt?
- Prüfe: Internetzuverbindung
- Prüfe: `--help` für Fehlerausgabe
- Prüfe: Hast du `./load_data_branch.sh` vor dem Scraper ausgeführt?

### Inkrementelle Updates funktionieren nicht
- Stelle sicher, dass du `./load_data_branch.sh` vor dem Scraper ausführst
- Nach dem Scraper: `./sync_data_branch.sh` um Daten zu versionieren
- Beispiel-Workflow:
  ```bash
  ./load_data_branch.sh  # Hole existierende Daten
  python scraper.py      # Scraper nutzt lokale Daten → inkrementell
  ./sync_data_branch.sh  # Speichere neue Daten in Git
  ```

### Frontend startet nicht
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml
npm install
npm run dev
```

### Excel-Datei wird nicht generiert
- Prüfe: `frontend/public/data/` - Existieren Spieltag-JSONs?
- Prüfe: `generate_excel_report.py` - Sind Ligas konfiguriert?

### GitHub Pages Deployment schlägt fehl
- Prüfe: `.github/workflows/daily-update-deploy.yml` existiert?
- Prüfe: GitHub Actions sind im Repo enabled?
- Prüfe: `gh-pages` Branch existiert?
- Prüfe: `data` Branch existiert und ist nicht leer?

---

## 📝 Lizenz & Attribution

- **Datenquelle**: [handball.net](https://www.handball.net)
- **Tools**: Selenium, BeautifulSoup4, React, Vite, Tailwind CSS
- **Lizenz**: MIT (für dieses Projekt)

---

## 🤝 Support

Fragen oder Probleme?
- Öffne einen **GitHub Issue**
- Prüfe die **Logs** (Browser-Console & Terminal)
- Vgl. mit **Beispiel-Config** in `config/config.example.json`

---

**Zuletzt aktualisiert**: Februar 2026 | **Version**: 2.0 (Config Refactoring, Statistics, GitHub Actions)
