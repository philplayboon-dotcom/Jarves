"""Einstiegspunkt fuer Jarves-AI."""

from __future__ import annotations

import sys

try:
    from jarves.app import run_app
except ModuleNotFoundError:
    # Fallback fuer direkten Skriptaufruf in IDE (z.B. Run Button) ohne gesetzten PYTHONPATH
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from jarves.app import run_app


def main() -> int:
    """Startet Jarves-AI."""
    return run_app(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
