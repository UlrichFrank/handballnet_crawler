#!/usr/bin/env python3
"""
GOAL TIMELINE VISUALIZATION
Generate graphics showing goal progression during handball matches.
"""

from typing import List, Dict
from collections import defaultdict


def calculate_game_flow(goals_timeline: List[Dict]) -> Dict:
    """
    Calculate complete game flow including:
    - Running score for each team
    - Momentum (consecutive goals)
    - Game situation after each goal (lead/tie/deficit)
    
    Args:
        goals_timeline: List of goals with {minute, second, scorer, team, seven_meter}
    
    Returns:
        Dict with enriched goal data including score, momentum, situation
    """
    
    if not goals_timeline:
        return {
            'goals': [],
            'total_goals': 0,
            'half1_goals': [],
            'half2_goals': []
        }
    
    enriched_goals = []
    home_score = 0
    away_score = 0
    last_scorer_team = None
    momentum = 1
    
    for goal in goals_timeline:
        team = goal['team']
        minute = goal['minute']
        
        # Update score
        if team == 'home':
            home_score += 1
        else:
            away_score += 1
        
        # Determine game situation based on which team scores and current score
        # 'lead': Team in Führung gehen/bleiben
        # 'tie': Ausgleich
        # 'deficit': Team in Rückstand geraten/bleiben
        if team == 'home':
            if home_score > away_score:
                situation = 'lead'      # Home team now leads
            elif home_score == away_score:
                situation = 'tie'       # Game is now tied
            else:
                situation = 'deficit'   # Home team still behind
        else:  # away team scored
            if away_score > home_score:
                situation = 'lead'      # Away team now leads
            elif away_score == home_score:
                situation = 'tie'       # Game is now tied
            else:
                situation = 'deficit'   # Away team still behind
        
        # Calculate momentum (consecutive goals by same team)
        if last_scorer_team == team:
            momentum += 1
        else:
            momentum = 1
            last_scorer_team = team
        
        enriched_goal = {
            **goal,
            'home_score': home_score,
            'away_score': away_score,
            'situation': situation,
            'momentum': momentum
        }
        
        enriched_goals.append(enriched_goal)
    
    # Separate into halves
    half1_goals = [g for g in enriched_goals if g['minute'] < 30]
    half2_goals = [g for g in enriched_goals if g['minute'] >= 30]
    
    return {
        'goals': enriched_goals,
        'total_goals': len(enriched_goals),
        'half1_goals': half1_goals,
        'half2_goals': half2_goals,
        'final_home_score': home_score,
        'final_away_score': away_score
    }


def prepare_graphic_data(game_flow: Dict, half_duration: int = 30) -> Dict:
    """
    Prepare data structure for graphic rendering.
    
    Organizes goals into 4 rows:
    - Row 1 (top): First half - Home team
    - Row 2: First half - Away team
    - Row 3: Second half - Home team
    - Row 4 (bottom): Second half - Away team
    
    Args:
        game_flow: Output from calculate_game_flow()
        half_duration: Minutes per half (usually 30)
    
    Returns:
        Dict with organized goal data for visualization
    """
    
    graphic_data = {
        'halves': [
            {
                'half': 1,
                'duration_minutes': half_duration,
                'home_goals': [],
                'away_goals': []
            },
            {
                'half': 2,
                'duration_minutes': half_duration,
                'home_goals': [],
                'away_goals': []
            }
        ],
        'final_score': f"{game_flow['final_home_score']}:{game_flow['final_away_score']}"
    }
    
    for goal in game_flow['goals']:
        minute = goal['minute']
        second = goal['second']
        
        # Calculate position in minutes (as float for precise positioning)
        time_in_minutes = minute + (second / 60.0)
        
        # Determine which half and team
        if minute < half_duration:
            half_idx = 0
        else:
            half_idx = 1
            time_in_minutes = time_in_minutes - half_duration
        
        # Prepare goal data for rendering
        goal_data = {
            'time_in_minutes': time_in_minutes,
            'scorer': goal['scorer'],
            'momentum': goal['momentum'],
            'situation': goal['situation'],
            'seven_meter': goal['seven_meter'],
            'score_home': goal['home_score'],
            'score_away': goal['away_score']
        }
        
        team_key = 'home_goals' if goal['team'] == 'home' else 'away_goals'
        graphic_data['halves'][half_idx][team_key].append(goal_data)
    
    return graphic_data


def determine_circle_color(situation: str, team: str) -> Dict:
    """
    Determine circle color based on game situation.
    
    Three situations (same for both teams):
    - lead: Team in Führung (Blau)
    - tie: Gleichstand (Grau)
    - deficit: Team im Rückstand (Orange)
    
    Returns:
        Dict with {fill_color, edge_color, alpha, pattern}
    """
    
    colors = {
        'lead': {
            'fill': '#3498db',      # Blue - team in lead
            'edge': '#2980b9',
            'alpha': 0.9,
            'pattern': 'solid'
        },
        'tie': {
            'fill': '#95a5a6',      # Gray - tied game
            'edge': '#7f8c8d',
            'alpha': 0.8,
            'pattern': 'solid'
        },
        'deficit': {
            'fill': '#e67e22',      # Orange - team in deficit
            'edge': '#d35400',
            'alpha': 0.9,
            'pattern': 'solid'
        }
    }
    
    return colors.get(situation, colors['tie'])



def calculate_circle_size(momentum: int) -> float:
    """
    Calculate circle radius based on momentum.
    Higher momentum = slightly larger circle.
    
    Args:
        momentum: Number of consecutive goals
    
    Returns:
        Radius size (in data units)
    """
    # Smaller base radius with lower momentum scaling
    base_radius = 0.12
    momentum_factor = 0.04  # Reduced from 0.15 to 0.04
    return base_radius + (momentum * momentum_factor)
