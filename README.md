# Handball Spiele Scraper & Report Generator

Leider bietet handball.net keine API, so dass dieses Projekt zur weiteren Auswertung von Ligadaten verwendet werden kann mit detaillierten Spielerstatistiken und Excel-Berichtsgenerierung.

## 🎯 Funktionen

✅ **Spiele-Datenerfassung**
- Extrahiert alle Spiele aus dem Spielplan einer Liga
- Unterstützt Pagination (multiple Seiten)
- Speichert Spieldatum, Teams und Spielereihenfolge

✅ **Spielerdaten-Erfassung**
- Extrahiert Spielerdaten aus den Aufstellungsseiten
- Erfasst: Tore, 2-Minuten-Strafen, gelbe/rote/blaue Karten
- Trennt Home und Away Spieler korrekt

✅ **Excel-Bericht**
- Ein Arbeitsblatt pro Team
- Alle Spiele (Heim 🏠 und Auswärts 🏃)
- Spielerdaten nach Spiel sortiert
- Automatische Summen pro Spieler und pro Spiel
- Spielergebnisse in den Spiel-Headern

## 📦 Installation

### Anforderungen
- Python 3.8+
- Chrome/Chromium Browser
- Internet-Verbindung

### Abhängigkeiten installieren

```bash
pip install selenium webdriver-manager beautifulsoup4 openpyxl
```

### Konfiguration

Erstellen Sie eine Datei `config/config.json`:

```json
{
  "authentication": {
    "base_url": "https://www.handball.net"
  },
  "league": {
    "name": "mc-ol-3-bw_bwhv",
    "date_from": "2025-07-01",
    "date_to": "2026-06-30"
  }
}
```

Passen Sie `name`, `date_from` und `date_to` an Ihre Liga an.

## 🚀 Verwendung

### 1. Spiele und Spielerdaten scrapen

```bash
python3 scraper.py
```

Dies wird:
- Alle Spiele der Liga vom Spielplan extrahieren
- Pagination durchlaufen (alle Seiten laden)
- Für jedes Spiel die Aufstellungsseite laden
- Spielerdaten extrahieren
- Ergebnisse in `output/handball_games.json` speichern

**Ausgabe:**
```
======================================================================
HANDBALL GAMES SCRAPER - Game-Centric Format
======================================================================
League: handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv
Date Range: 2025-07-01 to 2026-06-30

🌐 FETCHING GAMES FROM SPIELPLAN
📄 Loading Spielplan page 1...
  ✓ Found 50 new games on page 1 (total: 50)
📄 Loading Spielplan page 2...
  ✓ Found 6 new games on page 2 (total: 56)

✓ Total games found: 56

👥 EXTRACTING GAME DETAILS
  [  1/56] ✅ Sa, 20.09. | Team A (14) vs Team B (12)
  ...
```

### 2. Excel-Bericht generieren

```bash
python3 generate_excel_report.py
```

Dies wird:
- JSON-Daten laden
- Pro Team ein Arbeitsblatt erstellen
- Spielerdaten formatieren
- Summen berechnen
- Datei als `handball_players_report.xlsx` speichern

**Ausgabe:**
```
📊 Lade Spieldaten...
📋 10 Teams gefunden

[1/10] DJK Singen...
  -> 15 Spieler, 11 Spiele (Heim + Auswärts)
...

✅ Excel Report: handball_players_report.xlsx
```

## 📊 Ausgabedateien

### handball_games.json

Game-zentrierte Struktur mit allen Spielerdaten:

```json
{
  "games": [
    {
      "game_id": "handball4all.baden-wuerttemberg.8668846",
      "order": 0,
      "date": "Sa, 20.09.",
      "home": {
        "team_name": "Team A",
        "players": [
          {
            "name": "Player Name",
            "goals": 5,
            "two_min_penalties": 1,
            "yellow_cards": 0,
            "red_cards": 0,
            "blue_cards": 0
          }
        ]
      },
      "away": {
        "team_name": "Team B",
        "players": [...]
      }
    }
  ]
}
```

### handball_players_report.xlsx

Excel-Datei mit Tabs pro Team:

| Player | Spiel 1 🏠<br>Team A vs B<br>28:50 | Spiel 2 🏃<br>C vs Team A<br>25:30 | ... | Tore Gesamt | 2-Min Gesamt | Gelb | Rot | Blau |
|--------|-------|-------|-----|-------|--------|------|-----|------|
| Spieler 1 | 5 | 3 | ... | 8 | 1 | 0 | 0 | 0 |
| Spieler 2 | 0 | 4 | ... | 4 | 2 | 1 | 0 | 0 |
| GESAMT | 5 | 7 | ... | 12 | 3 | 1 | 0 | 0 |

**Spalten:**
- **Tore, 2-Min, Gelb, Rot, Blau** pro Spiel (5 Spalten pro Spiel)
- **Tore Gesamt, 2-Min Gesamt, Gelb, Rot, Blau** - Summen pro Spieler über alle Spiele

**Icons:**
- 🏠 = Heimspiel (Team spielt zu Hause)
- 🏃 = Auswärtsspiel (Team spielt auswärts)

## ⚙️ Konfiguration

### config/config.json

```json
{
  "authentication": {
    "base_url": "https://www.handball.net"
  },
  "league": {
    "name": "mc-ol-3-bw_bwhv",        // Liga-Bezeichner aus handball.net URL
    "date_from": "2025-07-01",        // Saison-Start (YYYY-MM-DD)
    "date_to": "2026-06-30"           // Saison-Ende (YYYY-MM-DD)
  }
}
```

**Liga-ID finden:**
1. Öffnen Sie handball.net und navigieren Sie zur gewünschten Liga
2. Schauen Sie auf die URL: `https://www.handball.net/ligen/{LIGA_ID}/spielplan`
3. Kopieren Sie die LIGA_ID

## 🛠️ Entwicklung

### Projektstruktur

```
hb_grabber/
├── scraper.py                      # Haupt-Scraper
├── generate_excel_report.py        # Excel-Generator
├── config/
│   └── config.json                 # Konfiguration
├── output/
│   └── handball_games.json         # Extrahierte Daten
├── handball_players_report.xlsx    # Excel-Report
└── README.md                       # Diese Datei
```

### Code-Style

- Python 3.8+
- Verwendet BeautifulSoup4 für HTML-Parsing
- Verwendet Selenium für dynamisches Laden
- Verwendet openpyxl für Excel-Erstellung

## 📄 Lizenzen & Attribution

- **handball.net** - Datenquelle (respektieren Sie deren Terms of Service)
- **Selenium** - Browser-Automatisierung
- **BeautifulSoup4** - HTML-Parsing
- **openpyxl** - Excel-Erstellung

