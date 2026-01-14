#!/usr/bin/env python3
"""
HANDBALL GAMES SCRAPER - CLEAN & SIMPLE
Extract all games with complete player statistics directly to game-centric JSON
"""

import time
import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings('ignore')

from hb_crawler.pdf_parser import extract_seven_meters_from_pdf, add_seven_meters_to_players

# Load config
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['ref']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
DATE_FROM = config['league']['date_from']
DATE_TO = config['league']['date_to']

# Handle SSL configuration - use certificate if provided
ssl_config = config.get('ssl', {})
cert_path = ssl_config.get('cert_path', '')
verify_ssl = True  # Always verify SSL with certificate

# Store cert_path for later (after ChromeDriver download)
resolved_cert_path = None
if cert_path:
    cert_path = os.path.expanduser(cert_path)
    if os.path.exists(cert_path):
        resolved_cert_path = cert_path
        # Disable requests warnings about SSL
        import requests
        requests.packages.urllib3.disable_warnings()
        # Try to apply certificate to urllib3 at module level
        import urllib3
        urllib3.disable_warnings()
    else:
        print(f"[WARNING] Certificate file not found: {cert_path}")

# Ensure webdriver-manager can download without cert issues
# We'll apply the certificate AFTER ChromeDriver is initialized
os.environ.pop('REQUESTS_CA_BUNDLE', None)
os.environ.pop('CURL_CA_BUNDLE', None)
os.environ['WDM_SSL_VERIFY'] = '0'

print("=" * 70)
print("HANDBALL GAMES SCRAPER - Game-Centric Format")
print("=" * 70)
print(f"League: {LEAGUE_ID}")
print(f"Date Range: {DATE_FROM} to {DATE_TO}")
print()

