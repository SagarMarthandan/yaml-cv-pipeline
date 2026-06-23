"""
config.py — Centralized configuration for YAML CV Pipeline.

Provides default paths and constants with environment variable override support.
"""
import os
from typing import Dict, Tuple


# Base paths (override with environment variables if needed)
# Calculate paths relative to skill directory for portability
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))  # Go up to YAML-CV directory

DEFAULT_MD_PATH = os.getenv(
    "YAML_CV_MD_PATH",
    os.path.join(PROJECT_ROOT, "Base Files", "Repo Info", "repo info.md")
)
DEFAULT_DB_PATH = os.getenv(
    "YAML_CV_DB_PATH",
    os.path.join(PROJECT_ROOT, "Base Files", "Repo Info", "zvec_portfolio")
)

# Embedding model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 maps text to 384-dimensional vectors

# Candidate locations for job matching (home + friends' cities)
CANDIDATES: Dict[str, Tuple[float, float]] = {
    "Kiel": (54.3233, 10.1228),
    "Frankfurt": (50.1109, 8.6821),
    "Berlin": (52.5200, 13.4050),
    "Köln": (50.9375, 6.9603)
}

# Pre-defined database of major German tech/business cities and their coordinates
CITY_COORDS: Dict[str, Tuple[float, float]] = {
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
