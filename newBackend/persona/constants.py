"""
Constants and shared paths for persona integration.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PERSONA_BASE_DIR = PROJECT_ROOT / "data" / "persona"
OPERATIONS_DIR = PERSONA_BASE_DIR / "operations"
PERSONAS_DIR = PERSONA_BASE_DIR / "personas"
DATASETS_DIR = PERSONA_BASE_DIR / "datasets"

# Ensure directories exist so downstream code can persist data safely.
for _path in (OPERATIONS_DIR, PERSONAS_DIR, DATASETS_DIR):
    _path.mkdir(parents=True, exist_ok=True)

DEFAULT_USER_ID = "default_user"
