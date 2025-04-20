"""Configure sys.path so multipass modules can be imported for testing."""

import sys
from pathlib import Path

library_path = Path(__file__).parent.parent / "library"
sys.path.insert(0, str(library_path.resolve()))
