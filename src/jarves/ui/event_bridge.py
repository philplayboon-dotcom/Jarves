"""Verbindet Worker-Signale mit ChatPanel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Slot

from jarves.domain.models import ProviderEvent

if TYPE_CHECKING:
    from collections.abc import Callable

    from jarves.ui.chat_panel import ChatPanel


class EventBridge(QObject):
    """Verarbeitet Worker-Events und leitet sie an das UI weiter.

    Verwirft stale Events und aktualisiert den RequestState.
    """

    def __init__(
        self,
        chat_panel: ChatPanel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.chat_panel = chat_panel
        self._active_session_id: str | None = None
        self._active_request_id: str | None = None
        self._on_request_finished: Callable[[], None] | None = None

    def set_active_ids(self, session_id: str, request_id: str) -> None:
        """Setzt die aktuell gueltigen IDs. Aeltere Events werden verworfen."""
        self._active_session_id = session_id
        self._active_request_id = request_id

    def set_request_finished_callback(self, callback: Callable[[], None]) -> None:
        """Setzt den Callback, der bei Abschluss der Anfrage aufgerufen wird."""
        self._on_request_finished = callback

    @Slot(ProviderEvent)
    def handle_event(self, event: ProviderEvent) -> None:
        """Verarbeitet ein ProviderEvent und aktualisiert das UI."""
        if (
            event.session_id != self._active_session_id
            or event.request_id != self._active_request_id
        ):
            # Stale event, ignore
            return

        if event.kind == "delta":
            self.chat_panel.append_assistant_delta(event.text)
        elif event.kind == "complete":
            self.chat_panel.finish_assistant_message(event.text if event.text else None)
            self._finish_request()
        elif event.kind == "error":
            self.chat_panel.append_error_message(event.text, event.error_code)
            self._finish_request()
        elif event.kind == "cancelled":
            self.chat_panel.append_system_notice(event.text)
            self._finish_request()

    def _finish_request(self) -> None:
        """Wird aufgerufen, wenn die Anfrage beendet ist (complete, error, cancelled)."""
        if self._on_request_finished is not None:
            self._on_request_finished()
