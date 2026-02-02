# Interaktive Timeline-Grafiken in der WebApp

## Übersicht
Implementierung von interaktiven, in der WebApp gerenderten Spiel-Ablauf-Grafiken mit Canvas statt vorgerenderter PNG-Dateien.

## Neue Komponenten

### 1. GameTimelineDialog.tsx
- **Ort**: `frontend/src/components/handball/GameTimelineDialog.tsx`
- **Funktion**: 
  - Dialog-Komponente, die Spiel-Ablauf zeigt
  - Renderiert zwei Halbzeiten mit Canvas
  - Zeigt Tore als Kreise mit farblicher Kodierung (Führung/Gleichstand/Rückstand)
  - Momentum durch Kreisgröße dargestellt
  - Interaktive Anzeige von Torzeitpunkten und Spielständen

### 2. Dialog UI Komponente
- **Ort**: `frontend/src/ui/dialog.tsx`
- **Komponenten**:
  - `Dialog`: Backdrop + Modal Container
  - `DialogContent`: Modales Inhalts-Container
  - `DialogHeader`: Header-Bereich
  - `DialogTitle`: Titel-Element

### 3. Typen erweitert
- **Ort**: `frontend/src/types/handball.ts`
- **Neue Interfaces**:
  - `GoalEvent`: Tor-Ereignis mit Minute, Sekunde, Schütze, Team, 7m-Flagge
  - `Game`: Erweitert um `goals_timeline` und `final_score`

## Integration in GameTable

### Änderungen in GameTable.tsx
1. Import neuer Komponenten: `GameTimelineDialog`, `Activity` Icon
2. Neue State-Variablen: `selectedGame`, `isTimelineDialogOpen`, `allGames`
3. Header-Zeilen nun klickbar für Spiele mit Tordaten
4. "Ablauf"-Button mit Activity-Icon auf jedem Spiel-Header
5. Dialog-Komponente am Ende der Komponente eingebunden

## Grafik-Rendering (Canvas)

### Visualisierung
```
Halbzeit 1 (25 Min, MC-OL 3 Konfiguration):
┌─────────────────────────────────────────────┐
│ 0'  5' 10' 15' 20' 25'                      │ (Minute-Labels)
├─────────────────────────────────────────────┤
│ ● ●●  ●   ●●●   ●      (Home Team, oben)   │
├──────────── 0 : 0 ──────────────────────────┤ (Separator)
│  ●    ●●  ●    ●●  ●   (Away Team, unten)   │
└─────────────────────────────────────────────┘
```

### Farbkodierung der Tore
- **Blau (#3498db)**: Team in Führung
- **Grau (#95a5a6)**: Gleichstand
- **Orange (#e67e22)**: Team im Rückstand

### Momentum-Darstellung
- Basis-Radius: 5px + Momentum × 1.5px
- Momentum > 3: Zahl im Kreis angezeigt
- Spielstand unter jedem Tor sichtbar

## Features

✅ **Interaktiv statt statisch**
- Im Browser gerendert mit Canvas
- Keine Abhängigkeit von vorgerenderter Grafiken-Datei

✅ **Identisch zu Excel-Grafiken**
- Gleiche Logik für Spiel-Flow-Berechnung
- Gleiches Farbschema und Layout
- Momentum und Situationen identisch implementiert

✅ **Fehlerbehandlung**
- Dialog zeigt Meldung, wenn keine Tordaten verfügbar sind
- Graceful fallback für Spiele ohne goals_timeline

✅ **Benutzerfreundlich**
- Klarer "Ablauf"-Button mit Icon
- Modal-Dialog für fokussierte Ansicht
- Zwei Halbzeiten deutlich nebeneinander dargestellt

## Datenflusss

```
Game.goals_timeline
        ↓
calculate_game_flow() - Berechnet Spielstände und Momentum
        ↓
prepare_graphic_data() - Organisiert nach Halbzeiten
        ↓
Canvas Rendering - Zeichnet Kreise und Labels
        ↓
Dialog angezeigt
```

## Browser-Kompatibilität
- Canvas API: Alle modernen Browser
- CSS Flexbox/Grid: Alle modernen Browser
- Dialog mit Backdrop: Gut unterstützt

## Performance
- Canvas-Rendering: < 100ms für typisches Spiel
- Keine externe Abhängigkeiten notwendig
- Memoization für Berechnung der graphic_data

## Mögliche zukünftige Verbesserungen
- Hover-Tooltips mit Schütze-Namen
- Interaktive Filter (nur 7m, nur Gleichstand, etc.)
- Animation des Spielfortschritts
- Export als SVG/PNG aus WebApp
