"""Domaenenfehler und Fehlercodes fuer Jarves-AI gemaess INTERFACES.md."""

from __future__ import annotations

from typing import Final

# Spezifizierte Fehlercodes
SERVER_UNAVAILABLE: Final[str] = "SERVER_UNAVAILABLE"
MODEL_NOT_FOUND: Final[str] = "MODEL_NOT_FOUND"
PROVIDER_TIMEOUT: Final[str] = "PROVIDER_TIMEOUT"
PROVIDER_PROTOCOL_ERROR: Final[str] = "PROVIDER_PROTOCOL_ERROR"
REQUEST_CANCELLED: Final[str] = "REQUEST_CANCELLED"
INVALID_ENDPOINT: Final[str] = "INVALID_ENDPOINT"
OUTSIDE_PROJECT: Final[str] = "OUTSIDE_PROJECT"
EXCLUDED_PATH: Final[str] = "EXCLUDED_PATH"
INVALID_SELECTION: Final[str] = "INVALID_SELECTION"
FILE_TOO_LARGE: Final[str] = "FILE_TOO_LARGE"
BINARY_FILE: Final[str] = "BINARY_FILE"
UNSUPPORTED_ENCODING: Final[str] = "UNSUPPORTED_ENCODING"
INPUT_TOO_LARGE: Final[str] = "INPUT_TOO_LARGE"
CAPTURE_FAILED: Final[str] = "CAPTURE_FAILED"
OCR_UNAVAILABLE: Final[str] = "OCR_UNAVAILABLE"
OCR_FAILED: Final[str] = "OCR_FAILED"


class DomainError(Exception):
    """Basisklasse fuer alle fachlichen Fehler in Jarves-AI."""

    def __init__(
        self,
        code: str,
        user_message: str,
        technical_detail: str | None = None,
    ) -> None:
        super().__init__(user_message)
        self.code = code
        self.user_message = user_message
        self.technical_detail = technical_detail

    def __str__(self) -> str:
        if self.technical_detail:
            return f"[{self.code}] {self.user_message} ({self.technical_detail})"
        return f"[{self.code}] {self.user_message}"
