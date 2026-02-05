#!/usr/bin/env python3
"""
HANDBALL GAMES SCRAPER - CLEAN & SIMPLE
Extract all games with complete player statistics directly to game-centric JSON
"""

import time
import json
import re
import os
import sys
import calendar
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings('ignore')

from utility.pdf_parser import extract_seven_meters_from_pdf, add_seven_meters_to_players, extract_goals_timeline_from_pdf
from utility.error_logger import ErrorLogger

# Load config from file (default or specified via --config argument)
def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from specified file"""
    config_path = Path(__file__).parent / "config" / config_file
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

# Parse command line arguments properly
config_file = "config.json"  # Default
league_name_arg = None

# Manual parsing to handle --config flag
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == "--config" and i + 1 < len(sys.argv):
        config_file = sys.argv[i + 1]
        i += 2  # Skip both --config and its value
    else:
        league_name_arg = arg
        i += 1

config = load_config(config_file)

BASE_URL = config['ref']['base_url']
DATE_FROM = config['crawler']['date_from']
DATE_TO = config['crawler']['date_to']

# Get leagues to process from command-line argument or use all configured leagues
if league_name_arg:
    # Find the specific league config - exact match on 'name' field
    league_config = None
    for league in config['leagues']:
        if league['name'] == league_name_arg:
            league_config = league
            break
    
    if not league_config:
        print(f"Error: League '{league_name_arg}' not found")
        print(f"\nUsage:")
        print(f"  python3 scraper.py                    # All leagues")
        print(f"  python3 scraper.py <league_name>      # Specific league")
        print(f"\nAvailable leagues:")
        for league in config['leagues']:
            print(f"  - {league['name']}")
        sys.exit(1)
    
    leagues_to_process = [league_config]
else:
    # Process all configured leagues
    leagues_to_process = config['leagues']

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

# Ensure SSL bundle env vars are clean during driver setup
# We'll apply the certificate AFTER ChromeDriver is initialized
os.environ.pop('REQUESTS_CA_BUNDLE', None)
os.environ.pop('CURL_CA_BUNDLE', None)

print("=" * 70)
print("HANDBALL GAMES SCRAPER - Game-Centric Format")
print("=" * 70)
print(f"Verarbeite {len(leagues_to_process)} Liga(n)")
print(f"Date Range: {DATE_FROM} to {DATE_TO}")
print()

def fuzzy_match_team_name(target, candidates, threshold=0.80):
    """
    Fuzzy match team name allowing for minor typos (up to 2 character differences)
    
    Args:
        target: Team name to match
        candidates: List of candidate team names
        threshold: Similarity threshold (0.80 = allows ~2 char difference)
    
    Returns:
        (matched_name, similarity_score) or (None, 0)
    """
    best_match = None
    best_score = 0
    
    target_lower = target.lower().strip()
    
    for candidate in candidates:
        candidate_lower = candidate.lower().strip()
        
        # Exact match
        if target_lower == candidate_lower:
            return (candidate, 1.0)
        
        # Fuzzy match using SequenceMatcher
        similarity = SequenceMatcher(None, target_lower, candidate_lower).ratio()
        if similarity > best_score:
            best_score = similarity
            best_match = candidate
    
    # Return match only if above threshold
    if best_score >= threshold:
        return (best_match, best_score)
    
    return (None, 0)

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
            # Set timeouts
            driver.set_page_load_timeout(30)  # Page load timeout: 30 seconds
            driver.implicitly_wait(10)  # Implicit wait: 10 seconds
            print(f"✓ Using system Chrome: {chrome_path}")
            
            # Apply SSL certificate for system Chrome
            if resolved_cert_path:
                os.environ['REQUESTS_CA_BUNDLE'] = resolved_cert_path
                os.environ['CURL_CA_BUNDLE'] = resolved_cert_path
            
            return driver
    except Exception as e:
        print(f"[Chrome] System Chrome failed: {str(e)[:100]}")
        print("[Chrome] Falling back to Selenium's built-in manager...\n")
    
    # Strategy 2: Use Selenium's built-in selenium-manager
    # This automatically handles ChromeDriver download on all platforms (Linux, macOS, Windows)
    try:
        print("[Chrome] Initializing ChromeDriver via Selenium's built-in manager...")
        driver = webdriver.Chrome(options=options)
        # Set timeouts
        driver.set_page_load_timeout(30)  # Page load timeout: 30 seconds
        driver.implicitly_wait(10)  # Implicit wait: 10 seconds
        print(f"✓ ChromeDriver initialized successfully")
        
        # Apply SSL certificate for subsequent requests
        if resolved_cert_path:
            os.environ['REQUESTS_CA_BUNDLE'] = resolved_cert_path
            os.environ['CURL_CA_BUNDLE'] = resolved_cert_path
        
        return driver
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"\n[ERROR] Chrome initialization failed: {error_msg}")
        raise

def extract_game_ids_from_spielplan(driver, league_id):
    """Load Spielplan with pagination (page=1, page=2, etc) and extract all game IDs with teams, dates, and order"""
    games_with_teams = []
    seen_ids = set()
    order = 0
    
    spielplan_url = f"{BASE_URL}/ligen/{league_id}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
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
                        # Check if this level has date (including "Heute" or "Today" indicator)
                        if re.search(r'([A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.|Heute)', parent_text):
                            game_info_text = parent_text
                            break
                        parent = parent.parent
                    
                    if not game_info_text:
                        continue
                    
                    # Parse the game info text - handle both regular dates and "Heute"
                    date_match = re.search(r'([A-Za-z]{2},\s*\d{1,2}\.\d{1,2}\.|Heute)', game_info_text)
                    if date_match:
                        date_text = date_match.group(1)
                        # Convert "Heute" to today's date in the format needed
                        if date_text == "Heute":
                            today = datetime.now()
                            day_name = calendar.day_name[today.weekday()][:2].capitalize()
                            date_text = f"{day_name}, {today.day:02d}.{today.month:02d}."
                    else:
                        date_text = "Unknown"
                    
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

def parse_date_to_yyyymmdd(date_text):
    """
    Convert date text like "Sa, 20.09." to yyyymmdd format.
    Handles handball season spanning Sep-May across two calendar years.
    """
    from datetime import datetime
    
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    try:
        # Handle "Heute" (today)
        if date_text == "Heute" or "Heute" in date_text:
            return now.strftime('%Y%m%d')
        
        # Format: "Sa, 20.09." → split by comma
        if ',' in date_text:
            date_part = date_text.split(',')[1].strip()
        else:
            date_part = date_text
        
        # Parse "20.09." → extract day and month
        day_month = date_part.split('.')
        day = int(day_month[0])
        month = int(day_month[1])
        
        # Determine year based on handball season (Sep-May spans two calendar years)
        if current_month <= 8 and month >= 9:
            # Current time is Jan-Aug, match is Sep-Dec → use previous year
            year = current_year - 1
        elif current_month >= 9 and month <= 8:
            # Current time is Sep-Dec, match is Jan-Aug → use next year
            year = current_year + 1
        else:
            # Same calendar year
            year = current_year
        
        return f"{year}{month:02d}{day:02d}"
    except Exception as e:
        print(f"  ⚠️  Could not parse date: '{date_text}' - {e}")
        return None

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
        print(f"    🔍 PDF Check...", end='', flush=True)
        
        try:
            driver.get(url)
            time.sleep(0.3)
        except Exception as e:
            print(f" (timeout/error: {str(e)[:20]})", flush=True)
            return None
        
        print(f" ok", flush=True)
        
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
        try:
            driver.get(spielbericht_url)
            time.sleep(0.5)
        except Exception as e:
            return None
        
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
        pass  # Silent fail - PDF is optional
        return None

def extract_officials_from_info(driver, game_id):
    """
    Extract officials (Schiedsrichter, Zeitnehmer, Sekretär) from the game's SPIELINFO page.
    Tries multiple HTML structures to find the officials.
    
    Returns:
        dict with keys: 'referees', 'timekeepers', 'secretaries' (or None if not found)
    """
    try:
        url = f"{BASE_URL}/spiele/{game_id}/info"
        driver.get(url)
        time.sleep(0.3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        officials = {
            'referees': [],
            'timekeepers': [],
            'secretaries': []
        }
        
        # Strategy 1: Look for <li class="w-full"> elements with category + name divs
        list_items = soup.find_all('li', class_='w-full')
        
        for li in list_items:
            divs = li.find_all('div')
            if len(divs) >= 2:
                category_div = divs[0]
                name_div = divs[1]
                
                category_text = category_div.get_text(strip=True)
                name_text = name_div.get_text(strip=True)
                
                if not category_text or not name_text:
                    continue
                
                # Validate: category must have official keywords, name must NOT
                has_category_keyword = any(kw in category_text for kw in ['Schiedsrichter', 'Zeitnehmer', 'Sekretär', 'Sekreter'])
                has_name_keyword = any(kw in name_text for kw in ['Schiedsrichter', 'Zeitnehmer', 'Sekretär', 'Sekreter'])
                
                if not has_category_keyword or has_name_keyword:
                    continue
                
                # Clean up concatenated names like "MarcBeck" → "Marc Beck"
                name_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', name_text)
                
                # Add to officials
                if 'Schiedsrichter' in category_text:
                    officials['referees'].append(name_text)
                elif 'Zeitnehmer' in category_text:
                    officials['timekeepers'].append(name_text)
                elif 'Sekretär' in category_text or 'Sekreter' in category_text:
                    officials['secretaries'].append(name_text)
        
        # Return officials only if we found any valid ones (not labels)
        if officials['referees'] or officials['timekeepers'] or officials['secretaries']:
            # Final filter: remove any remaining labels
            officials['referees'] = [r for r in officials['referees'] if 'Schiedsrichter' not in r and 'Zeitnehmer' not in r and 'Sekretär' not in r]
            officials['timekeepers'] = [t for t in officials['timekeepers'] if 'Schiedsrichter' not in t and 'Zeitnehmer' not in t and 'Sekretär' not in t]
            officials['secretaries'] = [s for s in officials['secretaries'] if 'Schiedsrichter' not in s and 'Zeitnehmer' not in s and 'Sekretär' not in s]
            
            if officials['referees'] or officials['timekeepers'] or officials['secretaries']:
                return officials
        
        return None
    
    except Exception as e:
        return None

def scrape_all_games(driver, games_with_teams, league_config=None, error_logger: ErrorLogger = None):
    """Scrape all games and return game-centric data - use Spielplan order"""
    games = []
    
    # Get half duration from league config
    half_duration = 30  # Default
    if league_config:
        half_duration = league_config.get('half_duration', 30)
    
    # Get league_id for error logging
    league_id = league_config.get('name', 'unknown') if league_config else 'unknown'
    
    print(f"   📝 Starting to extract game details...")
    sys.stdout.flush()  # Force output flush
    
    for idx, game_info in enumerate(games_with_teams, 1):
        game_id = game_info['game_id']
        spielplan_home = game_info['home_team']
        spielplan_away = game_info['away_team']
        date = game_info.get('date', 'Unknown')
        order = game_info['order']
        
        try:
            url = f"{BASE_URL}/spiele/{game_id}/aufstellung"
            print(f"  [{idx:3d}/{len(games_with_teams)}] Loading aufstellung...")
            sys.stdout.flush()
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
                # Try exact match first
                if team1_name == spielplan_home:
                    home_team, home_players = team1_name, team1_players
                    away_team, away_players = team2_name, team2_players
                elif team2_name == spielplan_home:
                    home_team, home_players = team2_name, team2_players
                    away_team, away_players = team1_name, team1_players
                else:
                    # Try fuzzy match
                    match, score = fuzzy_match_team_name(spielplan_home, [team1_name, team2_name])
                    if match:
                        if match == team1_name:
                            home_team, home_players = team1_name, team1_players
                            away_team, away_players = team2_name, team2_players
                        else:
                            home_team, home_players = team2_name, team2_players
                            away_team, away_players = team1_name, team1_players
                        print(f"    ⚠️  Fuzzy matched home team: '{spielplan_home}' ≈ '{match}' (score: {score:.2f})")
                    else:
                        # Fallback: just use order from HTML
                        home_team, home_players = team1_name, team1_players
                        away_team, away_players = team2_name, team2_players
                        print(f"    ❌ ERROR: Could not match home team '{spielplan_home}' (available: {team1_name}, {team2_name})")
            else:
                # Fallback: just use order from HTML
                home_team, home_players = team1_name, team1_players
                away_team, away_players = team2_name, team2_players
            
            # Try to fetch and parse Spielbericht PDF for seven meter data and goal timeline
            pdf_url = extract_spielbericht_pdf_url(driver, game_id)
            goals_timeline = []
            graphic_path = None
            if pdf_url:
                seven_meter_data = extract_seven_meters_from_pdf(pdf_url, BASE_URL)
                goals_timeline = extract_goals_timeline_from_pdf(pdf_url, BASE_URL)
                
                if seven_meter_data:
                    # Add seven meter data to players
                    home_players = add_seven_meters_to_players(home_players, seven_meter_data)
                    away_players = add_seven_meters_to_players(away_players, seven_meter_data)
            
            # Extract officials from /info page
            officials = extract_officials_from_info(driver, game_id)
            
            # Calculate final score from goals
            home_score = len([g for g in goals_timeline if g['team'] == 'home'])
            away_score = len([g for g in goals_timeline if g['team'] == 'away'])
            
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
                },
                'goals_timeline': goals_timeline,
                'final_score': f"{home_score}:{away_score}",
                'half_duration': half_duration,
                'officials': officials
            }
            
            
            games.append(game)
            print(f"  [{idx:3d}/{len(games_with_teams)}] ✅ {date} | {home_team} ({len(home_players)}) vs {away_team} ({len(away_players)})")
            sys.stdout.flush()  # Force flush output
        
        except Exception as e:
            error_str = str(e)[:60]
            print(f"  [{idx:3d}/{len(games_with_teams)}] ❌ {game_id}: {error_str}")
            sys.stdout.flush()  # Force flush output
            
            # Log error for retry in next run
            if error_logger:
                error_logger.add_failed_game(
                    game_id=game_id,
                    liga_id=league_id,
                    date=date,
                    home_team=spielplan_home or 'Unknown',
                    away_team=spielplan_away or 'Unknown',
                    error=str(e)
                )
            continue  # Continue with next game
    
    print(f"\n   ✓ Game extraction complete. {len(games)} games processed.")
    sys.stdout.flush()
    return games

def get_last_scraped_date(liga_id):
    """Get the last date (yyyymmdd) that was already scraped for this league."""
    data_dir = Path('frontend/public/data') / liga_id
    if not data_dir.exists():
        return None
    
    # Find latest date file (format: yyyymmdd.json)
    date_files = sorted([
        f.stem
        for f in data_dir.glob('*.json')
        if f.stem.isdigit() and len(f.stem) == 8
    ])
    
    if date_files:
        return date_files[-1]
    return None

def ensure_data_directories(liga_id):
    """Create data directories for a league if they don't exist."""
    data_dir = Path('frontend/public/data') / liga_id
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Verzeichnis vorbereitet: {data_dir.absolute()}")
    return data_dir

