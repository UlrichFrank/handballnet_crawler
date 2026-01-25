"""
PDF PARSER - Extract seven meter data from Spielbericht PDFs
"""

import re
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def extract_seven_meters_from_pdf(pdf_url: str, base_url: str = "https://www.handball.net", verify_ssl: bool = True) -> Dict[str, Dict[str, int]]:
    """
    Download and parse Spielbericht PDF to extract seven meter data.
    
    Handles both direct PDF URLs and spo.handball4all.de report URLs.
    Uses SSL certificate from environment (REQUESTS_CA_BUNDLE) if set.
    
    Returns:
        Dict with player names as keys and {'attempts': int, 'goals': int} as values
    """
    
    if pdfplumber is None:
        print("    ⚠️  pdfplumber not installed, skipping PDF parsing")
        return {}
    
    try:
        # Handle relative URLs
        if pdf_url.startswith('/'):
            pdf_url = base_url + pdf_url
        
        # Download PDF - certificate is configured via environment variable
        # For spo.handball4all.de, we may need to allow redirects
        response = requests.get(pdf_url, timeout=10, verify=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check if we actually got a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not response.content.startswith(b'%PDF'):
            return {}
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            seven_meter_data = _parse_pdf(tmp_path)
            return seven_meter_data
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
    
    except Exception as e:
        # Log the error for debugging
        print(f"    ⚠️  PDF download/parsing failed: {str(e)[:80]}")
        return {}


def _parse_pdf(pdf_path: str) -> Dict[str, Dict[str, int]]:
    """
    Parse PDF file and extract seven meter data.
    
    Looks for table entries with "7m" in the action column.
    Counts attempts (successful and failed) and goals per player.
    """
    
    seven_meter_data = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Start from page 3 (index 2) where the detailed game flow begins
            for page_num, page in enumerate(pdf.pages[2:] if len(pdf.pages) > 2 else []):
                tables = page.extract_tables()
                
                if not tables:
                    continue
                
                for table in tables:
                    for row in table:
                        if not row or len(row) < 4:
                            continue
                        
                        # Row format: [Zeit, Spielzeit, Spielstand, Aktion]
                        aktion = row[3] if len(row) > 3 else None
                        
                        if not aktion or "7m" not in aktion:
                            continue
                        
                        # Initialize player data if needed
                        # First, try to extract player name from the action
                        player_name = None
                        is_goal = False
                        
                        # Parse seven meter actions
                        if "7m-Tor durch" in aktion:
                            # Successful seven meter: "7m-Tor durch SPIELER"
                            match = re.search(
                                r'7m-Tor durch\s+(\w+\s+\w+)',
                                aktion
                            )
                            if match:
                                player_name = match.group(1)
                                is_goal = True
                        
                        elif "7m, KEIN Tor durch" in aktion:
                            # Failed seven meter: "7m, KEIN Tor durch SPIELER"
                            match = re.search(
                                r'7m, KEIN Tor durch\s+(\w+\s+\w+)',
                                aktion
                            )
                            if match:
                                player_name = match.group(1)
                                is_goal = False
                        
                        elif "7m" in aktion:
                            # Other 7m actions - try to find player name
                            # Look for names before "7m" or after "von"
                            match = re.search(
                                r'von\s+(\w+\s+\w+)\s+7m',
                                aktion
                            )
                            if not match:
                                # Try alternative: name at start or before action
                                match = re.search(
                                    r'(\w+\s+\w+).*7m',
                                    aktion
                                )
                            
                            if match:
                                player_name = match.group(1)
                                is_goal = False
                        
                        # Add to statistics if we found a player name
                        if player_name:
                            if player_name not in seven_meter_data:
                                seven_meter_data[player_name] = {
                                    'attempts': 0,
                                    'goals': 0
                                }
                            seven_meter_data[player_name]['attempts'] += 1
                            if is_goal:
                                seven_meter_data[player_name]['goals'] += 1
        
        if seven_meter_data:
            pass
    
    except Exception as e:
        print(f"    ⚠️  PDF parsing error: {str(e)[:60]}")
    
    return seven_meter_data


def extract_goals_timeline_from_pdf(pdf_url: str, base_url: str = "https://www.handball.net", verify_ssl: bool = True) -> List[Dict]:
    """
    Download and parse Spielbericht PDF to extract goal timeline.
    
    Returns:
        List of goals with {minute, second, scorer, team, seven_meter}
    """
    
    if pdfplumber is None:
        print("    ⚠️  pdfplumber not installed, skipping goal timeline extraction")
        return []
    
    try:
        if pdf_url.startswith('/'):
            pdf_url = base_url + pdf_url
        
        response = requests.get(pdf_url, timeout=10, verify=True, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not response.content.startswith(b'%PDF'):
            return []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            goals = _extract_goals_from_pdf(tmp_path)
            return goals
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    except Exception as e:
        print(f"    ⚠️  Goal timeline extraction failed: {str(e)[:80]}")
        return []


def _extract_goals_from_pdf(pdf_path: str, home_team_abbrev: str = None, away_team_abbrev: str = None) -> List[Dict]:
    """
    Parse PDF and extract all goals with timestamps.
    
    Row format: [Zeit, Spielzeit, Spielstand, Aktion]
    Goal patterns:
      - "Tor durch SPIELER (NUMBER, TEAM)"
      - "7m-Tor durch SPIELER (NUMBER, TEAM)"
    
    Args:
        pdf_path: Path to PDF file
        home_team_abbrev: Home team abbreviation from PDF (for team detection)
        away_team_abbrev: Away team abbreviation from PDF (for team detection)
    """
    
    goals = []
    home_abbrev = None
    away_abbrev = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages[2:] if len(pdf.pages) > 2 else []):
                tables = page.extract_tables()
                
                if not tables:
                    continue
                
                for table in tables:
                    for row in table:
                        if not row or len(row) < 4:
                            continue
                        
                        spielzeit = row[1] if len(row) > 1 else None
                        aktion = row[3] if len(row) > 3 else None
                        
                        if not spielzeit or not aktion:
                            continue
                        
                        # Check if it's a goal (not 7m attempt that failed)
                        is_seven_meter = False
                        scorer = None
                        team_abbrev = None
                        
                        if "7m-Tor durch" in aktion:
                            is_seven_meter = True
                            match = re.search(
                                r'7m-Tor durch\s+(\w+(?:\s+\w+)*)\s+\(\d+,\s*([^)]+)\)',
                                aktion
                            )
                            if match:
                                scorer = match.group(1).strip()
                                team_abbrev = match.group(2).strip()
                        
                        elif "Tor durch" in aktion and "7m" not in aktion:
                            match = re.search(
                                r'Tor durch\s+(\w+(?:\s+\w+)*)\s+\(\d+,\s*([^)]+)\)',
                                aktion
                            )
                            if match:
                                scorer = match.group(1).strip()
                                team_abbrev = match.group(2).strip()
                        
                        # Learn team abbreviations from first few goals
                        if scorer and team_abbrev:
                            if not home_abbrev and not away_abbrev:
                                home_abbrev = team_abbrev
                            elif not away_abbrev and team_abbrev != home_abbrev:
                                away_abbrev = team_abbrev
                            
                            try:
                                time_parts = spielzeit.split(':')
                                if len(time_parts) == 2:
                                    minute = int(time_parts[0])
                                    second = int(time_parts[1])
                                    
                                    # Determine team based on abbreviation
                                    team = "home" if team_abbrev == home_abbrev else "away"
                                    
                                    goals.append({
                                        'minute': minute,
                                        'second': second,
                                        'scorer': scorer,
                                        'team': team,
                                        'team_abbrev': team_abbrev,
                                        'seven_meter': is_seven_meter
                                    })
                            except (ValueError, IndexError):
                                pass
    
    except Exception as e:
        print(f"    ⚠️  Goal extraction error: {str(e)[:60]}")
    
    return goals


def add_seven_meters_to_players(players: List[Dict], seven_meter_data: Dict) -> List[Dict]:
    """
    Add seven meter statistics to player objects.
    """
    
    for player in players:
        name = player.get('name', '')
        
        if name in seven_meter_data:
            stats = seven_meter_data[name]
            player['seven_meters'] = stats['attempts']
            player['seven_meters_goals'] = stats['goals']
        else:
            player['seven_meters'] = 0
            player['seven_meters_goals'] = 0
    
    return players
