#!/usr/bin/env python3
import json
import time
from pathlib import Path
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
    
    print("=== Checking for pagination buttons ===\n")
    
    # Find all buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"Total buttons on page: {len(buttons)}\n")
    
    for i, btn in enumerate(buttons):
        text = btn.text.strip()
        enabled = not btn.get_attribute('disabled')
        aria = btn.get_attribute('aria-label')
        print(f"Button {i}: text='{text}' enabled={enabled} aria='{aria}'")
    
    # Specifically look for next/previous buttons
    print("\n=== Looking for navigation buttons ===\n")
    
    next_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '>')]")
    print(f"Found {len(next_buttons)} buttons with '>'")
    
    prev_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '<')]")
    print(f"Found {len(prev_buttons)} buttons with '<'")
    
    # Check page info
    print("\n=== Page text content (first 1000 chars) ===\n")
    body = driver.find_element(By.TAG_NAME, "body")
    text = body.text
    print(text[:1000])
    
finally:
    driver.quit()
