#!/usr/bin/env python3
"""
Debug search API issues
"""

import requests

def debug_search():
    print('🔍 Debugging search API 400 error')
    print('='*40)

    # Test different search parameters
    test_cases = [
        '/api/search?query=Sol',
        '/api/search?q=Sol', 
        '/api/search?query=Tiefe',
        '/api/search?q=Tiefe',
        '/api/search',
    ]

    for url in test_cases:
        full_url = 'http://localhost:8080' + url
        print(f'Testing: {url}')
        try:
            r = requests.get(full_url)
            print(f'  Status: {r.status_code}')
            if r.status_code != 200:
                print(f'  Error: {r.text[:200]}')
            else:
                data = r.json()
                print(f'  Success: {data.get("count", 0)} results')
        except Exception as e:
            print(f'  Exception: {e}')
        print()

if __name__ == '__main__':
    debug_search()