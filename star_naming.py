#!/usr/bin/env python3
"""
Star Naming System for Starmap Application
Provides hierarchical naming with preference for common names and constellation identifiers
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple

class StarNamingSystem:
    def __init__(self):
        """Initialize the star naming system"""
        self.constellation_names = {
            'And': 'Andromedae', 'Ant': 'Antliae', 'Aps': 'Apodis', 'Aqr': 'Aquarii', 'Aql': 'Aquilae',
            'Ara': 'Arae', 'Ari': 'Arietis', 'Aur': 'Aurigae', 'Boo': 'Boötis', 'Cae': 'Caeli',
            'Cam': 'Camelopardalis', 'Cnc': 'Cancri', 'CVn': 'Canum Venaticorum', 'CMa': 'Canis Majoris',
            'CMi': 'Canis Minoris', 'Cap': 'Capricorni', 'Car': 'Carinae', 'Cas': 'Cassiopeiae',
            'Cen': 'Centauri', 'Cep': 'Cephei', 'Cet': 'Ceti', 'Cha': 'Chamaeleontis', 'Cir': 'Circini',
            'Col': 'Columbae', 'Com': 'Comae Berenices', 'CrA': 'Coronae Australis', 'CrB': 'Coronae Borealis',
            'Crv': 'Corvi', 'Crt': 'Crateris', 'Cru': 'Crucis', 'Cyg': 'Cygni', 'Del': 'Delphini',
            'Dor': 'Doradus', 'Dra': 'Draconis', 'Equ': 'Equulei', 'Eri': 'Eridani', 'For': 'Fornacis',
            'Gem': 'Geminorum', 'Gru': 'Gruis', 'Her': 'Herculis', 'Hor': 'Horologii', 'Hya': 'Hydrae',
            'Hyi': 'Hydri', 'Ind': 'Indi', 'Lac': 'Lacertae', 'Leo': 'Leonis', 'LMi': 'Leonis Minoris',
            'Lep': 'Leporis', 'Lib': 'Librae', 'Lup': 'Lupi', 'Lyn': 'Lyncis', 'Lyr': 'Lyrae',
            'Men': 'Mensae', 'Mic': 'Microscopii', 'Mon': 'Monocerotis', 'Mus': 'Muscae', 'Nor': 'Normae',
            'Oct': 'Octantis', 'Oph': 'Ophiuchi', 'Ori': 'Orionis', 'Pav': 'Pavonis', 'Peg': 'Pegasi',
            'Per': 'Persei', 'Phe': 'Phoenicis', 'Pic': 'Pictoris', 'Psc': 'Piscium', 'PsA': 'Piscis Austrini',
            'Pup': 'Puppis', 'Pyx': 'Pyxidis', 'Ret': 'Reticuli', 'Sge': 'Sagittae', 'Sgr': 'Sagittarii',
            'Sco': 'Scorpii', 'Scl': 'Sculptoris', 'Sct': 'Scuti', 'Ser': 'Serpentis', 'Sex': 'Sextantis',
            'Tau': 'Tauri', 'Tel': 'Telescopii', 'Tri': 'Trianguli', 'TrA': 'Trianguli Australis',
            'Tuc': 'Tucanae', 'UMa': 'Ursa Majoris', 'UMi': 'Ursa Minoris', 'Vel': 'Velorum',
            'Vir': 'Virginis', 'Vol': 'Volantis', 'Vul': 'Vulpeculae'
        }
        
        self.greek_letters = {
            'Alp': 'α', 'Bet': 'β', 'Gam': 'γ', 'Del': 'δ', 'Eps': 'ε', 'Zet': 'ζ', 'Eta': 'η', 'The': 'θ',
            'Iot': 'ι', 'Kap': 'κ', 'Lam': 'λ', 'Mu': 'μ', 'Nu': 'ν', 'Xi': 'ξ', 'Omi': 'ο', 'Pi': 'π',
            'Rho': 'ρ', 'Sig': 'σ', 'Tau': 'τ', 'Ups': 'υ', 'Phi': 'φ', 'Chi': 'χ', 'Psi': 'ψ', 'Ome': 'ω'
        }

    def clean_value(self, value) -> str:
        """Clean and normalize a value from the CSV"""
        if pd.isna(value) or value == '' or value == 'Null' or str(value).strip() == '':
            return ''
        return str(value).strip()

    def format_constellation_designation(self, bayer: str, flamsteed: str, constellation: str, 
                                      component: str = '') -> str:
        """Format a proper constellation designation like '20 LMi' or 'α Cen A'"""
        if not constellation:
            return ''
            
        # Handle component designation (A, B, etc.)
        comp_suffix = f' {component}' if component and component not in ['1', ''] else ''
        
        # Prefer Flamsteed number if available
        if flamsteed and flamsteed != '0.0':
            flamsteed_num = str(int(float(flamsteed))) if '.' in str(flamsteed) else str(flamsteed)
            return f'{flamsteed_num} {constellation}{comp_suffix}'
        
        # Use Bayer designation with Greek letter
        elif bayer:
            # Clean up Bayer designation
            bayer_clean = bayer.replace('-1', '').replace('-2', '')
            greek_letter = self.greek_letters.get(bayer_clean, bayer_clean)
            return f'{greek_letter} {constellation}{comp_suffix}'
            
        return ''

    def generate_star_name(self, star_row: pd.Series) -> Dict[str, str]:
        """Generate comprehensive naming information for a star"""
        
        # Extract and clean values
        proper = self.clean_value(star_row.get('proper', ''))
        bayer = self.clean_value(star_row.get('bayer', ''))
        flamsteed = self.clean_value(star_row.get('flam', ''))
        constellation = self.clean_value(star_row.get('con', ''))
        bf_combined = self.clean_value(star_row.get('bf', ''))
        hip = self.clean_value(star_row.get('hip', ''))
        gliese = self.clean_value(star_row.get('gl', ''))
        hd = self.clean_value(star_row.get('hd', ''))
        var_name = self.clean_value(star_row.get('var', ''))
        component = self.clean_value(star_row.get('comp', ''))
        star_id = star_row.get('id', 0)
        
        # Build naming hierarchy
        names = []
        identifiers = []
        
        # 1. Proper name (highest priority)
        if proper:
            names.append(proper)
            if component and component not in ['1', '']:
                names[0] = f'{proper} {component}'
        
        # 2. Variable star designation
        if var_name:
            var_full = f'{var_name} {constellation}' if constellation else var_name
            identifiers.append(var_full)
        
        # 3. Bayer/Flamsteed combined designation
        if bf_combined:
            # Parse combined designation like "9Alp CMa" or "18Eps Eri"
            bf_parts = bf_combined.split()
            if len(bf_parts) >= 2:
                names.append(bf_combined)
        
        # 4. Individual constellation designation
        constellation_name = self.format_constellation_designation(bayer, flamsteed, constellation, component)
        if constellation_name and constellation_name not in names:
            names.append(constellation_name)
        
        # 5. Catalog numbers (fallbacks)
        if hip and hip != '0.0':
            hip_num = str(int(float(hip))) if '.' in str(hip) else str(hip)
            identifiers.append(f'HIP {hip_num}')
        
        if gliese:
            # Clean up Gliese designation
            gliese_clean = gliese.replace('Gl ', '').strip()
            if gliese_clean:
                identifiers.append(f'Gliese {gliese_clean}')
        
        if hd and hd != '0.0':
            hd_num = str(int(float(hd))) if '.' in str(hd) else str(hd)
            identifiers.append(f'HD {hd_num}')
        
        # 6. Fallback to star ID
        if not names and not identifiers:
            names.append(f'Star {star_id}')
        
        # Choose primary name
        primary_name = names[0] if names else (identifiers[0] if identifiers else f'Star {star_id}')
        
        # Create full constellation name for description
        constellation_full = self.constellation_names.get(constellation, constellation) if constellation else ''
        
        return {
            'primary_name': primary_name,
            'all_names': names,
            'catalog_ids': identifiers,
            'constellation_short': constellation,
            'constellation_full': constellation_full,
            'has_proper_name': bool(proper),
            'designation_type': self._get_designation_type(primary_name, proper, constellation_name, hip, gliese)
        }
    
    def _get_designation_type(self, primary_name: str, proper: str, constellation_name: str, 
                            hip: str, gliese: str) -> str:
        """Determine the type of the primary designation"""
        if proper:
            return 'proper'
        elif constellation_name:
            return 'constellation'
        elif hip and hip != '0.0':
            return 'hipparcos'
        elif gliese:
            return 'gliese'
        else:
            return 'catalog'

    def process_star_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process entire dataframe to add naming information"""
        naming_data = []
        
        for _, star_row in df.iterrows():
            star_naming = self.generate_star_name(star_row)
            naming_data.append(star_naming)
        
        # Add naming columns to dataframe
        for key in ['primary_name', 'all_names', 'catalog_ids', 'constellation_short', 
                   'constellation_full', 'has_proper_name', 'designation_type']:
            df[key] = [item[key] for item in naming_data]
        
        return df

    def search_stars_by_name(self, df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Search stars by any of their names or identifiers"""
        search_term = search_term.lower().strip()
        
        def matches_search(star_row):
            star_naming = self.generate_star_name(star_row)
            
            # Check primary name
            if search_term in star_naming['primary_name'].lower():
                return True
            
            # Check all names
            for name in star_naming['all_names']:
                if search_term in name.lower():
                    return True
            
            # Check catalog IDs
            for cat_id in star_naming['catalog_ids']:
                if search_term in cat_id.lower():
                    return True
            
            return False
        
        mask = df.apply(matches_search, axis=1)
        return df[mask]

# Example usage and testing
if __name__ == "__main__":
    # Test the naming system
    naming_system = StarNamingSystem()
    
    # Test data samples
    test_stars = [
        # Sirius
        {'id': 32263, 'proper': 'Sirius', 'bayer': 'Alp', 'flam': 9.0, 'con': 'CMa', 'bf': '9Alp CMa', 
         'hip': 32349.0, 'gl': 'Gl 244A', 'comp': '1'},
        
        # Proxima Centauri  
        {'id': 70666, 'proper': 'Proxima Centauri', 'bayer': '', 'flam': '', 'con': 'Cen', 'bf': '', 
         'hip': 70890.0, 'gl': 'Gl 551', 'comp': '1'},
         
        # Epsilon Eridani
        {'id': 16496, 'proper': 'Ran', 'bayer': 'Eps', 'flam': 18.0, 'con': 'Eri', 'bf': '18Eps Eri', 
         'hip': 16537.0, 'gl': 'Gl 144', 'comp': '1'},
         
        # Unnamed star with only catalog numbers
        {'id': 118720, 'proper': '', 'bayer': '', 'flam': '', 'con': 'Leo', 'bf': '', 
         'hip': '', 'gl': 'Gl 406', 'comp': '1'}
    ]
    
    for star_data in test_stars:
        star_series = pd.Series(star_data)
        naming = naming_system.generate_star_name(star_series)
        
        print(f"\nStar ID {star_data['id']}:")
        print(f"  Primary: {naming['primary_name']}")
        print(f"  Type: {naming['designation_type']}")
        print(f"  All names: {naming['all_names']}")
        print(f"  Catalog IDs: {naming['catalog_ids']}")
        print(f"  Constellation: {naming['constellation_full']}")