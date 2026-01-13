#!/usr/bin/env python3
"""
Extract game metadata (date, home/away teams) from Spielplan page
"""
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time

config_path = Path('config/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

def extract_game_metadata():
    """Extract game metadata from Spielplan"""
    
    print("📊 Extracting game metadata from Spielplan...")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
        driver.get(spielplan_url)
        time.sleep(3)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        games = {}  # {game_id: {date, home, away}}
        
        # Look for game rows/cards
        # The structure is usually: date - team1 vs team2 - result
        
        # Try to find all divs/rows with game info
        game_rows = soup.find_all(['div', 'tr'], class_=lambda x: x and ('game' in x.lower() or 'match' in x.lower() or 'row' in x.lower()) if x else False)
        
        print(f"Found {len(game_rows)} potential game rows")
        
        # Alternative: look for links to spiele pages with their context
        for link in soup.find_all('a', href=lambda x: x and '/spiele/handball4all' in x if x else False):
            href = link['href']
            
            # Extract game ID
            parts = href.split('/')
            try:
                spiele_idx = parts.index('spiele')
                if spiele_idx + 1 < len(parts):
                    game_id = parts[spiele_idx + 1]
                    if game_id.startswith('handball4all'):
                        # Get surrounding text for date and teams
                        parent = link.find_parent(['div', 'tr', 'td', 'p'], recursive=True)
                        if parent:
                            text = parent.get_text()
                            # Try to extract date
                            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', text)
                            date = date_match.group(1) if date_match else "Unknown"
                            
                            # Get team names from link text and parent
                            link_text = link.get_text(strip=True)
                            parent_text = parent.get_text(strip=True)
                            
                            games[game_id] = {
                                'date': date,
                                'home': 'Unknown',
                                'away': 'Unknown',
                                'text': parent_text[:100]
                            }
            except (ValueError, IndexError):
                pass
        
        print(f"Extracted {len(games)} games with metadata\n")
        
        # Save to file
        with open('game_metadata.json', 'w') as f:
            json.dump(games, f, indent=2)
        
        print(f"Metadata saved to game_metadata.json")
        
        # Show sample
        for gid, data in list(games.items())[:3]:
            print(f"  {gid}: {data['date']} - {data['text'][:60]}...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    extract_game_metadata()
