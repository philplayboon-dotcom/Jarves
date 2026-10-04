"""Port-Definitionen (Protocols) fuer Jarves-AI gemaess INTERFACES.md."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from jarves.domain.cancellation import CancellationToken
    from jarves.domain.models import (
        ChatRequest,
        ContextSource,
        ProviderEvent,
        SelectionSpec,
    )


class ModelProvider(Protocol):
    """Port fuer LLM-Inferenz-Provider (z.B. FakeProvider, OllamaProvider)."""

    def list_models(self) -> tuple[str, ...]:
        """Gibt die Liste verfuegbarer Modellnamen zurueck."""
        ...

    def stream_chat(
        self,
        request: ChatRequest,
        cancel: CancellationToken,
    ) -> Iterator[ProviderEvent]:
        """Streamt Antwort-Events fuer die gegebene Anfrage."""
        ...


class ProjectReader(Protocol):
    """Port zum sicheren Lesen von Projektdateien aus einem freigegebenen Root."""

    def read_text(
        self,
        root: Path,
        relative_path: str,
        line_start: int | None = None,
        line_end: int | None = None,
    ) -> ContextSource:
        """Liest Text aus einer Datei im freigegebenen Root."""
        ...


class ScreenshotPort(Protocol):
    """Port zur Erfassung von Bildschirmausschnitten (ab M6)."""

    def capture(self, spec: SelectionSpec) -> bytes:
        """Erfasst einen Bildschirmausschnitt als Byte-Array im RAM."""
        ...


class OcrPort(Protocol):
    """Port zur optischen Zeichenerkennung auf Bilddaten (ab M6)."""

    def recognize(
        self,
        image_data: bytes,
        language: str = "deu+eng",
    ) -> tuple[str, tuple[str, ...]]:
        """Erkennt Text in Bilddaten und liefert (extrahierter Text, Warnungen)."""
        ...
