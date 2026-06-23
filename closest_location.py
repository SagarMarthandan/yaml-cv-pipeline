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
from typing import Tuple
from config import CANDIDATES, CITY_COORDS


def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
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


def run_tests() -> None:
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


def main() -> None:
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
