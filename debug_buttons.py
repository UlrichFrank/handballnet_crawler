#!/usr/bin/env python3
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
    
    # Check for all buttons with SVG
    buttons_with_svg = driver.find_elements(By.XPATH, "//button[.//svg]")
    print(f"Buttons with SVG: {len(buttons_with_svg)}\n")
    
    # Find buttons with polyline
    buttons_with_polyline = driver.find_elements(By.XPATH, "//button[.//svg//polyline]")
    print(f"Buttons with polyline: {len(buttons_with_polyline)}\n")
    
    for i, btn in enumerate(buttons_with_polyline):
        polylines = btn.find_elements(By.XPATH, ".//svg//polyline")
        for polyline in polylines:
            points = polyline.get_attribute('points')
            print(f"Button {i}: polyline points='{points}'")
    
    # Check page content for page info
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    body_text = soup.body.get_text()
    
    # Look for "Seite X von Y" or similar
    import re
    page_match = re.search(r'Seite \d+', body_text)
    if page_match:
        print(f"\nFound: {page_match.group()}")
    
    von_match = re.search(r'von \d+', body_text)
    if von_match:
        print(f"Found: {von_match.group()}")
    
    # Count game links
    game_links = len(soup.find_all('a', href=re.compile(r'/spiele/handball4all')))
    print(f"\nTotal game links on page: {game_links}")
    
finally:
    driver.quit()
