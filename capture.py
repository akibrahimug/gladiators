"""Launcher for the network commands; works under `python3 -I` (which ignores PYTHONPATH).

Example: python3 -I capture.py head --out ~/gladiator-data/head
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gladiator_capture.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