def should_scrape_league(liga_id, date_from, date_to):
    """
    Determine what date range needs to be scraped.
    
    Returns:
        tuple: (start_date, end_date) both as YYYY-MM-DD strings
        If no scraping needed, start_date > end_date
    """
    from datetime import datetime, timedelta
    
    # Parse date strings like "2025-09-13"
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    except:
        print(f"⚠️  Invalid date format.")
        return to_date.strftime('%Y-%m-%d'), from_date.strftime('%Y-%m-%d')
    
    # If to_date is in future, use today instead
    today = datetime.now().date()
    if to_date > today:
        to_date = today
    
    last_scraped = get_last_scraped_date(liga_id)
    
    if last_scraped is None:
        # Never scraped before - start from configured date
        print(f"   📅 First scrape: Starting from {date_from}")
        return date_from, to_date.strftime('%Y-%m-%d')
    
    # Parse last_scraped (yyyymmdd format)
    try:
        last_year = int(last_scraped[:4])
        last_month = int(last_scraped[4:6])
        last_day = int(last_scraped[6:8])
        last_date = datetime(last_year, last_month, last_day).date()
    except:
        print(f"   ⚠️  Could not parse last scraped date: {last_scraped}")
        return date_from, to_date.strftime('%Y-%m-%d')
    
    # If last scraped is before end_date, continue scraping
    if last_date < to_date:
        next_date = last_date + timedelta(days=1)
        print(f"   📅 Incremental scrape: Last had data up to {last_date}, continuing from {next_date}")
        return next_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')
    
    print(f"   ✅ All data already scraped up to {last_date}")
    # Return invalid range (start > end) to indicate no scraping needed
    return to_date.strftime('%Y-%m-%d'), from_date.strftime('%Y-%m-%d')

