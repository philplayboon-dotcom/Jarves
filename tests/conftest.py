"""Globale Pytest-Konfiguration und Fixtures fuer Jarves-AI."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def mock_root_path(tmp_path: Path) -> Path:
    """Basis-Fixture fuer Dateisystem-Tests."""
    return tmp_path
