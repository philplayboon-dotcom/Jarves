"""Unit-Tests fuer Domaenenmodelle, Cancellation und Fehler (Task T02)."""

from __future__ import annotations

import concurrent.futures
import sys
from dataclasses import FrozenInstanceError

import pytest

from jarves.domain.cancellation import CancellationToken
from jarves.domain.errors import (
    BINARY_FILE,
    CAPTURE_FAILED,
    EXCLUDED_PATH,
    FILE_TOO_LARGE,
    INPUT_TOO_LARGE,
    INVALID_ENDPOINT,
    INVALID_SELECTION,
    MODEL_NOT_FOUND,
    OCR_FAILED,
    OCR_UNAVAILABLE,
    OUTSIDE_PROJECT,
    PROVIDER_PROTOCOL_ERROR,
    PROVIDER_TIMEOUT,
    REQUEST_CANCELLED,
    SERVER_UNAVAILABLE,
    UNSUPPORTED_ENCODING,
    DomainError,
)
from jarves.domain.models import (
    ChatMessage,
    ChatRequest,
    ContextPacket,
    ContextSource,
    ProviderEvent,
    ProviderSettings,
    RuntimeMetrics,
    SelectionSpec,
)


def test_domain_models_immutability() -> None:
    """Stellt sicher, dass die Domaenenmodelle unveraenderlich (frozen) sind."""
    source = ContextSource(
        id="src-1",
        kind="file",
        label="main.py",
        text="print('hello')",
        captured_at="2026-10-04T00:00:00Z",
    )
    with pytest.raises(FrozenInstanceError):
        # type: ignore[misc]
        source.label = "other.py"  # type: ignore[misc]

    msg = ChatMessage(role="user", content="Hilf mir")
    with pytest.raises(FrozenInstanceError):
        msg.content = "Neuer Text"  # type: ignore[misc]


def test_domain_packet_and_request() -> None:
    """Testet die Struktur von ContextPacket und ChatRequest."""
    source = ContextSource(
        id="src-1",
        kind="manual",
        label="Fehlerausgabe",
        text="ValueError: test",
        captured_at="2026-10-04T00:00:00Z",
    )
    msg = ChatMessage(role="user", content="Was bedeutet dieser Fehler?")
    packet = ContextPacket(
        session_id="sess-123",
        request_id="req-456",
        sources=(source,),
        messages=(msg,),
        estimated_prompt_tokens=42,
        warnings=(),
    )
    request = ChatRequest(packet=packet, model="qwen2.5-coder:1.5b")

    assert request.packet.session_id == "sess-123"
    assert request.packet.request_id == "req-456"
    assert request.model == "qwen2.5-coder:1.5b"
    assert request.num_ctx == 2048
    assert request.num_predict == 384


def test_provider_event_structure() -> None:
    """Testet ProviderEvent Erstellung."""
    event = ProviderEvent(
        session_id="sess-1",
        request_id="req-1",
        kind="delta",
        text="Antwortteil",
    )
    assert event.kind == "delta"
    assert event.text == "Antwortteil"
    assert event.error_code is None


def test_selection_spec_and_metrics() -> None:
    """Testet SelectionSpec, ProviderSettings und RuntimeMetrics."""
    spec = SelectionSpec(x=10, y=20, width=100, height=200)
    assert spec.x == 10 and spec.display_id == 0

    metrics = RuntimeMetrics(prompt_eval_count=120, eval_count=35, total_duration_ms=450.5)
    assert metrics.prompt_eval_count == 120

    settings = ProviderSettings()
    assert settings.endpoint == "http://127.0.0.1:11434"
    assert settings.num_ctx == 2048


def test_domain_errors() -> None:
    """Testet DomainError Formatierung und Fehlercodes."""
    all_codes = [
        SERVER_UNAVAILABLE,
        MODEL_NOT_FOUND,
        PROVIDER_TIMEOUT,
        PROVIDER_PROTOCOL_ERROR,
        REQUEST_CANCELLED,
        INVALID_ENDPOINT,
        OUTSIDE_PROJECT,
        EXCLUDED_PATH,
        INVALID_SELECTION,
        FILE_TOO_LARGE,
        BINARY_FILE,
        UNSUPPORTED_ENCODING,
        INPUT_TOO_LARGE,
        CAPTURE_FAILED,
        OCR_UNAVAILABLE,
        OCR_FAILED,
    ]
    assert len(all_codes) == 16

    err = DomainError(
        code=SERVER_UNAVAILABLE,
        user_message="Ollama-Server ist nicht erreichbar.",
        technical_detail="Connection refused on port 11434",
    )
    assert err.code == "SERVER_UNAVAILABLE"
    assert "Ollama-Server ist nicht erreichbar." in str(err)
    assert "Connection refused" in str(err)

    err_simple = DomainError(code=SERVER_UNAVAILABLE, user_message="Server down")
    assert str(err_simple) == "[SERVER_UNAVAILABLE] Server down"


def test_cancellation_token_basic() -> None:
    """Testet CancellationToken Grundfunktionalitaet."""
    token = CancellationToken()
    assert not token.is_cancelled()
    token.cancel()
    assert token.is_cancelled()


def test_cancellation_token_thread_safe() -> None:
    """Testet Thread-Sicherheit des CancellationToken unter Nebenlaeufigkeit."""
    token = CancellationToken()
    results: list[bool] = []

    def cancel_worker() -> None:
        token.cancel()

    def check_worker() -> bool:
        return token.is_cancelled()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(check_worker) for _ in range(20)]
        executor.submit(cancel_worker)
        futures.extend([executor.submit(check_worker) for _ in range(20)])
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Nach Abschluss aller Threads muss token definitiv cancelled sein
    assert token.is_cancelled()
    assert True in results


def test_domain_layer_isolation() -> None:
    """Stellt sicher, dass die Domain keine verbotenen Frameworks (Qt, httpx, etc.) importiert."""
    forbidden = ["PySide6", "PyQt5", "PyQt6", "httpx", "requests", "aiohttp", "urllib.request"]
    domain_modules = [m for m in sys.modules if m.startswith("jarves.domain")]
    assert domain_modules, "Domain-Module muessen geladen sein"

    for mod_name in domain_modules:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            val = getattr(mod, attr)
            if hasattr(val, "__module__") and val.__module__:
                for f in forbidden:
                    assert not val.__module__.startswith(f), (
                        f"Verbotener Import {f} in Domain-Modul {mod_name}"
                    )
