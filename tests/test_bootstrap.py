"""Bootstrap-Tests fuer Jarves-AI."""

from __future__ import annotations

import jarves
from jarves.app import run_app


def test_package_version() -> None:
    """Prueft, dass das Paket eine gueltige Version besitzt."""
    assert jarves.__version__ == "0.1.0"


def test_main_entrypoint_version(capsys: object) -> None:
    """Prueft den Bootstrap-Einstiegspunkt mit --version."""
    result = run_app(["--version"])
    assert result == 0
