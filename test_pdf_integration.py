#!/usr/bin/env python3
"""Test PDF integration with actual scraper - limited to first 2 games"""
import json
import os
import sys
import time
from pathlib import Path

# Add module to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper import scrape_all_games, setup_driver, get_games_info, BASE_URL, LEAGUE_ID, DATE_FROM, DATE_TO

print("=" * 70)
print("PDF INTEGRATION TEST - Scraper with PDF Extraction")
print("=" * 70)
print(f"League: {LEAGUE_ID}")
print(f"Date Range: {DATE_FROM} to {DATE_TO}")
print()

try:
    print("[1] Setting up Chrome driver...")
    driver = setup_driver()
    print("✓ Chrome driver ready\n")
    
    print("[2] Fetching game information from handball.net...")
    games_info = get_games_info(driver)
    print(f"✓ Found {len(games_info)} games\n")
    
    if not games_info:
        print("✗ No games found - check date range or league ID")
        driver.quit()
        sys.exit(1)
    
    # Limit to first 2 games for testing
    test_games = games_info[:2]
    print(f"[3] Testing with first {len(test_games)} games only")
    print(f"     Games to test: {[g['game_id'] for g in test_games]}\n")
    
    print("[4] Starting scraper with PDF extraction...")
    games = scrape_all_games(driver, test_games)
    
    print(f"\n✓ Scraping complete!")
    print(f"  Games scraped: {len(games)}")
    
    # Check for 7m data
    games_with_7m = 0
    players_with_7m = 0
    
    for game in games:
        has_7m = False
        for player in game.get('players', []):
            if player.get('seven_meters', 0) > 0 or player.get('seven_meters_goals', 0) > 0:
                print(f"\n  7m found: {player['name']} - "
                      f"{player['seven_meters']} attempts, {player['seven_meters_goals']} goals")
                players_with_7m += 1
                has_7m = True
        if has_7m:
            games_with_7m += 1
    
    print(f"\n" + "=" * 70)
    print(f"PDF INTEGRATION RESULTS")
    print("=" * 70)
    print(f"Games with 7m data: {games_with_7m}/{len(games)}")
    print(f"Players with 7m data: {players_with_7m}")
    
    if games_with_7m > 0:
        print("\n✓ PDF EXTRACTION WORKING - 7m data found!")
    else:
        print("\n⚠ No 7m data found (check if PDFs were downloaded)")
    
    # Save test output
    output_file = Path(__file__).parent / "output" / "test_pdf_integration.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Test output saved: {output_file}")
    
    driver.quit()

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
