"""Launcher for the read-only G02 run analysis (TASK-P02-003); works under `python3 -I`.

Example: python3 -I -B analyse.py live --run ~/gladiator-data/live-7d --out ~/gladiator-data/analysis/live-7d.json
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gladiator_capture.live_analysis import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
