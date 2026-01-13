#!/usr/bin/env python3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import json

config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver = setup_driver()
try:
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    print(f"Loading: {spielplan_url}\n")
    
    driver.get(spielplan_url)
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for table
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables\n")
    
    if tables:
        table = tables[0]
        rows = table.find_all('tr')
        print(f"First table has {len(rows)} rows\n")
        
        print("First 5 rows:")
        for i, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            print(f"\nRow {i}: {len(cells)} cells")
            for j, cell in enumerate(cells[:4]):
                text = cell.get_text(strip=True)
                print(f"  Cell[{j}]: {text[:50]}")
    
    # Look for pagination info
    print("\n" + "=" * 60)
    print("Looking for pagination info:")
    text = soup.get_text()
    
    # Search for numbers that might indicate total games
    import re
    numbers = re.findall(r'\d+', text)
    print(f"Numbers found in page: {numbers[:20]}")
    
    # Look for next button
    next_buttons = soup.find_all('a', text=re.compile(r'^[>»]$'))
    print(f"\nNext buttons found: {len(next_buttons)}")
    for btn in next_buttons:
        print(f"  {btn.get('href', 'no href')}")

finally:
    driver.quit()
