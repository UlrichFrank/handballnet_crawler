#!/usr/bin/env python3
"""
Extract game schedule (Spielplan) with dates and team pairings
"""
import json
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Load config
config_path = Path('config/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

def extract_spielplan():
    """Extract game data from Spielplan page"""
    
    print("📋 Extrahiere Spielplan mit Daten...")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
        driver.get(url)
        time.sleep(3)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        games = {}  # {game_id: {date, home_team, away_team}}
        
        # Find all rows in tables - Spielplan is usually in a table
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                # First cell usually contains date
                date_cell = cells[0].get_text(strip=True)
                
                # Look for game link in this row
                link = row.find('a', href=lambda x: x and '/spiele/handball4all' in x if x else False)
                
                if link:
                    href = link.get('href', '')
                    # Extract game ID
                    parts = href.split('/')
                    try:
                        spiele_idx = parts.index('spiele')
                        if spiele_idx + 1 < len(parts):
                            game_id = parts[spiele_idx + 1]
                            if game_id.startswith('handball4all'):
                                # Get team names from row
                                row_text = row.get_text(strip=True)
                                
                                # Extract date from first cell (format like "Mi 13.11.2024")
                                date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', date_cell)
                                date = date_match.group(1) if date_match else "Unknown"
                                
                                # Try to find team names (usually "Team1 - Team2" or "Team1 : Team2")
                                # Look for pattern like "Team1 - Team2"
                                teams_match = re.search(r'([^-:]+)\s+[-:]\s+([^:\d]+?)(?:\d+|\s*$)', row_text)
                                home = "Unknown"
                                away = "Unknown"
                                
                                if teams_match:
                                    home = teams_match.group(1).strip()
                                    away = teams_match.group(2).strip()
                                
                                games[game_id] = {
                                    'date': date,
                                    'home': home,
                                    'away': away,
                                    'vs': f"{home} - {away}"
                                }
                    except (ValueError, IndexError):
                        pass
        
        print(f"\n✓ Extracted {len(games)} games from Spielplan")
        
        # Save to JSON
        with open('spielplan_data.json', 'w') as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
        
        print(f"Saved to spielplan_data.json\n")
        
        # Show samples
        print("Sample games:")
        for gid, data in list(games.items())[:5]:
            print(f"  {data['date']} | {data['vs']}")
            print(f"    ID: {gid}\n")
        
        return games
        
    finally:
        driver.quit()

if __name__ == '__main__':
    extract_spielplan()
