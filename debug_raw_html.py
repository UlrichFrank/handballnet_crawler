#!/usr/bin/env python3
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    print("=== Initial page load (after 2 seconds) ===")
    time.sleep(2)
    
    # Check what's visible
    body = driver.find_element(By.TAG_NAME, "body")
    print(f"Body text length: {len(body.text)}")
    print(f"Body text preview:\n{body.text[:500]}\n")
    
    # Check for table
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Tables found: {len(tables)}\n")
    
    # Check for divs with content
    divs = driver.find_elements(By.TAG_NAME, "div")
    print(f"Total divs: {len(divs)}")
    
    # Look for specific classes/ids that might contain the table
    print("\n=== Looking for specific containers ===")
    main_content = driver.find_elements(By.CSS_SELECTOR, "[id*='content'], [class*='content'], [role='main']")
    print(f"Found {len(main_content)} potential content areas")
    
    # Try waiting for various elements
    print("\n=== Trying WebDriverWait with different conditions ===")
    
    try:
        elem = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        print("✓ Table appeared within 3 seconds")
    except:
        print("✗ Table did NOT appear within 3 seconds")
    
    try:
        elem = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr"))
        )
        print(f"✓ Found {len(elem)} <tr> elements")
    except:
        print("✗ No <tr> elements found")
    
    # Check page source for raw HTML
    print("\n=== Checking raw HTML source ===")
    source = driver.page_source
    print(f"Page source length: {len(source)}")
    print(f"Contains '<table>': {'<table' in source}")
    print(f"Contains 'Spielplan': {'Spielplan' in source}")
    print(f"Contains 'Sa,': {'Sa,' in source}")
    
    # Sample HTML
    if '<table' in source:
        start = source.find('<table')
        end = source.find('</table>', start) + 8
        print(f"\nTable HTML sample:\n{source[start:start+500]}\n")
    
finally:
    driver.quit()
