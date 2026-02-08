import sys
from pathlib import Path

# Automatically add project root to Python path when pytest runs
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))