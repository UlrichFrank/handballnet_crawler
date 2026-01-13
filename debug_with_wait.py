#!/usr/bin/env python3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    # Wait for table to load
    wait = WebDriverWait(driver, 10)
    print("Waiting for table to load...")
    table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    print("✅ Table loaded!\n")
    
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for table
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables\n")
    
    if tables:
        table = tables[0]
        rows = table.find_all('tr')
        print(f"First table has {len(rows)} rows\n")
        
        print("First 3 rows:")
        for i, row in enumerate(rows[:3]):
            cells = row.find_all(['td', 'th'])
            print(f"\nRow {i}: {len(cells)} cells")
            for j, cell in enumerate(cells[:5]):
                text = cell.get_text(strip=True)
                print(f"  Cell[{j}]: {text[:40]}")

finally:
    driver.quit()
