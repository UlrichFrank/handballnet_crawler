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
    
    print("=== Analyzing game link structure ===\n")
    
    game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all.*aufstellung'))
    print(f"Found {len(game_links)} 'aufstellung' links (the actual game page links)\n")
    
    if game_links:
        print("=== Structure of first game ===\n")
        first_link = game_links[0]
        
        # Print the link itself
        print(f"Link: {first_link.get('href')}")
        print(f"Link text: {first_link.text}")
        
        # Find its nearest container that might have date and teams
        parent = first_link
        for i in range(10):  # Go up max 10 levels
            parent = parent.parent
            if parent is None:
                break
            
            classes = parent.get('class', [])
            text = parent.get_text(strip=True)[:100]
            print(f"\nLevel {i}: <{parent.name}> class={classes}")
            print(f"  Text preview: {text}")
            
            # Check if this level contains date/teams
            if 'Sa,' in parent.get_text() and 'vs' in parent.get_text().lower():
                print(f"  ✓ This container has date and teams!")
                
                # Find all children that might have data
                print(f"\n  Children of this container:")
                for child in parent.find_all(recursive=False):
                    child_text = child.get_text(strip=True)[:80]
                    print(f"    <{child.name}>: {child_text}")
                
                break
    
    # Try to extract game info from a specific game container
    print("\n\n=== Attempting to extract first game data ===\n")
    
    # Find all divs that contain game info
    all_divs = soup.find_all('div')
    
    for div in all_divs[:1000]:  # Check first 1000 divs
        text = div.get_text(strip=True)
        
        # Look for divs that have date + teams pattern
        has_date = re.search(r'[A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.', text)
        has_link = div.find('a', href=re.compile(r'/spiele/handball4all.*aufstellung'))
        
        if has_date and has_link:
            print(f"✓ Found container with date and game link!")
            print(f"\nFull text:\n{text[:500]}\n")
            
            # Try to extract structured data
            date_match = re.search(r'([A-Za-z]{2}),\s*(\d{1,2}\.\d{1,2}\.)', text)
            if date_match:
                print(f"Date: {date_match.group(0)}")
            
            # Get game link
            link = div.find('a', href=re.compile(r'/spiele/handball4all.*aufstellung'))
            if link:
                game_id = link.get('href').split('/')[-2]
                print(f"Game ID: {game_id}")
            
            # Look for team names - they might be in child elements
            print(f"\nChild elements in this div:")
            for child in div.find_all(recursive=False)[:5]:
                child_text = child.get_text(strip=True)[:100]
                print(f"  {child_text}")
            
            break

finally:
    driver.quit()
