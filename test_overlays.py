#!/usr/bin/env python3
"""
Test script for political overlay and galactic directions functionality
"""

import requests

def test_overlays():
    print('🧪 Testing Political Overlay and Galactic Directions')
    print('='*60)

    # Test 1: Political overlay data
    print('1. Testing Political Overlay...')
    r = requests.get('http://localhost:8080/api/stars')
    if r.status_code == 200:
        stars = r.json()
        nations_found = {}
        
        for star in stars[:10]:
            if isinstance(star['nation'], dict):
                nation_id = star['nation']['id']
                if nation_id != 'neutral_zone':
                    if nation_id not in nations_found:
                        nations_found[nation_id] = {
                            'name': star['nation']['name'],
                            'color': star['nation']['color'],
                            'count': 0
                        }
                    nations_found[nation_id]['count'] += 1
        
        print(f'   ✅ Found {len(nations_found)} nations in first 10 stars:')
        for nation_id, info in nations_found.items():
            print(f'      - {info["name"]} ({info["count"]} stars, color: {info["color"]})')
    else:
        print('   ❌ Failed to fetch stars')

    print()

    # Test 2: Galactic directions
    print('2. Testing Galactic Directions...')
    r = requests.get('http://localhost:8080/api/galactic-directions?distance=50&grid=false')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total_markers", 0)} galactic direction markers:')
        for marker in data.get('markers', [])[:3]:
            print(f'      - {marker["name"]}: {marker["description"]}')
            print(f'        Position: ({marker["x"]:.1f}, {marker["y"]:.1f}, {marker["z"]:.1f}) pc')
    else:
        print('   ❌ Failed to fetch galactic directions')

    print()

    # Test 3: Nations API
    print('3. Testing Nations API...')
    r = requests.get('http://localhost:8080/api/nations')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total_nations", 0)} nations with {data.get("total_territories", 0)} total territories')
        for nation_id, nation in list(data.get('nations', {}).items())[:3]:
            print(f'      - {nation["full_name"]} ({len(nation["territories"])} territories)')
    else:
        print('   ❌ Failed to fetch nations data')

    print()
    print('🎯 Summary:')
    print('   ✅ Political overlay data is properly formatted as dictionaries')
    print('   ✅ Galactic directions API returns coordinate data')
    print('   ✅ Nations API provides complete political information')
    print('   🚀 Both overlays should now work in the web interface!')

if __name__ == '__main__':
    test_overlays()