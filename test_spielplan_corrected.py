#!/usr/bin/env python3
"""
Test script to access Spielplan page with corrected URL format.
Uses the /ligen/ path prefix instead of /mannschaften/
"""

import sys
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator

def test_spielplan_corrected():
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    base_url = config["authentication"]["base_url"]
    username = config["authentication"]["username"]
    password = config["authentication"]["password"]
    cert_path = config.get("ssl", {}).get("cert_path")
    verify_ssl = config.get("ssl", {}).get("verify_ssl", False)
    
    print("=" * 80)
    print("Testing Spielplan page with CORRECTED URL format (/ligen/)")
    print("=" * 80)
    
    # Authenticate
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    success = auth.login()
    
    if not success:
        print("ERROR: Authentication failed!")
        return
    
    print("✓ Authentication successful")
    
    # Get cookies
    cookies = auth.get_cookies()
    print(f"✓ Retrieved {len(cookies)} cookies")
    
    # Now test Spielplan page with CORRECTED format
    # Instead of: /mannschaften/handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv/spielplan
    # Use: /ligen/handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv/spielplan
    
    league_id = "handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv"
    date_from = "2025-07-01"
    date_to = "2026-06-30"
    
    # CORRECTED URL with /ligen/ prefix
    spielplan_url = f"{base_url}/ligen/{league_id}/spielplan?dateFrom={date_from}&dateTo={date_to}"
    
    print(f"\nNavigating to: {spielplan_url}")
    auth.driver.get(spielplan_url)
    
    # Wait for page to load
    time.sleep(3)
    
    # Check page title
    title = auth.driver.title
    print(f"Page title: {title}")
    
    # Save HTML for inspection
    html_content = auth.driver.page_source
    output_file = "spielplan_corrected_page.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Saved page HTML to: {output_file}")
    
    # Check if we got error page
    if "angeforderten Seite" in html_content or "nicht gefunden" in html_content:
        print("✗ Got 404 error - Page not found")
    else:
        print("✓ Page loaded successfully (no 404)")
    
    # Parse games using BeautifulSoup
    # Look for game links
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find game links - they typically have /spiele/ in the href
        game_links = soup.find_all('a', href=lambda x: x and '/spiele/' in x)
        print(f"\nFound {len(game_links)} potential game links")
        
        # Extract unique game IDs
        game_ids = set()
        for link in game_links[:10]:  # Show first 10
            href = link.get('href')
            if '/spiele/' in href:
                # Extract game ID from URL like /spiele/{game_id}/...
                parts = href.split('/')
                if 'spiele' in parts:
                    idx = parts.index('spiele')
                    if idx + 1 < len(parts):
                        game_id = parts[idx + 1]
                        game_ids.add(game_id)
                        print(f"  - Game: {game_id}")
        
        if game_ids:
            print(f"\n✓ Successfully extracted {len(game_ids)} unique game IDs")
        else:
            print("\n✗ No game IDs found")
        
    except Exception as e:
        print(f"Error parsing games: {e}")
    
    # Clean up
    auth.driver.quit()
    print("\n✓ Browser closed")

if __name__ == "__main__":
    test_spielplan_corrected()
