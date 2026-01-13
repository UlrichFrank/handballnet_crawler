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
    
    print("=== Looking for game data patterns ===\n")
    
    # Look for all links that might be game links
    game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all'))
    print(f"Found {len(game_links)} game links")
    
    if game_links:
        print("\nFirst 5 game links:")
        for link in game_links[:5]:
            print(f"  {link.get('href')}")
            print(f"  Parent: {link.parent.name}")
            print(f"  Text: {link.text[:50]}")
            print()
    
    # Try to find data in script tags (often contains JSON)
    print("=== Looking for JSON data in script tags ===\n")
    scripts = soup.find_all('script', type='application/json')
    print(f"Found {len(scripts)} JSON script tags")
    
    if scripts:
        for i, script in enumerate(scripts[:2]):
            try:
                data = json.loads(script.string)
                print(f"Script {i}: Keys = {list(data.keys())[:5]}")
                # Look for games in the data
                if isinstance(data, dict):
                    for key in data:
                        if 'game' in key.lower() or 'spiel' in key.lower():
                            print(f"  Found '{key}' key")
            except:
                pass
    
    # Look for divs with class names that might indicate games
    print("\n=== Looking for divs with game-like classes ===\n")
    
    divs_with_game_text = []
    for div in soup.find_all('div', class_=re.compile(r'game|spiel|match|row', re.I)):
        text = div.get_text(strip=True)
        if 'vs' in text.lower() or 'gegen' in text.lower() or re.search(r'\d+:\d+', text):
            divs_with_game_text.append((div.get('class'), text[:80]))
    
    print(f"Found {len(divs_with_game_text)} divs with game-like text")
    if divs_with_game_text:
        for cls, txt in divs_with_game_text[:5]:
            print(f"  Classes: {cls}")
            print(f"  Text: {txt}\n")
    
    # Look for specific data attributes
    print("\n=== Looking for data attributes ===\n")
    
    elements_with_data = soup.find_all(attrs={'data-game-id': True})
    print(f"Found {len(elements_with_data)} elements with data-game-id")
    
    elements_with_data2 = soup.find_all(attrs={'data-gameid': True})
    print(f"Found {len(elements_with_data2)} elements with data-gameid")
    
    # Check raw text for dates in the expected format
    print("\n=== Looking for date patterns ===\n")
    
    body_text = soup.body.get_text()
    date_pattern = r'[A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.'
    dates = re.findall(date_pattern, body_text)
    print(f"Found {len(dates)} date patterns like 'Sa, 20.09.'")
    if dates:
        print(f"Sample dates: {dates[:10]}")
    
finally:
    driver.quit()
