#!/usr/bin/env python3
"""
Extract all players from a handball league's games via Aufstellung pages
Workflow:
  1. Liga Spielplan (mit Datum-Filter) → Tabelle mit all Spielpaarungen
  2. Für jede Paarung: Klick auf Team → AUFSTELLUNG Tab
  3. HEIM/GAST Tab → Spieler aus Tabelle extrahieren
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import requests

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AufstellungExtractor:
    """Extracts players from game lineups (AUFSTELLUNG pages)"""
    
    def __init__(self, driver, base_url: str, cert_path: Optional[str] = None, verify_ssl: bool = True):
        self.driver = driver
        self.base_url = base_url
        self.cert_path = Path(cert_path).expanduser() if cert_path else None
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
    def get_league_games(self, league_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Fetch all games from league Spielplan with date filters
        Returns list of games with home/away teams
        """
        print(f"\n1. Fetching games from league: {league_id}")
        print(f"   Date range: {date_from} to {date_to}")
        
        # Construct URL with date parameters
        url = (
            f"{self.base_url}/mannschaften/handball4all.{league_id}/spielplan"
            f"?dateFrom={date_from}&dateTo={date_to}"
        )
        print(f"   URL: {url}\n")
        
        self.driver.get(url)
        time.sleep(2)
        
        # Parse HTML to find all games in the schedule table
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        games = []
        
        # Find game rows in the table
        # Looking for table rows with game data
        schedule_items = soup.find_all('div', class_=lambda x: x and 'schedule' in x.lower())
        
        if not schedule_items:
            print("⚠ No schedule items found, trying alternative selectors...")
            schedule_items = soup.find_all('div', class_=lambda x: x and any(
                keyword in (x or '').lower() 
                for keyword in ['game', 'match', 'spieltag', 'paarung']
            ))
        
        print(f"Found {len(schedule_items)} potential game containers")
        
        # For now, return empty - we'll enhance this after inspecting the HTML
        return games
    
    def get_players_from_aufstellung(self, team_id: str, game_id: str, is_home: bool = True) -> List[Dict[str, str]]:
        """
        Navigate to AUFSTELLUNG page and extract players for a specific team in a game
        
        Args:
            team_id: Team identifier
            game_id: Game identifier  
            is_home: True for HEIM (home), False for GAST (away)
            
        Returns:
            List of players with their data
        """
        players = []
        
        try:
            # Navigate to aufstellung page
            aufstellung_url = f"{self.base_url}/spiele/{game_id}/aufstellung"
            print(f"  Navigating to AUFSTELLUNG: {aufstellung_url}")
            
            self.driver.get(aufstellung_url)
            time.sleep(1)
            
            # Click HEIM or GAST tab
            team_type = "HEIM" if is_home else "GAST"
            print(f"    Looking for {team_type} tab...")
            
            try:
                tab_xpath = f"//button[contains(text(), '{team_type}')] | //a[contains(text(), '{team_type}')]"
                tab_element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, tab_xpath))
                )
                tab_element.click()
                time.sleep(1)
            except Exception as e:
                print(f"    ⚠ Could not find {team_type} tab: {e}")
                return players
            
            # Extract players from table
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find player table (looking for table with "Spieler" header)
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table has "Spieler" column
                headers = [th.get_text(strip=True) for th in table.find_all(['th', 'td'])]
                
                if any('spieler' in h.lower() for h in headers):
                    print(f"    ✓ Found player table with {len(headers)} columns")
                    
                    # Extract player rows
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            # First column is player name
                            player_name = cells[0].get_text(strip=True)
                            
                            if player_name:
                                player_data = {
                                    'name': player_name,
                                    'team_id': team_id,
                                    'team_type': team_type,
                                    'game_id': game_id,
                                }
                                
                                # Try to extract additional columns if available
                                if len(cells) > 1:
                                    player_data['number'] = cells[1].get_text(strip=True)
                                if len(cells) > 2:
                                    player_data['position'] = cells[2].get_text(strip=True)
                                
                                players.append(player_data)
                                print(f"      → {player_name}")
                    
                    break
            
            print(f"    ✓ Extracted {len(players)} players")
            
        except Exception as e:
            print(f"  ⚠ Error extracting players: {e}")
        
        return players
    
    def extract_all_players(self, league_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Main extraction workflow:
        1. Get all games from league Spielplan
        2. For each game: navigate to AUFSTELLUNG and extract players
        3. Return deduplicated list of all players
        """
        print("\n" + "="*80)
        print("PLAYER EXTRACTION FROM GAME LINEUPS (AUFSTELLUNG)")
        print("="*80)
        
        all_players = {}  # Deduplicate by (name, team)
        
        # Step 1: Get all games
        games = self.get_league_games(league_id, date_from, date_to)
        
        if not games:
            print("⚠ No games found")
            return []
        
        print(f"\n2. Processing {len(games)} games for player extraction...")
        
        # Step 2: For each game, extract players from both teams
        for i, game in enumerate(games, 1):
            print(f"\n[{i}/{len(games)}] Game: {game.get('date')} - "
                  f"{game.get('home_team')} vs {game.get('away_team')}")
            
            game_id = game.get('game_id')
            home_team_id = game.get('home_team_id')
            away_team_id = game.get('away_team_id')
            home_team_name = game.get('home_team')
            away_team_name = game.get('away_team')
            
            if not game_id or not home_team_id or not away_team_id:
                print("  ⚠ Missing game data, skipping")
                continue
            
            # Extract home team players
            home_players = self.get_players_from_aufstellung(home_team_id, game_id, is_home=True)
            for player in home_players:
                player['team_name'] = home_team_name
                key = (player['name'], home_team_name)
                all_players[key] = player
            
            # Extract away team players
            away_players = self.get_players_from_aufstellung(away_team_id, game_id, is_home=False)
            for player in away_players:
                player['team_name'] = away_team_name
                key = (player['name'], away_team_name)
                all_players[key] = player
        
        result = list(all_players.values())
        
        print("\n" + "="*80)
        print(f"EXTRACTION COMPLETE")
        print(f"Total unique players: {len(result)}")
        print("="*80)
        
        return result


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
    
    league_id = config.get("league", {}).get("league_id", "baden-wuerttemberg.mc-ol-3-bw_bwhv")
    date_from = config.get("league", {}).get("date_from", "2025-07-01")
    date_to = config.get("league", {}).get("date_to", "2026-06-30")
    
    print("="*80)
    print("HANDBALL.NET PLAYER EXTRACTION VIA AUFSTELLUNG")
    print("="*80)
    print(f"League: {league_id}")
    print(f"Date Range: {date_from} to {date_to}")
    print()
    
    # Authenticate with Selenium
    print("1. Authenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    auth.login()
    print("✓ Authentication successful\n")
    
    # Create extractor and run extraction
    extractor = AufstellungExtractor(auth.driver, base_url, cert_path, verify_ssl)
    
    try:
        players = extractor.extract_all_players(league_id, date_from, date_to)
        
        # Print results
        if players:
            print(f"\nExtracted {len(players)} unique players:")
            for i, player in enumerate(players[:10], 1):
                print(f"  {i}. {player['name']} ({player.get('team_name', 'Unknown team')})")
            if len(players) > 10:
                print(f"  ... and {len(players) - 10} more")
        else:
            print("No players extracted")
    
    finally:
        print("\nCleaning up...")
        auth.driver.quit()
        print("✓ Done")


if __name__ == '__main__':
    main()
