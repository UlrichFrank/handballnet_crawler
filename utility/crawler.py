"""Main crawler module for extracting player data from handball.net"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from pathlib import Path
import time


class HandballNetCrawler:
    """Crawls handball.net for player and team data"""
    
    def __init__(self, session: requests.Session, base_url: str, delay: float = 1, cert_path: Optional[str] = None, verify_ssl: bool = True, date_from: Optional[str] = None, date_to: Optional[str] = None):
        self.session = session
        self.base_url = base_url
        self.delay = delay
        self.players_data = []
        self.teams_data = []
        self.verify_ssl = verify_ssl
        self.cert_path = self._resolve_cert_path(cert_path) if cert_path else None
        self.date_from = date_from
        self.date_to = date_to
    
    def _resolve_cert_path(self, cert_path: str) -> Optional[str]:
        """Resolve certificate path, expanding ~ to home directory"""
        if not cert_path:
            return None
        expanded_path = Path(cert_path).expanduser()
        if expanded_path.exists():
            return str(expanded_path)
        else:
            print(f"⚠ Certificate file not found: {expanded_path}")
            return None
    
    def get_league_url(self, league_id: str, date_from: str, date_to: str) -> str:
        """Generate league URL"""
        return (
            f"{self.base_url}/ligen/handball4all.{league_id}/"
            f"tabelle"  # Use table view to get all teams
        )
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            verify = self.cert_path if self.cert_path else self.verify_ssl
            response = self.session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching {url}: {e}")
            return None
    
    def get_teams(self, league_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Extract all teams from a league
        
        Args:
            league_id: League identifier
            date_from: Start date (not used for tabelle)
            date_to: End date (not used for tabelle)
            
        Returns:
            List of team dictionaries
        """
        url = self.get_league_url(league_id, date_from, date_to)
        soup = self.fetch_page(url)
        
        if not soup:
            return []
        
        teams = []
        
        # Find the table with teams
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Position is in first cell
                    position = cells[0].get_text(strip=True)
                    
                    # Team name and link are in third cell
                    team_cell = cells[2]
                    team_name = team_cell.get_text(strip=True)
                    
                    # Find team link
                    team_link = team_cell.find('a')
                    if team_link and team_link.get('href'):
                        team_url = team_link.get('href')
                        # Convert relative to absolute URL
                        if not team_url.startswith('http'):
                            team_url = self.base_url + team_url
                        
                        teams.append({
                            'position': position,
                            'name': team_name,
                            'id': team_url.split('/')[-2],  # Extract ID from URL
                            'url': team_url,
                        })
                        print(f"  ✓ {position}. {team_name}")
        
        time.sleep(self.delay)
        return teams
    
    def get_players_for_team(self, team_url: str) -> List[Dict[str, Any]]:
        """
        Extract all players for a specific team
        
        Args:
            team_url: URL to team page or roster
            
        Returns:
            List of player dictionaries
        """
        soup = self.fetch_page(team_url)
        
        if not soup:
            return []
        
        players = []
        # Parse player information from page
        # TODO: Implement based on actual HTML structure
        
        time.sleep(self.delay)
        return players
    
    def extract_all_players(self, league_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """
        Extract all players from all teams in a league
        
        Args:
            league_id: League identifier
            date_from: Start date
            date_to: End date
            
        Returns:
            List of all players with their data
        """
        print(f"Extracting teams from league: {league_id}")
        teams = self.get_teams(league_id, date_from, date_to)
        
        print(f"Found {len(teams)} teams")
        
        all_players = []
        for i, team in enumerate(teams, 1):
            print(f"Processing team {i}/{len(teams)}: {team.get('name', 'Unknown')}")
            
            team_url = team.get('url')
            if team_url:
                players = self.get_players_for_team(team_url)
                for player in players:
                    player['team'] = team.get('name')
                    player['team_id'] = team.get('id')
                all_players.extend(players)
        
        self.players_data = all_players
        return all_players
    
    def get_extracted_data(self) -> Dict[str, Any]:
        """Get all extracted data"""
        return {
            'players': self.players_data,
            'teams': self.teams_data,
            'total_players': len(self.players_data),
            'total_teams': len(self.teams_data)
        }
    
    def get_games_from_spielplan(self, league_id: str) -> List[Dict[str, str]]:
        """Extract all game IDs from the Spielplan"""
        games = []
        spielplan_url = f"{self.base_url}/ligen/handball4all.{league_id}/spielplan"
        
        print(f"Fetching Spielplan from: {spielplan_url}")
        soup = self.fetch_page(spielplan_url)
        
        if not soup:
            print("Failed to fetch Spielplan")
            return games
        
        # Look for all game links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            # Look for aufstellung links
            if '/spiele/' in href and 'aufstellung' in href:
                # Extract game ID from URL like /spiele/handball4all.baden-wuerttemberg.8668846/aufstellung
                parts = href.split('/')
                if len(parts) >= 3:
                    game_id = parts[2]
                    if game_id not in [g['id'] for g in games]:
                        games.append({'id': game_id, 'url': f"{self.base_url}{href}"})
        
        print(f"Found {len(games)} unique games")
        return games
    
    def extract_from_aufstellung_pages(self, league_id: str, max_games: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extract players from Aufstellung (lineup) pages of games
        
        Args:
            league_id: League identifier
            max_games: Maximum number of games to process (None = all)
            
        Returns:
            List of all players with their data
        """
        print(f"Extracting players from AUFSTELLUNG pages for league: {league_id}")
        
        games = self.get_games_from_spielplan(league_id)
        
        if max_games:
            games = games[:max_games]
        
        all_players = {}  # Deduplicate by (name, team_name)
        
        for i, game in enumerate(games, 1):
            game_id = game['id']
            aufstellung_url = game['url']
            
            print(f"[{i}/{len(games)}] Processing game {game_id}...")
            
            try:
                players_from_game = self._parse_aufstellung_page(aufstellung_url)
                
                for player in players_from_game:
                    # Create deduplication key
                    key = (player.get('name', ''), player.get('team', ''))
                    if key[0] and key[1]:
                        all_players[key] = player
                
                print(f"  ✓ Extracted {len(players_from_game)} players")
                
                # Respect rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"  ⚠ Error processing game {game_id}: {e}")
                continue
        
        result = list(all_players.values())
        self.players_data = result
        print(f"\n✓ Total unique players: {len(result)}")
        return result
    
    def _parse_aufstellung_page(self, aufstellung_url: str) -> List[Dict[str, str]]:
        """
        Parse player data from an Aufstellung page
        
        Strategy: Since we're not certain of the exact HTML structure, we'll use text analysis
        to find player information in the page
        
        Args:
            aufstellung_url: URL to the aufstellung page
            
        Returns:
            List of player dictionaries with name and team
        """
        players = []
        
        try:
            soup = self.fetch_page(aufstellung_url)
            if not soup:
                return players
            
            # Get the text content
            text = soup.get_text()
            
            # For now, placeholder implementation
            # The actual parsing depends on discovering the HTML structure
            # We'll collect placeholder data showing what would be extracted
            
            # Extract game info from URL to determine which teams are playing
            # Format: /spiele/{league}.{game_id}/aufstellung
            parts = aufstellung_url.split('/')
            if len(parts) >= 4:
                game_id = parts[-2]
                
                # Look for team names in the page
                # This is a basic implementation - we'd need actual HTML inspection
                # to properly extract player lists
                
                # For testing, we could extract any text that looks like a player
                # (typically in format "Name Number" or similar)
                
                pass
            
            return players
            
        except Exception as e:
            print(f"Error parsing aufstellung page: {e}")
            return players
