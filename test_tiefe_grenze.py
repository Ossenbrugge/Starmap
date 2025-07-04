#!/usr/bin/env python3
"""
Test script for Tiefe-Grenze Tor fictional star
"""

import requests

def test_tiefe_grenze():
    print('🔍 Testing Tiefe-Grenze Tor after magnitude filter fix')
    print('='*55)

    # Get all stars and check for Tiefe-Grenze Tor
    r = requests.get('http://localhost:8080/api/stars')
    if r.status_code == 200:
        stars = r.json()
        
        # Find Tiefe-Grenze Tor
        tiefe_star = None
        for star in stars:
            if star['id'] == 999999:
                tiefe_star = star
                break
        
        if tiefe_star:
            print('✅ Found Tiefe-Grenze Tor in stars list:')
            print(f'  ID: {tiefe_star["id"]}')
            print(f'  Name: {tiefe_star["name"]}')
            print(f'  Magnitude: {tiefe_star.get("mag", "unknown")}')
            print(f'  Fictional Name: {tiefe_star.get("fictional_name", "none")}')
            print(f'  Fictional Source: {tiefe_star.get("fictional_source", "none")}')
            print(f'  Nation: {tiefe_star["nation"]["name"]}')
            
            if tiefe_star.get('fictional_name') == 'Tiefe-Grenze Tor':
                print('\n🎉 SUCCESS: Fictional name is working!')
            elif tiefe_star['name'] == 'Tiefe-Grenze Tor':
                print('\n🎉 PARTIAL SUCCESS: Star name is correct (this is actually the fictional name)')
            else:
                print('\n❌ Still issues with the star data')
        else:
            print('❌ Tiefe-Grenze Tor still not found in stars list')
            print(f'   (Loaded {len(stars)} total stars)')
            
            # Check if any stars have magnitude > 6
            high_mag_stars = [s for s in stars if s.get('mag', 0) > 6.0]
            print(f'   Stars with magnitude > 6.0: {len(high_mag_stars)}')
            
            # Check if any fictional stars exist
            fictional_stars = [s for s in stars if s.get('fictional_name') and s['fictional_name'] != 'none']
            print(f'   Stars with fictional names: {len(fictional_stars)}')
            for fstar in fictional_stars:
                print(f'     - {fstar["fictional_name"]} (ID: {fstar["id"]}, mag: {fstar.get("mag", "unknown")})')
    else:
        print(f'Error getting stars: {r.status_code}')

    # Test search functionality  
    print('\n🔍 Testing search for Tiefe-Grenze Tor...')
    r = requests.get('http://localhost:8080/api/search?query=Tiefe')
    if r.status_code == 200:
        data = r.json()
        print(f'Search results for "Tiefe": {data.get("count", 0)} matches')
        for result in data.get('results', []):
            print(f'  - {result.get("name", "unknown")} (ID: {result.get("id", "unknown")})')
    else:
        print(f'Search failed: {r.status_code}')

if __name__ == '__main__':
    test_tiefe_grenze()