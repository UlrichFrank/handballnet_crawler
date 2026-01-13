#!/usr/bin/env python3
"""
Filter handball_games.json to only include the 11 current season matches
"""
import json

# Alle 11 Spieltage der aktuellen Saison
spieltage = [
    "20.09.2025",  # Sa, 20.09.
    "28.09.2025",  # So, 28.09.
    "04.10.2025",  # Sa, 04.10.
    "12.10.2025",  # So, 12.10.
    "18.10.2025",  # Sa, 18.10.
    "08.11.2025",  # Sa, 08.11.
    "16.11.2025",  # So, 16.11.
    "23.11.2025",  # So, 23.11.
    "30.11.2025",  # So, 30.11.
    "06.12.2025",  # Sa, 06.12.
    "14.12.2025",  # So, 14.12.
]

with open('output/handball_games.json', 'r') as f:
    data = json.load(f)

# Filtere nur Spiele an den 11 Spieltagen mit Team Stuttgart
filtered_games = []
for game in data['games']:
    if game.get('date') in spieltage and game.get('home', {}).get('team_name'):
        # Filtere nur Spiele, an denen Team Stuttgart beteiligt ist
        home_team = game.get('home', {}).get('team_name', '')
        away_team = game.get('away', {}).get('team_name', '')
        if 'Team Stuttgart' in [home_team, away_team]:
            filtered_games.append(game)

print(f"Original: {len(data['games'])} Spiele")
print(f"Gefiltert: {len(filtered_games)} Spiele mit Team Stuttgart auf den 11 Spieltagen\n")

for i, game in enumerate(filtered_games, 1):
    home = game['home']['team_name']
    away = game['away']['team_name']
    indicator = "🏠 HOME" if home == "Team Stuttgart" else "🏃 AWAY"
    print(f"  {i}. {game['date']} | {home} vs {away} [{indicator}]")

# Speichere gefilterte Daten
filtered_data = {'games': filtered_games}
with open('output/handball_games.json', 'w') as f:
    json.dump(filtered_data, f, indent=2)

print(f"\n✅ handball_games.json aktualisiert mit {len(filtered_games)} Spielen")
