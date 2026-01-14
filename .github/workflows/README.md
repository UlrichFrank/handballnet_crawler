# GitHub Action für automatisierte Handball-Datenextraktion

Diese Workflow-Datei führt jeden Samstag und Sonntag um 18:00 Uhr UTC folgende Schritte aus:

## ⏰ Zeitplan

- **Zeit:** 18:00 Uhr UTC täglich
- **Tage:** Samstag und Sonntag
- **Cron:** `0 18 * * 6,0`

### Zeitzone anpassen

Wenn Sie eine andere Zeitzone haben, können Sie den Cron-Ausdruck anpassen:

```yaml
schedule:
  - cron: '0 18 * * 6,0'  # UTC
```

**Beispiele:**
- CET/CEST (Deutschland): `0 16 * * 6,0` (16:00 CET)
- EST/EDT (USA): `0 23 * * 6,0` (23:00 EST)
- PST/PDT (USA): `0 02 * * 0,1` (02:00 PST nächster Tag)

## 🔄 Workflow-Schritte

1. **Code auschecken** - Repository klonen
2. **Python 3.11 installieren** - Runtime-Umgebung vorbereiten
3. **Abhängigkeiten installieren** - Selenium, BeautifulSoup4, openpyxl
4. **ChromeDriver setup** - Browser-Automatisierung konfigurieren
5. **Daten scrapen** - `python3 scraper.py` ausführen
6. **Excel erstellen** - `python3 generate_excel_report.py` ausführen
7. **Artifacts hochladen** - Dateien speichern für Download
8. **Release erstellen** - Optionale GitHub Release mit Tags

## 📥 Dateien herunterladen

### Methode 1: Actions Artifacts

1. Gehen Sie zu **Actions** im Repository
2. Klicken Sie auf den letzten erfolgreichen Run
3. Scrollen Sie zu "Artifacts"
4. Laden Sie herunter:
   - `handball_players_report` (Excel-Datei)
   - `handball_games_data` (JSON-Datei)

### Methode 2: GitHub Releases

1. Gehen Sie zu **Releases** im Repository
2. Jeder erfolgreiche Run erstellt ein automatisches Release
3. Tag-Name: `handball-data-{Run-Nummer}`
4. Dateien sind im Release zum Download verfügbar

## 🔧 Konfiguration

### Requirements

Das Workflow benötigt folgende Dateien im Repository:

```
hb_grabber/
├── config/
│   └── config.json           ← Erforderlich!
├── scraper.py
├── generate_excel_report.py
└── .github/workflows/
    └── daily-scrape.yml      ← Diese Datei
```

### config.json Beispiel

```json
{
  "league": {
    "name": "mc-ol-3-bw_bwhv",
    "date_from": "2025-07-01",
    "date_to": "2026-06-30"
  }
}
```

## 🚀 Manuelles Auslösen

Sie können die Action auch manuell auslösen:

1. Gehen Sie zu **Actions** im Repository
2. Wählen Sie "Daily Handball Data Scrape"
3. Klicken Sie "Run workflow"
4. Wählen Sie den Branch aus
5. Klicken Sie "Run workflow"

## 📊 Ausgabedateien

### handball_players_report.xlsx
- Excel-Datei mit Spielerdaten
- Ein Tab pro Team
- Alle Spiele und Statistiken
- Verfügbar für 30 Tage im Actions-Bereich

### handball_games.json
- Raw-Daten im JSON-Format
- Alle Spiele und Spieler
- Verfügbar für 30 Tage im Actions-Bereich

## ⚠️ Fehlerbehebung

### Action schlägt fehl

Prüfen Sie:

1. **Ist config.json vorhanden?**
   - Muss unter `config/config.json` liegen
   - Muss gültiges JSON sein

2. **Ist die Liga-ID korrekt?**
   - Finden Sie sie in der handball.net URL
   - Format: `handball4all.bundesland.liga-id`

3. **Hat der Runner Internet-Zugriff?**
   - handball.net sollte erreichbar sein
   - Firewalls könnten blockieren

4. **ChromeDriver-Kompatibilität?**
   - Die Action nutzt ChromeDriver 131.0
   - Wird automatisch installiert

### Logs anschauen

1. Gehen Sie zu **Actions**
2. Klicken Sie auf den fehlgeschlagenen Run
3. Klicken Sie auf "Run Handball Scraper"
4. Sehen Sie den Fehler im Output

## 🔒 Sicherheit

- **GitHub Token:** Wird automatisch bereitgestellt (`secrets.GITHUB_TOKEN`)
- **Credentials:** Keine hartcodierten Passwörter
- **Dateien:** Nur öffentliche handball.net Daten
- **Datenschutz:** Spielerdaten sind öffentlich auf handball.net

## 📈 Speicherverwaltung

- **Artifact Retention:** 30 Tage (konfigurierbar in `retention-days`)
- **Release:** Archiviert automatisch
- **Disk:** GitHub bietet 500 MB pro Action-Artifact

Bei häufiger Nutzung können Sie Retention reduzieren:

```yaml
retention-days: 7  # Nur 7 Tage behalten
```

## 🎯 Nächste Schritte

1. **Push zu GitHub** - Datei muss in `.github/workflows/` liegen
2. **Test run** - Manuell über "Run workflow" auslösen
3. **Zeitplan prüfen** - Automatische Runs sollten Sa/So 18:00 starten
4. **Ergebnisse überprüfen** - Artifacts überprüfen

## 📝 Anpassungen

### Häufiger laufen lassen

```yaml
on:
  schedule:
    - cron: '0 18 * * *'  # Jeden Tag um 18:00
```

### Weniger Speicher

```yaml
retention-days: 7  # Nur 7 Tage speichern
```

### Keine Releases erstellen

Entfernen Sie den "Create Release" Step aus der YAML-Datei
