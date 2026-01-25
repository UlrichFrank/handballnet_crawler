#!/usr/bin/env python3
"""
GOAL TIMELINE GRAPHIC GENERATOR
Create visualization graphics for goal progression.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
from pathlib import Path
from typing import Dict
import os


def generate_goal_timeline_graphic(game_data: Dict, output_path: str = None, half_duration: int = None) -> str:
    """
    Generate goal timeline graphic showing both halves.
    
    Args:
        game_data: Dict with game info and goals_timeline
        output_path: Where to save the graphic (default: output/graphics/)
        half_duration: Minutes per half (default: from game_data or 30)
    
    Returns:
        Path to generated graphic
    """
    
    if not game_data.get('goals_timeline'):
        print("    ⚠️  No goals_timeline data, skipping graphic generation")
        return None
    
    from goal_visualization import calculate_game_flow, prepare_graphic_data
    
    # Determine half duration
    if half_duration is None:
        half_duration = game_data.get('half_duration', 30)
    
    home_team = game_data['home']['team_name']
    away_team = game_data['away']['team_name']
    final_score = game_data.get('final_score', f"?:?")
    
    # Calculate game flow
    print(f"       📊 Generiere Grafik: {home_team} vs {away_team} ({final_score})")
    game_flow = calculate_game_flow(game_data['goals_timeline'])
    graphic_data = prepare_graphic_data(game_flow, half_duration=half_duration)
    
    game_date = game_data.get('date', 'Unknown')
    
    # Create figure - reduced height, no title
    fig, axes = plt.subplots(2, 1, figsize=(16, 4))
    # Remove the figure title completely
    
    # Render both halves
    for half_idx, (ax, half_data) in enumerate(zip(axes, graphic_data['halves'])):
        duration = half_data['duration_minutes']
        goals_count = len(half_data['home_goals']) + len(half_data['away_goals'])
        
        _render_half(
            ax, 
            duration,
            half_data['home_goals'],
            half_data['away_goals'],
            home_team,
            away_team,
            half_number=half_idx + 1
        )
    
    plt.tight_layout()
    
    # Determine output path
    if not output_path:
        output_dir = Path('output/graphics')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename from teams and date
        safe_home = game_data['home']['team_name'].replace('/', '_').replace(' ', '_')[:20]
        safe_away = game_data['away']['team_name'].replace('/', '_').replace(' ', '_')[:20]
        safe_date = game_date.replace(', ', '_').replace('.', '').replace(' ', '')
        filename = f"{safe_home}_vs_{safe_away}_{safe_date}.png"
        output_path = str(output_dir / filename)
    
    # Save figure
    os.makedirs(Path(output_path).parent, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Get file size
    file_size_kb = Path(output_path).stat().st_size / 1024
    total_goals = len(game_data['goals_timeline'])
    
    print(f"          ✅ Grafik gespeichert: {Path(output_path).name} ({file_size_kb:.1f} KB, {total_goals} Tore)")
    
    return output_path


def _render_half(ax, duration: int, 
                 home_goals: list, away_goals: list,
                 home_team: str, away_team: str,
                 half_number: int = 1):
    """
    Render a single half (top = home, bottom = away).
    
    Args:
        ax: Matplotlib axis
        duration: Duration in minutes
        home_goals: List of home team goals
        away_goals: List of away team goals
        home_team: Home team name
        away_team: Away team name
        half_number: 1 for first half, 2 for second half (for minute labels)
    """
    
    from goal_visualization import determine_circle_color, calculate_circle_size
    
    # Setup axis
    ax.set_xlim(-1, duration + 1)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    
    # Remove y-axis completely - no team names displayed
    ax.set_yticks([])
    ax.set_yticklabels([])
    
    # X-axis (minutes) - remove all ticks and labels
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # Remove ALL grid lines
    ax.grid(False)
    
    # Calculate actual minute labels based on half number
    start_minute = (half_number - 1) * duration
    
    # Add minute labels at bottom - show actual game minutes
    for minute_offset in range(0, duration + 1, 5):
        actual_minute = start_minute + minute_offset
        ax.text(minute_offset, -1.3, f"{actual_minute}'", ha='center', fontsize=9)
    
    # Add dotted horizontal line between teams (separator line)
    ax.plot([-1, duration + 1], [0, 0], 'k--', linewidth=1, alpha=0.3, zorder=1)
    
    # Remove all spines (no visible borders except dotted line)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Draw goals for home team (top)
    for goal in home_goals:
        x = goal['time_in_minutes']
        y = 0.6  # Home team row
        
        color_info = determine_circle_color(goal['situation'], 'home')
        radius = calculate_circle_size(goal['momentum'])
        
        circle = Circle(
            (x, y),
            radius,
            color=color_info['fill'],
            ec=color_info['edge'],
            linewidth=2,
            alpha=color_info['alpha'],
            zorder=3
        )
        ax.add_patch(circle)
        
        # Add momentum number only for high momentum
        if goal['momentum'] > 3:
            ax.text(x, y, str(goal['momentum']), 
                   ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    
    # Draw goals for away team (bottom)
    for goal in away_goals:
        x = goal['time_in_minutes']
        y = -0.6  # Away team row
        
        color_info = determine_circle_color(goal['situation'], 'away')
        radius = calculate_circle_size(goal['momentum'])
        
        circle = Circle(
            (x, y),
            radius,
            color=color_info['fill'],
            ec=color_info['edge'],
            linewidth=2,
            alpha=color_info['alpha'],
            zorder=3
        )
        ax.add_patch(circle)
        
        # Add momentum number only for high momentum
        if goal['momentum'] > 3:
            ax.text(x, y, str(goal['momentum']), 
                   ha='center', va='center', fontsize=7, fontweight='bold', color='white')
