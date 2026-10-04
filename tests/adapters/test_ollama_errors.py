"""Fehler-, Timeout- und Policy-Härtungstests fuer OllamaProvider (Task T09)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx
import pytest

from jarves.domain.cancellation import CancellationToken
from jarves.domain.errors import (
    INVALID_ENDPOINT,
    MODEL_NOT_FOUND,
    PROVIDER_PROTOCOL_ERROR,
    PROVIDER_TIMEOUT,
    SERVER_UNAVAILABLE,
    DomainError,
)
from jarves.domain.models import (
    ChatMessage,
    ChatRequest,
    ContextPacket,
    ContextSource,
)
from jarves.infrastructure.providers.ollama import (
    OllamaProvider,
    validate_and_normalize_endpoint,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


def _create_test_request(
    model: str = "qwen2.5-coder:1.5b",
    session_id: str = "sess-err-01",
    request_id: str = "req-err-01",
    user_prompt: str = "Test",
) -> ChatRequest:
    """Hilfsfunktion fuer typisierte Test-ChatRequests."""
    source = ContextSource(
        id="src-1",
        kind="manual",
        label="Quelle",
        text="Text",
        captured_at="2026-10-04T00:00:00Z",
    )
    msg = ChatMessage(role="user", content=user_prompt)
    packet = ContextPacket(
        session_id=session_id,
        request_id=request_id,
        sources=(source,),
        messages=(msg,),
        estimated_prompt_tokens=10,
        warnings=(),
    )
    return ChatRequest(packet=packet, model=model)


# --- 1. Endpoint-Validierung & Policy Tests ---


@pytest.mark.parametrize(
    ("raw_endpoint", "expected_normalized"),
    [
        ("http://127.0.0.1:11434", "http://127.0.0.1:11434"),
        ("http://localhost:11434", "http://127.0.0.1:11434"),
        ("http://localhost:11434/", "http://127.0.0.1:11434"),
        ("http://[::1]:11434", "http://[::1]:11434"),
        ("http://127.0.0.1", "http://127.0.0.1"),
        ("http://localhost", "http://127.0.0.1"),
    ],
)
def test_endpoint_valid_loopback(raw_endpoint: str, expected_normalized: str) -> None:
    """Prueft, dass alle zulaessigen Loopback-Formate akzeptiert und normalisiert werden."""
    normalized = validate_and_normalize_endpoint(raw_endpoint)
    assert normalized == expected_normalized


@pytest.mark.parametrize(
    "invalid_endpoint",
    [
        "https://127.0.0.1:11434",  # HTTPS verboten fuer lokalen Loopback
        "http://example.com:11434",  # Remote Host verboten
        "http://user:pass@127.0.0.1:11434",  # Credentials verboten
        "http://192.168.1.50:11434",  # Privates LAN verboten
        "http://0.0.0.0:11434",  # Bind-All nicht zulaessig
        "http://127.0.0.1:11434?param=1",  # Query verboten
        "http://127.0.0.1:11434#frag",  # Fragment verboten
        "http://127.0.0.1:70000",  # Port > 65535
        "http://127.0.0.1:0",  # Port 0
        "ftp://127.0.0.1:11434",  # Nicht-HTTP Schema
        "",  # Leer
        "invalid-endpoint",  # Kein URL-Format
    ],
)
def test_endpoint_policy_rejections(invalid_endpoint: str) -> None:
    """Prueft, dass Remote-Hosts, Credentials, HTTPS und ungueltige URLs abgewiesen werden."""
    with pytest.raises(DomainError) as exc_info:
        validate_and_normalize_endpoint(invalid_endpoint)
    assert exc_info.value.code == INVALID_ENDPOINT


def test_stream_chat_invalid_endpoint_yields_error_event() -> None:
    """Prueft, dass stream_chat bei ungueltigem Endpoint ein error-Event liefert."""
    provider = OllamaProvider(endpoint="http://remote-server.com:11434")
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == INVALID_ENDPOINT


# --- 2. Fehlerfaelle bei list_models() ---


def test_list_models_server_unavailable() -> None:
    """Prueft Wandlung von ConnectError in SERVER_UNAVAILABLE."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()
    assert exc_info.value.code == SERVER_UNAVAILABLE


def test_list_models_timeout() -> None:
    """Prueft Wandlung von TimeoutException in PROVIDER_TIMEOUT."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Read timed out")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()
    assert exc_info.value.code == PROVIDER_TIMEOUT


def test_list_models_http_error_status() -> None:
    """Prueft Wandlung von HTTP 500 in PROVIDER_PROTOCOL_ERROR."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()
    assert exc_info.value.code == PROVIDER_PROTOCOL_ERROR


