"""Einstiegspunkt fuer Jarves-AI."""

from __future__ import annotations

import sys

from jarves.app import run_app


def main() -> int:
    """Startet Jarves-AI."""
    return run_app(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
