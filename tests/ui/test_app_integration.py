"""Integrationstests fuer Composition Root und Fake UI Demo (Gate G1)."""

from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from jarves.app import JarvesApplication
from jarves.infrastructure.providers.fake import FakeProvider
from jarves.ui.main_window import MainWindow

os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture
def qapp() -> QApplication:
    """Stellt sicher, dass eine QApplication existiert."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_app_initialization(qapp: QApplication) -> None:
    """Testet die Initialisierung der Anwendung im Composition Root."""
    provider = FakeProvider(models=["qwen2.5-coder:1.5b", "fake-model"])
    window = MainWindow()
    app_instance = JarvesApplication(provider=provider, main_window=window)

    assert app_instance.session_manager.session_state == "active"
    assert app_instance.session_manager.session_id is not None
    assert app_instance.chat_panel.lbl_session_status.text() == "Sitzung: Aktiv"
    assert app_instance.chat_panel.lbl_model_info.text() == "Modell: qwen2.5-coder:1.5b"
    assert "Jarves-AI gestartet" in app_instance.chat_panel.chat_history_browser.toPlainText()


def test_app_send_and_stream_flow(qapp: QApplication) -> None:
    """Testet den vollstaendigen Ablauf vom Senden bis zum Abschluss des Streamings."""
    provider = FakeProvider(
        default_deltas=["Erste Zeile.\n", "Zweite Zeile."],
    )
    window = MainWindow()
    app_instance = JarvesApplication(provider=provider, main_window=window)

    # Senden ausloesen
    app_instance.chat_panel.input_edit.setPlainText("Hallo Jarves!")
    app_instance.chat_panel._on_send_clicked()

    # Warten, bis der Hintergrundworker fertig ist
    if app_instance._active_worker is not None:
        app_instance._active_worker.wait(2000)
    QCoreApplication.processEvents()

    chat_text = app_instance.chat_panel.chat_history_browser.toPlainText()
    assert "Hallo Jarves!" in chat_text
    assert "Erste Zeile." in chat_text
    assert "Zweite Zeile." in chat_text
    assert app_instance.session_manager.request_state == "idle"
    assert app_instance.chat_panel.lbl_request_status.text() == "Bereit"


def test_app_cancel_flow(qapp: QApplication) -> None:
    """Testet den Abbruch einer laufenden Anfrage."""
    provider = FakeProvider()
    window = MainWindow()
    app_instance = JarvesApplication(provider=provider, main_window=window)

    # Anfrage starten
    app_instance.handle_send_request("Lange Anfrage")
    assert app_instance.session_manager.request_state == "running"

    # Abbruch anfordern
    app_instance.handle_cancel_request()

    if app_instance._active_worker is not None:
        app_instance._active_worker.wait(2000)
    QCoreApplication.processEvents()

    assert app_instance.session_manager.request_state == "idle"
    chat_text = app_instance.chat_panel.chat_history_browser.toPlainText()
    assert "Lange Anfrage" in chat_text


def test_app_error_flow(qapp: QApplication) -> None:
    """Testet die Fehleranzeige im Chatverlauf bei einem Provider-Fehler."""
    provider = FakeProvider(
        error_code="SERVER_UNAVAILABLE",
        error_message="Ollama ist nicht erreichbar.",
    )
    window = MainWindow()
    app_instance = JarvesApplication(provider=provider, main_window=window)

    app_instance.handle_send_request("Fehlertest")

    if app_instance._active_worker is not None:
        app_instance._active_worker.wait(2000)
    QCoreApplication.processEvents()

    assert app_instance.session_manager.request_state == "idle"
    chat_text = app_instance.chat_panel.chat_history_browser.toPlainText()
    assert "Fehler (SERVER_UNAVAILABLE): Ollama ist nicht erreichbar." in chat_text