def test_list_models_invalid_json() -> None:
    """Prueft Wandlung von korruptem JSON in PROVIDER_PROTOCOL_ERROR."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="This is not JSON")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()
    assert exc_info.value.code == PROVIDER_PROTOCOL_ERROR


def test_list_models_missing_models_key() -> None:
    """Prueft Wandlung von unerwarteter JSON-Struktur in PROVIDER_PROTOCOL_ERROR."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"wrong_key": []})

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()
    assert exc_info.value.code == PROVIDER_PROTOCOL_ERROR


# --- 3. Fehlerfaelle bei stream_chat() ---


def test_stream_chat_server_unavailable_on_connect() -> None:
    """Prueft Verbindungsfehler vor Stream-Start."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == SERVER_UNAVAILABLE


def test_stream_chat_timeout_on_connect() -> None:
    """Prueft Timeout vor Stream-Start."""

    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("Connect timed out")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == PROVIDER_TIMEOUT


def test_stream_chat_http_404_model_not_found() -> None:
    """Prueft HTTP 404 Antwort (Modell nicht vorhanden)."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "model 'nonexistent' not found"})

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request(model="nonexistent")
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == MODEL_NOT_FOUND
    assert "nonexistent" in events[0].text


def test_stream_chat_http_500_protocol_error() -> None:
    """Prueft HTTP 500 Fehler."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Ollama Crash")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == PROVIDER_PROTOCOL_ERROR


def test_stream_chat_in_stream_model_not_found_error() -> None:
    """Prueft Fehler im NDJSON-Stream mit Modell-nicht-gefunden Meldung."""

    def handler(_request: httpx.Request) -> httpx.Response:
        body = json.dumps({"error": "model 'xyz' not found, try pulling it first"}) + "\n"
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request(model="xyz")
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == MODEL_NOT_FOUND


def test_stream_chat_in_stream_generic_error() -> None:
    """Prueft generische Fehlermeldung im NDJSON-Stream."""

    def handler(_request: httpx.Request) -> httpx.Response:
        body = json.dumps({"error": "CUDA out of memory"}) + "\n"
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == PROVIDER_PROTOCOL_ERROR
    assert "CUDA out of memory" in events[0].text


def test_stream_chat_corrupt_json_in_stream() -> None:
    """Prueft fehlerhafte JSON-Zeile im Stream."""

    def handler(_request: httpx.Request) -> httpx.Response:
        body = (
            json.dumps({"message": {"role": "assistant", "content": "Guter Start "}})
            + "\n{BROKEN_JSON\n"
        )
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 2
    assert events[0].kind == "delta" and events[0].text == "Guter Start "
    assert events[1].kind == "error"
    assert events[1].error_code == PROVIDER_PROTOCOL_ERROR


def test_stream_chat_non_dict_json_item() -> None:
    """Prueft JSON-Array oder Primitiv anstelle von JSON-Objekt im Stream."""

    def handler(_request: httpx.Request) -> httpx.Response:
        body = '"nur ein String"\n'
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == PROVIDER_PROTOCOL_ERROR


def test_stream_chat_premature_close_without_done() -> None:
    """Prueft vorzeitiges Schliessen der HTTP-Verbindung ohne done=True."""

    def handler(_request: httpx.Request) -> httpx.Response:
        body = json.dumps({"message": {"role": "assistant", "content": "Unvollstaendig"}}) + "\n"
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 2
    assert events[0].kind == "delta" and events[0].text == "Unvollstaendig"
    assert events[1].kind == "error"
    assert events[1].error_code == PROVIDER_PROTOCOL_ERROR


def test_stream_chat_mid_stream_read_timeout_no_retry() -> None:
    """Prueft Timeout waehrend Stream-Lesens; stellt sicher, dass kein Retry erfolgt."""
    call_count = 0

    def chunk_generator() -> Iterator[bytes]:
        yield (
            json.dumps({"message": {"role": "assistant", "content": "Erster Teil "}}) + "\n"
        ).encode("utf-8")
        raise httpx.ReadTimeout("Stream unterbrochen durch Timeout")

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, content=chunk_generator())

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    # Genau 1 Request, kein Retry
    assert call_count == 1
    assert len(events) == 2
    assert events[0].kind == "delta" and events[0].text == "Erster Teil "
    assert events[1].kind == "error"
    assert events[1].error_code == PROVIDER_TIMEOUT


def test_stream_chat_mid_stream_network_error() -> None:
    """Prueft Verbindungsabbruch waehrend des Streamings."""

    def chunk_generator() -> Iterator[bytes]:
        yield (json.dumps({"message": {"role": "assistant", "content": "Teil A "}}) + "\n").encode(
            "utf-8"
        )
        raise httpx.RemoteProtocolError("Server terminated connection unexpectedly")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=chunk_generator())

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 2
    assert events[0].kind == "delta" and events[0].text == "Teil A "
    assert events[1].kind == "error"
    assert events[1].error_code == SERVER_UNAVAILABLE
