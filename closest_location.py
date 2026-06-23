#!/usr/bin/env python3
"""
closest_location.py — Location Tailoring Tool for YAML CV Pipeline.

Determines the closest candidate city (Kiel, Frankfurt, Berlin, Köln)
based on the job description's location.
"""

import os
import sys
import math
import yaml

# Candidate locations and coordinates
CANDIDATES = {
    "Kiel": (54.3233, 10.1228),
    "Frankfurt": (50.1109, 8.6821),
    "Berlin": (52.5200, 13.4050),
    "Köln": (50.9375, 6.9603)
}

# Pre-defined database of major German tech/business cities and their coordinates
CITY_COORDS = {
    # Top tech hubs / major cities
    "berlin": (52.5200, 13.4050),
    "hamburg": (53.5511, 9.9937),
    "munich": (48.1351, 11.5820),
    "münchen": (48.1351, 11.5820),
    "cologne": (50.9375, 6.9603),
    "köln": (50.9375, 6.9603),
    "frankfurt": (50.1109, 8.6821),
    "stuttgart": (48.7758, 9.1829),
    "düsseldorf": (51.2271, 6.7735),
    "dusseldorf": (51.2271, 6.7735),
    "leipzig": (51.3397, 12.3731),
    "dortmund": (51.5136, 7.4653),
    "essen": (51.4556, 7.0116),
    "bremen": (53.0793, 8.8017),
    "dresden": (51.0504, 13.7373),
    "hanover": (52.3759, 9.7320),
    "hannover": (52.3759, 9.7320),
    "nuremberg": (49.4521, 11.0768),
    "nürnberg": (49.4521, 11.0768),
    "duisburg": (51.4344, 6.7623),
    "bochum": (51.4818, 7.2162),
    "wuppertal": (51.2562, 7.1508),
    "bielefeld": (52.0302, 8.5325),
    "bonn": (50.7374, 7.0982),
    "münster": (51.9607, 7.6261),
    "munster": (51.9607, 7.6261),
    "karlsruhe": (49.0069, 8.4037),
    "mannheim": (49.4875, 8.4660),
    "augsburg": (48.3705, 10.8978),
    "wiesbaden": (50.0782, 8.2398),
    "gelsenkirchen": (51.5177, 7.0857),
    "mönchengladbach": (51.1805, 6.4428),
    "monchengladbach": (51.1805, 6.4428),
    "braunschweig": (52.2689, 10.5268),
    "chemnitz": (50.8278, 12.9274),
    "kiel": (54.3233, 10.1228),
    "aachen": (50.7753, 6.0839),
    "halle": (51.4828, 11.9698),
    "magdeburg": (52.1243, 11.6290),
    "freiburg": (47.9990, 7.8421),
    "krefeld": (51.3388, 6.5853),
    "mainz": (49.9929, 8.2473),
    "lübeck": (53.8655, 10.6866),
    "lubeck": (53.8655, 10.6866),
    "erfurt": (50.9848, 11.0299),
    "oberhausen": (51.4700, 6.8648),
    "rostock": (54.0924, 12.0991),
    "kassel": (51.3127, 9.4797),
    "hagen": (51.3671, 7.4633),
    "potsdam": (52.3989, 13.0657),
    "saarbrücken": (49.2402, 6.9969),
    "saarbrucken": (49.2402, 6.9969),
    "hamm": (51.6811, 7.8188),
    "ludwigshafen": (49.4836, 8.4485),
    "mülheim": (51.4273, 6.8824),
    "mulheim": (51.4273, 6.8824),
    "oldenburg": (53.1435, 8.2146),
    "osnabrück": (52.2799, 8.0472),
    "osnabruck": (52.2799, 8.0472),
    "leverkusen": (51.0459, 6.9984),
    "heidelberg": (49.3988, 8.6724),
    "solingen": (51.1652, 7.0671),
    # Additional tech/corporate centers
    "walldorf": (49.2638, 8.6444),
    "darmstadt": (49.8728, 8.6512),
    "kaiserslautern": (49.4447, 7.7491),
    "ingolstadt": (48.7665, 11.4258),
    "regensburg": (49.0134, 12.1016),
    "erlangen": (49.5896, 11.0119),
    "ulm": (48.4011, 9.9790),
    "koblenz": (50.3569, 7.5890),
    "offenbach": (50.1055, 8.7611),
    "heilbronn": (49.1426, 9.2103),
    "würzburg": (49.7913, 9.9534),
    "wurzburg": (49.7913, 9.9534),
    "fürth": (49.4774, 10.9893),
    "furth": (49.4774, 10.9893),
    "jena": (50.9271, 11.5892),
    "paderborn": (51.7189, 8.7575),
    "siegen": (50.8748, 8.0243),
    "trier": (49.7496, 6.6371)
}


