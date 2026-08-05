"""Put each study's source on the import path so tests can exercise the real
algorithms (the studies are scripts, not installed packages)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for study in ("studies/sorts", "studies/bin_packing", "studies/networks"):
    sys.path.insert(0, str(ROOT / study))
