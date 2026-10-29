"""Launcher for the P02 validation runner; works under `python3 -I` (which ignores PYTHONPATH)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gladiator_capture.validate import main  # noqa: E402

if __name__ == "__main__":
    main()
