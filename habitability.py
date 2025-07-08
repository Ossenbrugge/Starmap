#!/usr/bin/env python3
"""
Habitability Assessment Module
Calculates habitability scores for stars based on current scientific understanding
"""

import math
import re
from typing import Dict, Tuple, Optional


class HabitabilityAssessment:
    """
    Assesses star habitability based on scientific criteria including:
    - Stellar classification and spectral type
    - Stellar luminosity and temperature
    - Stellar stability and age
    - Magnetic field considerations
    - Habitable zone calculations
    """
    
    def __init__(self):
        # Cache for habitability calculations
        self._habitability_cache = {}
        
        # Stellar classification data
        self.stellar_properties = {
            'O': {'temp_range': (30000, 60000), 'mass_range': (15, 60), 'lifetime': 0.01, 'stability': 0.1},
            'B': {'temp_range': (10000, 30000), 'mass_range': (2.1, 15), 'lifetime': 0.1, 'stability': 0.3},
            'A': {'temp_range': (7500, 10000), 'mass_range': (1.4, 2.1), 'lifetime': 1.0, 'stability': 0.5},
            'F': {'temp_range': (6000, 7500), 'mass_range': (1.04, 1.4), 'lifetime': 4.0, 'stability': 0.7},
            'G': {'temp_range': (5200, 6000), 'mass_range': (0.8, 1.04), 'lifetime': 10.0, 'stability': 0.9},
            'K': {'temp_range': (3700, 5200), 'mass_range': (0.45, 0.8), 'lifetime': 45.0, 'stability': 0.95},
            'M': {'temp_range': (2400, 3700), 'mass_range': (0.08, 0.45), 'lifetime': 100.0, 'stability': 0.7}
        }
        
        # Habitability scoring weights
        self.weights = {
            'stellar_type': 0.3,
            'luminosity': 0.2,
            'stability': 0.2,
            'age_factor': 0.15,
            'magnetic_field': 0.1,
            'metallicity': 0.05
        }
    
    def parse_spectral_type(self, spectral_type: str) -> Tuple[str, int, str]:
        """
        Parse spectral type string (e.g., 'G2V', 'K5III', 'M3.5V')
        Returns: (class, subclass, luminosity_class)
        """
        if not spectral_type or spectral_type == 'nan':
            return 'Unknown', 0, 'V'
        
        # Clean the spectral type
        spectral_type = str(spectral_type).strip().upper()
        
        # Extract main class (O, B, A, F, G, K, M)
        main_class = 'Unknown'
        for class_letter in ['O', 'B', 'A', 'F', 'G', 'K', 'M']:
            if class_letter in spectral_type:
                main_class = class_letter
                break
        
        # Extract subclass (0-9)
        subclass = 5  # Default to middle
        subclass_match = re.search(r'([0-9](?:\.[0-9])?)', spectral_type)
        if subclass_match:
            subclass = float(subclass_match.group(1))
        
        # Extract luminosity class (I, II, III, IV, V, VI, VII)
        luminosity_class = 'V'  # Default to main sequence
        if 'III' in spectral_type:
            luminosity_class = 'III'
        elif 'II' in spectral_type:
            luminosity_class = 'II'
        elif 'IV' in spectral_type:
            luminosity_class = 'IV'
        elif 'VI' in spectral_type:
            luminosity_class = 'VI'
        elif 'I' in spectral_type:
            luminosity_class = 'I'
        
        return main_class, subclass, luminosity_class
    
    def calculate_stellar_type_score(self, spectral_type: str) -> float:
        """
        Calculate habitability score based on stellar type
        K-type stars score highest, followed by G-type, then F-type
        """
        main_class, subclass, luminosity_class = self.parse_spectral_type(spectral_type)
        
        # Only main sequence stars (V) are considered truly habitable
        if luminosity_class != 'V':
            return 0.1
        
        # Base scores by stellar class
        base_scores = {
            'O': 0.0,  # Too hot, too short-lived
            'B': 0.0,  # Too hot, too short-lived
            'A': 0.1,  # Too hot, relatively short-lived
            'F': 0.6,  # Hot but potentially habitable
            'G': 0.9,  # Solar-type, well-tested
            'K': 1.0,  # "Goldilocks" stars - best for habitability
            'M': 0.4,  # Cooler but flare-prone and tidal locking issues
            'Unknown': 0.0
        }
        
        base_score = base_scores.get(main_class, 0.0)
        
        # Adjust based on subclass (lower numbers are hotter)
        if main_class in ['F', 'G', 'K']:
            # For potentially habitable classes, prefer middle range
            if 2 <= subclass <= 7:
                subclass_modifier = 1.0
            elif 0 <= subclass <= 1 or 8 <= subclass <= 9:
                subclass_modifier = 0.8
            else:
                subclass_modifier = 0.9
        else:
            subclass_modifier = 1.0
        
        return base_score * subclass_modifier
    
    def calculate_luminosity_score(self, luminosity: float, spectral_type: str) -> float:
        """
        Calculate score based on stellar luminosity
        Too bright = harsh radiation, too dim = narrow habitable zone
        """
        if not luminosity or luminosity <= 0:
            return 0.3  # Unknown luminosity gets neutral score
        
        # Optimal range is 0.1 to 2.0 solar luminosities
        if 0.1 <= luminosity <= 2.0:
            # Peak around 0.5-1.5 solar luminosities
            if 0.5 <= luminosity <= 1.5:
                return 1.0
            elif 0.1 <= luminosity < 0.5:
                return 0.7 + 0.3 * (luminosity - 0.1) / 0.4
            else:  # 1.5 < luminosity <= 2.0
                return 1.0 - 0.3 * (luminosity - 1.5) / 0.5
        elif 0.01 <= luminosity < 0.1:
            # Very dim stars (M dwarfs)
            return 0.5
        elif 2.0 < luminosity <= 10.0:
            # Bright stars - less suitable
            return 0.8 - 0.6 * (luminosity - 2.0) / 8.0
        else:
            # Very bright or very dim
            return 0.1
    
    def calculate_stability_score(self, spectral_type: str, magnitude: float) -> float:
        """
        Calculate stability score based on stellar type and variability
        """
        main_class, subclass, luminosity_class = self.parse_spectral_type(spectral_type)
        
        # Base stability from stellar properties
        base_stability = self.stellar_properties.get(main_class, {}).get('stability', 0.5)
        
        # Main sequence stars are more stable
        if luminosity_class == 'V':
            stability_modifier = 1.0
        elif luminosity_class in ['IV', 'VI']:
            stability_modifier = 0.8
        else:
            stability_modifier = 0.3  # Giants, supergiants are unstable
        
        return base_stability * stability_modifier
    
    def calculate_age_factor_score(self, spectral_type: str, distance: float) -> float:
        """
        Calculate age factor based on stellar type and estimated age
        Older stars in the galactic neighborhood are preferable
        """
        main_class, subclass, luminosity_class = self.parse_spectral_type(spectral_type)
        
        # Base lifetime from stellar properties (in billions of years)
        base_lifetime = self.stellar_properties.get(main_class, {}).get('lifetime', 1.0)
        
        # Assume stars have been around for a reasonable time
        # Closer stars in our neighborhood tend to be older
        if distance > 0:
            # Nearby stars (< 50 ly) in our local neighborhood
            if distance <= 50:
                age_factor = 0.9
            # Intermediate distance (50-200 ly)
            elif distance <= 200:
                age_factor = 0.8
            # Distant stars (> 200 ly)
            else:
                age_factor = 0.7
        else:
            age_factor = 0.5
        
        # Very long-lived stars (K, M) get bonus
        if main_class in ['K', 'M']:
            age_factor *= 1.1
        elif main_class in ['F', 'G']:
            age_factor *= 1.0
        else:
            age_factor *= 0.5
        
        return min(age_factor, 1.0)
    
    def calculate_magnetic_field_score(self, spectral_type: str) -> float:
        """
        Calculate magnetic field score based on stellar type
        Based on 2024 research on stellar magnetism and habitability
        """
        main_class, subclass, luminosity_class = self.parse_spectral_type(spectral_type)
        
        # Magnetic field strength and stability by stellar class
        magnetic_scores = {
            'O': 0.2,  # Strong but unstable
            'B': 0.3,  # Strong but unstable
            'A': 0.4,  # Moderate magnetic fields
            'F': 0.7,  # Good magnetic field properties
            'G': 0.9,  # Solar-type magnetic fields (well-studied)
            'K': 0.8,  # Good magnetic fields, less active than G
            'M': 0.5,  # Weak but can have strong flares
            'Unknown': 0.3
        }
        
        base_score = magnetic_scores.get(main_class, 0.3)
        
        # Main sequence stars have better magnetic field properties
        if luminosity_class == 'V':
            return base_score
        else:
            return base_score * 0.5
    
    def calculate_metallicity_score(self, spectral_type: str) -> float:
        """
        Estimate metallicity score based on stellar type and age
        Higher metallicity = more heavy elements for planet formation
        """
        main_class, subclass, luminosity_class = self.parse_spectral_type(spectral_type)
        
        # F, G, K stars typically have good metallicity
        if main_class in ['F', 'G', 'K']:
            return 0.8
        elif main_class == 'M':
            return 0.6  # Often metal-poor but can vary
        else:
            return 0.4  # Other types less favorable
    
    def calculate_habitability_score(self, star_data: Dict) -> Dict:
        """
        Calculate comprehensive habitability score for a star (cached)
        
        Args:
            star_data: Dictionary containing star properties (spectral_type, luminosity, magnitude, distance)
            
        Returns:
            Dictionary with habitability score and breakdown
        """
        # Create cache key from star properties
        spectral_type = star_data.get('spect', 'Unknown')
        luminosity = star_data.get('lum', 1.0)
        magnitude = star_data.get('mag', 5.0)
        distance = star_data.get('dist', 100.0)
        
        cache_key = f"{spectral_type}_{luminosity}_{magnitude}_{distance}"
        
        # Check cache first
        if cache_key in self._habitability_cache:
            return self._habitability_cache[cache_key]
        
        # Calculate individual scores
        stellar_type_score = self.calculate_stellar_type_score(spectral_type)
        luminosity_score = self.calculate_luminosity_score(luminosity, spectral_type)
        stability_score = self.calculate_stability_score(spectral_type, magnitude)
        age_factor_score = self.calculate_age_factor_score(spectral_type, distance)
        magnetic_field_score = self.calculate_magnetic_field_score(spectral_type)
        metallicity_score = self.calculate_metallicity_score(spectral_type)
        
        # Calculate weighted total score
        total_score = (
            stellar_type_score * self.weights['stellar_type'] +
            luminosity_score * self.weights['luminosity'] +
            stability_score * self.weights['stability'] +
            age_factor_score * self.weights['age_factor'] +
            magnetic_field_score * self.weights['magnetic_field'] +
            metallicity_score * self.weights['metallicity']
        )
        
        # Determine habitability category
        if total_score >= 0.8:
            category = "Excellent"
            exploration_priority = "High"
        elif total_score >= 0.6:
            category = "Good"
            exploration_priority = "Medium-High"
        elif total_score >= 0.4:
            category = "Moderate"
            exploration_priority = "Medium"
        elif total_score >= 0.2:
            category = "Poor"
            exploration_priority = "Low"
        else:
            category = "Unsuitable"
            exploration_priority = "None"
        
        result = {
            'habitability_score': round(total_score, 3),
            'habitability_category': category,
            'exploration_priority': exploration_priority,
            'score_breakdown': {
                'stellar_type': round(stellar_type_score, 3),
                'luminosity': round(luminosity_score, 3),
                'stability': round(stability_score, 3),
                'age_factor': round(age_factor_score, 3),
                'magnetic_field': round(magnetic_field_score, 3),
                'metallicity': round(metallicity_score, 3)
            },
            'parsed_spectral_type': self.parse_spectral_type(spectral_type)
        }
        
        # Cache the result
        self._habitability_cache[cache_key] = result
        
        return result
    
    def get_habitability_explanation(self, habitability_data: Dict) -> str:
        """
        Generate a human-readable explanation of the habitability assessment
        """
        score = habitability_data['habitability_score']
        category = habitability_data['habitability_category']
        main_class = habitability_data['parsed_spectral_type'][0]
        
        explanations = {
            'Excellent': f"This {main_class}-type star shows excellent potential for hosting habitable worlds. ",
            'Good': f"This {main_class}-type star has good prospects for habitability. ",
            'Moderate': f"This {main_class}-type star shows moderate potential for habitable planets. ",
            'Poor': f"This {main_class}-type star has limited potential for habitability. ",
            'Unsuitable': f"This {main_class}-type star is not suitable for habitable worlds. "
        }
        
        base_explanation = explanations.get(category, "Habitability assessment unavailable. ")
        
        # Add specific details based on stellar type
        if main_class == 'G':
            base_explanation += "Solar-type stars like our Sun are well-tested for supporting life."
        elif main_class == 'K':
            base_explanation += "Orange dwarf stars are considered ideal 'Goldilocks' stars with long lifetimes and stable habitable zones."
        elif main_class == 'F':
            base_explanation += "This hotter star may have a wider habitable zone but shorter lifespan than solar-type stars."
        elif main_class == 'M':
            base_explanation += "Red dwarf stars have very long lifetimes but narrow habitable zones and potential tidal locking issues."
        elif main_class in ['A', 'B', 'O']:
            base_explanation += "This hot, massive star has a short lifespan unsuitable for complex life development."
        
        return base_explanation