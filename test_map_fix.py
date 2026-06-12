#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_generator import generate_map_content

def test_map():
    print('Testing map generation...')
    
    itinerary = {
        'destination': 'Hangzhou',
        'days': 2,
        'currency_symbol': 'RMB',
        'hotel': {'name': 'West Lake Hotel'},
        'daily_plan': [
            {
                'day': 1,
                'date': '2024-01-01',
                'attractions': [
                    {'name': 'West Lake', 'coord': [120.1552, 30.2741]},
                    {'name': 'Lingyin Temple', 'coord': [120.1416, 30.2964]}
                ],
                'transports': [
                    {'from': 'West Lake', 'to': 'Lingyin Temple', 'name': 'Taxi', 'icon': 'car', 'time': 25, 'cost': 35}
                ]
            },
            {
                'day': 2,
                'date': '2024-01-02',
                'attractions': [
                    {'name': 'Leifeng Pagoda', 'coord': [120.1618, 30.2337]}
                ],
                'transports': []
            }
        ]
    }
    
    try:
        result = generate_map_content(itinerary)
        print('SUCCESS: Map generated')
        print('HTML length:', len(result))
        
        # Save file
        os.makedirs('./public', exist_ok=True)
        with open('./public/test_result.html', 'w', encoding='utf-8') as f:
            f.write(result)
        print('File saved: ./public/test_result.html')
        return True
    except Exception as e:
        print('ERROR:', str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_map()