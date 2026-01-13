#!/usr/bin/env python3
"""
Convert team-centric data to game-centric format
Creates handball_games.json with home/away structure
"""
import json
from pathlib import Path

# Load the detailed player data
with open('output/handball_players_detailed.json', 'r') as f:
    detailed_data = json.load(f)

# Create game-centric structure
games = []
game_map = {}  # {game_id: {home_team: ..., away_team: ...}}

# Extract all games from team data
teams_data = detailed_data['teams']

for team_name, team_info in teams_data.items():
    for player in team_info['players']:
        if 'game_details' in player:
            for game_detail in player['game_details']:
                game_id = game_detail['game_id']
                date = game_detail['date']
                opponent_teams = game_detail['opponent_teams']
                
                # Create game key
                game_key = f"{date}_{sorted(opponent_teams + [team_name])}"
                
                if game_id not in game_map:
                    game_map[game_id] = {
                        'game_id': game_id,
                        'date': date,
                        'home': None,
                        'away': None
                    }

# Now reconstruct games with home/away designation
# We need to look at the actual game structure from detailed data
reconstructed_games = {}

for team_name, team_info in teams_data.items():
    for player in team_info['players']:
        if 'game_details' in player:
            for game_detail in player['game_details']:
                game_id = game_detail['game_id']
                
                if game_id not in reconstructed_games:
                    reconstructed_games[game_id] = {
                        'game_id': game_id,
                        'date': game_detail['date'],
                        'home': {'team_name': None, 'players': []},
                        'away': {'team_name': None, 'players': []}
                    }
                
                # Add this player to the game
                player_info = {
                    'name': player['name'],
                    'goals': game_detail['goals'],
                    'two_min_penalties': game_detail['two_min_penalties'],
                    'yellow_cards': game_detail['yellow_cards'],
                    'red_cards': game_detail['red_cards'],
                    'blue_cards': game_detail['blue_cards']
                }
                
                # Determine if team is home or away (needs heuristic)
                # For now, we'll use a simple approach based on team order
                if reconstructed_games[game_id]['home']['team_name'] is None:
                    reconstructed_games[game_id]['home']['team_name'] = team_name
                    reconstructed_games[game_id]['home']['players'].append(player_info)
                elif reconstructed_games[game_id]['away']['team_name'] is None:
                    reconstructed_games[game_id]['away']['team_name'] = team_name
                    reconstructed_games[game_id]['away']['players'].append(player_info)

# Convert to list and filter valid games
final_games = []
for game_id, game_data in reconstructed_games.items():
    if (game_data['home']['team_name'] and game_data['away']['team_name'] and
        len(game_data['home']['players']) > 0 and len(game_data['away']['players']) > 0):
        final_games.append(game_data)

# Sort by date
final_games = sorted(final_games, key=lambda g: g.get('date', ''))

# Save to file
output_data = {'games': final_games}
with open('output/handball_games.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"✅ Created handball_games.json with {len(final_games)} games")
print(f"\nTeams per game:")
teams_set = set()
for game in final_games:
    teams_set.add(game['home']['team_name'])
    teams_set.add(game['away']['team_name'])

print(f"Total unique teams: {len(teams_set)}")
print(f"Teams: {sorted(teams_set)}")

# Show sample
if final_games:
    sample = final_games[0]
    print(f"\nSample game:")
    print(f"  Date: {sample['date']}")
    print(f"  {sample['home']['team_name']} ({len(sample['home']['players'])} players) vs {sample['away']['team_name']} ({len(sample['away']['players'])} players)")