def scrape_league(driver, league_config):
    """Scrape a single league using daily iteration"""
    league_name = league_config['name']
    league_display_name = league_config['display_name']
    league_id = f"handball4all.baden-wuerttemberg.{league_name}"
    
    # Use league name as data folder ID
    data_liga_id = league_name
    
    print(f"\n{'=' * 70}")
    print(f"🏐 {league_display_name}")
    print(f"   📁 frontend/public/data/{data_liga_id}/")
    print(f"{'=' * 70}\n")
    
    # Step 1: Ensure directories exist
    ensure_data_directories(data_liga_id)
    
    # Step 2: Determine what dates to scrape
    start_date, end_date = should_scrape_league(data_liga_id, DATE_FROM, DATE_TO)
    
    # Check if scraping needed (start_date > end_date means already up to date)
    if start_date > end_date:
        print(f"✅ Already up to date\n")
        return
    
    # Step 3: Scrape daily
    stats = scrape_daily(driver, data_liga_id, league_id, start_date, end_date)
    
    # Step 4: Summary
    print(f"\n{'=' * 70}")
    print(f"✅ COMPLETE: {league_display_name}")
    print(f"{'=' * 70}")
    print(f"   ✓ Spieltage: {stats['spieltage_saved']}")
    print(f"   ✓ Games: {stats['games_total']}")
    if stats['spieltage_failed'] > 0:
        print(f"   ⚠️  Failed: {stats['spieltage_failed']}")
    print()


