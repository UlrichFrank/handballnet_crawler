#!/usr/bin/env python3
"""
Extract ALL games from ALL teams for current season (11 Spieltage)
Captures home and away matches with complete player statistics
"""

import time
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings('ignore')

# Config
config_path = Path(__file__).parent / "config" / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

BASE_URL = config['authentication']['base_url']
LEAGUE_ID = f"handball4all.baden-wuerttemberg.{config['league']['name']}"
USERNAME = config['authentication']['username']
PASSWORD = config['authentication']['password']

# 11 Spieltage der aktuellen Saison
SPIELTAGE = [
    "20.09.2025",  # Sa, 20.09.
    "28.09.2025",  # So, 28.09.
    "04.10.2025",  # Sa, 04.10.
    "12.10.2025",  # So, 12.10.
    "18.10.2025",  # Sa, 18.10.
    "08.11.2025",  # Sa, 08.11.
    "16.11.2025",  # So, 16.11.
    "23.11.2025",  # So, 23.11.
    "30.11.2025",  # So, 30.11.
    "06.12.2025",  # Sa, 06.12.
    "14.12.2025",  # So, 14.12.
]

def setup_driver():
    """Setup Selenium WebDriver with authentication"""
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    # Login
    print("🔐 Authenticating...")
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login_button").click()
    
    time.sleep(3)
    print("✅ Authenticated\n")
    
    return driver

def extract_players_from_aufstellung(html):
    """Extract players with statistics from AUFSTELLUNG page"""
    soup = BeautifulSoup(html, 'html.parser')
    players_by_team = {}
    
    tables = soup.find_all('table', class_='mb-4 w-full text-base')
    
    for table in tables:
        # Get team name from h3 before table
        team_name = "Unknown"
        current = table
        while current:
            current = current.find_previous('h3')
            if current:
                team_name = current.get_text(strip=True).strip()
                break
        
        players = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 2:
                name = tds[0].get_text(strip=True)
                if name and name not in ['Name', 'GESAMT']:
                    player_stats = {
                        'name': name,
                        'goals': 0,
                        'two_min_penalties': 0,
                        'yellow_cards': 0,
                        'red_cards': 0,
                        'blue_cards': 0
                    }
                    
                    for i, td in enumerate(tds[1:], start=1):
                        text = td.get_text(strip=True)
                        if not text or text == '-':
                            continue
                        
                        try:
                            val = int(text)
                            if i == 1:
                                player_stats['goals'] = val
                            elif i == 2:
                                player_stats['two_min_penalties'] = val
                            elif i == 3:
                                player_stats['yellow_cards'] = val
                            elif i == 4:
                                player_stats['red_cards'] = val
                            elif i == 5:
                                player_stats['blue_cards'] = val
                        except ValueError:
                            pass
                    
                    players.append(player_stats)
        
        if players and team_name != "Unknown":
            players_by_team[team_name] = players
    
    return players_by_team

def extract_game_info(html):
    """Extract home team, away team, and game status"""
    soup = BeautifulSoup(html, 'html.parser')
    
    home_team = None
    away_team = None
    
    # Look for team names in the page
    team_headers = soup.find_all('h3')
    if len(team_headers) >= 2:
        home_team = team_headers[0].get_text(strip=True).strip()
        away_team = team_headers[1].get_text(strip=True).strip()
    
    return home_team, away_team

def extract_game_date(html):
    """Extract game date from page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for date in various locations
    date_text = soup.find(text=re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
    if date_text:
        match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', str(date_text))
        if match:
            return match.group(1)
    
    return None

def scrape_all_games(driver):
    """Scrape all games from all teams for the current season"""
    games = []
    spielplan_url = f"{BASE_URL}/spielplan/{LEAGUE_ID}"
    
    print(f"📊 Accessing Spielplan: {spielplan_url}\n")
    driver.get(spielplan_url)
    time.sleep(3)
    
    # Get all game links
    game_links = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/spiele/handball4all' in href:
            if href not in [g['url'] for g in games]:
                game_links.append(href)
    
    print(f"🔍 Found {len(game_links)} game links\n")
    
    for idx, game_link in enumerate(game_links, 1):
        print(f"[{idx}/{len(game_links)}] Processing {game_link[:60]}...")
        
        driver.get(f"{BASE_URL}{game_link}")
        time.sleep(1.5)
        
        html = driver.page_source
        home_team, away_team = extract_game_info(html)
        game_date = extract_game_date(html)
        
        # Only include games from the 11 Spieltage
        if game_date not in SPIELTAGE:
            print(f"           ❌ Skipped (date {game_date} not in current season)")
            continue
        
        if not home_team or not away_team:
            print(f"           ⚠️ Skipped (missing team info)")
            continue
        
        players_by_team = extract_players_from_aufstellung(html)
        
        if home_team not in players_by_team or away_team not in players_by_team:
            print(f"           ⚠️ Skipped (missing player data)")
            continue
        
        game = {
            'game_id': game_link.split('/')[-1],
            'date': game_date,
            'home': {
                'team_name': home_team,
                'players': players_by_team[home_team]
            },
            'away': {
                'team_name': away_team,
                'players': players_by_team[away_team]
            }
        }
        
        games.append(game)
        print(f"           ✅ {home_team} vs {away_team} ({len(players_by_team[home_team])} vs {len(players_by_team[away_team])} players)")
    
    return games

def main():
    driver = None
    try:
        driver = setup_driver()
        
        print("=" * 70)
        print("📅 EXTRACTING ALL GAMES - CURRENT SEASON (11 SPIELTAGE)")
        print("=" * 70)
        print(f"Spieltage: {', '.join(SPIELTAGE)}\n")
        
        games = scrape_all_games(driver)
        
        if games:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            data = {'games': games}
            with open(output_dir / 'handball_games.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n" + "=" * 70)
            print(f"✅ EXTRACTION COMPLETE")
            print(f"=" * 70)
            print(f"Total games: {len(games)}")
            
            # Summary by team
            teams = {}
            for game in games:
                for team in [game['home']['team_name'], game['away']['team_name']]:
                    if team not in teams:
                        teams[team] = {'home': 0, 'away': 0}
                    if team == game['home']['team_name']:
                        teams[team]['home'] += 1
                    else:
                        teams[team]['away'] += 1
            
            print(f"\nTeams ({len(teams)}):")
            for team in sorted(teams.keys()):
                print(f"  {team}: {teams[team]['home']} Home + {teams[team]['away']} Away = {teams[team]['home'] + teams[team]['away']} Total")
        
        else:
            print("❌ No games extracted!")
    
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()