def haversine(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0  # Earth radius in kilometers

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def find_closest_candidate(city_name: str) -> str:
    """Find which of the candidate cities is closest to the given city name."""
    norm = city_name.strip().lower()

    # Remote, country-wide, or unspecified locations default to Kiel
    remote_keywords = {
        "remote", "wfh", "home office", "homeoffice", "germany", 
        "deutschland", "deutschlandweit", "germany-wide", "anywhere", 
        "virtual", "telecommute"
    }
    if not norm or any(kw in norm for kw in remote_keywords):
        return "Kiel, Germany"

    # Identify the target coordinates by finding a matching city in our database
    target_coords = None
    matched_city_name = None

    # Try exact match first
    if norm in CITY_COORDS:
        target_coords = CITY_COORDS[norm]
        matched_city_name = norm
    else:
        # Try substring match (e.g. "Frankfurt am Main" -> "frankfurt")
        for city, coords in CITY_COORDS.items():
            if city in norm:
                target_coords = coords
                matched_city_name = city
                break

    # If no city coordinates are found, default to Kiel
    if not target_coords:
        print(f"Warning: Location '{city_name}' not found in database. Defaulting to Kiel, Germany.", file=sys.stderr)
        return "Kiel, Germany"

    # Calculate distance to all available candidates
    closest_city = "Kiel"
    min_dist = float('inf')

    for candidate, coords in CANDIDATES.items():
        dist = haversine(target_coords, coords)
        if dist < min_dist:
            min_dist = dist
            closest_city = candidate

    # Return standard formatted string
    return f"{closest_city}, Germany"


def extract_location_from_yaml(yaml_path: str) -> str:
    """Extract location from Job_Description.yaml or other YAML files."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return ""
        
        # Check direct 'location' key
        if 'location' in data and data['location']:
            return str(data['location'])

        # Fallback: scan section content for a location indicator
        # Check under standard fields or sections
        for sec in data.get('sections', []):
            if isinstance(sec, dict) and sec.get('title', '').lower() == 'location':
                return str(sec.get('content', '') or sec.get('bullets', [''])[0])
            
        return ""
    except Exception as e:
        print(f"Error reading YAML from {yaml_path}: {e}", file=sys.stderr)
        return ""


def run_tests():
    """Run verification tests."""
    test_cases = [
        ("Munich", "Frankfurt, Germany"),
        ("München", "Frankfurt, Germany"),
        ("Stuttgart", "Frankfurt, Germany"),
        ("Walldorf", "Frankfurt, Germany"),
        ("Frankfurt am Main", "Frankfurt, Germany"),
        ("Frankfurt", "Frankfurt, Germany"),
        ("Berlin", "Berlin, Germany"),
        ("Dresden", "Berlin, Germany"),
        ("Leipzig", "Berlin, Germany"),
        ("Köln", "Köln, Germany"),
        ("Cologne", "Köln, Germany"),
        ("Düsseldorf", "Köln, Germany"),
        ("Dusseldorf", "Köln, Germany"),
        ("Bonn", "Köln, Germany"),
        ("Aachen", "Köln, Germany"),
        ("Hamburg", "Kiel, Germany"),
        ("Kiel", "Kiel, Germany"),
        ("Lübeck", "Kiel, Germany"),
        ("Remote / Home Office", "Kiel, Germany"),
        ("Deutschlandweit", "Kiel, Germany"),
        ("Germany-wide", "Kiel, Germany"),
        ("UnknownCityName", "Kiel, Germany")
    ]

    passed = 0
    for inp, expected in test_cases:
        actual = find_closest_candidate(inp)
        if actual == expected:
            passed += 1
            print(f"PASS: '{inp}' -> '{actual}'")
        else:
            print(f"FAIL: '{inp}' -> expected '{expected}', got '{actual}'")

    print(f"\nResults: {passed}/{len(test_cases)} tests passed.")
    if passed == len(test_cases):
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python closest_location.py <location_string>")
        print("  python closest_location.py <Job_Description.yaml>")
        print("  python closest_location.py --test")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--test":
        run_tests()

    # Check if the argument is a YAML file path
    if arg.lower().endswith(('.yaml', '.yml')) and os.path.exists(arg):
        loc_str = extract_location_from_yaml(arg)
        if not loc_str:
            # Check if file name itself contains a location, or default
            loc_str = ""
    else:
        loc_str = arg

    result = find_closest_candidate(loc_str)
    print(result)


if __name__ == '__main__':
    main()
