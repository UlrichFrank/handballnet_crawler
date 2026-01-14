#!/usr/bin/env python3
"""Test PDF parsing with local file"""

import sys
import os
os.chdir('/Users/ulrich.frank/Dev/private/hb_grabber')
sys.path.insert(0, '/Users/ulrich.frank/Dev/private/hb_grabber')

from hb_crawler.pdf_parser import _parse_pdf, add_seven_meters_to_players

pdf_path = '2026-01-10_PresseInfoLang_906069.pdf'

if not os.path.exists(pdf_path):
    print(f"ERROR: {pdf_path} not found")
    sys.exit(1)

print("\n" + "="*70)
print("FULL TEST: PDF Seven Meter Parsing")
print("="*70)

print(f"\n[1] Parsing: {pdf_path}")
seven_meter_data = _parse_pdf(pdf_path)

if not seven_meter_data:
    print("    ERROR: No seven meter data found")
    sys.exit(1)

print(f"    SUCCESS: Found {len(seven_meter_data)} players\n")

print("[2] Seven Meter Results:")
print("-"*70)

for player_name, stats in sorted(seven_meter_data.items(), key=lambda x: x[1]['attempts'], reverse=True):
    attempts = stats['attempts']
    goals = stats['goals']
    success = (goals/attempts*100) if attempts else 0
    print(f"    {player_name:28} | {attempts} attempts | {goals} goals | {success:.0f}% success")

total_attempts = sum(s['attempts'] for s in seven_meter_data.values())
total_goals = sum(s['goals'] for s in seven_meter_data.values())
total_success = (total_goals/total_attempts*100) if total_attempts else 0
print("-"*70)
print(f"    {'TOTAL':28} | {total_attempts} attempts | {total_goals} goals | {total_success:.0f}% success")

print("\n[3] Testing player enrichment:")
print("-"*70)

test_players = [
    {'name': 'Moritz Bächle', 'goals': 3, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
    {'name': 'Matti Kraaz', 'goals': 1, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
    {'name': 'Felix Heuser', 'goals': 5, 'two_min_penalties': 0, 'yellow_cards': 0, 'red_cards': 0, 'blue_cards': 0, 'seven_meters': 0, 'seven_meters_goals': 0},
]

enriched = add_seven_meters_to_players(test_players, seven_meter_data)

for p in enriched:
    found = "FOUND" if p['name'] in seven_meter_data else "no data"
    print(f"    {p['name']:28} | 7m: {p['seven_meters']} attempts, {p['seven_meters_goals']} goals ({found})")

print("\n" + "="*70)
print("SUCCESS: All tests passed!")
print("="*70 + "\n")
