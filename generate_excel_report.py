#!/usr/bin/env python3
"""
Generate Excel report from game-centric handball_games.json
Shows for each team: HOME and AWAY games with all player statistics
"""

import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from collections import OrderedDict

def load_games_data():
    """Load game-centric data"""
    with open('output/handball_games.json', 'r') as f:
        return json.load(f)

def create_report():
    print("📊 Lade Spieldaten...")
    data = load_games_data()
    games = data['games']
    
    # Collect all teams and their games (home and away)
    team_games = {}
    
    for game in games:
        home_team = game['home']['team_name']
        away_team = game['away']['team_name']
        game_id = game['game_id']
        date = game['date']
        
        if not home_team or not away_team:
            continue
        
        # Home game
        if home_team not in team_games:
            team_games[home_team] = OrderedDict()
        team_games[home_team][game_id] = {
            'date': date,
            'opponent': away_team,
            'is_home': True,
            'players': game['home']['players']
        }
        
        # Away game
        if away_team not in team_games:
            team_games[away_team] = OrderedDict()
        team_games[away_team][game_id] = {
            'date': date,
            'opponent': home_team,
            'is_home': False,
            'players': game['away']['players']
        }
    
    print(f"📋 {len(team_games)} Teams gefunden\n")
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    h_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    h_font = Font(color="FFFFFF", bold=True, size=10)
    s_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    s_font = Font(bold=True, size=9)
    p_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    p_font = Font(bold=True)
    c_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    l_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    total_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    total_font = Font(bold=True, size=10)
    
    labels = ["Tore", "2-Min", "Gelb", "Rot", "Blau"]
    
    for tidx, (team_name, games_dict) in enumerate(sorted(team_games.items()), 1):
        print(f"[{tidx}/{len(team_games)}] {team_name}...")
        
        sname = team_name.replace('/', '-').replace('?', '').replace('[', '').replace(']', '')[:31]
        ws = wb.create_sheet(title=sname)
        
        all_players_set = set()
        for game_data in games_dict.values():
            for player in game_data['players']:
                all_players_set.add(player['name'])
        
        players = sorted(list(all_players_set))
        
        print(f"  -> {len(players)} Spieler, {len(games_dict)} Spiele (Heim + Auswärts)")
        
        col = 2
        for game_id, game_data in games_dict.items():
            home_away = "🏠" if game_data['is_home'] else "🏃"
            header = f"{game_data['date']}\n{home_away} {team_name}\nvs\n{game_data['opponent']}"
            
            ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + 4)
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = h_font
            cell.fill = h_fill
            cell.alignment = c_align
            cell.border = border
            
            col += 5
        
        col = 2
        for _ in games_dict:
            for label in labels:
                cell = ws.cell(row=2, column=col)
                cell.value = label
                cell.font = s_font
                cell.fill = s_fill
                cell.alignment = c_align
                cell.border = border
                col += 1
        
        a1 = ws.cell(row=1, column=1)
        a1.value = "Match"
        a1.font = h_font
        a1.fill = h_fill
        a1.alignment = c_align
        a1.border = border
        
        a2 = ws.cell(row=2, column=1)
        a2.value = "Player"
        a2.font = s_font
        a2.fill = s_fill
        a2.alignment = c_align
        a2.border = border
        
        game_totals = {}
        
        for prow, player_name in enumerate(players, start=3):
            ca = ws.cell(row=prow, column=1)
            ca.value = player_name
            ca.font = p_font
            ca.fill = p_fill
            ca.alignment = l_align
            ca.border = border
            
            col = 2
            game_idx = 0
            for game_id, game_data in games_dict.items():
                if game_idx not in game_totals:
                    game_totals[game_idx] = [0, 0, 0, 0, 0]
                
                player_stats = None
                for player in game_data['players']:
                    if player['name'] == player_name:
                        player_stats = player
                        break
                
                if player_stats:
                    stats = [
                        player_stats['goals'],
                        player_stats['two_min_penalties'],
                        player_stats['yellow_cards'],
                        player_stats['red_cards'],
                        player_stats['blue_cards']
                    ]
                    for i, val in enumerate(stats):
                        game_totals[game_idx][i] += val
                else:
                    stats = [0, 0, 0, 0, 0]
                
                for stat_val in stats:
                    cell = ws.cell(row=prow, column=col)
                    cell.value = stat_val if stat_val > 0 else "-"
                    cell.alignment = c_align
                    cell.border = border
                    col += 1
                
                game_idx += 1
        
        totals_row = len(players) + 3
        
        ta = ws.cell(row=totals_row, column=1)
        ta.value = "GESAMT"
        ta.font = total_font
        ta.fill = total_fill
        ta.alignment = l_align
        ta.border = border
        
        col = 2
        for game_idx in range(len(games_dict)):
            stats = game_totals[game_idx]
            for stat_val in stats:
                cell = ws.cell(row=totals_row, column=col)
                cell.value = stat_val if stat_val > 0 else "-"
                cell.font = total_font
                cell.fill = total_fill
                cell.alignment = c_align
                cell.border = border
                col += 1
        
        ws.column_dimensions['A'].width = 25
        for c in range(2, col):
            ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = 10
        
        ws.row_dimensions[1].height = 50
        ws.row_dimensions[2].height = 20
    
    wb.save('handball_players_report.xlsx')
    print(f"\n✅ Excel Report: handball_players_report.xlsx")
    print(f"   - Ein Tab pro Team")
    print(f"   - ALLE Spiele (Heim 🏠 + Auswärts 🏃)")
    print(f"   - Spielerdaten aus beiden Aufstellungen")
    print(f"   - GESAMT-Zeile mit Summen")

if __name__ == '__main__':
    create_report()
