"""Unit-Tests fuer den deterministischen FakeProvider (Task T03)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from jarves.domain.cancellation import CancellationToken
from jarves.domain.errors import (
    MODEL_NOT_FOUND,
    SERVER_UNAVAILABLE,
    DomainError,
)
from jarves.domain.models import (
    ChatMessage,
    ChatRequest,
    ContextPacket,
    ContextSource,
    ProviderEvent,
)
from jarves.infrastructure.providers.fake import FakeProvider

if TYPE_CHECKING:
    from jarves.domain.ports import ModelProvider


def _create_test_request(
    model: str = "fake-model",
    session_id: str = "sess-test-01",
    request_id: str = "req-test-01",
    user_prompt: str = "Hallo Jarves",
) -> ChatRequest:
    """Hilfsfunktion zum Erzeugen einer typisierten Testanfrage."""
    source = ContextSource(
        id="src-1",
        kind="manual",
        label="Testquelle",
        text="Kontextzeile",
        captured_at="2026-10-04T00:00:00Z",
    )
    msg = ChatMessage(role="user", content=user_prompt)
    packet = ContextPacket(
        session_id=session_id,
        request_id=request_id,
        sources=(source,),
        messages=(msg,),
        estimated_prompt_tokens=25,
        warnings=(),
    )
    return ChatRequest(packet=packet, model=model)


def test_fake_provider_satisfies_model_provider_protocol() -> None:
    """Stellt sicher, dass FakeProvider die ModelProvider Schnittstelle erfuellt."""
    provider: ModelProvider = FakeProvider()
    assert hasattr(provider, "list_models")
    assert hasattr(provider, "stream_chat")
    assert callable(provider.list_models)
    assert callable(provider.stream_chat)


def test_list_models_default_and_custom() -> None:
    """Prueft das Auslesen von Modellnamen (Standard und benutzerspezifisch)."""
    default_provider = FakeProvider()
    models = default_provider.list_models()
    assert models == ("fake-model", "qwen2.5-coder:1.5b")

    custom_provider = FakeProvider(models=["custom-1", "custom-2"])
    assert custom_provider.list_models() == ("custom-1", "custom-2")


def test_list_models_raises_domain_error() -> None:
    """Prueft, dass list_models konfigurierte DomainErrors ausloest."""
    err = DomainError(code=SERVER_UNAVAILABLE, user_message="Server nicht erreichbar")
    provider = FakeProvider(list_models_error=err)

    with pytest.raises(DomainError) as exc_info:
        provider.list_models()

    assert exc_info.value.code == SERVER_UNAVAILABLE
    assert "Server nicht erreichbar" in str(exc_info.value)

    # Nach set_list_models_error(None) wieder erfolgreich
    provider.set_list_models_error(None)
    assert provider.list_models() == ("fake-model", "qwen2.5-coder:1.5b")


def test_stream_chat_standard_flow() -> None:
    """Prueft regulaeren Ablauf mit Deltas und abschliessendem Complete-Event."""
    provider = FakeProvider(default_deltas=["Token 1, ", "Token 2, ", "Fertig."])
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    assert len(events) == 4
    for event in events:
        assert event.session_id == "sess-test-01"
        assert event.request_id == "req-test-01"

    assert events[0].kind == "delta" and events[0].text == "Token 1, "
    assert events[1].kind == "delta" and events[1].text == "Token 2, "
    assert events[2].kind == "delta" and events[2].text == "Fertig."

    # Terminales Event ist genau einmal vorhanden und vom Typ "complete"
    assert events[3].kind == "complete"
    assert events[3].error_code is None


def test_stream_chat_model_specific_responses() -> None:
    """Prueft, dass modellspezifische Antworten zurueckgegeben werden."""
    provider = FakeProvider(
        models=["m1", "m2"],
        default_deltas=["Standard"],
        responses={"m2": ["Modell 2 ", "Spezifisch"]},
    )
    cancel = CancellationToken()

    req_m1 = _create_test_request(model="m1")
    events_m1 = list(provider.stream_chat(req_m1, cancel))
    assert [e.text for e in events_m1 if e.kind == "delta"] == ["Standard"]
    assert events_m1[-1].kind == "complete"

    req_m2 = _create_test_request(model="m2")
    events_m2 = list(provider.stream_chat(req_m2, cancel))
    assert [e.text for e in events_m2 if e.kind == "delta"] == ["Modell 2 ", "Spezifisch"]
    assert events_m2[-1].kind == "complete"


def test_stream_chat_unknown_model_error() -> None:
    """Prueft Verhalten bei Anforderung eines unbekannten Modells."""
    provider = FakeProvider(models=["known-model"])
    request = _create_test_request(model="unknown-model")
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    assert len(events) == 1
    event = events[0]
    assert event.kind == "error"
    assert event.error_code == MODEL_NOT_FOUND
    assert "unknown-model" in event.text


def test_stream_chat_pre_cancelled() -> None:
    """Prueft Abbruch, wenn das Token vor Aufruf bereits gesetzt ist."""
    provider = FakeProvider()
    request = _create_test_request()
    cancel = CancellationToken()
    cancel.cancel()

    events = list(provider.stream_chat(request, cancel))

    assert len(events) == 1
    assert events[0].kind == "cancelled"
    assert events[0].session_id == request.packet.session_id
    assert events[0].request_id == request.packet.request_id


def test_stream_chat_mid_stream_cancellation() -> None:
    """Prueft Abbruch waehrend des laufenden Streamings."""
    provider = FakeProvider(default_deltas=["Delta 1", "Delta 2", "Delta 3", "Delta 4"])
    request = _create_test_request()
    cancel = CancellationToken()

    collected_events: list[ProviderEvent] = []
    for event in provider.stream_chat(request, cancel):
        collected_events.append(event)
        if len(collected_events) == 2:
            # Nach 2 Deltas Abbruch ausloesen
            cancel.cancel()

    # Es muessen 2 Deltas + 1 Cancelled-Event vorliegen
    assert len(collected_events) == 3
    assert collected_events[0].kind == "delta"
    assert collected_events[1].kind == "delta"
    assert collected_events[2].kind == "cancelled"

    # Terminales Event ist einziges Nicht-Delta
    terminal_events = [e for e in collected_events if e.kind != "delta"]
    assert len(terminal_events) == 1
    assert terminal_events[0].kind == "cancelled"


def test_stream_chat_immediate_error() -> None:
    """Prueft sofortige Fehler-Emission ohne vorangehende Deltas."""
    provider = FakeProvider(
        error_code=SERVER_UNAVAILABLE,
        error_message="Ollama-Dienst nicht gestartet",
    )
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    assert len(events) == 1
    assert events[0].kind == "error"
    assert events[0].error_code == SERVER_UNAVAILABLE
    assert events[0].text == "Ollama-Dienst nicht gestartet"


def test_stream_chat_mid_stream_error() -> None:
    """Prueft Fehler-Emission nach bereits gesendeten Deltas."""
    provider = FakeProvider(
        default_deltas=["Teil 1", "Teil 2", "Teil 3"],
        error_code=SERVER_UNAVAILABLE,
        error_message="Verbindung unterbrochen",
        error_at_delta=2,
    )
    request = _create_test_request()
    cancel = CancellationToken()

    events = list(provider.stream_chat(request, cancel))

    # Erwartet: 2 Deltas ("Teil 1", "Teil 2") gefolgt von terminalem Fehler-Event
    assert len(events) == 3
    assert events[0].kind == "delta" and events[0].text == "Teil 1"
    assert events[1].kind == "delta" and events[1].text == "Teil 2"
    assert events[2].kind == "error"
    assert events[2].error_code == SERVER_UNAVAILABLE
    assert events[2].text == "Verbindung unterbrochen"


def test_dynamic_configuration_methods() -> None:
    """Prueft dynamisches Setzen und Zuruecksetzen von Antworten und Fehlern."""
    provider = FakeProvider()
    request = _create_test_request()
    cancel = CancellationToken()

    # 1. Konfiguriere Fehler
    provider.set_error(SERVER_UNAVAILABLE, "Temporaerer Ausfall")
    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 1
    assert events[0].kind == "error"

    # 2. Fehler zuruecksetzen und neue Deltas setzen
    provider.clear_error()
    provider.set_responses(default_deltas=["Neu 1", "Neu 2"])
    events = list(provider.stream_chat(request, cancel))
    assert len(events) == 3
    assert [e.text for e in events if e.kind == "delta"] == ["Neu 1", "Neu 2"]
    assert events[-1].kind == "complete"
