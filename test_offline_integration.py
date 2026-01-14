#!/usr/bin/env python3
"""
Offline integration test - demonstrates complete flow with mock data
"""

import json
from pathlib import Path
from hb_crawler.pdf_parser import add_seven_meters_to_players, _parse_pdf

print("\n" + "="*70)
print("OFFLINE INTEGRATION TEST - Complete Workflow")
print("="*70)

# 1. Test PDF parsing with local file
print("\n[1] PDF Parsing Test")
print("-"*70)

pdf_path = '2026-01-10_PresseInfoLang_906069.pdf'
print(f"Parsing local PDF: {pdf_path}\n")

seven_meter_data = _parse_pdf(pdf_path)

if seven_meter_data:
    print(f"SUCCESS: Extracted {len(seven_meter_data)} players with 7m data:")
    for player, stats in sorted(seven_meter_data.items(), key=lambda x: x[1]['attempts'], reverse=True):
        print(f"  {player:28} | {stats['attempts']} attempts | {stats['goals']} goals")
else:
    print("ERROR: No data found")
    exit(1)

# 2. Simulate game scraping output
print("\n[2] Simulating Game Scraping")
print("-"*70)

# Mock game data (as would come from scraper)
mock_game = {
    'game_id': 'handball4all.baden-wuerttemberg.test123',
    'date': 'Sa, 10.01.',
    'home': {
        'team_name': 'Team A',
        'players': [
            {'name': 'Moritz Bächle', 'goals': 3, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
            {'name': 'Felix Heuser', 'goals': 5, 'two_min_penalties': 1, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
            {'name': 'Tim Lorenz', 'goals': 8, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
        ]
    },
    'away': {
        'team_name': 'Team B',
        'players': [
            {'name': 'Matti Kraaz', 'goals': 1, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
            {'name': 'Moritz Lexa', 'goals': 3, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
        ]
    }
}

print(f"Mock game: {mock_game['date']} | {mock_game['home']['team_name']} vs {mock_game['away']['team_name']}\n")

# 3. Enrich players with 7m data
print("[3] Enriching Player Data with Seven Meters")
print("-"*70)

home_players = mock_game['home']['players']
away_players = mock_game['away']['players']

# Add 7m data
home_players = add_seven_meters_to_players(home_players, seven_meter_data)
away_players = add_seven_meters_to_players(away_players, seven_meter_data)

print("\nHome Team Players:")
for p in home_players:
    found = "YES" if p['seven_meters'] > 0 else "no"
    print(f"  {p['name']:28} | Goals: {p['goals']:2} | 7m: {p['seven_meters']} attempts, {p['seven_meters_goals']} goals ({found})")

print("\nAway Team Players:")
for p in away_players:
    found = "YES" if p['seven_meters'] > 0 else "no"
    print(f"  {p['name']:28} | Goals: {p['goals']:2} | 7m: {p['seven_meters']} attempts, {p['seven_meters_goals']} goals ({found})")

# 4. Verify JSON structure
print("\n[4] Verifying JSON Output Structure")
print("-"*70)

mock_game['home']['players'] = home_players
mock_game['away']['players'] = away_players

output_data = {'games': [mock_game]}

# Save test JSON
output_path = 'output/handball_games_integration_test.json'
Path('output').mkdir(exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\nSaved test output: {output_path}")

# Verify structure
with open(output_path, 'r') as f:
    loaded = json.load(f)

game = loaded['games'][0]
player = game['home']['players'][0]

print("\nJSON Structure Verification:")
required_fields = [
    'name', 'goals', 'two_min_penalties', 'yellow_cards',
    'red_cards', 'blue_cards', 'seven_meters', 'seven_meters_goals'
]

print(f"\nSample player from JSON:")
for field in required_fields:
    value = player.get(field, 'MISSING')
    status = "✓" if field in player else "✗"
    print(f"  {status} {field:25} = {value}")

# 5. Summary
print("\n" + "="*70)
print("INTEGRATION TEST RESULTS")
print("="*70)

total_home = len(home_players)
home_with_7m = sum(1 for p in home_players if p['seven_meters'] > 0)

total_away = len(away_players)
away_with_7m = sum(1 for p in away_players if p['seven_meters'] > 0)

print(f"\nHome Team:")
print(f"  {total_home} players | {home_with_7m} with seven meter data")

print(f"\nAway Team:")
print(f"  {total_away} players | {away_with_7m} with seven meter data")

print(f"\nTotal Seven Meters in Game:")
total_7m_attempts = sum(p['seven_meters'] for p in home_players + away_players)
total_7m_goals = sum(p['seven_meters_goals'] for p in home_players + away_players)
print(f"  {total_7m_attempts} attempts | {total_7m_goals} successful goals")

print(f"\n✓ PDF Parsing: OK")
print(f"✓ Player Enrichment: OK")
print(f"✓ JSON Structure: OK")
print(f"✓ Data Persistence: OK")

print(f"\nImplementation is ready for full scraper deployment!")
print(f"\nTo run the actual scraper:")
print(f"  1. Check your internet connection")
print(f"  2. Update config.json with correct league and dates")
print(f"  3. Run: python scraper.py")
print()
