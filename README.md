# Handball Spiele Scraper & Report Generator

Leider bietet handball.net keine API, so dass dieses Projekt zur weiteren Auswertung von Ligadaten verwendet werden kann mit detaillierten Spielerstatistiken und Excel-Berichtsgenerierung.

## 🎯 Funktionen

✅ **Mehrere Ligas**
- Konfigurieren Sie mehrere Ligas in einer Config-Datei
- Globale Time Range für alle Ligas
- Separate JSON- und Excel-Dateien pro Liga

✅ **Spiele-Datenerfassung**
- Extrahiert alle Spiele aus dem Spielplan jeder Liga
- Unterstützt Pagination (multiple Seiten)
- Speichert Spieldatum, Teams und Spielereihenfolge

✅ **Spielerdaten-Erfassung**
- Extrahiert Spielerdaten aus den Aufstellungsseiten
- Erfasst: Tore, 7-Meter-Versuche/-Tore, 2-Minuten-Strafen, gelbe/rote/blaue Karten
- Trennt Home und Away Spieler korrekt

✅ **Excel-Bericht**
- Ein Arbeitsblatt pro Team
- Alle Spiele (Heim 🏠 und Auswärts 🏃)
- Spielerdaten nach Spiel sortiert
- Automatische Summen pro Spieler und pro Spiel
- Fixierte Spalten (Spielername) und Zeile (Header) für komfortables Scrollen

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

Erstellen Sie eine Datei `config/config.json` basierend auf `config/config.example.json`:

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
      "out_name": "spiele_c_jugend"
    },
    {
      "name": "gd-bol-srm_srm",
      "display_name": "Handball4all Baden-Württemberg MD-BOL",
      "out_name": "spiele_d_jugend"
    }
  ]
}
```

Passen Sie `leagues`, `date_from` und `date_to` an.

## 🚀 Verwendung

### 1. Spiele und Spielerdaten scrapen

```bash
# Alle Ligas scrapen
python3 scraper.py

# Nur eine spezifische Liga scrapen
python3 scraper.py mc-ol-3-bw_bwhv
```

Dies wird:
- Für jede Liga alle Spiele vom Spielplan extrahieren
- Pagination durchlaufen (alle Seiten laden)
- Für jedes Spiel die Aufstellungsseite laden
- Spielerdaten extrahieren
- Ergebnisse in `output/{out_name}.json` speichern (eine Datei pro Liga)

**Ausgabe:**
```
======================================================================
HANDBALL GAMES SCRAPER - Game-Centric Format
======================================================================
Verarbeite 2 Liga(n)
Date Range: 2025-09-13 to 2026-05-10

======================================================================
SCRAPING: Handball4all Baden-Württemberg MC-OL 3
League ID: handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv
Output: spiele_c_jugend.json
======================================================================

🌐 FETCHING GAMES FROM SPIELPLAN
📄 Loading Spielplan page 1...
  ✓ Found 50 new games on page 1 (total: 50)
...

✅ Saved: output/spiele_c_jugend.json

======================================================================
SCRAPING: Handball4all Baden-Württemberg MD-BOL
...
✅ Saved: output/spiele_d_jugend.json

======================================================================
✅ ALL LEAGUES SCRAPED
======================================================================
```

### 2. Excel-Bericht generieren

```bash
# Excel für alle Ligas generieren
python3 generate_excel_report.py

# Excel nur für eine spezifische Liga generieren
python3 generate_excel_report.py mc-ol-3-bw_bwhv
```

Dies wird:
- JSON-Daten laden
- Pro Team ein Arbeitsblatt erstellen
- Spielerdaten formatieren
- Summen berechnen
- Dateien als `output/{out_name}.xlsx` speichern (eine Datei pro Liga)

**Ausgabe:**
```
📊 Generiere Excel Report für: Handball4all Baden-Württemberg MC-OL 3
   Lade Spieldaten...
   📋 12 Teams gefunden
   [1/12] DJK Singen...
      -> 15 Spieler, 22 Spiele (Heim + Auswärts)
   [2/12] HSG Konstanz...
   ...
   ✅ Gespeichert: output/spiele_c_jugend.xlsx

📊 Generiere Excel Report für: Handball4all Baden-Württemberg MD-BOL
   ...
   ✅ Gespeichert: output/spiele_d_jugend.xlsx

