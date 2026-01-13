# Nächste Schritte - Handball.net Crawler Implementation

## 1. HTML-Struktur analysieren

### 1.1 Liga-Seite analysieren
- URL: `https://www.handball.net/ligen/handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv/spielplan?dateFrom=2025-07-01&dateTo=2026-06-30`
- **Aufgaben:**
  - Browser öffnen und Seite aufrufen
  - DevTools (F12) öffnen → Elements/Inspector Tab
  - Team-Links und deren Container identifizieren
  - Benötigte HTML-Selektoren notieren:
    - Team-Namen CSS-Selector
    - Team-Links/URLs CSS-Selector
    - ggf. Team-IDs oder andere Identifikatoren

### 1.2 Team-Kader-Seite analysieren
- Typische URL: `https://www.handball.net/ligen/.../team/...`
- **Aufgaben:**
  - Eine Team-Seite öffnen
  - Spieler-Tabelle/Liste identifizieren
  - HTML-Struktur der Spieler-Einträge analysieren
  - Benötigte Datenfelder identifizieren:
    - Spielernummer
    - Spielername
    - Position
    - Geburtstag
    - Größe/Gewicht (falls vorhanden)
    - Andere relevante Daten

### 1.3 Anmeldeprozess analysieren
- **Aufgabe:**
  - Login-Formular inspizieren
  - Feldnamen identifizieren (username/email field, password field)
  - Ggf. CSRF-Token oder Hidden Fields ausmachen
  - POST-Ziel und Datenformat überprüfen

---

## 2. Parser-Funktionen implementieren

### 2.1 Team-Parser (`crawler.py`)

```python
def parse_teams(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse team list from league page
    
    Returns:
        List of dicts with: id, name, url, ...
    """
    teams = []
    # TODO: Implementieren basierend auf HTML-Struktur
    # - CSS-Selektoren nutzen
    # - Team-Info extrahieren
    # - Relative URLs zu absoluten URLs konvertieren
    return teams
```

**Checklist:**
- [ ] CSS-Selektoren für Teams identifizieren
- [ ] BeautifulSoup-Code schreiben zum Extrahieren
- [ ] URL-Konvertierung implementieren (urljoin)
- [ ] Error-Handling für fehlende Felder
- [ ] Test mit echten Daten durchführen

### 2.2 Spieler-Parser (`crawler.py`)

```python
def parse_players(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse player list from team roster page
    
    Returns:
        List of dicts with: name, number, position, birthdate, ...
    """
    players = []
    # TODO: Implementieren basierend auf HTML-Struktur
    # - Spieler-Tabelle/Container finden
    # - Jede Zeile/Eintrag parsen
    # - Datenfelder extrahieren
    return players
```

**Checklist:**
- [ ] CSS-Selektoren für Spieler-Tabelle identifizieren
- [ ] Spieler-Reihen-Selektor definieren
- [ ] Datenfelder-Mapping erstellen
- [ ] Datenbereinigung (Whitespace, Formatierung)
- [ ] Test mit echten Daten durchführen

### 2.3 Authentication-Funktion (`authenticator.py`)

**Aufgaben:**
- [ ] Login-Formular-Feldnamen in `login_data` korrigieren
- [ ] CSRF-Token-Handling implementieren (falls nötig)
- [ ] Login-Erfolgsverifikation verbessern
- [ ] Session-Cookies prüfen

---

## 3. Konfiguration finalisieren

### 3.1 config.json erstellen

```bash
cp config/config.example.json config/config.json
```

**Felder ausfüllen:**
- `authentication.username`: Handball.net Benutzername
- `authentication.password`: Handball.net Passwort
- `league.name`: Liga-ID aus URL (z.B. `handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv`)
- `league.date_from/date_to`: Gewünschter Zeitraum

### 3.2 .env-Datei erstellen (Optional)

```bash
cp .env.example .env
```

