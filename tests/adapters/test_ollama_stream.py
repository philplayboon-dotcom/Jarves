"""Adapter-Tests fuer NDJSON-Streaming und list_models mit OllamaProvider (Task T08)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx

from jarves.domain.cancellation import CancellationToken
from jarves.domain.models import (
    ChatMessage,
    ChatRequest,
    ContextPacket,
    ContextSource,
    ProviderEvent,
    ProviderSettings,
)
from jarves.infrastructure.providers.ollama import OllamaProvider

if TYPE_CHECKING:
    from collections.abc import Iterator

    from jarves.domain.ports import ModelProvider


def _create_test_request(
    model: str = "qwen2.5-coder:1.5b",
    session_id: str = "sess-ollama-01",
    request_id: str = "req-ollama-01",
    user_prompt: str = "Hallo Ollama",
    num_ctx: int = 2048,
    num_predict: int = 384,
    temperature: float = 0.2,
) -> ChatRequest:
    """Hilfsfunktion zum Erzeugen einer typisierten Testanfrage."""
    source = ContextSource(
        id="src-1",
        kind="manual",
        label="Testquelle",
        text="Kontext",
        captured_at="2026-10-04T00:00:00Z",
    )
    msg = ChatMessage(role="user", content=user_prompt)
    packet = ContextPacket(
        session_id=session_id,
        request_id=request_id,
        sources=(source,),
        messages=(msg,),
        estimated_prompt_tokens=20,
        warnings=(),
    )
    return ChatRequest(
        packet=packet,
        model=model,
        num_ctx=num_ctx,
        num_predict=num_predict,
        temperature=temperature,
    )


def test_ollama_provider_satisfies_model_provider_protocol() -> None:
    """Stellt sicher, dass OllamaProvider die ModelProvider Schnittstelle erfuellt."""
    provider: ModelProvider = OllamaProvider()
    assert hasattr(provider, "list_models")
    assert hasattr(provider, "stream_chat")
    assert callable(provider.list_models)
    assert callable(provider.stream_chat)


def test_list_models_success() -> None:
    """Prueft das erfolgreiche Abfragen der Modellliste ueber /api/tags."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/tags"
        payload = {
            "models": [
                {"name": "qwen2.5-coder:1.5b", "size": 1000},
                {"name": "llama3.2:1b", "size": 2000},
            ]
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)

    models = provider.list_models()
    assert models == ("qwen2.5-coder:1.5b", "llama3.2:1b")