✅ Alle Excel Reports erstellt
```

## 📊 Ausgabedateien

### {out_name}.json (z.B. spiele_c_jugend.json)

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
            "seven_meters": 2,
            "seven_meters_goals": 1,
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

### {out_name}.xlsx (z.B. spiele_c_jugend.xlsx)

Excel-Datei mit Tabs pro Team:

| Player | Spiel 1 🏠<br>Team A vs B<br>28:50 | Spiel 2 🏃<br>C vs Team A<br>25:30 | ... | Tore<br>Gesamt | 7m<br>Vers. | 7m<br>Tore | 2-Min<br>Gesamt | Gelb | Rot | Blau |
|--------|-------|-------|-----|-------|--------|-------|--------|------|-----|------|
| Spieler 1 | 5 | 3 | ... | 8 | 2 | 1 | 1 | 0 | 0 | 0 |
| Spieler 2 | 0 | 4 | ... | 4 | 3 | 2 | 2 | 1 | 0 | 0 |
| GESAMT | 5 | 7 | ... | 12 | 5 | 3 | 3 | 1 | 0 | 0 |

**Spalten pro Spiel:**
- **Tore** - Anzahl geworfener Tore
- **7m Vers.** - 7-Meter-Versuche
- **7m Tore** - Erfolgreiche 7-Meter-Würfe
- **2-Min** - 2-Minuten-Strafen
- **Gelb** - Gelbe Karten
- **Rot** - Rote Karten
- **Blau** - Blaue Karten

**Besonderheiten:**
- **Fixierte Spalte A** - Spielername bleibt sichtbar beim Scrollen nach rechts
- **Fixierte Zeile 2** - Header bleibt sichtbar beim Scrollen nach unten
- **Tore Gesamt** - Zeigt 0 statt "-" für Spieler ohne Tore
- Andere Spalten zeigen "-" wenn der Wert 0 ist

**Icons:**
- 🏠 = Heimspiel (Team spielt zu Hause)
- 🏃 = Auswärtsspiel (Team spielt auswärts)

## ⚙️ Konfiguration

### config/config.json

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
    "date_from": "2025-09-13",        // Saison-Start (YYYY-MM-DD) - gilt für alle Ligas
    "date_to": "2026-05-10"           // Saison-Ende (YYYY-MM-DD) - gilt für alle Ligas
  },
  "leagues": [
    {
      "name": "mc-ol-3-bw_bwhv",              // Liga-Bezeichner aus handball.net URL
      "display_name": "C-Jugend",             // Anzeigename
      "out_name": "spiele_c_jugend"           // Basis für Ausgabedateien (json + xlsx)
    },
    {
      "name": "gd-bol-srm_srm",
      "display_name": "D-Jugend",
      "out_name": "spiele_d_jugend"
    }
  ]
}
```

**Konfigurationsoptionen:**

| Option | Beschreibung |
|--------|-------------|
| `ref.base_url` | handball.net URL (normalerweise nicht ändern) |
| `ssl.verify_ssl` | SSL-Zertifikat-Validierung aktivieren |
| `ssl.cert_path` | Pfad zu benutzerdefiniertem SSL-Zertifikat (optional) |
| `crawler.timeout` | Timeout für Selenium in Sekunden |
| `crawler.retry_attempts` | Wiederholungsversuche bei Fehlern |
| `crawler.delay_between_requests` | Verzögerung zwischen Requests in Sekunden |
| `crawler.date_from` | Saisonstartdatum (YYYY-MM-DD) |
| `crawler.date_to` | Saisonendatum (YYYY-MM-DD) |
| `leagues[].name` | Liga-ID von handball.net |
| `leagues[].display_name` | Anzeigename für Logs |
| `leagues[].out_name` | Basis für Ausgabedateien (ohne Erweiterung) |

**Liga-ID finden:**
1. Öffnen Sie handball.net und navigieren Sie zur gewünschten Liga
2. Schauen Sie auf die URL: `https://www.handball.net/ligen/{LIGA_ID}/spielplan`
3. Kopieren Sie die LIGA_ID

## 🛠️ Entwicklung

### Projektstruktur

```
hb_grabber/
├── scraper.py                         # Haupt-Scraper (verarbeitet alle Ligas)
├── generate_excel_report.py           # Excel-Generator (verarbeitet alle Ligas)
├── config/
│   ├── config.json                    # Konfiguration (mehrere Ligas)
│   └── config.example.json            # Beispiel-Konfiguration
├── output/
│   ├── spiele_c_jugend.json           # JSON für C-Jugend
│   ├── spiele_c_jugend.xlsx           # Excel für C-Jugend
│   ├── spiele_d_jugend.json           # JSON für D-Jugend
│   └── spiele_d_jugend.xlsx           # Excel für D-Jugend
├── .github/workflows/
│   └── daily-scrape.yml               # GitHub Actions Workflow
└── README.md                          # Diese Datei
```

### Workflow

1. **Scraper läuft**: Iteriert durch alle konfigurierten Ligas und erzeugt pro Liga ein JSON
2. **Excel-Generator läuft**: Iteriert durch alle JSONs und erzeugt pro Liga ein Excel-Report
3. **GitHub Actions**: Automatisiert beide Schritte täglich (Samstag und Sonntag)
4. **Artifacts**: Alle Dateien sind in GitHub als Artifacts verfügbar

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

