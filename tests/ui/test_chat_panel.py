"""UI-Tests fuer ChatPanel und MainWindow."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from jarves.ui.chat_panel import ChatPanel
from jarves.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Stellt sicher, dass eine QApplication-Instanz fuer Headless-Tests existiert."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["--platform", "offscreen"])
    return app  # type: ignore[return-value]


@pytest.mark.ui
def test_chat_panel_initial_state(qapp: QApplication) -> None:
    """Prueft die Initialisierung des ChatPanels."""
    panel = ChatPanel()

    assert "Inaktiv" in panel.lbl_session_status.text()
    assert "Modell: -" in panel.lbl_model_info.text()
    assert "Bereit" in panel.lbl_request_status.text()
    assert not panel.btn_send.isEnabled()
    assert not panel.btn_cancel.isEnabled()
    assert not panel.input_edit.isReadOnly()
    assert panel.input_edit.toPlainText() == ""


@pytest.mark.ui
def test_chat_panel_send_button_enables_with_text(qapp: QApplication) -> None:
    """Prueft, dass der Senden-Button nur bei vorhandenem Text aktivierbar ist."""
    panel = ChatPanel()

    # Leerer Text / Leerzeichen -> Button inaktiv
    panel.input_edit.setPlainText("   ")
    assert not panel.btn_send.isEnabled()

    # Gueltiger Text -> Button aktiv
    panel.input_edit.setPlainText("Hallo Modell!")
    assert panel.btn_send.isEnabled()

    # Text geleert -> Button wieder inaktiv
    panel.input_edit.setPlainText("")
    assert not panel.btn_send.isEnabled()


@pytest.mark.ui
def test_chat_panel_send_signal(qapp: QApplication) -> None:
    """Prueft, dass Senden das send_requested-Signal mit dem Text emittiert."""
    panel = ChatPanel()
    emitted_texts: list[str] = []

    panel.send_requested.connect(emitted_texts.append)

    panel.input_edit.setPlainText("Testfrage fuer Jarves")
    panel.btn_send.click()

    assert emitted_texts == ["Testfrage fuer Jarves"]
    assert panel.input_edit.toPlainText() == ""
    assert not panel.btn_send.isEnabled()


@pytest.mark.ui
def test_chat_panel_cancel_signal(qapp: QApplication) -> None:
    """Prueft, dass Abbrechen das cancel_requested-Signal emittiert, wenn Status running ist."""
    panel = ChatPanel()
    cancelled = False

    def on_cancel() -> None:
        nonlocal cancelled
        cancelled = True

    panel.cancel_requested.connect(on_cancel)

    # Im Idle-Zustand tut Klick nichts
    panel.btn_cancel.click()
    assert not cancelled

    # Im Running-Zustand ist Abbrechen aktiv
    panel.set_request_state("running")
    assert panel.btn_cancel.isEnabled()
    assert not panel.btn_send.isEnabled()
    assert panel.input_edit.isReadOnly()

    panel.btn_cancel.click()
    assert cancelled


@pytest.mark.ui
def test_chat_panel_state_transitions(qapp: QApplication) -> None:
    """Prueft die UI-Aktualisierungen bei Zustandswechseln."""
    panel = ChatPanel()

    panel.set_session_state("active")
    assert "Aktiv" in panel.lbl_session_status.text()

    panel.set_session_state("paused")
    assert "Pausiert" in panel.lbl_session_status.text()

    panel.set_model_name("qwen2.5-coder:1.5b")
    assert "Modell: qwen2.5-coder:1.5b" in panel.lbl_model_info.text()

    panel.set_request_state("cancelling")
    assert "Wird abgebrochen" in panel.lbl_request_status.text()
    assert not panel.btn_cancel.isEnabled()
    assert not panel.btn_send.isEnabled()


@pytest.mark.ui
def test_chat_panel_messages_and_streaming(qapp: QApplication) -> None:
    """Prueft das Hinzufuegen von Nachrichten, Streaming-Deltas und Fehlern."""
    panel = ChatPanel()

    panel.append_user_message("Wie funktioniert der Controller?")
    history_text = panel.chat_history_browser.toPlainText()
    assert "Du:" in history_text
    assert "Wie funktioniert der Controller?" in history_text

    # Assistenten-Streaming
    panel.start_assistant_message()
    panel.append_assistant_delta("Der Controller ")
    panel.append_assistant_delta("verwaltet die Sitzung.")
    panel.finish_assistant_message()

    history_text = panel.chat_history_browser.toPlainText()
    assert "Assistent:" in history_text
    assert "Der Controller verwaltet die Sitzung." in history_text

    # Systemhinweis
    panel.append_system_notice("Anfrage wurde abgebrochen.")
    history_text = panel.chat_history_browser.toPlainText()
    assert "Anfrage wurde abgebrochen." in history_text

    # Fehlerhinweis
    panel.append_error_message("Ollama ist nicht erreichbar.", error_code="SERVER_UNAVAILABLE")
    history_text = panel.chat_history_browser.toPlainText()
    assert "SERVER_UNAVAILABLE" in history_text
    assert "Ollama ist nicht erreichbar." in history_text

    # Clear
    panel.clear_chat()
    assert panel.chat_history_browser.toPlainText() == ""


@pytest.mark.ui
def test_main_window_initialization(qapp: QApplication) -> None:
    """Prueft, dass das Hauptfenster ordnungsgemaess initialisiert wird."""
    window = MainWindow()

    assert "Jarves-AI" in window.windowTitle()
    assert window.chat_panel is not None
    assert window.status_bar is not None
    assert window.status_bar.currentMessage() == "Bereit"
    assert window.menuBar() is not None
