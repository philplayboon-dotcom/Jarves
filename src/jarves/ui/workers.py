"""Background worker fuer Inference."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from jarves.domain.models import ProviderEvent

if TYPE_CHECKING:
    from jarves.domain.cancellation import CancellationToken
    from jarves.domain.models import ChatRequest

logger = logging.getLogger(__name__)


class InferenceWorker(QThread):
    """Führt die Provider-Inferenz im Hintergrund aus.

    Sendet ProviderEvents als Qt-Signale in den Haupt-Thread.
    """

    event_received = Signal(ProviderEvent)

    def __init__(
        self,
        provider,  # Typ-Annotation für Provider-Interface vereinfacht belassen
        request: ChatRequest,
        cancel_token: CancellationToken,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.provider = provider
        self.request = request
        self.cancel_token = cancel_token

    def run(self) -> None:
        """Startet den Inferenz-Vorgang im Hintergrund."""
        try:
            for event in self.provider.stream_chat(self.request, self.cancel_token):
                self.event_received.emit(event)
        except Exception as e:
            logger.exception("Unexpected error during inference")
            error_event = ProviderEvent(
                session_id=self.request.packet.session_id,
                request_id=self.request.packet.request_id,
                kind="error",
                error_code="UNEXPECTED_ERROR",
                text=f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            )
            self.event_received.emit(error_event)
