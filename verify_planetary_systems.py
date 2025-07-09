#!/usr/bin/env python3
"""
Verify that all fictional planets are properly attached to real world stars
Checks for:
1. Fictional planets using real star IDs (not fictional 200xxx IDs)
2. Fictional planets attached to stars that don't exist
3. Proper mapping after star ID de-duplication
"""

import pandas as pd
import json
from fictional_planets import fictional_planet_systems
from fictional_names import fictional_star_names

def main():
    print("🔍 PLANETARY SYSTEMS VERIFICATION")
    print("="*60)
    
    # Load real stars
    real_stars = pd.read_csv('stars_output.csv')
    real_star_ids = set(real_stars['id'].tolist())
    
    # Load fictional stars
    fictional_stars = pd.read_csv('fictional_stars.csv')
    fictional_star_ids = set(fictional_stars['id'].tolist())
    
    print(f"📊 DATA OVERVIEW:")
    print(f"  - Real stars: {len(real_stars):,}")
    print(f"  - Fictional stars: {len(fictional_stars):,}")
    print(f"  - Planetary systems: {len(fictional_planet_systems):,}")
    
    # Analyze planetary systems
    print(f"\n🪐 PLANETARY SYSTEMS ANALYSIS:")
    print("="*60)
    
    all_systems = []
    real_star_systems = []
    fictional_star_systems = []
    missing_star_systems = []
    
    total_planets = 0
    
    for star_id, planets in fictional_planet_systems.items():
        total_planets += len(planets)
        
        system_info = {
            'star_id': star_id,
            'planet_count': len(planets),
            'planets': planets,
            'star_type': 'unknown',
            'star_exists': False,
            'star_name': 'Unknown'
        }
        
        if star_id in real_star_ids:
            system_info['star_type'] = 'real'
            system_info['star_exists'] = True
            real_star_info = real_stars[real_stars['id'] == star_id].iloc[0]
            system_info['star_name'] = real_star_info.get('proper', f'Star {star_id}')
            real_star_systems.append(system_info)
        elif star_id in fictional_star_ids:
            system_info['star_type'] = 'fictional'
            system_info['star_exists'] = True
            fictional_star_info = fictional_stars[fictional_stars['id'] == star_id].iloc[0]
            system_info['star_name'] = fictional_star_info.get('proper', f'Star {star_id}')
            fictional_star_systems.append(system_info)
        else:
            system_info['star_type'] = 'missing'
            system_info['star_exists'] = False
            missing_star_systems.append(system_info)
        
        all_systems.append(system_info)
    
    print(f"📋 SYSTEM BREAKDOWN:")
    print(f"  - Total planetary systems: {len(fictional_planet_systems):,}")
    print(f"  - Total planets: {total_planets:,}")
    print(f"  - Systems around real stars: {len(real_star_systems):,}")
    print(f"  - Systems around fictional stars: {len(fictional_star_systems):,}")
    print(f"  - Systems with missing stars: {len(missing_star_systems):,}")
    
    # Check for 200xxx IDs (problematic fictional IDs)
    print(f"\n🔍 CHECKING FOR PROBLEMATIC FICTIONAL IDs (200xxx):")
    print("="*60)
    
    problematic_ids = []
    for star_id in fictional_planet_systems.keys():
        if str(star_id).startswith('200'):
            problematic_ids.append(star_id)
    
    if problematic_ids:
        print(f"❌ Found {len(problematic_ids)} systems using 200xxx IDs:")
        for star_id in problematic_ids:
            system = next(s for s in all_systems if s['star_id'] == star_id)
            print(f"  - ID {star_id}: {system['planet_count']} planets, Star: {system['star_name']}")
    else:
        print("✅ No problematic 200xxx IDs found")
    
    # Detailed analysis of each system
    print(f"\n📊 DETAILED SYSTEM ANALYSIS:")
    print("="*60)
    
    print(f"\n🌟 REAL STAR SYSTEMS ({len(real_star_systems)}):")
    for system in sorted(real_star_systems, key=lambda x: x['planet_count'], reverse=True):
        star_info = real_stars[real_stars['id'] == system['star_id']].iloc[0]
        fictional_name = fictional_star_names.get(system['star_id'], {}).get('fictional_name', 'N/A')
        
        confirmed_planets = sum(1 for p in system['planets'] if p.get('confirmed', False))
        fictional_planets = sum(1 for p in system['planets'] if not p.get('confirmed', False))
        
        print(f"  ✅ ID {system['star_id']}: {system['star_name']}")
        print(f"     Fictional name: {fictional_name}")
        print(f"     Distance: {star_info.get('dist', 'N/A'):.2f} ly")
        print(f"     Spectral type: {star_info.get('spect', 'N/A')}")
        print(f"     Planets: {system['planet_count']} ({confirmed_planets} confirmed, {fictional_planets} fictional)")
        print()
    
    print(f"\n🎭 FICTIONAL STAR SYSTEMS ({len(fictional_star_systems)}):")
    for system in sorted(fictional_star_systems, key=lambda x: x['planet_count'], reverse=True):
        star_info = fictional_stars[fictional_stars['id'] == system['star_id']].iloc[0]
        fictional_name = fictional_star_names.get(system['star_id'], {}).get('fictional_name', 'N/A')
        
        confirmed_planets = sum(1 for p in system['planets'] if p.get('confirmed', False))
        fictional_planets = sum(1 for p in system['planets'] if not p.get('confirmed', False))
        
        print(f"  🎭 ID {system['star_id']}: {system['star_name']}")
        print(f"     Fictional name: {fictional_name}")
        print(f"     Distance: {star_info.get('dist', 'N/A'):.2f} ly")
        print(f"     Spectral type: {star_info.get('spect', 'N/A')}")
        print(f"     Planets: {system['planet_count']} ({confirmed_planets} confirmed, {fictional_planets} fictional)")
        print()
    
    if missing_star_systems:
        print(f"\n❌ MISSING STAR SYSTEMS ({len(missing_star_systems)}):")
        for system in sorted(missing_star_systems, key=lambda x: x['planet_count'], reverse=True):
            print(f"  ❌ ID {system['star_id']}: {system['planet_count']} planets, Star not found in database")
            print(f"     Sample planet: {system['planets'][0]['name']}")
            print()
    
    # Check for proper de-duplication
    print(f"\n🔄 CHECKING STAR ID DE-DUPLICATION:")
    print("="*60)
    
    # Check if any systems use stars that were supposed to be de-duplicated
    deduplication_issues = []
    
    for system in all_systems:
        star_id = system['star_id']
        
        # Check if this star has a fictional name mapping
        if star_id in fictional_star_names:
            fictional_name = fictional_star_names[star_id]['fictional_name']
            
            # Check if this star exists in both real and fictional datasets
            is_real = star_id in real_star_ids
            is_fictional = star_id in fictional_star_ids
            
            if is_real and is_fictional:
                deduplication_issues.append({
                    'star_id': star_id,
                    'fictional_name': fictional_name,
                    'planet_count': system['planet_count'],
                    'issue': 'Star exists in both real and fictional datasets'
                })
            elif not is_real and not is_fictional:
                deduplication_issues.append({
                    'star_id': star_id,
                    'fictional_name': fictional_name,
                    'planet_count': system['planet_count'],
                    'issue': 'Star missing from both datasets'
                })
    
    if deduplication_issues:
        print(f"❌ Found {len(deduplication_issues)} de-duplication issues:")
        for issue in deduplication_issues:
            print(f"  - ID {issue['star_id']} ({issue['fictional_name']}): {issue['issue']}")
    else:
        print("✅ No de-duplication issues found")
    
    # Final verification
    print(f"\n🎯 FINAL VERIFICATION:")
    print("="*60)
    
    all_good = True
    
    # Check 1: All systems should use real star IDs
    fictional_id_systems = len([s for s in all_systems if s['star_type'] == 'fictional'])
    if fictional_id_systems > 0:
        print(f"⚠️  {fictional_id_systems} systems use fictional star IDs")
        all_good = False
    else:
        print("✅ All systems use real star IDs")
    
    # Check 2: No missing stars
    if len(missing_star_systems) > 0:
        print(f"❌ {len(missing_star_systems)} systems reference missing stars")
        all_good = False
    else:
        print("✅ All systems reference existing stars")
    
    # Check 3: No 200xxx IDs
    if len(problematic_ids) > 0:
        print(f"❌ {len(problematic_ids)} systems use problematic 200xxx IDs")
        all_good = False
    else:
        print("✅ No problematic 200xxx IDs found")
    
    # Check 4: No de-duplication issues
    if len(deduplication_issues) > 0:
        print(f"❌ {len(deduplication_issues)} de-duplication issues found")
        all_good = False
    else:
        print("✅ No de-duplication issues found")
    
    if all_good:
        print(f"\n🎉 ALL CHECKS PASSED!")
        print("✅ All fictional planets are properly attached to real world stars")
        print("✅ Star ID de-duplication is working correctly")
        print("✅ No problematic fictional IDs found")
    else:
        print(f"\n⚠️  ISSUES FOUND - See details above")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print("="*60)
    print(f"🌟 Star Systems:")
    print(f"  - Real stars with planets: {len(real_star_systems)}")
    print(f"  - Fictional stars with planets: {len(fictional_star_systems)}")
    print(f"  - Missing stars: {len(missing_star_systems)}")
    print(f"  - Total systems: {len(all_systems)}")
    
    print(f"\n🪐 Planets:")
    print(f"  - Total planets: {total_planets}")
    print(f"  - Confirmed planets: {sum(sum(1 for p in s['planets'] if p.get('confirmed', False)) for s in all_systems)}")
    print(f"  - Fictional planets: {sum(sum(1 for p in s['planets'] if not p.get('confirmed', False)) for s in all_systems)}")
    
    # Create a detailed report
    print(f"\n📋 CREATING DETAILED REPORT...")
    
    report = {
        'verification_summary': {
            'total_systems': len(all_systems),
            'real_star_systems': len(real_star_systems),
            'fictional_star_systems': len(fictional_star_systems),
            'missing_star_systems': len(missing_star_systems),
            'total_planets': total_planets,
            'problematic_ids': len(problematic_ids),
            'deduplication_issues': len(deduplication_issues),
            'all_checks_passed': all_good
        },
        'systems_by_type': {
            'real_stars': [
                {
                    'star_id': s['star_id'],
                    'star_name': s['star_name'],
                    'fictional_name': fictional_star_names.get(s['star_id'], {}).get('fictional_name', 'N/A'),
                    'planet_count': s['planet_count'],
                    'confirmed_planets': sum(1 for p in s['planets'] if p.get('confirmed', False)),
                    'fictional_planets': sum(1 for p in s['planets'] if not p.get('confirmed', False))
                } for s in real_star_systems
            ],
            'fictional_stars': [
                {
                    'star_id': s['star_id'],
                    'star_name': s['star_name'],
                    'fictional_name': fictional_star_names.get(s['star_id'], {}).get('fictional_name', 'N/A'),
                    'planet_count': s['planet_count'],
                    'confirmed_planets': sum(1 for p in s['planets'] if p.get('confirmed', False)),
                    'fictional_planets': sum(1 for p in s['planets'] if not p.get('confirmed', False))
                } for s in fictional_star_systems
            ],
            'missing_stars': [
                {
                    'star_id': s['star_id'],
                    'planet_count': s['planet_count'],
                    'sample_planet': s['planets'][0]['name'] if s['planets'] else 'N/A'
                } for s in missing_star_systems
            ]
        },
        'issues': {
            'problematic_ids': problematic_ids,
            'deduplication_issues': deduplication_issues
        }
    }
    
    with open('planetary_systems_verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✅ Report saved to planetary_systems_verification_report.json")

if __name__ == "__main__":
    main()