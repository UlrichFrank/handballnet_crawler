"""Error logging and retry mechanism for failed games"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class ErrorLogger:
    """Manages failed game attempts for retry in future runs"""
    
    def __init__(self, error_log_path: str = 'frontend/public/error_log.json'):
        self.error_log_path = Path(error_log_path)
        self.failed_games: List[Dict[str, Any]] = []
        self.load_existing_errors()
    
    def load_existing_errors(self):
        """Load previously failed games from error log"""
        if self.error_log_path.exists():
            try:
                with open(self.error_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.failed_games = data.get('failed_games', [])
                    print(f"📋 Loaded {len(self.failed_games)} previously failed games for retry")
            except Exception as e:
                print(f"⚠️  Could not load error log: {e}")
                self.failed_games = []
        else:
            self.failed_games = []
    
    def add_failed_game(self, game_id: str, liga_id: str, date: str, 
                       home_team: str, away_team: str, error: str, 
                       retry_count: int = 0):
        """Log a failed game for retry"""
        failed_game = {
            'game_id': game_id,
            'liga_id': liga_id,
            'date': date,
            'home_team': home_team,
            'away_team': away_team,
            'error': error[:200],  # Truncate long errors
            'last_error_time': datetime.now().isoformat(),
            'retry_count': retry_count
        }
        self.failed_games.append(failed_game)
    
    def get_failed_games_for_retry(self) -> List[Dict[str, Any]]:
        """Get list of previously failed games to retry"""
        return self.failed_games.copy()
    
    def remove_successful_game(self, game_id: str):
        """Remove a game from failed list after successful retry"""
        self.failed_games = [g for g in self.failed_games if g['game_id'] != game_id]
    
    def increment_retry_count(self, game_id: str):
        """Increment retry attempt for a game"""
        for game in self.failed_games:
            if game['game_id'] == game_id:
                game['retry_count'] = game.get('retry_count', 0) + 1
                break
    
    def save(self):
        """Save error log to file"""
        try:
            self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'failed_games': self.failed_games,
                'last_updated': datetime.now().isoformat(),
                'total_failed': len(self.failed_games)
            }
            with open(self.error_log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Error log saved: {len(self.failed_games)} failed games")
        except Exception as e:
            print(f"❌ Could not save error log: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of failed games by liga"""
        summary = {}
        for game in self.failed_games:
            liga_id = game['liga_id']
            if liga_id not in summary:
                summary[liga_id] = []
            summary[liga_id].append({
                'game_id': game['game_id'],
                'teams': f"{game['home_team']} vs {game['away_team']}",
                'date': game['date'],
                'error': game['error'],
                'retry_count': game.get('retry_count', 0)
            })
        return summary