def save_spieltag_file(liga_id, date_yyyymmdd, games):
    """
    Save games for a single matchday to yyyymmdd.json file.
    
    Args:
        liga_id: League identifier
        date_yyyymmdd: Date in YYYYMMDD format
        games: List of game dictionaries
    """
    data_dir = Path('frontend/public/data') / liga_id
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = data_dir / f'{date_yyyymmdd}.json'
    
    try:
        # Check if file already exists and merge
        if output_file.exists():
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
            existing_games = existing_data.get('games', [])
            existing_ids = {g.get('game_id') for g in existing_games}
            
            # Add only new games
            new_games = [g for g in games if g.get('game_id') not in existing_ids]
            
            if new_games:
                merged_games = existing_games + new_games
                print(f"      ✍️  Writing (update): {output_file}")
                sys.stdout.flush()
                with open(output_file, 'w') as f:
                    json.dump({'date': date_yyyymmdd, 'games': merged_games}, f, indent=2)
                print(f"      ✅ Updated (+{len(new_games)} new, total: {len(merged_games)})")
                sys.stdout.flush()
            else:
                print(f"      ℹ️  No new games to add")
                sys.stdout.flush()
        else:
            # Create new file
            print(f"      ✍️  Writing (new): {output_file}")
            sys.stdout.flush()
            with open(output_file, 'w') as f:
                json.dump({'date': date_yyyymmdd, 'games': games}, f, indent=2)
            print(f"      ✅ Created ({len(games)} games)")
            sys.stdout.flush()
        
        return True
    except Exception as e:
        print(f"      ❌ Error saving {output_file}: {e}")
        sys.stdout.flush()
        return False

