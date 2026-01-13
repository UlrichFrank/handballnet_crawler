#!/usr/bin/env python3
"""
Simple test: Navigate to Spielplan after auth and save HTML
"""

import sys
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator


# Load configuration
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

base_url = config["authentication"]["base_url"]
username = config["authentication"]["username"]
password = config["authentication"]["password"]
cert_path = config.get("ssl", {}).get("cert_path")
verify_ssl = config.get("ssl", {}).get("verify_ssl", False)

league_id = config.get("league", {}).get("league_id", "baden-wuerttemberg.mc-ol-3-bw_bwhv")
date_from = config.get("league", {}).get("date_from", "2025-07-01")
date_to = config.get("league", {}).get("date_to", "2026-06-30")

print("="*80)
print("SIMPLE SPIELPLAN INSPECTION TEST")
print("="*80)

try:
    # Authenticate
    print("\n1. Authenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    success = auth.login()
    
    if not success:
        print("✗ Authentication failed!")
        sys.exit(1)
    
    print("✓ Authenticated\n")
    
    # Wait a bit for cookies to settle
    time.sleep(2)
    
    # Navigate to Spielplan
    print("2. Navigating to Spielplan...")
    url = (
        f"{base_url}/mannschaften/handball4all.{league_id}/spielplan"
        f"?dateFrom={date_from}&dateTo={date_to}"
    )
    print(f"   URL: {url}")
    
    auth.driver.get(url)
    time.sleep(3)
    
    print(f"   Current URL: {auth.driver.current_url}")
    
    # Save HTML
    html_content = auth.driver.page_source
    html_file = Path(__file__).parent / "spielplan_page.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ Saved HTML to: {html_file}")
    
    # Analyze HTML
    print("\n3. Analyzing HTML structure...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find tables
    tables = soup.find_all('table')
    print(f"   Found {len(tables)} tables")
    
    # Find all links with 'spiele' (games)
    game_links = [a for a in soup.find_all('a', href=True) if '/spiele/' in a['href']]
    print(f"   Found {len(game_links)} game links")
    
    if game_links:
        print(f"\n   First 10 game links:")
        for link in game_links[:10]:
            href = link['href']
            text = link.get_text(strip=True)[:50]
            print(f"     {text:<50} {href}")
    
    # Look for team links
    team_links = [a for a in soup.find_all('a', href=True) 
                  if '/mannschaften/' in a['href'] and 'handball4all' in a['href']]
    unique_teams = {}
    for link in team_links:
        href = link['href']
        text = link.get_text(strip=True)
        if text and href not in unique_teams:
            unique_teams[href] = text
    
    print(f"\n   Found {len(unique_teams)} unique teams")
    for href, text in list(unique_teams.items())[:10]:
        print(f"     {text:<50} {href[:60]}")
    
    print("\n✓ Done")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nCleaning up...")
    try:
        auth.driver.quit()
    except:
        pass
