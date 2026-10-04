"""Composition Root fuer Jarves-AI."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

try:
    from jarves.application.session import SessionManager
    from jarves.domain.models import ChatMessage, ChatRequest, ContextPacket
    from jarves.infrastructure.providers.fake import FakeProvider
    from jarves.infrastructure.providers.ollama import OllamaProvider
    from jarves.ui.event_bridge import EventBridge
    from jarves.ui.main_window import MainWindow
    from jarves.ui.settings_dialog import ModelSettings
    from jarves.ui.workers import InferenceWorker
except ModuleNotFoundError:
    # Fallback fuer direkten Skriptaufruf in IDE ohne gesetzten PYTHONPATH
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from jarves.application.session import SessionManager
    from jarves.domain.models import ChatMessage, ChatRequest, ContextPacket
    from jarves.infrastructure.providers.fake import FakeProvider
    from jarves.infrastructure.providers.ollama import OllamaProvider
    from jarves.ui.event_bridge import EventBridge
    from jarves.ui.main_window import MainWindow
    from jarves.ui.settings_dialog import ModelSettings
    from jarves.ui.workers import InferenceWorker

if TYPE_CHECKING:
    from jarves.domain.ports import ModelProvider


class JarvesApplication:
    """Verdrahtet SessionManager, Provider, EventBridge und UI."""

    def __init__(
        self,
        provider: ModelProvider | None = None,
        main_window: MainWindow | None = None,
    ) -> None:
        self.session_manager = SessionManager()
        self.provider: ModelProvider = provider or FakeProvider()
        self.main_window = main_window or MainWindow()
        self.chat_panel = self.main_window.chat_panel

        self.event_bridge = EventBridge(self.chat_panel)
        self.event_bridge.set_request_finished_callback(self._on_request_finished)

        self._active_worker: InferenceWorker | None = None

        # Standardeinstellungen ermitteln
        provider_type = "ollama" if isinstance(self.provider, OllamaProvider) else "fake"
        endpoint = (
            getattr(self.provider, "_endpoint", "http://127.0.0.1:11434")
            if provider_type == "ollama"
            else "http://127.0.0.1:11434"
        )
        self.settings = ModelSettings(
            provider_type=provider_type,
            endpoint=endpoint,
            model="fake-model" if provider_type == "fake" else "qwen2.5-coder:1.5b",
        )

        self._connect_signals()
        self._initialize_state()

    def _connect_signals(self) -> None:
        self.chat_panel.send_requested.connect(self.handle_send_request)
        self.chat_panel.cancel_requested.connect(self.handle_cancel_request)
        self.main_window.settings_changed.connect(self.apply_settings)

    def _initialize_state(self) -> None:
        # Initialisiere erste Sitzung
        session_id = self.session_manager.start_session()
        self.chat_panel.set_session_state("active")

        # Initialisiere Modell-Anzeige
        try:
            models = self.provider.list_models()
            model_name = models[0] if models else self.settings.model
        except Exception:
            model_name = self.settings.model

        self.settings = ModelSettings(
            provider_type=self.settings.provider_type,
            endpoint=self.settings.endpoint,
            model=model_name,
        )
        self.main_window.set_settings(self.settings)
        self.chat_panel.set_model_name(model_name)
        mode_label = (
            "Ollama" if self.settings.provider_type == "ollama" else "Demo-Modus mit Fake-Provider"
        )
        self.chat_panel.append_system_notice(
            f"Jarves-AI gestartet ({mode_label}). Sitzung: {session_id[:8]}..."
        )

    def apply_settings(self, settings: ModelSettings) -> None:
        """Wendet geaenderte Modell- und Provider-Einstellungen an."""
        self.settings = settings
        self.main_window.set_settings(settings)

        if settings.provider_type == "ollama":
            self.provider = OllamaProvider(endpoint=settings.endpoint)
        else:
            self.provider = FakeProvider()

        self.chat_panel.set_model_name(settings.model)
        self.main_window.status_bar.showMessage(f"Modell auf '{settings.model}' gesetzt.", 3000)
        mode_label = "Lokales Ollama" if settings.provider_type == "ollama" else "Demo-Modus"
        self.chat_panel.append_system_notice(
            f"Einstellungen aktualisiert: {settings.model} ({mode_label})"
        )

    def handle_send_request(self, text: str) -> None:
        """Wird ausgeloest, wenn der Nutzer im Chat eine Nachricht sendet."""
        if self.session_manager.session_state == "inactive":
            self.session_manager.start_session()
            self.chat_panel.set_session_state("active")

        if self.session_manager.request_state != "idle":
            return

        session_id = self.session_manager.session_id or ""
        request_id, cancel_token = self.session_manager.start_request()

        self.chat_panel.set_request_state("running")
        self.chat_panel.append_user_message(text)
        self.chat_panel.start_assistant_message()

        self.event_bridge.set_active_ids(session_id, request_id)

        # ContextPacket und ChatRequest erstellen
        msg = ChatMessage(role="user", content=text)
        packet = ContextPacket(
            session_id=session_id,
            request_id=request_id,
            sources=(),
            messages=(msg,),
            estimated_prompt_tokens=len(text.encode("utf-8")),
            warnings=(),
        )
        model_name = self.settings.model or "fake-model"
        request = ChatRequest(packet=packet, model=model_name)

        # Worker starten
        worker = InferenceWorker(self.provider, request, cancel_token)
        self._active_worker = worker
        worker.event_received.connect(self.event_bridge.handle_event)
        worker.finished.connect(self._on_worker_thread_finished)
        worker.start()

    def handle_cancel_request(self) -> None:
        """Bricht die laufende Anfrage ab."""
        if self.session_manager.request_state == "running":
            self.session_manager.cancel_request()
            self.chat_panel.set_request_state("cancelling")

    def _on_request_finished(self) -> None:
        """Callback von der EventBridge bei Erreichen eines terminalen Events."""
        if self.session_manager.request_state in ("running", "cancelling"):
            self.session_manager.finish_request()
        self.chat_panel.set_request_state("idle")

    def _on_worker_thread_finished(self) -> None:
        """Aufraeumen des Worker-Threads nach Beendigung."""
        if self._active_worker is not None:
            self._active_worker.deleteLater()
            self._active_worker = None


def create_app(
    provider: ModelProvider | None = None,
) -> tuple[QApplication, MainWindow, JarvesApplication]:
    """Erstellt und verdrahtet die Anwendungskomponenten."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    main_window = MainWindow()
    jarves_app = JarvesApplication(provider=provider, main_window=main_window)
    return app, main_window, jarves_app


def run_app(argv: list[str] | None = None) -> int:
    """Startet die Jarves-AI Desktop-Anwendung."""
    if argv is None:
        argv = sys.argv[1:]

    if "--version" in argv:
        sys.stdout.write("Jarves-AI v0.1.0\n")
        return 0

    app, window, _ = create_app()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(run_app())
