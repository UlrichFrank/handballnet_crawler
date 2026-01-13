#!/usr/bin/env python3
import json
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

with open('config/config.json') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    driver.get(url)
    time.sleep(2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    print("HTML Structure Analysis:\n")
    
    # Find all elements with game links
    links = soup.find_all('a', href=lambda x: x and '/spiele/handball4all' in x if x else False)
    print(f"Game links: {len(links)}\n")
    
    if links:
        print("First 5 game link contexts:")
        for link in links[:5]:
            parent = link.find_parent(['div', 'tr', 'li'])
            if not parent:
                parent = link.find_parent()
            
            if parent:
                text = parent.get_text(strip=True)[:150]
                href = link.get('href', '')
                print(f"Text: {text}")
                print(f"Href: {href}\n")
    
finally:
    driver.quit()
