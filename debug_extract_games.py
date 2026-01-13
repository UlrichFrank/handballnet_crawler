#!/usr/bin/env python3
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load config
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    print(f"Loading: {spielplan_url}\n")
    
    driver.get(spielplan_url)
    time.sleep(3)
    
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    
    print("=== Extracting games from page ===\n")
    
    # Find all game links (to spielbericht)
    game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all.*spielbericht'))
    print(f"Found {len(game_links)} game links\n")
    
    # Extract unique game IDs
    game_ids = set()
    games_data = []
    
    for link in game_links:
        href = link.get('href', '')
        parts = href.split('/')
        try:
            # Format: /spiele/handball4all.xxx.yyyy/spielbericht
            if 'spiele' in parts and len(parts) > parts.index('spiele') + 1:
                spiele_idx = parts.index('spiele')
                game_id = parts[spiele_idx + 1]
                if game_id not in game_ids:
                    game_ids.add(game_id)
                    # Find the parent container that has all game info
                    parent = link.parent
                    for _ in range(15):
                        if parent is None:
                            break
                        parent_text = parent.get_text(strip=True)
                        # Check if this level has date and team names
                        if re.search(r'[A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.', parent_text):
                            # This is likely the game container
                            games_data.append({
                                'game_id': game_id,
                                'raw_text': parent_text[:500],
                                'href': href
                            })
                            break
                        parent = parent.parent
        except (ValueError, IndexError):
            pass
    
    print(f"Extracted {len(games_data)} unique games\n")
    
    print("=== Sample games ===\n")
    for game in games_data[:3]:
        print(f"Game ID: {game['game_id']}")
        print(f"Text: {game['raw_text']}\n")
    
    # Count how many games we found
    print(f"\nTotal unique games: {len(game_ids)}")
    
finally:
    driver.quit()