def setup_driver():
    """Setup Chrome driver with SSL certificate support"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Use certificate if available
    if resolved_cert_path:
        options.add_argument(f'--ssl-version=TLSv1.2')
        print(f"[SSL] Using certificate: {resolved_cert_path}")
    
    # Strategy 1: Try system Chrome first (most reliable on macOS)
    try:
        print("[Chrome] Trying system Chrome first...")
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            options.binary_location = chrome_path
            driver = webdriver.Chrome(options=options)
            print(f"✓ Using system Chrome: {chrome_path}")
            
            # Apply SSL certificate for system Chrome
            if resolved_cert_path:
                os.environ['REQUESTS_CA_BUNDLE'] = resolved_cert_path
                os.environ['CURL_CA_BUNDLE'] = resolved_cert_path
            
            return driver
    except Exception as e:
        print(f"[Chrome] System Chrome failed: {str(e)[:100]}")
        print("[Chrome] Falling back to webdriver-manager...\n")
    
    # Strategy 2: Try webdriver-manager with retry logic
    os.environ['WDM_LOG'] = '0'  # Disable verbose logging
    os.environ['WDM_TIMEOUT'] = '15'  # Set timeout
    # IMPORTANT: Keep SSL verification disabled for webdriver-manager download
    os.environ['WDM_SSL_VERIFY'] = '0'
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Chrome] Initializing ChromeDriver via webdriver-manager (attempt {attempt}/{max_retries})...")
            driver_path = ChromeDriverManager().install()
            print(f"[Chrome] Using ChromeDriver: {driver_path}")
            
            driver = webdriver.Chrome(
                service=Service(driver_path),
                options=options
            )
            print(f"✓ ChromeDriver initialized successfully")
            
            # Now that we have the driver, apply SSL certificate for subsequent requests
            if resolved_cert_path:
                os.environ['REQUESTS_CA_BUNDLE'] = resolved_cert_path
                os.environ['CURL_CA_BUNDLE'] = resolved_cert_path
            
            return driver
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"[Chrome] Attempt {attempt} failed: {error_msg}")
            if attempt < max_retries:
                print(f"[Chrome] Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"\n[ERROR] All Chrome initialization attempts failed!")
                raise

def extract_game_ids_from_spielplan(driver):
    """Load Spielplan with pagination (page=1, page=2, etc) and extract all game IDs with teams, dates, and order"""
    games_with_teams = []
    seen_ids = set()
    order = 0
    
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    page = 1
    total_games = None
    
    while True:
        print(f"📄 Loading Spielplan page {page}...")
        
        url = f"{spielplan_url}&page={page}"
        driver.get(url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract total games count on first page
        if total_games is None:
            game_count_div = soup.find('div', class_='text-sm', string=re.compile(r'Spiele gefunden'))
            if game_count_div:
                match = re.search(r'(\d+)\s*Spiele gefunden', game_count_div.get_text())
                if match:
                    total_games = int(match.group(1))
                    print(f"   ℹ️  Total games: {total_games}")
        
        page_games = []
        
        # Find all game links from spielbericht
        game_links = soup.find_all('a', href=re.compile(r'/spiele/handball4all.*spielbericht'))
        
        for link in game_links:
            href = link.get('href', '')
            parts = href.split('/')
            
            try:
                spiele_idx = parts.index('spiele')
                game_id = parts[spiele_idx + 1]
                
                if game_id not in seen_ids:
                    # Find parent container with game info
                    parent = link.parent
                    game_info_text = None
                    
                    for _ in range(15):
                        if parent is None:
                            break
                        parent_text = parent.get_text(strip=True)
                        # Check if this level has date
                        if re.search(r'[A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.', parent_text):
                            game_info_text = parent_text
                            break
                        parent = parent.parent
                    
                    if not game_info_text:
                        continue
                    
                    # Parse the game info text
                    date_match = re.search(r'([A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.)', game_info_text)
                    date_text = date_match.group(1) if date_match else "Unknown"
                    
                    # Extract score pattern to identify team split
                    score_match = re.search(r'(\d+):(\d+)', game_info_text)
                    
                    home_team = None
                    away_team = None
                    
                    if score_match:
                        score_pos = score_match.start()
                        # Everything between date and score is likely home team
                        text_after_date = game_info_text[date_match.end() if date_match else 0:score_pos].strip()
                        home_team = text_after_date
                        
                        # Everything after score is likely away team
                        text_after_score = game_info_text[score_match.end():].strip()
                        away_team = text_after_score
                    
                    page_games.append({
                        'game_id': game_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': date_text,
                        'order': order
                    })
                    seen_ids.add(game_id)
                    games_with_teams.append({
                        'game_id': game_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': date_text,
                        'order': order
                    })
                    order += 1
            except (ValueError, IndexError):
                pass
        
        print(f"  ✓ Found {len(page_games)} new games on page {page} (total: {len(games_with_teams)})")
        
        if len(page_games) == 0:
            print(f"  ℹ️  No games found on this page, stopping")
            break
        
        # Check if we should continue to next page
        # If we have total_games count, check if we've reached it
        if total_games and len(games_with_teams) >= total_games:
            print(f"  ✓ Reached total game count ({total_games})")
            break
        
        page += 1
        if page > 20:  # Safety limit
            print(f"  ⚠️  Reached page limit (20), stopping")
            break
    
    return games_with_teams

def extract_players_from_aufstellung(html):
    """Extract players from AUFSTELLUNG page - match tables to team names"""
    soup = BeautifulSoup(html, 'html.parser')
    players_by_team = {}
    
    # Find all h3 headings and their following tables
    h3_list = soup.find_all('h3')
    
    # Filter to get valid team names (skip navigation items and consecutive duplicates)
    team_h3_pairs = []  # List of (h3_element, team_name)
    prev_name = None
    
    for h3 in h3_list:
        name = h3.get_text(strip=True)
        # Filter out navigation/section headings and consecutive duplicates
        if (name and 
            name not in ['Fan-Services', 'Vereinsservices', 'News', 'Ligen, Vereine & Verbände', 'mein.handball.net', 'Kontakt'] and
            name != prev_name):  # Skip if same as previous h3
            team_h3_pairs.append((h3, name))
            prev_name = name
        elif name and name not in ['Fan-Services', 'Vereinsservices', 'News', 'Ligen, Vereine & Verbände', 'mein.handball.net', 'Kontakt']:
            prev_name = name
    
    # We need exactly 2 teams
    if len(team_h3_pairs) < 2:
        return players_by_team
    
    # For each team h3, find the table that follows it
    team_table_pairs = []
    for h3_elem, team_name in team_h3_pairs[:2]:  # Only process first 2 teams
        # Find the next table after this h3
        next_table = h3_elem.find_next('table')
        if next_table:
            team_table_pairs.append((team_name, next_table))
    
    # If we still don't have 2 team-table pairs, fall back to simple index matching
    if len(team_table_pairs) < 2:
        tables = soup.find_all('table')
        if len(tables) < 2:
            return players_by_team
        
        team_names = [name for _, name in team_h3_pairs[:2]]
        for table_idx, table in enumerate(tables[:2]):
            if table_idx < len(team_names):
                team_table_pairs.append((team_names[table_idx], table))
    
    # Now extract players from each table
    for team_name, table in team_table_pairs:
        tbody = table.find('tbody')
        if not tbody:
            rows = table.find_all('tr')
        else:
            rows = tbody.find_all('tr')
        
        if not rows:
            continue
        
        players = []
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                name_cell = cells[1] if len(cells) > 1 else cells[0]
                name = name_cell.get_text(strip=True)
                
                if not name or name in ['Name', 'GESAMT', 'Spieler', '']:
                    continue
                
                # Extract stats
                goals = 0
                two_min_penalties = 0
                yellow_cards = 0
                red_cards = 0
                blue_cards = 0
                
                try:
                    if len(cells) > 2:
                        val = cells[2].get_text(strip=True)
                        goals = int(val) if val and val.isdigit() else 0
                except:
                    pass
                
                try:
                    if len(cells) > 3:
                        val = cells[3].get_text(strip=True)
                        two_min_penalties = int(val) if val and val.isdigit() else 0
                except:
                    pass
                
                if len(cells) > 4:
                    card_cell = cells[4]
                    yellow_cards = len(card_cell.find_all('img', src=re.compile('yellow', re.I)))
                    red_cards = len(card_cell.find_all('img', src=re.compile('red', re.I)))
                    blue_cards = len(card_cell.find_all('img', src=re.compile('blue', re.I)))
                
                player = {
                    'name': name,
                    'goals': goals,
                    'two_min_penalties': two_min_penalties,
                    'yellow_cards': yellow_cards,
                    'red_cards': red_cards,
                    'blue_cards': blue_cards,
                    'seven_meters': 0,
                    'seven_meters_goals': 0
                }
                players.append(player)
        
        if players:
            players_by_team[team_name] = players
    
    return players_by_team

def extract_game_date(html):
    """Extract game date from page - format: Sa, 20.09."""
    soup = BeautifulSoup(html, 'html.parser')
    date_text = soup.get_text()
    
    # Match pattern: "Sa, 20.09." (Weekday abbreviation, comma, day.month.)
    match = re.search(r'([A-Za-z]{2}),\s*(\d{1,2}\.\d{1,2}\.)', date_text)
    if match:
        return f"{match.group(1)}, {match.group(2)}"
    
    # Fallback: try just day.month pattern
    match = re.search(r'(\d{1,2}\.\d{1,2}\.)', date_text)
    if match:
        return match.group(1)
    
    return "Unknown"

def extract_spielbericht_pdf_url(driver, game_id):
    """
    Extract the Spielbericht PDF download link from the game's SPIELINFO page.
    
    Navigates to /spiele/{game_id}/info (SPIELINFO tab) to find the PDF link.
    The link leads to a redirect page which contains the actual PDF URL.
    
    Returns:
        URL to PDF or None if not found
    """
    try:
        # Navigate to SPIELINFO page where the Spielbericht download link is
        url = f"{BASE_URL}/spiele/{game_id}/info"
        print(f"    🔍 Checking SPIELINFO page for PDF...")
        driver.get(url)
        time.sleep(0.5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for link with "Spielbericht" text or href containing spielbericht
        all_links = soup.find_all('a', href=True)
        
        spielbericht_link = None
        for link in all_links:
            href = link.get('href', '').lower()
            text = link.get_text(strip=True).lower()
            
            # Look for "Spielbericht herunterladen" or similar
            if 'spielbericht' in href or 'spielbericht' in text:
                spielbericht_link = link.get('href')
                break
        
        if not spielbericht_link:
            # Alternative: Look for any download link
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if 'pdf' in href.lower() and ('download' in text or 'bericht' in text):
                    spielbericht_link = link.get('href')
                    break
        
        if not spielbericht_link:
            return None
        
        # Handle relative URLs
        if spielbericht_link.startswith('/'):
            spielbericht_url = BASE_URL + spielbericht_link
        else:
            spielbericht_url = spielbericht_link
        
        # Follow the Spielbericht link - it may redirect or have a form submission
        driver.get(spielbericht_url)
        time.sleep(1)  # Give page time to render/redirect
        
        # Check the current URL after navigation
        current_url = driver.current_url
        
        # Check if we're on an external report page
        if 'spo.handball4all.de' in current_url:
            return current_url
        
        # Try to find PDF link on the current page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            # Look for spo.handball4all.de PDF reports or direct PDF links
            if 'spo.handball4all.de' in href or href.endswith('.pdf'):
                return href
        
        # Try to extract from JavaScript or look for report link
        # Sometimes the link is in a form or data attribute
        html_content = driver.page_source
        
        # Look for spo.handball4all.de URLs in the HTML source
        import re as regex_module
        spo_links = regex_module.findall(r'https?://spo\.handball4all\.de[^\s"\'<>]+', html_content)
        if spo_links:
            pdf_url = spo_links[0]
            return pdf_url
        
        # No PDF URL found
        return None
    
    except Exception as e:
        # Log the error for debugging
        print(f"    ⚠️  Error fetching PDF URL: {str(e)[:80]}")
        import traceback
        print(f"       {traceback.format_exc().split(chr(10))[-2]}")
        return None

def scrape_all_games(driver, games_with_teams):
    """Scrape all games and return game-centric data - use Spielplan order"""
    games = []
    
    for idx, game_info in enumerate(games_with_teams, 1):
        game_id = game_info['game_id']
        spielplan_home = game_info['home_team']
        spielplan_away = game_info['away_team']
        date = game_info.get('date', 'Unknown')
        order = game_info['order']
        
        try:
            url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
            driver.get(url)
            time.sleep(1)
            
            html = driver.page_source
            players_by_team = extract_players_from_aufstellung(html)
            
            # Must have at least 2 teams with players
            if len(players_by_team) < 2:
                print(f"  [{idx:3d}/{len(games_with_teams)}] ❌ {game_id}: Incomplete ({len(players_by_team)} teams)")
                continue
            
            # Get the team names from extracted data
            teams_from_html = list(players_by_team.items())
            team1_name, team1_players = teams_from_html[0]
            team2_name, team2_players = teams_from_html[1]
            
            # Determine home/away based on Spielplan data if available
            if spielplan_home and spielplan_away:
                # Use Spielplan data to determine order
                if team1_name == spielplan_home:
                    home_team, home_players = team1_name, team1_players
                    away_team, away_players = team2_name, team2_players
                elif team2_name == spielplan_home:
                    home_team, home_players = team2_name, team2_players
                    away_team, away_players = team1_name, team1_players
                else:
                    # Fallback: just use order from HTML
                    home_team, home_players = team1_name, team1_players
                    away_team, away_players = team2_name, team2_players
            else:
                # Fallback: just use order from HTML
                home_team, home_players = team1_name, team1_players
                away_team, away_players = team2_name, team2_players
            
            # Try to fetch and parse Spielbericht PDF for seven meter data
            pdf_url = extract_spielbericht_pdf_url(driver, game_id)
            if pdf_url:
                seven_meter_data = extract_seven_meters_from_pdf(pdf_url, BASE_URL)
                
                if seven_meter_data:
                    # Add seven meter data to players
                    home_players = add_seven_meters_to_players(home_players, seven_meter_data)
                    away_players = add_seven_meters_to_players(away_players, seven_meter_data)
            
            game = {
                'game_id': game_id,
                'order': order,
                'date': date,
                'home': {
                    'team_name': home_team,
                    'players': home_players
                },
                'away': {
                    'team_name': away_team,
                    'players': away_players
                }
            }
            
            games.append(game)
            print(f"  [{idx:3d}/{len(games_with_teams)}] ✅ {date} | {home_team} ({len(home_players)}) vs {away_team} ({len(away_players)})")
        
        except Exception as e:
            print(f"  [{idx:3d}/{len(games_with_teams)}] ❌ {game_id}: {str(e)[:40]}")
    
    return games

def main():
    driver = None
    try:
        driver = setup_driver()
        
        # Get all game IDs with team info from Spielplan
        print("\n🌐 FETCHING GAMES FROM SPIELPLAN")
        games_info = extract_game_ids_from_spielplan(driver)
        print(f"\n✓ Total games found: {len(games_info)}\n")
        
        # Scrape each game
        print("👥 EXTRACTING GAME DETAILS")
        games = scrape_all_games(driver, games_info)
        
        print(f"\n" + "=" * 70)
        print(f"✅ SCRAPING COMPLETE")
        print(f"=" * 70)
        print(f"✓ {len(games)} games with complete data\n")
        
        # Summary
        teams = set()
        for game in games:
            teams.add(game['home']['team_name'])
            teams.add(game['away']['team_name'])
        
        print(f"Teams ({len(teams)}):")
        for team in sorted(teams):
            home_count = sum(1 for g in games if g['home']['team_name'] == team)
            away_count = sum(1 for g in games if g['away']['team_name'] == team)
            total = home_count + away_count
            print(f"  {team}: {home_count} Home + {away_count} Away = {total}")
        
        # Save to JSON (sorted by order)
        games_sorted = sorted(games, key=lambda g: g.get('order', float('inf')))
        output = {'games': games_sorted}
        Path('output').mkdir(exist_ok=True)
        
        with open('output/handball_games.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Saved: output/handball_games.json")
        
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()
