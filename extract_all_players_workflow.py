#!/usr/bin/env python3
"""
Complete workflow to extract all players from a league's games.

Steps:
1. Navigate to Spielplan page
2. Extract all game IDs
3. For each game, navigate to AUFSTELLUNG page
4. Click HEIM/GAST tabs
5. Extract player names from table
6. Deduplicate and export
"""

import sys
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator


def extract_games_from_spielplan(html_content: str) -> list:
    """Extract game IDs from Spielplan page HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all game links
    game_links = soup.find_all('a', href=lambda x: x and '/spiele/' in x and 'handball4all' in x)
    
    # Extract unique game IDs
    game_ids = set()
    for link in game_links:
        href = link.get('href', '')
        # Extract game ID from /spiele/handball4all.xxx.yyyyy/...
        if '/spiele/handball4all' in href:
            parts = href.split('/')
            if 'spiele' in parts:
                idx = parts.index('spiele')
                if idx + 1 < len(parts):
                    game_id = parts[idx + 1]
                    game_ids.add(game_id)
    
    return sorted(list(game_ids))


def extract_players_from_aufstellung(html_content: str) -> list:
    """Extract player names from AUFSTELLUNG page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    players = []
    
    # Try multiple strategies to find player table
    # Strategy 1: Look for tables with player column headers
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells:
                # Get first cell (usually player name in AUFSTELLUNG)
                cell_text = cells[0].get_text(strip=True)
                if cell_text and len(cell_text) > 1:
                    # Filter out numbers and empty cells
                    if not cell_text.isdigit() and cell_text not in ['', '#', 'Nr.', 'Spieler']:
                        players.append(cell_text)
    
    # Strategy 2: Look for divs/spans with player names
    if not players:
        # Look for elements containing player info
        possible_elements = soup.find_all(['span', 'div'], 
            class_=lambda x: x and any(term in x.lower() for term in ['player', 'spieler', 'name']))
        for elem in possible_elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 2:
                players.append(text)
    
    return list(set(players))  # Deduplicate


def main():
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    base_url = config["authentication"]["base_url"]
    username = config["authentication"]["username"]
    password = config["authentication"]["password"]
    cert_path = config.get("ssl", {}).get("cert_path")
    verify_ssl = config.get("ssl", {}).get("verify_ssl", False)
    
    league_id = "handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv"
    date_from = "2025-07-01"
    date_to = "2026-06-30"
    
    print("=" * 80)
    print("COMPLETE PLAYER EXTRACTION WORKFLOW")
    print("=" * 80)
    
    # Step 1: Authenticate
    print("\nStep 1: Authenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    success = auth.login()
    
    if not success:
        print("✗ Authentication failed!")
        return
    
    print("✓ Authenticated")
    
    # Step 2: Navigate to Spielplan and extract games
    print("\nStep 2: Loading Spielplan page...")
    spielplan_url = f"{base_url}/ligen/{league_id}/spielplan?dateFrom={date_from}&dateTo={date_to}"
    auth.driver.get(spielplan_url)
    time.sleep(3)
    
    spielplan_html = auth.driver.page_source
    game_ids = extract_games_from_spielplan(spielplan_html)
    print(f"✓ Found {len(game_ids)} games in Spielplan")
    
    # Step 3: For each game, navigate to AUFSTELLUNG and extract players
    print("\nStep 3: Extracting players from games...")
    all_players = defaultdict(set)  # team_name -> set of player names
    
    for idx, game_id in enumerate(game_ids[:5], 1):  # Test with first 5 games
        print(f"\n  Game {idx}/{min(5, len(game_ids))}: {game_id}")
        
        # Navigate to AUFSTELLUNG page
        aufstellung_url = f"{base_url}/spiele/{game_id}/aufstellung"
        auth.driver.get(aufstellung_url)
        time.sleep(1.5)
        
        # Check if page loaded
        if 'AUFSTELLUNG' in auth.driver.page_source or 'Aufstellung' in auth.driver.page_source:
            html = auth.driver.page_source
            
            # Try to extract team names and players
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for team names (usually in headers or tabs)
            team_headers = soup.find_all(['h2', 'h3', 'div', 'span'], 
                class_=lambda x: x and any(t in x.lower() for t in ['heim', 'gast', 'home', 'away']))
            
            teams = []
            for header in team_headers:
                text = header.get_text(strip=True)
                if text:
                    teams.append(text[:50])
            
            if teams:
                print(f"    - Teams found: {teams[0] if teams else 'Unknown'}")
            
            # Extract players
            players = extract_players_from_aufstellung(html)
            print(f"    - Players extracted: {len(players)}")
            
            # Try to assign to teams (simplified - just alternate)
            if players and teams:
                for p_idx, player in enumerate(players):
                    team_idx = p_idx % len(teams)
                    team = teams[team_idx] if team_idx < len(teams) else "Unknown"
                    all_players[team].add(player)
        else:
            print(f"    ⚠ Page did not load properly")
    
    # Step 4: Summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    
    total_players = sum(len(players) for players in all_players.values())
    print(f"\nTotal unique players found: {total_players}")
    
    for team, players in sorted(all_players.items()):
        print(f"\n{team}: {len(players)} players")
        for player in sorted(list(players))[:5]:
            print(f"  - {player}")
        if len(players) > 5:
            print(f"  ... and {len(players) - 5} more")
    
    # Clean up
    print("\n✓ Closing browser...")
    auth.driver.quit()
    
    return all_players


if __name__ == "__main__":
    main()
