#!/usr/bin/env python3
"""
GENERATE GRAPHICS FROM JSON
Create goal timeline graphics from previously scraped JSON data.
Uses config.json to determine which JSON files to process.
"""

import json
import sys
from pathlib import Path
from generate_goal_graphic import generate_goal_timeline_graphic


def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from specified file"""
    config_path = Path(config_file)
    if not config_path.exists():
        config_path = Path("config") / config_file
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def process_json_files(data_folder: Path, league_name: str, half_duration: int):
    """
    Process all spieltag JSON files in a data folder and generate graphics.
    
    Args:
        data_folder: Path to folder with yyyymmdd.json files
        league_name: Name of the league (for display)
        half_duration: Minutes per half from config
    """
    
    if not data_folder.exists():
        print(f"   ⚠️  Daten-Ordner nicht gefunden: {data_folder}")
        return 0, 0, 0
    
    # Get all yyyymmdd.json files
    json_files = sorted(list(data_folder.glob('*.json')))
    
    if not json_files:
        print(f"   ⚠️  Keine Spieltag-Dateien gefunden in {data_folder}")
        return 0, 0, 0
    
    # Generate graphics
    success_count = 0
    skip_count = 0
    total_size_kb = 0
    
    for json_path in json_files:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        games = data.get('games', [])
        if not games:
            continue
        
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
                print(f"   ⚠️  Fehler bei {json_path.name}: {e}")
                skip_count += 1
        
        # Save updated JSON with graphic paths
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    return success_count, skip_count, total_size_kb


def main():
    """
    Process all leagues defined in config.
    Load and process all spieltag JSON files from frontend/public/data/{data_folder}/.
    """
    
    # Parse command line arguments properly
    config_file = "config.json"  # Default
    
    # Manual parsing to handle --config flag
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--config" and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
            i += 2  # Skip both --config and its value
        else:
            i += 1
    
    # Load config
    config = load_config(config_file)
    
    leagues = config.get('leagues', [])
    if not leagues:
        print("❌ Keine Leagues in config definiert")
        return
    
    print("\n" + "=" * 70)
    print(f"🎨 GENERIERE GRAFIKEN ({len(leagues)} Ligen)")
    print("=" * 70 + "\n")
    
    total_success = 0
    total_skip = 0
    grand_total_kb = 0
    
    for league in leagues:
        league_name = league.get('display_name', league.get('name', 'Unknown'))
        data_folder_name = league.get('name', 'unknown')
        half_duration = league.get('half_duration', 30)
        
        data_folder = Path('frontend/public/data') / data_folder_name
        
        print(f"📂 {league_name}")
        print(f"   🏐 ({half_duration} Min pro Halbzeit)")
        
        success_count, skip_count, total_size_kb = process_json_files(
            data_folder, 
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
    if grand_total_kb > 0:
        print(f"📁 Gesamtgröße: {grand_total_kb:.1f} KB")
    print(f"📂 Speicherort: frontend/public/graphics/")
    print(f"📄 JSON-Dateien aktualisiert\n")


if __name__ == '__main__':
    main()
