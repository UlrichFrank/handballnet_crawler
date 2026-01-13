#!/usr/bin/env python3
"""
Extract players from handball.net via the Aufstellung workflow

Workflow (as described by user):
1. Liga Spielplan → Tabelle mit allen Spielpaarungen (Datum, Heim, Gast, Ergebnis)
2. Klick auf Heim- oder Gastmannschaft → Team Spielplan
3. Klick auf "AUFSTELLUNG" → Aufstellung page
4. Klick auf "HEIM" oder "GAST" → Spieler-Tabelle in Spalte 1 (Spieler)

Key: AUFSTELLUNG pages are player rosters for each game
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AufstellungPlayerExtractor:
    """Extract all players from game lineups (AUFSTELLUNG)"""
    
    def __init__(self, auth: HandballNetSeleniumAuthenticator, base_url: str):
        self.driver = auth.driver
        self.base_url = base_url
        self.all_players = {}  # Deduplicate: (player_name, team_name) -> data
    
    def navigate_to_aufstellung_page(self, game_id: str) -> bool:
        """Navigate to the AUFSTELLUNG (lineup) page for a game"""
        url = f"{self.base_url}/spiele/{game_id}/aufstellung"
        print(f"  → Navigating to AUFSTELLUNG: {url}")
        try:
            self.driver.get(url)
            time.sleep(1)
            # Check if page loaded successfully
            if "404" in self.driver.page_source or "nicht gefunden" in self.driver.page_source.lower():
                print(f"    ⚠ Game not found (404)")
                return False
            return True
        except Exception as e:
            print(f"    ⚠ Failed to navigate: {e}")
            return False
    
    def click_tab(self, team_type: str) -> bool:
        """Click on HEIM or GAST tab"""
        print(f"    Clicking '{team_type}' tab...")
        tab_selectors = [
            (By.XPATH, f"//button[contains(text(), '{team_type}')] | //a[contains(text(), '{team_type}')]"),
            (By.XPATH, f"//div[contains(@class, 'tab')]//button[contains(text(), '{team_type}')]"),
            (By.XPATH, f"//button[contains(@class, 'active'), text()='{team_type}']"),
        ]
        
        for selector in tab_selectors:
            try:
                tab_element = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(selector)
                )
                tab_element.click()
                time.sleep(0.5)
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        print(f"    ⚠ Could not find '{team_type}' tab")
        return False
    
    def extract_players_from_aufstellung_table(self, game_id: str, team_type: str, team_name: str) -> List[Dict[str, str]]:
        """
        Extract players from the AUFSTELLUNG table
        Expected HTML structure: Table with "Spieler" column
        """
        players = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find the table with player data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains "Spieler" column
                headers = [th.get_text(strip=True) for th in table.find_all(['th', 'td'])[:10]]
                has_spieler = any('spieler' in h.lower() for h in headers)
                
                if not has_spieler:
                    continue
                
                print(f"      ✓ Found player table")
                
                # Extract player rows
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    # First column is player name
                    player_name = cells[0].get_text(strip=True)
                    
                    if not player_name or len(player_name) < 2:
                        continue
                    
                    # Create player entry
                    player_data = {
                        'name': player_name,
                        'team_name': team_name,
                        'team_type': team_type,
                        'game_id': game_id,
                    }
                    
                    # Extract additional columns if available
                    if len(cells) > 1:
                        player_data['number'] = cells[1].get_text(strip=True)
                    if len(cells) > 2:
                        player_data['position'] = cells[2].get_text(strip=True)
                    
                    players.append(player_data)
                    print(f"        → {player_name}")
                
                break
            
            print(f"      Total: {len(players)} players")
            return players
        
        except Exception as e:
            print(f"      ⚠ Error extracting players: {e}")
            return players
    
    def extract_players_for_game(self, game_id: str, home_team: str, away_team: str) -> int:
        """
        Extract players from a single game's AUFSTELLUNG page
        
        Returns: number of unique players added
        """
        print(f"\n  [Game {game_id}]")
        
        # Navigate to AUFSTELLUNG page
        if not self.navigate_to_aufstellung_page(game_id):
            return 0
        
        players_added = 0
        
        # Try both HOME and AWAY teams
        for team_name, team_type in [(home_team, "HEIM"), (away_team, "GAST")]:
            print(f"    Processing {team_type} ({team_name})...")
            
            # Click team type tab
            if not self.click_tab(team_type):
                continue
            
            # Extract players
            players = self.extract_players_from_aufstellung_table(game_id, team_type, team_name)
            
            # Deduplicate
            for player in players:
                key = (player['name'], player['team_name'])
                if key not in self.all_players:
                    self.all_players[key] = player
                    players_added += 1
        
        return players_added
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all deduplicated players"""
        return list(self.all_players.values())


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
    
    print("="*80)
    print("PLAYER EXTRACTION VIA AUFSTELLUNG WORKFLOW")
    print("="*80)
    
    # Authenticate
    print("\n1. Authenticating with handball.net...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    success = auth.login()
    
    if not success:
        print("✗ Authentication failed!")
        return
    
    print("✓ Authenticated\n")
    
    try:
        # Initialize extractor
        extractor = AufstellungPlayerExtractor(auth, base_url)
        
        # Example: Extract from a known game
        # Format: game_id should be like "handball4all.baden-wuerttemberg.8668846"
        
        print("2. Testing with example game...")
        print("   (You'll need to provide game IDs from Spielplan)\n")
        
        # Test with a few example game IDs
        # These would come from the Spielplan page in production
        test_games = [
            # Format: (game_id, home_team, away_team)
            # ("handball4all.baden-wuerttemberg.XXXXXXX", "Team A", "Team B"),
        ]
        
        if test_games:
            total_players_added = 0
            for game_id, home_team, away_team in test_games:
                added = extractor.extract_players_for_game(game_id, home_team, away_team)
                total_players_added += added
            
            print(f"\n3. Results:")
            print(f"   Total unique players: {len(extractor.get_all_players())}")
            print(f"   Players added: {total_players_added}")
            
            # Show sample
            players = extractor.get_all_players()
            if players:
                print(f"\n   Sample players:")
                for player in players[:10]:
                    print(f"     - {player['name']} ({player['team_name']}, {player['team_type']})")
                if len(players) > 10:
                    print(f"     ... and {len(players) - 10} more")
        else:
            print("   ⚠ No test games provided. To use this script:")
            print("   1. Manually navigate to /spielplan on the Spielplan page")
            print("   2. Extract game IDs from the game table")
            print("   3. Provide them to this script")
            print("   4. Script will automatically navigate to AUFSTELLUNG and extract players")
    
    finally:
        print("\nCleaning up...")
        auth.driver.quit()
        print("✓ Done")


if __name__ == '__main__':
    main()
