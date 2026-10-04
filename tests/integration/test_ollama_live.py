"""Opt-in Live-Integrationstest gegen laufenden lokalen Ollama-Server."""

from __future__ import annotations

import pytest

from jarves.domain.cancellation import CancellationToken
from jarves.domain.models import ChatMessage, ChatRequest, ContextPacket
from jarves.infrastructure.providers.ollama import OllamaProvider


@pytest.mark.integration
@pytest.mark.ollama
def test_live_ollama_list_models_and_stream() -> None:
    """Testet echten lokalen Ollama-Aufruf (falls Server laeuft)."""
    provider = OllamaProvider(endpoint="http://127.0.0.1:11434")

    # 1. list_models
    models = provider.list_models()
    assert len(models) > 0, "Mindestens ein Modell sollte verfuegbar sein"
    chosen_model = models[0]

    # 2. stream_chat
    token = CancellationToken()
    msg = ChatMessage(role="user", content="Antworte nur mit dem Wort 'TEST'.")
    packet = ContextPacket(
        session_id="live-sess",
        request_id="live-req",
        sources=(),
        messages=(msg,),
        estimated_prompt_tokens=10,
        warnings=(),
    )
    request = ChatRequest(packet=packet, model=chosen_model, num_predict=10)

    events = list(provider.stream_chat(request, token))
    assert len(events) >= 2, "Erwartet mindestens 1 Delta und 1 Complete-Event"
    assert events[-1].kind == "complete"
    full_text = "".join(e.text for e in events if e.kind == "delta")
    assert len(full_text) > 0
