#!/usr/bin/env python3
"""
GENERATE GRAPHICS FROM JSON
Create goal timeline graphics from previously scraped JSON data.
Uses config.json to determine which JSON files to process.
"""

import json
from pathlib import Path
from generate_goal_graphic import generate_goal_timeline_graphic


def process_json_file(json_path: Path, league_name: str, half_duration: int):
    """
    Process a single JSON file and generate graphics.
    
    Args:
        json_path: Path to JSON file with games data
        league_name: Name of the league (for display)
        half_duration: Minutes per half from config
    """
    
    if not json_path.exists():
        print(f"   ⚠️  JSON-Datei nicht gefunden: {json_path}")
        return 0, 0, 0
    
    # Load games from JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    games = data.get('games', [])
    if not games:
        print(f"   ⚠️  Keine Spiele in {json_path.name} gefunden")
        return 0, 0, 0
    
    # Generate graphics
    success_count = 0
    skip_count = 0
    total_size_kb = 0
    
    for idx, game in enumerate(games, 1):
        # Skip games without goals
        if not game.get('goals_timeline'):
            skip_count += 1
            continue
        
        # Attempt to generate graphic
        try:
            graphic_path = generate_goal_timeline_graphic(
                game,
                half_duration=half_duration
            )
            
            if graphic_path and Path(graphic_path).exists():
                success_count += 1
                file_size = Path(graphic_path).stat().st_size / 1024
                total_size_kb += file_size
                
                # Update game data with graphic path
                game['graphic_path'] = graphic_path
            
        except Exception as e:
            print(f"   ⚠️  Fehler bei Spiel {idx}: {e}")
            skip_count += 1
    
    # Save updated JSON with graphic paths
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return success_count, skip_count, total_size_kb


def main():
    """
    Process all leagues defined in config.json.
    """
    
    # Load config
    config_path = Path('config/config.json')
    if not config_path.exists():
        print("❌ config/config.json nicht gefunden")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    leagues = config.get('leagues', [])
    if not leagues:
        print("❌ Keine Leagues in config.json definiert")
        return
    
    print("\n" + "=" * 70)
    print(f"📊 GENERIERE GRAFIKEN ({len(leagues)} Ligen)")
    print("=" * 70 + "\n")
    
    total_success = 0
    total_skip = 0
    grand_total_kb = 0
    
    for league in leagues:
        league_name = league.get('name', 'Unknown')
        out_name = league.get('out_name', 'unknown')
        half_duration = league.get('half_duration', 30)
        
        json_file = Path('output') / f"{out_name}.json"
        
        print(f"📂 Verarbeite: {out_name}.json")
        print(f"   🏐 Liga: {league_name} ({half_duration} Min pro Halbzeit)")
        
        success_count, skip_count, total_size_kb = process_json_file(
            json_file, 
            league_name,
            half_duration
        )
        
        total_success += success_count
        total_skip += skip_count
        grand_total_kb += total_size_kb
        
        if success_count > 0 or skip_count > 0:
            print(f"   ✅ {success_count} Grafiken generiert")
            if skip_count > 0:
                print(f"   ⊘ {skip_count} Spiele übersprungen (keine Tore)")
            if total_size_kb > 0:
                print(f"   📁 Größe: {total_size_kb:.1f} KB")
        print()
    
    print("=" * 70)
    print(f"✅ GRAFIK-GENERIERUNG ABGESCHLOSSEN")
    print("=" * 70)
    print(f"✓ {total_success} Grafiken gesamt generiert")
    if total_skip > 0:
        print(f"⊘ {total_skip} Spiele übersprungen (keine Tore)")
    print(f"📁 Gesamtgröße: {grand_total_kb:.1f} KB")
    print(f"📂 Speicherort: output/graphics/")
    print(f"📄 JSON-Dateien aktualisiert\n")


if __name__ == '__main__':
    main()
