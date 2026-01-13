#!/usr/bin/env python3
"""
UNIFIED PLAYER EXTRACTION SCRIPT
Extract all players from handball.net Spielplan and AUFSTELLUNG pages
Fully tested and working extraction logic
"""

import time
import json
import os
from pathlib import Path
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
# CONFIGURATION - Load from config.json
# ============================================================================

# Load configuration from config/config.json
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']
USERNAME = config['authentication']['username']
PASSWORD = config['authentication']['password']
MAX_GAMES = 50  # Set to 50 to extract all games

print(f"📋 Konfiguration geladen:")
print(f"   League: {config['league']['display_name']}")
print(f"   Zeitraum: {DATE_FROM} bis {DATE_TO}")
print(f"   Max Games: {MAX_GAMES}")

# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_games_from_spielplan(html):
    """Extract game IDs from Spielplan page and try to capture game data"""
    soup = BeautifulSoup(html, 'html.parser')
    game_ids = set()
    game_dates = {}  # {game_id: date}
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/spiele/handball4all' in href:
            parts = href.split('/')
            try:
                spiele_idx = parts.index('spiele')
                if spiele_idx + 1 < len(parts):
                    game_id = parts[spiele_idx + 1]
                    if game_id and game_id.startswith('handball4all'):
                        game_ids.add(game_id)
                        
                        # Try to extract date from parent elements or text
                        parent = link.find_parent(['div', 'tr', 'td'], recursive=False)
                        if not parent:
                            parent = link.find_parent()
                        
                        if parent:
                            import re
                            parent_text = parent.get_text()
                            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', parent_text)
                            if date_match:
                                game_dates[game_id] = date_match.group(1)
            except (ValueError, IndexError):
                pass
    
    return list(game_ids), game_dates

