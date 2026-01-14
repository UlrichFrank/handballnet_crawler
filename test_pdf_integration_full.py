#!/usr/bin/env python3
"""
Integrated test: Scraper + PDF extraction
Tests that seven_meters data is correctly extracted and enriched
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from hb_crawler.pdf_parser import extract_seven_meters_from_pdf, add_seven_meters_to_players

# Configuration
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

BASE_URL = config['ref']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"

# SSL Setup
ssl_config = config.get('ssl', {})
cert_path = ssl_config.get('cert_path', '')
if cert_path:
    cert_path = os.path.expanduser(cert_path)
    if os.path.exists(cert_path):
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path

print("=" * 70)
print("INTEGRATED TEST: Scraper + PDF Extraction")
print("=" * 70)

def setup_driver():
    """Setup Chrome driver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver_path = ChromeDriverManager().install()
        return webdriver.Chrome(service=Service(driver_path), options=options)
    except Exception:
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            options.binary_location = chrome_path
        return webdriver.Chrome(options=options)

def get_recent_games(driver, days_back=7):
    """Get games from the last N days"""
    print(f"\n[1] Loading games from last {days_back} days...")
    
    # Calculate date range
    date_to = datetime.now().date()
    date_from = date_to - timedelta(days=days_back)
    
    print(f"    Date range: {date_from} to {date_to}")
    
    # Navigate to spielplan
    spielplan_url = f"{BASE_URL}?eID=api&action=getSpielplandaten&saisonID={LEAGUE_ID}&datum_von={date_from}&datum_bis={date_to}"
    print(f"    Loading: {spielplan_url[:80]}...")
    
    driver.get(spielplan_url)
    time.sleep(2)
    
    try:
        content = driver.find_element(By.TAG_NAME, "pre").text
        spielplan = json.loads(content)
        games = spielplan.get('Spielplan', [])
        print(f"    ✓ Found {len(games)} games")
        return games[:3]  # Test with first 3 games
    except Exception as e:
        print(f"    ✗ Error loading spielplan: {str(e)[:80]}")
        return []

def extract_players_from_aufstellung(driver, game_id):
    """Extract players from game aufstellung page"""
    print(f"\n[2] Loading aufstellung for game {game_id}...")
    
    aufstellung_url = f"{BASE_URL}?eID=api&action=getAufstellung&saisonID={LEAGUE_ID}&spielID={game_id}"
    
    try:
        driver.get(aufstellung_url)
        time.sleep(1)
        
        content = driver.find_element(By.TAG_NAME, "pre").text
        aufstellung = json.loads(content)
        
        # Extract players from both teams
        all_players = []
        for team in aufstellung.get('Aufstellung', {}).values():
            for player in team.get('Spieler', []):
                all_players.append({
                    'name': player.get('Spieler'),
                    'goals': 0,
                    'two_min_penalties': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'blue_cards': 0,
                    'seven_meters': 0,
                    'seven_meters_goals': 0
                })
        
        print(f"    ✓ Found {len(all_players)} players")
        return all_players
    except Exception as e:
        print(f"    ✗ Error loading aufstellung: {str(e)[:80]}")
        return []

def find_and_extract_pdf(driver, game_id):
    """Find PDF link and extract seven-meter data"""
    print(f"\n[3] Looking for Spielbericht PDF...")
    
    aufstellung_url = f"{BASE_URL}?eID=api&action=getAufstellung&saisonID={LEAGUE_ID}&spielID={game_id}"
    
    try:
        driver.get(aufstellung_url)
        time.sleep(1)
        
        # Get page HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for PDF link
        pdf_link = None
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'spielbericht' in href.lower() and '.pdf' in href.lower():
                pdf_link = href
                break
        
        if not pdf_link:
            print(f"    ✗ No PDF link found on aufstellung page")
            return {}
        
        # Make URL absolute if needed
        if pdf_link.startswith('/'):
            pdf_link = BASE_URL.rstrip('/') + pdf_link
        elif not pdf_link.startswith('http'):
            pdf_link = BASE_URL.rstrip('/') + '/' + pdf_link
        
        print(f"    ✓ Found PDF: {pdf_link[:60]}...")
        
        # Extract seven-meter data
        print(f"    Parsing PDF...")
        seven_meter_data = extract_seven_meters_from_pdf(pdf_link, BASE_URL, verify_ssl=True)
        print(f"    ✓ Extracted {len(seven_meter_data)} players with seven-meter data")
        return seven_meter_data
        
    except Exception as e:
        print(f"    ✗ Error finding/parsing PDF: {str(e)[:80]}")
        return {}

def main():
    driver = None
    try:
        print("\n[Setup] Initializing Chrome driver...")
        driver = setup_driver()
        print("    ✓ Chrome driver ready")
        
        # Get recent games
        games = get_recent_games(driver, days_back=14)
        if not games:
            print("\n✗ No games found")
            return
        
        # Test first game
        test_game = games[0]
        game_id = test_game.get('SpieleID')
        print(f"\n[TEST] Testing with game ID: {game_id}")
        print(f"    {test_game.get('Team1', 'Team1')} vs {test_game.get('Team2', 'Team2')}")
        print(f"    {test_game.get('Datum', 'Date unknown')}")
        
        # Extract players
        players = extract_players_from_aufstellung(driver, game_id)
        if not players:
            print("    ✗ No players found")
            return
        
        print(f"    Players before enrichment: {players[0]}")
        
        # Extract PDF and get seven-meter data
        seven_meter_data = find_and_extract_pdf(driver, game_id)
        
        if seven_meter_data:
            # Enrich players
            enriched_players = add_seven_meters_to_players(players, seven_meter_data)
            
            print(f"\n[4] Results:")
            print(f"    Players with seven-meter data:")
            count = 0
            for player in enriched_players:
                if player['seven_meters'] > 0:
                    print(f"      - {player['name']}: {player['seven_meters']} attempts, {player['seven_meters_goals']} goals")
                    count += 1
            
            if count == 0:
                print(f"      (No players with seven-meter data found)")
            
            print(f"\n✓ Integration test completed successfully!")
            return True
        else:
            print(f"\n⚠ No PDF seven-meter data extracted (game might not have detailed report)")
            return None
            
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test cancelled by user")
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
                print("\n[Cleanup] Chrome driver closed")
            except:
                pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