def test_list_models_with_string_items() -> None:
    """Prueft Toleranz wenn models-Array direkt Strings enthaelt."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"models": ["model-a", "model-b"]})

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    assert provider.list_models() == ("model-a", "model-b")


def test_stream_chat_success_and_request_payload() -> None:
    """Prueft vollstaendigen NDJSON-Stream und Korrektheit des gesendeten Bodys."""
    recorded_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        assert request.method == "POST"
        assert request.url.path == "/api/chat"

        req_json = json.loads(request.read())
        assert req_json["model"] == "qwen2.5-coder:1.5b"
        assert req_json["stream"] is True
        assert req_json["messages"] == [{"role": "user", "content": "Hallo Ollama"}]
        assert req_json["options"] == {
            "num_ctx": 2048,
            "num_predict": 384,
            "temperature": 0.2,
        }
        assert req_json["keep_alive"] == "1m"
        assert "tools" not in req_json
        assert "images" not in req_json
        assert "think" not in req_json

        lines = [
            json.dumps({"message": {"role": "assistant", "content": "Hallo! "}}),
            json.dumps({"message": {"role": "assistant", "content": "Ich bin "}}),
            json.dumps({"message": {"role": "assistant", "content": "Jarves."}}),
            json.dumps({"done": True}),
        ]
        body = "\n".join(lines) + "\n"
        return httpx.Response(200, content=body.encode("utf-8"))

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    assert len(recorded_requests) == 1
    assert len(events) == 4

    for event in events:
        assert event.session_id == "sess-ollama-01"
        assert event.request_id == "req-ollama-01"

    deltas = [e.text for e in events if e.kind == "delta"]
    assert deltas == ["Hallo! ", "Ich bin ", "Jarves."]

    assert events[-1].kind == "complete"
    assert events[-1].error_code is None


def test_stream_chat_utf8_split_across_chunks() -> None:
    """Prueft, dass Multi-Byte UTF-8 Zeichen ueber Chunkgrenzen hinweg dekodiert werden."""

    def chunk_generator() -> Iterator[bytes]:
        # 'Grüße 🚀' enthaelt Mehrbyte-Zeichen (ü: 2B, ß: 2B, 🚀: 4B)
        full_line1 = (
            json.dumps({"message": {"role": "assistant", "content": "Schöne Grüße 🚀"}}).encode(
                "utf-8"
            )
            + b"\n"
        )
        full_line2 = json.dumps({"done": True}).encode("utf-8") + b"\n"

        # Schneide line1 mitten im UTF-8 Character durch
        split_pos = 45
        yield full_line1[:split_pos]
        yield full_line1[split_pos:]
        yield full_line2

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=chunk_generator())

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    assert events[-1].kind == "complete"
    deltas = [e.text for e in events if e.kind == "delta"]
    assert deltas == ["Schöne Grüße 🚀"]


def test_stream_chat_empty_lines_and_spaces() -> None:
    """Prueft Robustheit gegenueber Leerzeilen und Whitespace im NDJSON-Stream."""

    def handler(_request: httpx.Request) -> httpx.Response:
        content = (
            b"\n\n  \n"
            + json.dumps({"message": {"role": "assistant", "content": "Antwort"}}).encode("utf-8")
            + b"\n\n   \n"
            + json.dumps({"done": True}).encode("utf-8")
            + b"\n\n"
        )
        return httpx.Response(200, content=content)

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 2
    assert events[0].kind == "delta" and events[0].text == "Antwort"
    assert events[1].kind == "complete"


def test_stream_chat_cancellation_before_request() -> None:
    """Prueft, dass bei vorab gesetztem Cancel-Token kein HTTP-Aufruf stattfindet."""
    called = False

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, content=b"")

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()
    cancel.cancel()

    events = list(provider.stream_chat(request, cancel))

    assert not called
    assert len(events) == 1
    assert events[0].kind == "cancelled"
    assert events[0].session_id == request.packet.session_id
    assert events[0].request_id == request.packet.request_id


def test_stream_chat_cancellation_mid_stream() -> None:
    """Prueft Abbruch waehrend des laufenden Streamings."""

    def chunk_generator() -> Iterator[bytes]:
        for i in range(5):
            line = json.dumps({"message": {"role": "assistant", "content": f"Teil {i} "}}) + "\n"
            yield line.encode("utf-8")
        yield json.dumps({"done": True}).encode("utf-8") + b"\n"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=chunk_generator())

    transport = httpx.MockTransport(handler)
    provider = OllamaProvider(transport=transport)
    request = _create_test_request()
    cancel = CancellationToken()

    collected_events: list[ProviderEvent] = []
    for event in provider.stream_chat(request, cancel):
        collected_events.append(event)
        if len(collected_events) == 2:
            cancel.cancel()

    assert len(collected_events) == 3
    assert collected_events[0].kind == "delta" and collected_events[0].text == "Teil 0 "
    assert collected_events[1].kind == "delta" and collected_events[1].text == "Teil 1 "
    assert collected_events[2].kind == "cancelled"

    terminal_events = [e for e in collected_events if e.kind != "delta"]
    assert len(terminal_events) == 1
    assert terminal_events[0].kind == "cancelled"


def test_provider_initialization_with_settings() -> None:
    """Prueft Initialisierung von OllamaProvider ueber ProviderSettings."""
    settings = ProviderSettings(
        endpoint="http://localhost:11434",
        timeout_seconds=45.0,
    )
    provider = OllamaProvider(settings=settings)
    assert provider._endpoint == "http://localhost:11434"
    assert provider._timeout_seconds == 45.0
