"""
config.py — Centralized configuration for YAML CV Pipeline.

Provides default paths and constants with environment variable override support.
"""
import os


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
