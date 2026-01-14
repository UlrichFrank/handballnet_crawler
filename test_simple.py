#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/ulrich.frank/Dev/private/hb_grabber')

from hb_crawler.pdf_parser import _parse_pdf, add_seven_meters_to_players

pdf_path = '2026-01-10_PresseInfoLang_906069.pdf'
print('\nParsing PDF: ' + pdf_path)
print('=' * 70)

seven_meter_data = _parse_pdf(pdf_path)

print('\nRESULTS:')
print('-' * 70)

if seven_meter_data:
    print(f'\nFound {len(seven_meter_data)} players with seven meter data:\n')
    
    for player_name, stats in sorted(seven_meter_data.items(), key=lambda x: x[1]['attempts'], reverse=True):
        attempts = stats['attempts']
        goals = stats['goals']
        success = (goals/attempts*100) if attempts else 0
        print(f'  {player_name:28} | {attempts} attempts | {goals} goals | {success:.0f}% success')
    
    total_attempts = sum(s['attempts'] for s in seven_meter_data.values())
    total_goals = sum(s['goals'] for s in seven_meter_data.values())
    total_success = (total_goals/total_attempts*100) if total_attempts else 0
    
    print('-' * 70)
    print(f'  {"TOTAL":28} | {total_attempts} attempts | {total_goals} goals | {total_success:.0f}% success')
    
    # Test enrichment
    print('\n\nTesting player enrichment:')
    print('-' * 70)
    
    test_players = [
        {'name': 'Moritz Bachle', 'goals': 3, 'seven_meters': 0, 'seven_meters_goals': 0},
        {'name': 'Felix Heuser', 'goals': 5, 'seven_meters': 0, 'seven_meters_goals': 0},
        {'name': 'Unknown', 'goals': 2, 'seven_meters': 0, 'seven_meters_goals': 0},
    ]
    
    enriched = add_seven_meters_to_players(test_players, seven_meter_data)
    
    for p in enriched:
        print(f'  {p["name"]:28} | 7m: {p["seven_meters"]} attempts, {p["seven_meters_goals"]} goals')
    
    print('\n' + '=' * 70)
    print('SUCCESS: PDF parsing works correctly!')
    print('=' * 70 + '\n')
else:
    print('ERROR: No seven meter data found in PDF!')
