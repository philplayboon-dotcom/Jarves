"""Tests fuer InferenceWorker und EventBridge."""

import os
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication

from jarves.domain.cancellation import CancellationToken
from jarves.domain.models import ChatRequest, ContextPacket, ProviderEvent
from jarves.infrastructure.providers.fake import FakeProvider
from jarves.ui.chat_panel import ChatPanel
from jarves.ui.event_bridge import EventBridge
from jarves.ui.workers import InferenceWorker

# Set offscreen platform for headless Qt tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    """Provides a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def chat_panel(qapp):
    """Fixture for ChatPanel."""
    panel = ChatPanel()
    return panel


@pytest.fixture
def dummy_request():
    packet = ContextPacket(
        session_id="session-1",
        request_id="request-1",
        sources=(),
        messages=(),
        estimated_prompt_tokens=10,
        warnings=(),
    )
    return ChatRequest(packet=packet, model="fake-model")


def test_worker_emits_events(qapp, dummy_request):
    """Testet, dass der Worker Events vom FakeProvider sendet."""
    provider = FakeProvider(default_deltas=["Hallo ", "Welt"])
    cancel_token = CancellationToken()

    worker = InferenceWorker(provider, dummy_request, cancel_token)

    received_events = []
    worker.event_received.connect(received_events.append)

    loop = QEventLoop()
    worker.finished.connect(loop.quit)
    worker.start()
    loop.exec()

    assert len(received_events) == 3  # 2 deltas + 1 complete
    assert received_events[0].kind == "delta"
    assert received_events[0].text == "Hallo "
    assert received_events[1].kind == "delta"
    assert received_events[1].text == "Welt"
    assert received_events[2].kind == "complete"


def test_worker_cancel_interrupts_stream(qapp, dummy_request):
    """Testet, dass ein Cancel den Stream abbricht."""
    provider = FakeProvider(default_deltas=["Eins", "Zwei", "Drei"])
    cancel_token = CancellationToken()
    cancel_token.cancel()  # Sofort abbrechen

    worker = InferenceWorker(provider, dummy_request, cancel_token)
    received_events = []
    worker.event_received.connect(received_events.append)

    loop = QEventLoop()
    worker.finished.connect(loop.quit)
    worker.start()
    loop.exec()

    assert len(received_events) == 1
    assert received_events[0].kind == "cancelled"


def test_event_bridge_forwards_events(qapp, chat_panel, dummy_request):
    """Testet, dass die EventBridge gueltige Events an das Panel leitet."""
    bridge = EventBridge(chat_panel)
    bridge.set_active_ids("session-1", "request-1")

    callback_mock = Mock()
    bridge.set_request_finished_callback(callback_mock)

    # Delta Event
    delta_event = ProviderEvent("session-1", "request-1", "delta", "Hallo")
    bridge.handle_event(delta_event)
    assert "Hallo" in chat_panel.chat_history_browser.toPlainText()
    callback_mock.assert_not_called()

    # Complete Event
    complete_event = ProviderEvent("session-1", "request-1", "complete")
    bridge.handle_event(complete_event)
    callback_mock.assert_called_once()


def test_event_bridge_discards_stale_events(qapp, chat_panel):
    """Testet, dass die EventBridge veraltete Events ignoriert."""
    bridge = EventBridge(chat_panel)
    bridge.set_active_ids("session-2", "request-2")

    callback_mock = Mock()
    bridge.set_request_finished_callback(callback_mock)

    stale_event = ProviderEvent("session-1", "request-1", "delta", "Veraltet")
    bridge.handle_event(stale_event)

    assert "Veraltet" not in chat_panel.chat_history_browser.toPlainText()
    callback_mock.assert_not_called()
