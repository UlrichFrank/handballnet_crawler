#!/usr/bin/env python3
"""
UNIFIED PLAYER EXTRACTION SCRIPT
Extract all players from handball.net Spielplan and AUFSTELLUNG pages
Fully tested and working extraction logic
"""

import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://www.handball.net"
LEAGUE_ID = "handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv"
DATE_FROM = "2024-11-01"
DATE_TO = "2025-12-31"
MAX_GAMES = 50  # Set to 50 to extract all games

# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_games_from_spielplan(html):
    """Extract game IDs from Spielplan page"""
    soup = BeautifulSoup(html, 'html.parser')
    game_ids = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/spiele/' in href and '/aufstellung' not in href:
            parts = href.split('/')
            if len(parts) >= 3 and parts[-2] == 'spiele':
                game_id = parts[-1]
                if game_id and game_id.startswith('handball4all'):
                    game_ids.add(game_id)
    
    return list(game_ids)

def extract_players_from_aufstellung(html):
    """Extract players from AUFSTELLUNG page"""
    soup = BeautifulSoup(html, 'html.parser')
    players_by_team = {}
    tables = soup.find_all('table', class_='mb-4 w-full text-base')
    seen_teams = set()
    
    for table in tables:
        # Get team name from h3 before table
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
        
        # Extract players
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

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main extraction workflow"""
    
    print("=" * 70)
    print("HANDBALL.NET PLAYER EXTRACTION")
    print("=" * 70)
    print(f"League: {LEAGUE_ID}")
    print(f"Date Range: {DATE_FROM} to {DATE_TO}")
    print(f"Max Games: {MAX_GAMES}")
    print()
    
    # Setup Chrome driver
    print("🌐 Setting up Chrome WebDriver...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Load Spielplan
        print("📋 Loading Spielplan...")
        spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
        driver.get(spielplan_url)
        time.sleep(3)
        
        html = driver.page_source
        game_ids = extract_games_from_spielplan(html)
        print(f"✓ Found {len(game_ids)} games")
        
        # Limit to MAX_GAMES
        game_ids = game_ids[:MAX_GAMES]
        print(f"Processing: {len(game_ids)} games")
        
        # Extract players from each game
        print(f"\n👥 Extracting players...")
        
        all_players = {}  # {team_name: set of player names}
        game_results = []
        errors = []
        
        for idx, game_id in enumerate(game_ids, 1):
            try:
                aufstellung_url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
                driver.get(aufstellung_url)
                time.sleep(1)
                
                html = driver.page_source
                players_by_team = extract_players_from_aufstellung(html)
                
                teams_str = " | ".join([f"{t}: {len(p)}" for t, p in players_by_team.items()])
                print(f"  [{idx:2d}/{len(game_ids)}] {game_id}: {teams_str}")
                
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
                
                game_results.append(game_data)
                
            except Exception as e:
                error_msg = f"Game {game_id}: {str(e)[:50]}"
                errors.append(error_msg)
                print(f"  [{idx:2d}/{len(game_ids)}] ❌ {error_msg}")
        
        # Deduplicate and create final output
        print(f"\n" + "=" * 70)
        print(f"✓ EXTRACTION COMPLETE")
        print("=" * 70)
        
        if errors:
            print(f"\n⚠ {len(errors)} errors encountered:")
            for err in errors[:5]:
                print(f"  - {err}")
        
        print(f"\n📊 RESULTS:")
        print(f"  Games processed: {len(game_results)}")
        print(f"  Teams found: {len(all_players)}")
        
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
            print(f"\n  {team_name}:")
            print(f"    Count: {len(players)} unique players")
            print(f"    First 5: {', '.join(players[:5])}")
            if len(players) > 5:
                print(f"    ... and {len(players) - 5} more")
            total_unique += len(players)
        
        print(f"\n  Total unique players: {total_unique}")
        
        # Export to JSON
        output_file = f'extracted_players_{len(game_results)}_games.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Results saved to: {output_file}")
        
        return final_data
        
    finally:
        if driver:
            driver.quit()
            print("\n🏁 WebDriver closed")

if __name__ == '__main__':
    main()
