#!/usr/bin/env python3
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from collections import OrderedDict

def load_data():
    with open('output/handball_players_detailed.json', 'r') as f:
        return json.load(f)

def get_teams_in_game(all_teams, game_id):
    teams = set()
    for tname, tdata in all_teams.items():
        for player in tdata['players']:
            for game in player.get('game_details', []):
                if game['game_id'] == game_id:
                    teams.add(tname)
                    break
    return list(teams)

def create_report():
    print("📊 Lade Daten...")
    data = load_data()
    all_teams = data['teams']
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    print(f"📋 {len(all_teams)} Teams gefunden\n")
    
    h_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    h_font = Font(color="FFFFFF", bold=True, size=10)
    s_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    s_font = Font(bold=True, size=9)
    p_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    p_font = Font(bold=True)
    c_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    l_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for tidx, (tname, tdata) in enumerate(sorted(all_teams.items()), 1):
        print(f"[{tidx}/{len(all_teams)}] {tname}...")
        
        sname = tname.replace('/', '-').replace('?', '').replace('[', '').replace(']', '')[:31]
        ws = wb.create_sheet(title=sname)
        
        players = sorted(tdata['players'], key=lambda p: p['name'])
        
        tgames = OrderedDict()
        for player in players:
            for game in player.get('game_details', []):
                if game['game_id'] not in tgames:
                    tgames_in = get_teams_in_game(all_teams, game['game_id'])
                    tgames[game['game_id']] = {
                        'date': game['date'],
                        'teams': tgames_in
                    }
        
        print(f"  -> {len(players)} Spieler, {len(tgames)} Spiele")
        
        labels = ["Tore", "2-Min", "Gelb", "Rot", "Blau"]
        
        col = 2
        for gid, ginfo in tgames.items():
            opp = [t for t in ginfo['teams'] if t != tname]
            opp_str = opp[0] if len(opp) == 1 else " vs ".join(opp) if opp else "Unknown"
            header = f"{ginfo['date']}\n{opp_str}"
            
            ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + 4)
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = h_font
            cell.fill = h_fill
            cell.alignment = c_align
            cell.border = border
            
            col += 5
        
        col = 2
        for _ in tgames:
            for label in labels:
                cell = ws.cell(row=2, column=col)
                cell.value = label
                cell.font = s_font
                cell.fill = s_fill
                cell.alignment = c_align
                cell.border = border
                col += 1
        
        a1 = ws.cell(row=1, column=1)
        a1.value = "Spieler"
        a1.font = h_font
        a1.fill = h_fill
        a1.alignment = c_align
        a1.border = border
        ws.merge_cells('A1:A2')
        
        # Collect stats for totals row
        game_totals = {}  # {game_idx: [goals, 2min, yellow, red, blue]}
        
        for prow, player in enumerate(players, start=3):
            ca = ws.cell(row=prow, column=1)
            ca.value = player['name']
            ca.font = p_font
            ca.fill = p_fill
            ca.alignment = l_align
            ca.border = border
            
            gmap = {g['game_id']: g for g in player.get('game_details', [])}
            
            col = 2
            game_idx = 0
            for gid in tgames.keys():
                if game_idx not in game_totals:
                    game_totals[game_idx] = [0, 0, 0, 0, 0]
                
                if gid in gmap:
                    g = gmap[gid]
                    stats = [g['goals'], g['two_min_penalties'], g['yellow_cards'], g['red_cards'], g['blue_cards']]
                else:
                    stats = [0, 0, 0, 0, 0]
                
                # Accumulate totals
                for i, sv in enumerate(stats):
                    game_totals[game_idx][i] += sv
                
                for sv in stats:
                    cell = ws.cell(row=prow, column=col)
                    cell.value = sv if sv > 0 else "-"
                    cell.alignment = c_align
                    cell.border = border
                    col += 1
                
                game_idx += 1
        
        # Add totals row
        totals_row = len(players) + 3
        total_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        total_font = Font(bold=True, size=10)
        
        ta = ws.cell(row=totals_row, column=1)
        ta.value = "GESAMT"
        ta.font = total_font
        ta.fill = total_fill
        ta.alignment = l_align
        ta.border = border
        
        col = 2
        for game_idx in range(len(tgames)):
            stats = game_totals[game_idx]
            for sv in stats:
                cell = ws.cell(row=totals_row, column=col)
                cell.value = sv if sv > 0 else "-"
                cell.font = total_font
                cell.fill = total_fill
                cell.alignment = c_align
                cell.border = border
                col += 1
        
        ws.column_dimensions['A'].width = 25
        for c in range(2, col):
            ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = 10
        
        ws.row_dimensions[1].height = 40
        ws.row_dimensions[2].height = 20
    
    wb.save('handball_players_report.xlsx')
    print(f"\n✅ Excel Report: handball_players_report.xlsx")
    print(f"   - Ein Tab pro Team")
    print(f"   - Spalte A: Spielernamen")
    print(f"   - Zeile 1: Datum + Gegner")
    print(f"   - Zeile 2: Tore, 2-Min, Gelb, Rot, Blau")

if __name__ == '__main__':
    create_report()