Für sichere Speicherung von Anmeldedaten:
```
HB_USERNAME=dein_username
HB_PASSWORD=dein_password
```

---

## 4. Testing & Debugging

### 4.1 Authentifizierung testen

```bash
python3 -c "
from hb_crawler.authenticator import HandballNetAuthenticator
auth = HandballNetAuthenticator('https://www.handball.net', 'user', 'pass')
print('Login result:', auth.login())
"
```

### 4.2 Einzelne Seite fetchen und parsen

```bash
python3 -c "
from hb_crawler.crawler import HandballNetCrawler
import requests
session = requests.Session()
crawler = HandballNetCrawler(session, 'https://www.handball.net')
soup = crawler.fetch_page('https://...')
print('Teams found:', len(soup.find_all('...')))
"
```

### 4.3 Vollständigen Crawler starten

```bash
python3 main.py
```

---

## 5. Error-Handling & Robustheit

**Zu implementieren:**
- [ ] Retry-Logik für fehlgeschlagene Requests
- [ ] Timeout-Handling
- [ ] Rate-Limiting (Delays zwischen Requests)
- [ ] Logging für Debugging
- [ ] Graceful Error-Messages
- [ ] Exception-Handling für HTML-Parser-Fehler

---

## 6. Erweiterte Features (Optional)

- [ ] Caching von bereits gecrawlten Daten
- [ ] Incremental Updates (nur neue Spieler fetchen)
- [ ] Daten-Validierung und Bereinigung
- [ ] Progress-Bar für lange Läufe
- [ ] Konfigurierbare Output-Formate
- [ ] Unit Tests schreiben
- [ ] Docker-Container für einfache Bereitstellung

---

## 7. Troubleshooting

| Problem | Lösung |
|---------|--------|
| Login schlägt fehl | HTML-Struktur des Login-Formulars überprüfen, CSRF-Token implementieren |
| Keine Teams gefunden | CSS-Selektoren in Developer Tools verifizieren |
| Spieler-Daten unvollständig | Zusätzliche HTML-Selektoren hinzufügen, Feldmapping überprüfen |
| Timeout | `timeout`-Wert in config erhöhen, Delay zwischen Requests vergrößern |
| SSL-Zertifikat-Fehler | `verify=True` in session.get() Aufrufen überprüfen |

---

## Execution Order

```
1. Setup
   ├── Virtual Environment aktivieren
   └── Dependencies installieren

2. Analysis
   ├── HTML-Struktur analysieren
   └── Datenfelder definieren

3. Implementation
   ├── Authentication implementieren
   ├── Team-Parser schreiben
   ├── Spieler-Parser schreiben
   └── Hauptlogik zusammenführen

4. Configuration
   ├── config.json erstellen
   └── .env-Datei (optional) erstellen

5. Testing
   ├── Einzelne Funktionen testen
   ├── Ende-zu-Ende Test durchführen
   └── Output validieren

6. Refinement
   ├── Error-Handling verbessern
   ├── Logging hinzufügen
   └── Performance optimieren
```

---

## Notizen für Implementierung

- **BeautifulSoup Tipps:**
  - `soup.find()` für einzelnes Element
  - `soup.find_all()` für mehrere Elemente
  - `soup.select()` für CSS-Selektoren
  - `.get_text()` oder `.text` für Text-Inhalte
  - `.get('href')` für Attribute

- **Requests Session:**
  - Cookies werden automatisch gespeichert nach Login
  - Alle nachfolgenden Requests verwenden die Session

- **URL-Handling:**
  - `urljoin()` für Konvertierung relativer zu absoluten URLs
  - `urllib.parse.urljoin()` importieren

---

## Hilfreiche Links

- [BeautifulSoup Dokumentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python Requests Dokumentation](https://requests.readthedocs.io/)
- [CSS Selektoren Referenz](https://www.w3schools.com/cssref/selectors.php)
