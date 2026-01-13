#!/usr/bin/env python3
"""
Quick test: Extract players from first 5 games using local HTML files
"""

import json
from bs4 import BeautifulSoup
import os

def extract_players_from_aufstellung_fixed(html):
    """Extract players from AUFSTELLUNG page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    players_by_team = {}
    tables = soup.find_all('table', class_='mb-4 w-full text-base')
    seen_teams = set()
    
    for table in tables:
        # Get team name from the h3 heading before this table
        team_name = "Unknown"
        current = table
        while current:
            current = current.find_previous('h3')
            if current:
                team_name = current.get_text(strip=True)
                break
        
        # Skip duplicate team entries
        if team_name in seen_teams:
            continue
        seen_teams.add(team_name)
        
        # Extract players from tbody
        tbody = table.find('tbody')
        if not tbody:
            continue
        
        rows = tbody.find_all('tr')
        team_players = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                number = cells[0].get_text(strip=True)
                player_name = cells[1].get_text(strip=True)
                
                if player_name:
                    team_players.append({
                        'number': number,
                        'name': player_name
                    })
        
        if team_name and team_players:
            players_by_team[team_name] = team_players
    
    return players_by_team

# Test with the already-saved HTML file
print("Testing extraction with saved HTML file...")
with open('aufstellung_inspect.html', 'r') as f:
    html = f.read()

players = extract_players_from_aufstellung_fixed(html)

print("\n✓ Extraction Results:")
all_players = {}
for team, player_list in players.items():
    player_names = [p['name'] for p in player_list]
    all_players[team] = set(player_names)
    print(f"  {team}: {len(player_names)} players")
    for p in player_list[:3]:
        print(f"    - {p['number']} {p['name']}")
    if len(player_list) > 3:
        print(f"    ... and {len(player_list) - 3} more")

# Create output
total = sum(len(p) for p in all_players.values())
print(f"\nTotal unique players: {total}")

output = {
    'sample_game': 'handball4all.baden-wuerttemberg.8668826',
    'teams': {}
}

for team, names in all_players.items():
    output['teams'][team] = {
        'count': len(names),
        'players': sorted(list(names))
    }

with open('test_extraction_result.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved to test_extraction_result.json")
