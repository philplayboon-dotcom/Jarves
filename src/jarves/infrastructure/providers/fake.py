"""Deterministischer FakeProvider fuer Tests und Offline-Entwicklung."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jarves.domain.errors import MODEL_NOT_FOUND, DomainError
from jarves.domain.models import ProviderEvent

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from jarves.domain.cancellation import CancellationToken
    from jarves.domain.models import ChatRequest


class FakeProvider:
    """Deterministischer Inferenz-Provider gemaess ModelProvider Port.

    Ermoeglicht vollstaendige Simulation von Streaming-, Abbruch-, Fehler-
    und Modell-Listen-Szenarien ohne Netzwerk- oder Modell-Laufzeiten.
    """

    def __init__(
        self,
        models: Sequence[str] = ("fake-model", "qwen2.5-coder:1.5b"),
        default_deltas: Sequence[str] = ("Hallo! ", "Ich bin ", "Jarves."),
        responses: dict[str, Sequence[str]] | None = None,
        error_code: str | None = None,
        error_message: str = "Simulierter Provider-Fehler",
        error_at_delta: int | None = None,
        list_models_error: DomainError | None = None,
        require_known_model: bool = True,
    ) -> None:
        self._models: tuple[str, ...] = tuple(models)
        self._default_deltas: tuple[str, ...] = tuple(default_deltas)
        self._responses: dict[str, tuple[str, ...]] = (
            {k: tuple(v) for k, v in responses.items()} if responses else {}
        )
        self._error_code: str | None = error_code
        self._error_message: str = error_message
        self._error_at_delta: int | None = error_at_delta
        self._list_models_error: DomainError | None = list_models_error
        self._require_known_model: bool = require_known_model

    def list_models(self) -> tuple[str, ...]:
        """Liefert die verfuegbaren Modellnamen oder wirft DomainError."""
        if self._list_models_error is not None:
            raise self._list_models_error
        return self._models

    def set_error(
        self,
        error_code: str | None,
        error_message: str = "Simulierter Provider-Fehler",
        error_at_delta: int | None = None,
    ) -> None:
        """Konfiguriert ein Fehlerszenario fuer nachfolgende Aufrufe."""
        self._error_code = error_code
        self._error_message = error_message
        self._error_at_delta = error_at_delta

    def clear_error(self) -> None:
        """Entfernt konfigurierte Fehlerszenarien."""
        self._error_code = None
        self._error_message = "Simulierter Provider-Fehler"
        self._error_at_delta = None
        self._list_models_error = None

    def set_list_models_error(self, error: DomainError | None) -> None:
        """Konfiguriert einen Fehler fuer list_models()."""
        self._list_models_error = error

    def set_responses(
        self,
        default_deltas: Sequence[str] | None = None,
        responses: dict[str, Sequence[str]] | None = None,
    ) -> None:
        """Aktualisiert die Standard- oder Modellspezifischen Antwort-Deltas."""
        if default_deltas is not None:
            self._default_deltas = tuple(default_deltas)
        if responses is not None:
            self._responses = {k: tuple(v) for k, v in responses.items()}

    def stream_chat(
        self,
        request: ChatRequest,
        cancel: CancellationToken,
    ) -> Iterator[ProviderEvent]:
        """Streamt deterministische Events fuer die gegebene Anfrage.

        Garantiert pro Stream genau ein terminales Event ('complete', 'cancelled', oder 'error').
        """
        session_id = request.packet.session_id
        request_id = request.packet.request_id

        # 1. Pruefen, ob vor Streambeginn bereits abgebrochen wurde
        if cancel.is_cancelled():
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="cancelled",
                text="Anfrage vor Beginn abgebrochen.",
            )
            return

        # 2. Modell-Gueltigkeit pruefen (falls strikt gefordert)
        if self._require_known_model and request.model not in self._models:
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=MODEL_NOT_FOUND,
                text=f"Modell '{request.model}' ist nicht verfuegbar.",
            )
            return

        # 3. Sofortiger Fehler vor ersten Deltas
        if self._error_code is not None and (
            self._error_at_delta is None or self._error_at_delta <= 0
        ):
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=self._error_code,
                text=self._error_message,
            )
            return

        # 4. Deltas bestimmen
        deltas = self._responses.get(request.model, self._default_deltas)

        # 5. Deltas streamen mit Abbruch- und Fehlerpruefungen
        for index, delta in enumerate(deltas):
            if cancel.is_cancelled():
                yield ProviderEvent(
                    session_id=session_id,
                    request_id=request_id,
                    kind="cancelled",
                    text="Anfrage waehrend Stream abgebrochen.",
                )
                return

            if (
                self._error_code is not None
                and self._error_at_delta is not None
                and index == self._error_at_delta
            ):
                yield ProviderEvent(
                    session_id=session_id,
                    request_id=request_id,
                    kind="error",
                    error_code=self._error_code,
                    text=self._error_message,
                )
                return

            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="delta",
                text=delta,
            )

        # 6. Pruefen auf Abbruch oder Fehler nach dem letzten Delta
        if cancel.is_cancelled():
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="cancelled",
                text="Anfrage nach Deltas abgebrochen.",
            )
            return

        if (
            self._error_code is not None
            and self._error_at_delta is not None
            and self._error_at_delta >= len(deltas)
        ):
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=self._error_code,
                text=self._error_message,
            )
            return

        # 7. Erfolgreich abgeschlossen
        yield ProviderEvent(
            session_id=session_id,
            request_id=request_id,
            kind="complete",
        )
