"""Thread-safe Cancellation-Token fuer Provider-Streams und Workflows."""

from __future__ import annotations

import threading


class CancellationToken:
    """Thread-sicherer Token zur Signalisierung eines Abbruchs."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        """Setzt das Abbruch-Signal."""
        self._event.set()

    def is_cancelled(self) -> bool:
        """Prueft, ob ein Abbruch angefordert wurde."""
        return self._event.is_set()