def scrape_daily(driver, liga_id, league_id, start_date_str, end_date_str):
    """
    Scrape games chronologically, day by day.
    
    Args:
        driver: Selenium WebDriver
        liga_id: League identifier (e.g., "mc-ol-3-bw_bwhv")
        league_id: Full league ID for handball4all
        start_date_str: Start date (YYYY-MM-DD)
        end_date_str: End date (YYYY-MM-DD)
    
    Returns:
        dict: Statistics about scraping (games_total, spieltage_saved, errors)
    """
    from datetime import datetime, timedelta
    
    # Initialize error logger
    error_logger = ErrorLogger()
    
    stats = {
        'games_total': 0,
        'spieltage_saved': 0,
        'spieltage_failed': 0,
        'games_with_errors': 0
    }
    
    # Parse date range
    try:
        current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except Exception as e:
        print(f"❌ Error parsing dates: {e}")
        return stats
    
    print(f"\n📅 Scraping daily from {start_date_str} to {end_date_str}\n")
    
    # Load ALL games from Spielplan once
    print(f"🌐 FETCHING ALL GAMES FROM SPIELPLAN")
    try:
        all_games_info = extract_game_ids_from_spielplan(driver, league_id)
        print(f"\n✓ Total games found: {len(all_games_info)}\n")
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        return stats
    
    if not all_games_info:
        print(f"⚠️  No games found")
        return stats
    
    # Iterate day by day with compression for empty days
    empty_days_start = None
    empty_days_count = 0
    
    while current_date <= end_date:
        date_str_formatted = current_date.strftime('%Y-%m-%d')
        date_yyyymmdd = current_date.strftime('%Y%m%d')
        
        # Filter games for this specific date
        games_for_date = [g for g in all_games_info if parse_date_to_yyyymmdd(g.get('date', '')) == date_yyyymmdd]
        
        if not games_for_date:
            # Track empty days
            if empty_days_start is None:
                empty_days_start = date_str_formatted
            empty_days_count += 1
            current_date += timedelta(days=1)
            continue
        
        # Print accumulated empty days (if any)
        if empty_days_count > 0:
            empty_days_end = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
            if empty_days_count == 1:
                print(f"⏭️  No games: {empty_days_start}")
            else:
                print(f"⏭️  No games: {empty_days_start} to {empty_days_end} ({empty_days_count} days)")
            print()
            empty_days_start = None
            empty_days_count = 0
        
        # Process day with games
        print(f"📅 {date_str_formatted}")
        
        try:
            print(f"   ✓ Found {len(games_for_date)} game(s)")
            sys.stdout.flush()
            
            # Scrape details for each game
            print(f"   👥 Scraping game details...")
            sys.stdout.flush()
            
            # Get league config for error logging
            league_config = {'name': liga_id}
            
            try:
                scraped_games = scrape_all_games(driver, games_for_date, league_config, error_logger)
                print(f"   ✓ Scraped {len(scraped_games)} game(s)")
                sys.stdout.flush()
            except Exception as e:
                print(f"   ⚠️  Error scraping games: {e}")
                sys.stdout.flush()
                stats['spieltage_failed'] += 1
                stats['games_with_errors'] += len(games_for_date)
                current_date += timedelta(days=1)
                continue
            
            # Save to file
            print(f"   💾 Saving...")
            sys.stdout.flush()
            
            if save_spieltag_file(liga_id, date_yyyymmdd, scraped_games):
                stats['spieltage_saved'] += 1
                stats['games_total'] += len(scraped_games)
            else:
                stats['spieltage_failed'] += 1
                stats['games_with_errors'] += len(scraped_games)
        
        except Exception as e:
            print(f"   ❌ Error processing day: {e}")
            sys.stdout.flush()
            stats['spieltage_failed'] += 1
        
        print()
        current_date += timedelta(days=1)
    
    # Print remaining empty days
    if empty_days_count > 0:
        empty_days_end = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
        if empty_days_count == 1:
            print(f"⏭️  No games: {empty_days_start}")
        else:
            print(f"⏭️  No games: {empty_days_start} to {empty_days_end} ({empty_days_count} days)")
    
    # Save error log at the end
    if error_logger.failed_games:
        error_logger.save()
        print(f"\n⚠️  Error summary:")
        summary = error_logger.get_summary()
        for liga, games in summary.items():
            print(f"   {liga}: {len(games)} failed game(s)")
            for game in games[:3]:  # Show first 3 errors
                print(f"      - {game['teams']} ({game['date']}): {game['error']}")
            if len(games) > 3:
                print(f"      ... and {len(games) - 3} more")
    
    return stats


