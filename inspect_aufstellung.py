#!/usr/bin/env python3
"""
Inspect AUFSTELLUNG page structure
"""

import sys
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator


def main():
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    base_url = config["authentication"]["base_url"]
    username = config["authentication"]["username"]
    password = config["authentication"]["password"]
    cert_path = config.get("ssl", {}).get("cert_path")
    verify_ssl = config.get("ssl", {}).get("verify_ssl", False)
    
    print("Authenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    auth.login()
    
    # Test with first game
    game_id = "handball4all.baden-wuerttemberg.8668826"
    aufstellung_url = f"{base_url}/spiele/{game_id}/aufstellung"
    
    print(f"Navigating to: {aufstellung_url}")
    auth.driver.get(aufstellung_url)
    time.sleep(3)
    
    # Save HTML for inspection
    html = auth.driver.page_source
    with open("aufstellung_inspect.html", "w") as f:
        f.write(html)
    
    print(f"✓ Saved HTML to aufstellung_inspect.html")
    
    # Analyze structure
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\n--- Page Analysis ---")
    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
    
    # Look for tabs/buttons
    tabs = soup.find_all(['button', 'a', 'div'], 
        text=lambda x: x and any(t in x.upper() for t in ['HEIM', 'GAST', 'HOME', 'AWAY', 'AUFSTELLUNG']))
    
    print(f"\nFound {len(tabs)} potential tab elements:")
    for tab in tabs[:10]:
        print(f"  - Tag: {tab.name}, Text: {tab.get_text(strip=True)[:50]}")
    
    # Look for tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} tables")
    
    for idx, table in enumerate(tables[:2]):
        print(f"\nTable {idx+1}:")
        rows = table.find_all('tr')
        print(f"  - Rows: {len(rows)}")
        if rows:
            first_row = rows[0]
            cells = first_row.find_all(['th', 'td'])
            print(f"  - First row cells: {len(cells)}")
            for cell in cells[:5]:
                print(f"    - {cell.get_text(strip=True)[:40]}")
    
    # Look for divs with "spieler" (player)
    player_divs = soup.find_all(['div', 'span'], 
        class_=lambda x: x and 'spieler' in x.lower())
    print(f"\nFound {len(player_divs)} player-related divs/spans")
    
    # Look for any text that looks like player names
    print("\n--- Raw Text Search ---")
    all_text = soup.get_text()
    lines = [l.strip() for l in all_text.split('\n') if l.strip() and len(l.strip()) > 3]
    
    # Find lines that might be player names (usually title case)
    probable_players = []
    for line in lines:
        if any(c.isupper() for c in line) and not line.isupper() and len(line) < 50:
            # Check if it looks like a name
            if ' ' in line or any(c.isalpha() for c in line):
                probable_players.append(line)
    
    print(f"Probable player names ({len(probable_players)} total):")
    for p in probable_players[:20]:
        print(f"  - {p}")
    
    auth.driver.quit()


if __name__ == "__main__":
    main()
