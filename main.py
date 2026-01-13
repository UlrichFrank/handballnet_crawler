#!/usr/bin/env python3
"""Main entry point for handball.net crawler"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

from hb_crawler.authenticator import HandballNetAuthenticator
from hb_crawler.selenium_authenticator import HandballNetSeleniumAuthenticator
from hb_crawler.crawler import HandballNetCrawler
from hb_crawler.exporter import DataExporter


def load_config(config_file: str = 'config/config.json') -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Config file not found: {config_file}")
        print(f"  Create {config_file} from config/config.example.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        sys.exit(1)


def main():
    """Main crawler execution"""
    
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    config = load_config()
    
    # Get credentials from config or environment
    auth_config = config['authentication']
    username = os.getenv('HB_USERNAME') or auth_config['username']
    password = os.getenv('HB_PASSWORD') or auth_config['password']
    base_url = os.getenv('HB_BASE_URL') or auth_config.get('base_url', 'https://www.handball.net')
    
    # Get SSL configuration
    ssl_config = config.get('ssl', {})
    cert_path = ssl_config.get('cert_path')
    verify_ssl = ssl_config.get('verify_ssl', True)
    
    if not username or not password or username == 'your_username':
        print("✗ Missing credentials. Please set HB_USERNAME and HB_PASSWORD")
        print("  Either in .env file or in config/config.json")
        sys.exit(1)
    
    # Initialize authenticator and login
    print("Initializing authentication...")
    auth = HandballNetSeleniumAuthenticator(
        base_url,
        username,
        password,
        cert_path=cert_path,
        verify_ssl=verify_ssl,
        headless=True
    )
    
    if not auth.login():
        print("✗ Failed to authenticate. Exiting.")
        sys.exit(1)
    
    # Initialize crawler with new session (Selenium doesn't provide persistent sessions)
    # The crawler will handle authentication separately if needed
    import requests
    session = requests.Session()
    
    # Add cookies from Selenium if available
    if hasattr(auth, 'get_cookies'):
        cookies = auth.get_cookies()
        for name, value in cookies.items():
            session.cookies.set(name, value)
    
    crawler = HandballNetCrawler(
        session=session,
        base_url=base_url,
        delay=config['crawler']['delay_between_requests'],
        cert_path=cert_path,
        verify_ssl=verify_ssl
    )
    
    # Extract player data
    league_config = config['league']
    print(f"\nStarting data extraction for: {league_config['display_name']}")
    print("-" * 50)
    
    players = crawler.extract_all_players(
        league_id=league_config['name'],
        date_from=league_config['date_from'],
        date_to=league_config['date_to']
    )
    
    # Export data
    print("-" * 50)
    output_config = config['output']
    output_file = Path('output') / output_config['file']
    
    if output_config['format'] == 'json':
        DataExporter.to_json(players, str(output_file))
    elif output_config['format'] == 'csv':
        csv_file = str(output_file).replace('.json', '.csv')
        DataExporter.to_csv(players, csv_file)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Total players extracted: {len(players)}")
    print("=" * 50)


if __name__ == '__main__':
    main()
