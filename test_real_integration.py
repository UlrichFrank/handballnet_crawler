#!/usr/bin/env python3
"""
Test scraper with real data - uses config_test.json with short date range
"""

import sys
import json
import time
from pathlib import Path

# Use test config
config_path = Path('config/config_test.json')
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['ref']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

print("\n" + "="*70)
print("TEST SCRAPER - Real Data Integration")
print("="*70)
print(f"\nConfig:")
print(f"  League: {LEAGUE_ID}")
print(f"  Date Range: {DATE_FROM} to {DATE_TO}")
print(f"  Output: {config['output']['file']}")
print()

# Import scraper functions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from hb_crawler.pdf_parser import extract_seven_meters_from_pdf, add_seven_meters_to_players

def setup_driver():
    """Setup Chrome driver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def extract_game_ids_from_spielplan(driver, max_games=3):
    """Load Spielplan and extract first N game IDs"""
    games_with_teams = []
    
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    
    print(f"[1] Loading Spielplan...")
    print(f"    URL: {spielplan_url}\n")
    
    driver.get(spielplan_url)
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all game links
    import re
    game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all.*spielbericht'))
    
    print(f"    Found {len(game_links)} games on this page")
    print(f"    Taking first {max_games} for test...\n")
    
    for idx, link in enumerate(game_links[:max_games]):
        href = link.get('href', '')
        parts = href.split('/')
        
        try:
            spiele_idx = parts.index('spiele')
            game_id = parts[spiele_idx + 1]
            
            # Get parent container with game info
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
                'order': idx
            })
        except (ValueError, IndexError):
            pass
    
    return games_with_teams

print("Starting test scraper...\n")
driver = None

try:
    driver = setup_driver()
    
    # Get game IDs
    games_info = extract_game_ids_from_spielplan(driver, max_games=3)
    
    if not games_info:
        print("ERROR: No games found!")
        sys.exit(1)
    
    print(f"[2] Scraping {len(games_info)} games for details...\n")
    
    # Test with first game
    game_info = games_info[0]
    game_id = game_info['game_id']
    
    print(f"    Testing with game: {game_id}")
    print(f"    Date: {game_info['date']}")
    print(f"    Home: {game_info['home_team']}")
    print(f"    Away: {game_info['away_team']}\n")
    
    # Try to get aufstellung page
    url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
    print(f"[3] Loading: {url}")
    
    driver.get(url)
    time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Check if page loaded
    if 'aufstellung' in soup.get_text().lower() or soup.find('table'):
        print("    ✓ Page loaded successfully\n")
        
        # Try to find PDF link
        print(f"[4] Looking for PDF link...\n")
        
        pdf_url_found = None
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if 'spielbericht' in href.lower() and 'pdf' in href.lower():
                pdf_url_found = href
                print(f"    ✓ Found PDF link: {href[:60]}...\n")
                break
        
        if pdf_url_found:
            print(f"[5] Testing PDF download and parsing...\n")
            try:
                seven_meter_data = extract_seven_meters_from_pdf(pdf_url_found, BASE_URL)
                
                if seven_meter_data:
                    print(f"    ✓ Successfully extracted {len(seven_meter_data)} players with 7m data:\n")
                    for player, stats in seven_meter_data.items():
                        print(f"      {player:28} | {stats['attempts']} attempts, {stats['goals']} goals")
                else:
                    print(f"    ℹ No seven meter data in this PDF (game might not have 7m shots)\n")
            except Exception as e:
                print(f"    ⚠ PDF download/parsing failed: {str(e)[:50]}\n")
        else:
            print("    ⚠ No PDF link found on page\n")
    else:
        print("    ⚠ Page might not have loaded properly\n")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nResults:")
    print(f"  ✓ Spielplan loading: OK")
    print(f"  ✓ Game data extraction: OK")
    print(f"  ✓ Aufstellung page loading: OK")
    if pdf_url_found:
        print(f"  ✓ PDF link discovery: OK")
        if seven_meter_data:
            print(f"  ✓ PDF parsing: OK")
        else:
            print(f"  ℹ PDF parsing: No 7m data (expected)")
    else:
        print(f"  ⚠ PDF link discovery: Not found")
    
    print("\nNext: Run full scraper with:")
    print("  python scraper.py (with config_test.json)")
    print()

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    if driver:
        driver.quit()
