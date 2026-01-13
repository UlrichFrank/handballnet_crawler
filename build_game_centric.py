#!/usr/bin/env python3
"""
Build game-centric format from existing detailed player data
"""
import json
from collections import defaultdict

# Load detailed data with game info
with open('output/handball_players_detailed.json', 'r') as f:
    detailed_data = json.load(f)

# Parse games from player game_details
games_dict = defaultdict(lambda: {'home': None, 'away': None, 'date': None})

teams_data = detailed_data['teams']

# First pass: collect all game references
for team_name, team_info in teams_data.items():
    for player in team_info['players']:
        if 'game_details' not in player:
            continue
        
        for game_info in player['game_details']:
            game_id = game_info['game_id']
            date = game_info['date']
            
            if date:
                games_dict[game_id]['date'] = date

# Second pass: assign teams as home/away based on opponent_teams
for team_name, team_info in teams_data.items():
    for player in team_info['players']:
        if 'game_details' not in player:
            continue
        
        for game_info in player['game_details']:
            game_id = game_info['game_id']
            opponent_teams = game_info.get('opponent_teams', [])
            
            # Determine home vs away
            # If this is the first team we see for this game, mark as home
            if games_dict[game_id]['home'] is None:
                games_dict[game_id]['home'] = {
                    'team_name': team_name,
                    'players': []
                }
            elif games_dict[game_id]['away'] is None and games_dict[game_id]['home']['team_name'] != team_name:
                games_dict[game_id]['away'] = {
                    'team_name': team_name,
                    'players': []
                }

# Third pass: add player data
for team_name, team_info in teams_data.items():
    for player in team_info['players']:
        if 'game_details' not in player:
            continue
        
        for game_info in player['game_details']:
            game_id = game_info['game_id']
            
            player_entry = {
                'name': player['name'],
                'goals': game_info['goals'],
                'two_min_penalties': game_info['two_min_penalties'],
                'yellow_cards': game_info['yellow_cards'],
                'red_cards': game_info['red_cards'],
                'blue_cards': game_info['blue_cards']
            }
            
            # Add to home team
            if games_dict[game_id]['home'] and games_dict[game_id]['home']['team_name'] == team_name:
                games_dict[game_id]['home']['players'].append(player_entry)
            # Add to away team
            elif games_dict[game_id]['away'] and games_dict[game_id]['away']['team_name'] == team_name:
                games_dict[game_id]['away']['players'].append(player_entry)

# Filter complete games and sort
final_games = []
for game_id, game_data in games_dict.items():
    if (game_data['home'] and game_data['away'] and 
        game_data['home']['team_name'] and game_data['away']['team_name'] and
        len(game_data['home']['players']) > 0 and len(game_data['away']['players']) > 0):
        
        game_entry = {
            'game_id': game_id,
            'date': game_data['date'],
            'home': game_data['home'],
            'away': game_data['away']
        }
        final_games.append(game_entry)

# Sort by date
final_games = sorted(final_games, key=lambda g: g.get('date', ''))

# Save
output = {'games': final_games}
with open('output/handball_games.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"✅ Created handball_games.json")
print(f"   {len(final_games)} complete games")
print(f"   {len(set(g['home']['team_name'] for g in final_games) | set(g['away']['team_name'] for g in final_games))} teams")

if final_games:
    print(f"\nFirst game: {final_games[0]['date']} | {final_games[0]['home']['team_name']} vs {final_games[0]['away']['team_name']}")
    print(f"Last game:  {final_games[-1]['date']} | {final_games[-1]['home']['team_name']} vs {final_games[-1]['away']['team_name']}")
