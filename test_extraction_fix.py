#!/usr/bin/env python3
"""
Fixed player extraction from AUFSTELLUNG page HTML
"""

from bs4 import BeautifulSoup

def extract_players_from_aufstellung_fixed(html):
    """Extract players from AUFSTELLUNG page - FIXED VERSION"""
    soup = BeautifulSoup(html, 'html.parser')
    
    players_by_team = {}
    
    # Find all tables (should have multiple - one per team view, plus admin section)
    tables = soup.find_all('table', class_='mb-4 w-full text-base')
    
    print(f"Found {len(tables)} tables")
    
    for idx, table in enumerate(tables):
        print(f"\n--- Table {idx + 1} ---")
        
        # Get team name from the h3 heading before this table
        # Look backwards for the nearest h3
        team_name = "Unknown"
        current = table
        while current:
            current = current.find_previous('h3')
            if current:
                team_name = current.get_text(strip=True)
                break
        
        print(f"Team: {team_name}")
        
        # Extract players from tbody
        tbody = table.find('tbody')
        if not tbody:
            print(f"  No tbody found in table {idx + 1}")
            continue
        
        rows = tbody.find_all('tr')
        print(f"  Rows: {len(rows)}")
        
        team_players = []
        for row_idx, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 2:
                # First cell is number, second cell is player name
                number = cells[0].get_text(strip=True)
                player_name = cells[1].get_text(strip=True)
                
                if player_name:  # Only add if name is not empty
                    team_players.append({
                        'number': number,
                        'name': player_name
                    })
                    print(f"  {number}. {player_name}")
        
        if team_name and team_players:
            if team_name not in players_by_team:
                players_by_team[team_name] = []
            players_by_team[team_name].extend(team_players)
    
    print(f"\n=== Summary ===")
    for team, players in players_by_team.items():
        print(f"{team}: {len(players)} players")
        for p in players[:3]:
            print(f"  - {p['number']} {p['name']}")
        if len(players) > 3:
            print(f"  ... and {len(players) - 3} more")
    
    return players_by_team

# Test with saved HTML
with open('aufstellung_inspect.html', 'r') as f:
    html = f.read()

players = extract_players_from_aufstellung_fixed(html)
print(f"\n✓ Extraction complete - Found {sum(len(p) for p in players.values())} total players")