def update_meta_index(liga_id=None):
    """
    Update meta.json with all available Spieltage.
    
    Args:
        liga_id: Optional - if provided, update only this league
                 if None, update all leagues (slower, but complete)
    """
    print(f"\n🔄 Updating meta.json...")
    sys.stdout.flush()
    
    meta_file = Path('frontend/public/data/meta.json')
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Try to load existing meta
    if meta_file.exists():
        with open(meta_file, 'r') as f:
            meta = json.load(f)
    else:
        meta = {
            'last_updated': datetime.now().isoformat() + 'Z',
            'leagues': {}
        }
    
    # Build a map of league names to display names from config
    league_display_names = {}
    for league_config in config['leagues']:
        league_display_names[league_config['name']] = league_config['display_name']
    
    data_dir = Path('frontend/public/data')
    
    # If specific liga_id provided, update only that league
    if liga_id:
        liga_folder = data_dir / liga_id
        if liga_folder.exists() and liga_folder.is_dir():
            # Find all date-based files (format: yyyymmdd.json)
            date_files = sorted([
                f.stem
                for f in liga_folder.glob('*.json')
                if f.stem.isdigit() and len(f.stem) == 8
            ])
            
            if date_files:
                display_name = league_display_names.get(liga_id, liga_id)
                meta['leagues'][liga_id] = {
                    'name': display_name,
                    'spieltage': date_files,
                    'last_updated': datetime.now().isoformat() + 'Z'
                }
                print(f"   ✅ {liga_id}: {len(date_files)} Spieltag(e)")
                sys.stdout.flush()
    else:
        # Update all leagues
        for liga_folder in sorted(data_dir.iterdir()):
            if not liga_folder.is_dir():
                continue
            
            liga_id_item = liga_folder.name
            
            # Find all date-based files (format: yyyymmdd.json)
            date_files = sorted([
                f.stem
                for f in liga_folder.glob('*.json')
                if f.stem.isdigit() and len(f.stem) == 8
            ])
            
            if date_files:
                display_name = league_display_names.get(liga_id_item, liga_id_item)
                meta['leagues'][liga_id_item] = {
                    'name': display_name,
                    'spieltage': date_files,
                    'last_updated': datetime.now().isoformat() + 'Z'
                }
                print(f"   ✅ {liga_id_item}: {len(date_files)} Spieltag(e)")
                sys.stdout.flush()
    
    # Update timestamp
    meta['last_updated'] = datetime.now().isoformat() + 'Z'
    
    print(f"   ✍️  Writing: {meta_file.absolute()}")
    sys.stdout.flush()
    with open(meta_file, 'w') as f:
        json.dump(meta, f, indent=2)
    
    print(f"   ✅ meta.json updated")
    sys.stdout.flush()

def main():
    driver = None
    total_spieltage = 0
    total_games = 0
    
    try:
        driver = setup_driver()
        
        # Process each league
        for league_config in leagues_to_process:
            scrape_league(driver, league_config)
            
            # Update meta index after each league
            update_meta_index(league_config['name'])
        
        # Final summary
        print(f"\n{'=' * 70}")
        print(f"✅ ALL LEAGUES COMPLETE")
        print(f"{'=' * 70}\n")
        
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()