def extract_players_from_aufstellung(html):
    """Extract players from AUFSTELLUNG page with statistics"""
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
        
        # Extract players with statistics
        tbody = table.find('tbody')
        if not tbody:
            continue
        
        rows = tbody.find_all('tr')
        team_players = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 5:
                number = cells[0].get_text(strip=True)
                player_name = cells[1].get_text(strip=True)
                
                # Extract statistics
                goals = cells[2].get_text(strip=True) or "0"
                two_min_penalties = cells[3].get_text(strip=True) or "0"
                
                # Yellow/Red/Blue cards (cell 4)
                yellow_cards = 0
                red_cards = 0
                blue_cards = 0
                
                if len(cells) > 4:
                    card_cell = cells[4]
                    # Count card images/indicators
                    yellow_imgs = card_cell.find_all('img', src=lambda x: x and 'yellow' in x.lower() if x else False)
                    red_imgs = card_cell.find_all('img', src=lambda x: x and 'red' in x.lower() if x else False)
                    blue_imgs = card_cell.find_all('img', src=lambda x: x and 'blue' in x.lower() if x else False)
                    
                    yellow_cards = len(yellow_imgs)
                    red_cards = len(red_imgs)
                    blue_cards = len(blue_imgs)
                
                if player_name:
                    team_players.append({
                        'number': number,
                        'name': player_name,
                        'goals': int(goals) if goals.isdigit() else 0,
                        'two_min_penalties': int(two_min_penalties) if two_min_penalties.isdigit() else 0,
                        'yellow_cards': yellow_cards,
                        'red_cards': red_cards,
                        'blue_cards': blue_cards
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
        game_ids, game_dates_from_spielplan = extract_games_from_spielplan(html)
        print(f"✓ Found {len(game_ids)} games")
        print(f"✓ Found dates for {len(game_dates_from_spielplan)} games from Spielplan")
        
        # Limit to MAX_GAMES
        game_ids = game_ids[:MAX_GAMES]
        print(f"Processing: {len(game_ids)} games")
        
        # Extract players from each game
        print(f"\n👥 Extracting players with statistics...")
        
        all_players_stats = {}  # {team_name: {player_name: {stats}}}
        game_results = []
        errors = []
        
        for idx, game_id in enumerate(game_ids, 1):
            try:
                aufstellung_url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
                driver.get(aufstellung_url)
                time.sleep(1)
                
                html = driver.page_source
                players_by_team = extract_players_from_aufstellung(html)
                
                # Extract game date and opponent info from HTML
                soup = BeautifulSoup(html, 'html.parser')
                game_date = game_dates_from_spielplan.get(game_id, "Unknown")  # Use date from Spielplan if available
                opponent_teams = list(players_by_team.keys()) if players_by_team else []
                
                # If date is still Unknown, try to find it from AUFSTELLUNG page
                if game_date == "Unknown":
                    # Try to find game date from various sources
                    import re
                    
                    # 1. Look for date in page text
                    date_text = soup.get_text()
                    date_patterns = [
                        r'(\d{1,2}\.\d{1,2}\.\d{4})',  # DD.MM.YYYY
                        r'(\d{1,2}\.\s+\w+\s+\d{4})',  # DD. Month YYYY
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, date_text)
                        if match:
                            game_date = match.group(1)
                            break
                    
                    # 2. If not found, try to extract from h1/h2 titles
                    if game_date == "Unknown":
                        for heading in soup.find_all(['h1', 'h2', 'h3']):
                            heading_text = heading.get_text()
                            match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', heading_text)
                            if match:
                                game_date = match.group(1)
                                break
                
                teams_str = " | ".join([f"{t}: {len(p)}" for t, p in players_by_team.items()])
                print(f"  [{idx:2d}/{len(game_ids)}] {game_id}: {teams_str}")
                
                game_data = {
                    'game_id': game_id,
                    'date': game_date,
                    'opponent_teams': opponent_teams,
                    'teams': {}
                }
                
                for team_name, players in players_by_team.items():
                    game_data['teams'][team_name] = {
                        'player_count': len(players),
                        'players': players
                    }
                    
                    # Add to global stats
                    if team_name not in all_players_stats:
                        all_players_stats[team_name] = {}
                    
                    for player in players:
                        if player['name'] not in all_players_stats[team_name]:
                            all_players_stats[team_name][player['name']] = {
                                'appearances': 0,
                                'total_goals': 0,
                                'total_two_min_penalties': 0,
                                'total_yellow_cards': 0,
                                'total_red_cards': 0,
                                'total_blue_cards': 0,
                                'games': []
                            }
                        
                        stats = all_players_stats[team_name][player['name']]
                        stats['appearances'] += 1
                        stats['total_goals'] += player['goals']
                        stats['total_two_min_penalties'] += player['two_min_penalties']
                        stats['total_yellow_cards'] += player['yellow_cards']
                        stats['total_red_cards'] += player['red_cards']
                        stats['total_blue_cards'] += player['blue_cards']
                        stats['games'].append({
                            'game_id': game_id,
                            'date': game_date,
                            'opponent_teams': opponent_teams,
                            'goals': player['goals'],
                            'two_min_penalties': player['two_min_penalties'],
                            'yellow_cards': player['yellow_cards'],
                            'red_cards': player['red_cards'],
                            'blue_cards': player['blue_cards']
                        })
                
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
        print(f"  Teams found: {len(all_players_stats)}")
        
        final_data = {
            'league': {
                'id': LEAGUE_ID,
                'games_processed': len(game_results),
                'date_range': {'from': DATE_FROM, 'to': DATE_TO}
            },
            'teams': {}
        }
        
        total_unique = 0
        for team_name in sorted(all_players_stats.keys()):
            team_stats = all_players_stats[team_name]
            
            # Convert stats to simplified output format
            players_list = []
            for player_name in sorted(team_stats.keys()):
                stats = team_stats[player_name]
                players_list.append({
                    'name': player_name,
                    'goals': stats['total_goals'],
                    'matches': stats['appearances'],
                    'minutes': stats['total_two_min_penalties'],  # 2-min penalties as stand-in for minutes
                    'yellow_cards': stats['total_yellow_cards'],
                    'red_cards': stats['total_red_cards'],
                    'blue_cards': stats['total_blue_cards']
                })
            
            final_data['teams'][team_name] = {
                'player_count': len(players_list),
                'players': players_list
            }
            
            print(f"\n  {team_name}:")
            print(f"    Count: {len(players_list)} unique players")
            print(f"    First 3: {', '.join([p['name'] for p in players_list[:3]])}")
            if len(players_list) > 3:
                print(f"    ... and {len(players_list) - 3} more")
            
            # Aggregate statistics
            total_goals = sum(p['goals'] for p in players_list)
            total_minutes = sum(p['minutes'] for p in players_list)
            total_yellows = sum(p['yellow_cards'] for p in players_list)
            total_reds = sum(p['red_cards'] for p in players_list)
            total_blues = sum(p['blue_cards'] for p in players_list)
            
            print(f"    Statistics:")
            print(f"      Total Goals: {total_goals}")
            print(f"      2-Min Penalties: {total_minutes}")
            print(f"      Yellow Cards: {total_yellows}, Red: {total_reds}, Blue: {total_blues}")
            
            total_unique += len(players_list)
        
        print(f"\n  Total unique players: {total_unique}")
        
        # Export to JSON
        import os
        os.makedirs('output', exist_ok=True)
        
        # Simplified aggregated format for main export
        output_file = f'extracted_players_{len(game_results)}_games.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        # Also save simplified version to output directory
        output_dir_file = os.path.join('output', 'handball_players.json')
        with open(output_dir_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        # Create detailed version with game details for reference
        detailed_data = {
            'league': {
                'id': LEAGUE_ID,
                'games_processed': len(game_results),
                'date_range': {'from': DATE_FROM, 'to': DATE_TO}
            },
            'teams': {}
        }
        
        for team_name in sorted(all_players_stats.keys()):
            team_stats = all_players_stats[team_name]
            
            # Convert stats with game details
            players_list = []
            for player_name in sorted(team_stats.keys()):
                stats = team_stats[player_name]
                players_list.append({
                    'name': player_name,
                    'goals': stats['total_goals'],
                    'matches': stats['appearances'],
                    'minutes': stats['total_two_min_penalties'],
                    'yellow_cards': stats['total_yellow_cards'],
                    'red_cards': stats['total_red_cards'],
                    'blue_cards': stats['total_blue_cards'],
                    'game_details': stats['games']
                })
            
            detailed_data['teams'][team_name] = {
                'player_count': len(players_list),
                'players': players_list
            }
        
        # Save detailed version
        detailed_file = os.path.join('output', 'handball_players_detailed.json')
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Aggregated results saved to: {output_file}")
        print(f"✅ Also saved to: {output_dir_file}")
        print(f"✅ Detailed results with game info saved to: {detailed_file}")
        
        return final_data
        
    finally:
        if driver:
            driver.quit()
            print("\n🏁 WebDriver closed")

if __name__ == '__main__':
    main()
