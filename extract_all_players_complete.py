#!/usr/bin/env python3
"""
Complete workflow: Extract all players from all games in Spielplan
Fixed extraction + deduplification + JSON export
"""

import time
import json
from bs4 import BeautifulSoup
from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Configuration
BASE_URL = config['authentication']['base_url']
USERNAME = config['authentication']['username']
PASSWORD = config['authentication']['password']
LEAGUE_ID = "handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv"
DATE_FROM = "2024-11-01"
DATE_TO = "2025-12-31"

def extract_games_from_spielplan(html):
    """Extract game IDs from Spielplan page"""
    soup = BeautifulSoup(html, 'html.parser')
    game_ids = set()
    
    # Find all links to game pages
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/spiele/' in href and '/aufstellung' not in href:
            # Extract game ID from /spiele/{game_id} URLs
            parts = href.split('/')
            if len(parts) >= 3 and parts[-2] == 'spiele':
                game_id = parts[-1]
                if game_id and game_id.startswith('handball4all'):
                    game_ids.add(game_id)
    
    return list(game_ids)

def extract_players_from_aufstellung_fixed(html):
    """Extract players from AUFSTELLUNG page - FIXED VERSION"""
    soup = BeautifulSoup(html, 'html.parser')
    
    players_by_team = {}
    
    # Find all tables
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

# Initialize authentication
print("🔐 Authenticating...")
auth = HandballNetSeleniumAuthenticator(
    base_url=BASE_URL,
    username=USERNAME,
    password=PASSWORD
)
if not auth.login():
    print("❌ Authentication failed")
    exit(1)

cookies = auth.get_cookies()
print(f"✓ Authenticated with {len(cookies)} cookies")

# Load Spielplan
print(f"\n📋 Loading Spielplan...")
spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
auth.driver.get(spielplan_url)
time.sleep(3)

html = auth.driver.page_source
game_ids = extract_games_from_spielplan(html)
print(f"✓ Found {len(game_ids)} games")

# Extract players from each game
print(f"\n👥 Extracting players from {len(game_ids)} games...")

all_players = {}  # {team_name: set of player names}
game_results = []

for idx, game_id in enumerate(game_ids, 1):
    try:
        aufstellung_url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
        auth.driver.get(aufstellung_url)
        time.sleep(1)
        
        html = auth.driver.page_source
        players_by_team = extract_players_from_aufstellung_fixed(html)
        
        print(f"  [{idx}/{len(game_ids)}] {game_id}: ", end="")
        
        game_data = {
            'game_id': game_id,
            'teams': {}
        }
        
        for team_name, players in players_by_team.items():
            player_names = [p['name'] for p in players]
            game_data['teams'][team_name] = player_names
            
            # Add to global set
            if team_name not in all_players:
                all_players[team_name] = set()
            all_players[team_name].update(player_names)
            
            print(f"{team_name} ({len(player_names)} players)", end=" | ")
        
        print()
        game_results.append(game_data)
        
    except Exception as e:
        print(f"  [{idx}/{len(game_ids)}] ❌ Error: {str(e)[:50]}")

# Deduplicate and create final output
print(f"\n✓ Extraction complete!")
print(f"\n📊 Deduplicated Results:")

final_data = {
    'league': {
        'id': LEAGUE_ID,
        'games_processed': len(game_results),
        'date_range': {'from': DATE_FROM, 'to': DATE_TO}
    },
    'teams': {}
}

total_unique = 0
for team_name in sorted(all_players.keys()):
    players = sorted(list(all_players[team_name]))
    final_data['teams'][team_name] = {
        'player_count': len(players),
        'players': players
    }
    print(f"  {team_name}: {len(players)} unique players")
    total_unique += len(players)

print(f"\n  Total unique players: {total_unique}")

# Export to JSON
output_file = 'extracted_players.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Results saved to {output_file}")

# Close driver
auth.driver.quit()
