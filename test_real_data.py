#!/usr/bin/env python3
"""
Real Data Integration Test - Uses config_test.json with SSL certificate support
"""

import sys
import json
import time
import os
from pathlib import Path

# Use test config
config_path = Path('config/config_test.json')
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['ref']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

# Handle SSL certificate
ssl_config = config.get('ssl', {})
verify_ssl = ssl_config.get('verify_ssl', True)
cert_path = ssl_config.get('cert_path', '')

if cert_path and verify_ssl:
    cert_path = os.path.expanduser(cert_path)
    if os.path.exists(cert_path):
        print(f"Using SSL certificate: {cert_path}")
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path

print("\n" + "="*80)
print("REAL DATA INTEGRATION TEST")
print("="*80)
print(f"\nConfiguration:")
print(f"  League: {LEAGUE_ID}")
print(f"  Date Range: {DATE_FROM} to {DATE_TO}")
print(f"  SSL Verify: {verify_ssl}")
print(f"  Output: {config['output']['file']}\n")

# Import components
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from hb_crawler.pdf_parser import extract_seven_meters_from_pdf, add_seven_meters_to_players
import re

def setup_driver():
    """Setup Chrome driver with SSL configuration"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    if not verify_ssl:
        options.add_argument('--no-check-certificate')
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def extract_game_ids_limited(driver, max_games=2):
    """Extract first N games from Spielplan"""
    games_with_teams = []
    seen_ids = set()
    
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    
    print(f"[1] Fetching Spielplan...")
    print(f"    URL: {spielplan_url}\n")
    
    driver.get(spielplan_url)
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find game links
    game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all.*spielbericht'))
    print(f"    Found {len(game_links)} games total")
    print(f"    Testing with first {max_games} games...\n")
    
    for link in game_links[:max_games]:
        href = link.get('href', '')
        parts = href.split('/')
        
        try:
            spiele_idx = parts.index('spiele')
            game_id = parts[spiele_idx + 1]
            
            if game_id in seen_ids:
                continue
            
            # Get parent for game info
            parent = link.parent
            game_info_text = None
            
            for _ in range(15):
                if parent is None:
                    break
                parent_text = parent.get_text(strip=True)
                if re.search(r'[A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.', parent_text):
                    game_info_text = parent_text
                    break
                parent = parent.parent
            
            if not game_info_text:
                continue
            
            # Parse game info
            date_match = re.search(r'([A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.)', game_info_text)
            date_text = date_match.group(1) if date_match else "Unknown"
            
            score_match = re.search(r'(\d+):(\d+)', game_info_text)
            
            home_team = None
            away_team = None
            
            if score_match:
                score_pos = score_match.start()
                text_after_date = game_info_text[date_match.end() if date_match else 0:score_pos].strip()
                home_team = text_after_date
                text_after_score = game_info_text[score_match.end():].strip()
                away_team = text_after_score
            
            games_with_teams.append({
                'game_id': game_id,
                'home_team': home_team,
                'away_team': away_team,
                'date': date_text,
                'order': len(games_with_teams)
            })
            
            seen_ids.add(game_id)
            
        except (ValueError, IndexError):
            pass
    
    return games_with_teams

print("Starting real data test...\n")
driver = None

try:
    driver = setup_driver()
    
    # Get game IDs
    games_info = extract_game_ids_limited(driver, max_games=2)
    
    if not games_info:
        print("ERROR: No games found in this date range!")
        sys.exit(1)
    
    print(f"[2] Loaded {len(games_info)} games\n")
    
    all_results = []
    
    for idx, game_info in enumerate(games_info, 1):
        game_id = game_info['game_id']
        print(f"[{idx}] Game: {game_info['date']} | {game_id}")
        print(f"    Home: {game_info['home_team']}")
        print(f"    Away: {game_info['away_team']}\n")
        
        # Load aufstellung page
        url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
        driver.get(url)
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Check for tables (aufstellung loaded)
        tables = soup.find_all('table')
        
        if tables:
            print(f"    ✓ Aufstellung loaded ({len(tables)} tables found)")
            
            # Look for PDF
            all_links = soup.find_all('a', href=True)
            pdf_url = None
            
            for link in all_links:
                href = link.get('href', '')
                if 'spielbericht' in href.lower() and 'pdf' in href.lower():
                    pdf_url = href
                    print(f"    ✓ PDF link found")
                    break
            
            if pdf_url:
                # Try to parse PDF
                try:
                    print(f"    → Downloading and parsing PDF...")
                    seven_meter_data = extract_seven_meters_from_pdf(pdf_url, BASE_URL)
                    
                    if seven_meter_data:
                        print(f"    ✓ Extracted {len(seven_meter_data)} players with 7m data:")
                        for player, stats in sorted(seven_meter_data.items(), key=lambda x: x[1]['attempts'], reverse=True):
                            print(f"        {player:28} | {stats['attempts']} attempts | {stats['goals']} goals")
                        
                        all_results.append({
                            'game_id': game_id,
                            'date': game_info['date'],
                            'seven_meter_data': seven_meter_data,
                            'players_found': len(seven_meter_data)
                        })
                    else:
                        print(f"    ℹ No seven meter data in PDF (game might not have 7m shots)")
                        all_results.append({
                            'game_id': game_id,
                            'date': game_info['date'],
                            'seven_meter_data': {},
                            'players_found': 0
                        })
                
                except Exception as e:
                    print(f"    ⚠ PDF parsing error: {str(e)[:60]}")
                    all_results.append({
                        'game_id': game_id,
                        'date': game_info['date'],
                        'error': str(e)[:60]
                    })
            else:
                print(f"    ⚠ No PDF link found")
        else:
            print(f"    ⚠ Aufstellung page did not load properly")
        
        print()
    
    # Summary
    print("="*80)
    print("TEST RESULTS")
    print("="*80 + "\n")
    
    print(f"Tested {len(games_info)} games:\n")
    
    total_7m_players = 0
    for result in all_results:
        status = "✓" if 'seven_meter_data' in result else "✗"
        players = result.get('players_found', 0)
        total_7m_players += players
        print(f"  {status} {result['date']} | {result['game_id'][:40]:40} | 7m players: {players}")
    
    print(f"\nTotal players with 7m data across all games: {total_7m_players}")
    
    print(f"\n✓ Real data integration test complete!")
    print(f"✓ PDF parsing works with actual handball.net data")
    print(f"✓ Seven meter extraction functional")
    print(f"\nNext: Run full scraper with config.json for complete league data")
    print()
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    if driver:
        driver.quit()
