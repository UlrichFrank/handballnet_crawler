#!/usr/bin/env python3
"""
Debug script: Find available leagues for authenticated user
Navigate to mein-profil and inspect available resources
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
    
    print("="*80)
    print("DEBUG: FIND AVAILABLE LEAGUES")
    print("="*80)
    
    # Authenticate
    print("\n1. Authenticating...")
    auth = HandballNetSeleniumAuthenticator(base_url, username, password, cert_path, verify_ssl, headless=False)
    success = auth.login()
    
    if not success:
        print("✗ Authentication failed!")
        return
    
    print("✓ Authenticated\n")
    
    try:
        # Check current URL
        print(f"Current URL: {auth.driver.current_url}\n")
        
        # Parse mein-profil page
        print("2. Analyzing mein-profil page...")
        soup = BeautifulSoup(auth.driver.page_source, 'html.parser')
        
        # Look for league links
        links = soup.find_all('a', href=True)
        league_links = [l for l in links if 'mannschaften' in l.get('href', '')]
        
        print(f"   Found {len(league_links)} team/league links:\n")
        
        leagues = {}
        for link in league_links[:20]:
            href = link['href']
            text = link.get_text(strip=True)
            if href not in leagues and len(text) > 0:
                leagues[href] = text
                print(f"   {text:<50} → {href}")
        
        # Look for Spielplan references
        print(f"\n3. Looking for Spielplan pages...")
        spielplan_links = [l for l in links if 'spielplan' in l.get('href', '')]
        
        print(f"   Found {len(spielplan_links)} Spielplan links:\n")
        
        for link in spielplan_links[:10]:
            href = link['href']
            text = link.get_text(strip=True)[:50]
            print(f"   {text:<50} → {href}")
        
        # Try to navigate to Spielplansuche
        print(f"\n4. Navigating to Spielplansuche...")
        auth.driver.get(f"{base_url}/spielplansuche")
        time.sleep(2)
        
        print(f"   URL: {auth.driver.current_url}")
        
        # Save HTML for inspection
        html_file = Path(__file__).parent / "spielplansuche_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(auth.driver.page_source)
        print(f"   Saved HTML to: {html_file}")
        
    finally:
        print("\nCleaning up...")
        auth.driver.quit()
        print("✓ Done")


if __name__ == '__main__':
    main()
