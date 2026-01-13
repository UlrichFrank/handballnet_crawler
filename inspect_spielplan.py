#!/usr/bin/env python3
"""
Test script to inspect the league Spielplan page structure
"""

import sys
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator


def inspect_league_page():
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
    print("INSPECT LEAGUE SPIELPLAN PAGE STRUCTURE")
    print("="*80)
    
    # Authenticate
    print(f"\nAuthenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    auth.login()
    print("✓ Authenticated\n")
    
    try:
        # Navigate to league Spielplan
        url = (
            f"{base_url}/mannschaften/handball4all.{league_id}/spielplan"
            f"?dateFrom={date_from}&dateTo={date_to}"
        )
        print(f"Loading: {url}")
        
        # Set proper timeouts
        auth.driver.set_page_load_timeout(30)
        auth.driver.implicitly_wait(10)
        
        auth.driver.get(url)
        
        # Wait for page to load
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        try:
            WebDriverWait(auth.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
            )
            print("✓ Page loaded with tables")
        except Exception as e:
            print(f"⚠ Timeout waiting for tables: {e}")
        
        time.sleep(2)
        
        # Parse HTML
        soup = BeautifulSoup(auth.driver.page_source, 'html.parser')
        
        # Save HTML for inspection
        html_file = Path(__file__).parent / "spielplan_page.html"
        with open(html_file, 'w') as f:
            f.write(soup.prettify())
        print(f"✓ Saved HTML to: {html_file}\n")
        
        # Analyze structure
        print("PAGE STRUCTURE ANALYSIS:")
        print("-" * 80)
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")
        
        for i, table in enumerate(tables[:3], 1):  # Inspect first 3 tables
            print(f"\n[Table {i}]")
            
            # Get headers
            headers = table.find_all('th')
            if headers:
                header_texts = [h.get_text(strip=True)[:30] for h in headers]
                print(f"  Headers ({len(header_texts)}): {header_texts}")
            
            # Get first few rows
            rows = table.find_all('tr')
            print(f"  Rows: {len(rows)}")
            
            if rows:
                for j, row in enumerate(rows[:2], 1):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True)[:40] for cell in cells]
                    print(f"    Row {j}: {cell_texts[:5]}")  # First 5 cells
        
        # Find any game links
        print("\n\nLOOKING FOR GAME LINKS:")
        print("-" * 80)
        
        links = soup.find_all('a', href=True)
        game_links = [l for l in links if '/spiele/' in l.get('href', '')]
        print(f"Found {len(game_links)} game links")
        
        if game_links:
            print("\nFirst 10 game links:")
            for link in game_links[:10]:
                href = link.get('href')
                text = link.get_text(strip=True)[:40]
                print(f"  {text:<40} → {href}")
        
        # Look for team names
        print("\n\nLOOKING FOR TEAM NAMES:")
        print("-" * 80)
        
        team_links = [l for l in links if '/mannschaften/' in l.get('href', '') and 'handball4all' in l.get('href', '')]
        unique_teams = {}
        for link in team_links[:20]:
            href = link.get('href')
            text = link.get_text(strip=True)
            if text and href not in unique_teams:
                unique_teams[href] = text
        
        print(f"Found {len(unique_teams)} unique team links")
        for href, text in list(unique_teams.items())[:10]:
            print(f"  {text:<40} → {href[:60]}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n✗ Error during inspection: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nClosing driver...")
        try:
            auth.driver.quit()
        except:
            pass
        print("✓ Done")


if __name__ == '__main__':
    inspect_league_page()
