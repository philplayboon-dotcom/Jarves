"""ChatPanel UI-Komponente fuer Jarves-AI."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from jarves.domain.models import RequestState, SessionState


class ChatPanel(QWidget):
    """Zentrale Chat-Komponente mit Statusanzeige, Verlauf, Eingabefeld und Aktionen.

    Entkopplung:
    - Sendet Signale (send_requested, cancel_requested), wenn Aktionen getriggert werden.
    - Stellt Methoden bereit, um von aussen (Controller/Worker/EventBridge) aktualisiert zu werden.
    """

    send_requested = Signal(str)
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._session_state: SessionState = "inactive"
        self._request_state: RequestState = "idle"
        self._current_model: str = "-"
        self._current_streaming_text: str = ""

        self._setup_ui()
        self._update_state_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 1. Statusleiste (oben)
        self.status_bar_frame = QFrame(self)
        self.status_bar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(self.status_bar_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)

        self.lbl_session_status = QLabel("Sitzung: Inaktiv", self)
        self.lbl_model_info = QLabel("Modell: -", self)
        self.lbl_request_status = QLabel("Bereit", self)

        status_layout.addWidget(self.lbl_session_status)
        status_layout.addSpacing(16)
        status_layout.addWidget(self.lbl_model_info)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_request_status)

        main_layout.addWidget(self.status_bar_frame)

        # 2. Splitter fuer Chat-Verlauf und Eingabe
        splitter = QSplitter(Qt.Orientation.Vertical, self)

        # Chat-Historie (QTextBrowser fuer sichere, scrollbare Textanzeige)
        self.chat_history_browser = QTextBrowser(self)
        # Keine externen Links oeffnen (Security-Grenze)
        self.chat_history_browser.setOpenExternalLinks(False)
        self.chat_history_browser.setOpenLinks(False)
        self.chat_history_browser.setPlaceholderText("Noch keine Nachrichten vorhanden.")
        font = QFont("Segoe UI", 10)
        self.chat_history_browser.setFont(font)
        splitter.addWidget(self.chat_history_browser)

        # Eingabebereich Container
        input_container = QWidget(self)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 4, 0, 0)
        input_layout.setSpacing(4)

        # Eingabefeld (QPlainTextEdit)
        self.input_edit = QPlainTextEdit(input_container)
        self.input_edit.setPlaceholderText(
            "Nachricht oder Frage eingeben... (Strg+Enter zum Senden)"
        )
        self.input_edit.setFont(font)
        self.input_edit.textChanged.connect(self._on_input_text_changed)
        input_layout.addWidget(self.input_edit)

        # Button-Leiste
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_send = QPushButton("Senden", input_container)
        self.btn_send.clicked.connect(self._on_send_clicked)
        self.btn_send.setEnabled(False)

        self.btn_cancel = QPushButton("Abbrechen", input_container)
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        self.btn_cancel.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_send)

        input_layout.addLayout(button_layout)
        splitter.addWidget(input_container)

        # Groessenverhaeltnis Splitter (z.B. 4:1)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    # --- Zustaende und Status-Updates ---

    def set_session_state(self, state: SessionState) -> None:
        """Aktualisiert den Zustand der Sitzung (inactive, active, paused)."""
        self._session_state = state
        self._update_state_ui()

    def set_request_state(self, state: RequestState) -> None:
        """Aktualisiert den Zustand der Anfrage (idle, running, cancelling)."""
        self._request_state = state
        self._update_state_ui()

    def set_model_name(self, model_name: str) -> None:
        """Setzt den Namen des aktiven Modells."""
        self._current_model = model_name or "-"
        self.lbl_model_info.setText(f"Modell: {self._current_model}")

    def _update_state_ui(self) -> None:
        # Sitzungsanzeige
        session_text_map = {
            "inactive": "Inaktiv",
            "active": "Aktiv",
            "paused": "Pausiert",
        }
        session_str = session_text_map.get(self._session_state, self._session_state.title())
        self.lbl_session_status.setText(f"Sitzung: {session_str}")

        # Requestanzeige
        request_text_map = {
            "idle": "Bereit",
            "running": "Generiere Antwort...",
            "cancelling": "Wird abgebrochen...",
        }
        req_str = request_text_map.get(self._request_state, self._request_state.title())
        self.lbl_request_status.setText(req_str)

        # Button-Zustaende
        is_running = self._request_state in ("running", "cancelling")
        has_text = bool(self.input_edit.toPlainText().strip())

        self.btn_send.setEnabled(not is_running and has_text)
        self.btn_cancel.setEnabled(self._request_state == "running")
        self.input_edit.setReadOnly(is_running)

    def _on_input_text_changed(self) -> None:
        if self._request_state == "idle":
            has_text = bool(self.input_edit.toPlainText().strip())
            self.btn_send.setEnabled(has_text)

    # --- Benutzeraktionen ---

    def _on_send_clicked(self) -> None:
        text = self.input_edit.toPlainText().strip()
        if not text or self._request_state != "idle":
            return

        self.input_edit.clear()
        self.send_requested.emit(text)

    def _on_cancel_clicked(self) -> None:
        if self._request_state == "running":
            self.cancel_requested.emit()

    # --- Nachrichtenanzeige & Streaming ---

    def append_user_message(self, text: str) -> None:
        """Fuegt eine Nutzernachricht in den Chatverlauf ein."""
        escaped = html.escape(text).replace("\n", "<br>")
        html_msg = f'<div style="margin-bottom: 8px;"><b>Du:</b><br>{escaped}</div>'
        self.chat_history_browser.append(html_msg)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> None:
        """Bereitet die Anzeige fuer eine neue gestreamte Assistentenantwort vor."""
        self._current_streaming_text = ""
        self.chat_history_browser.append(
            '<div><b>Assistent:</b><br><span id="current_stream"></span></div>'
        )
        self._scroll_to_bottom()

    def append_assistant_delta(self, delta_text: str) -> None:
        """Haengt Textfragmente (Delta) an die laufende Assistentenantwort an."""
        if not delta_text:
            return
        self._current_streaming_text += delta_text
        # Cursor an das Ende setzen und Plain Text anhaengen
        cursor = self.chat_history_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(delta_text)
        self.chat_history_browser.setTextCursor(cursor)
        self._scroll_to_bottom()

    def finish_assistant_message(self, final_text: str | None = None) -> None:
        """Schliesst die Assistentenantwort ab."""
        if final_text is not None and not self._current_streaming_text:
            cursor = self.chat_history_browser.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(final_text)
            self.chat_history_browser.setTextCursor(cursor)
        self._current_streaming_text = ""
        self.chat_history_browser.append("<br>")
        self._scroll_to_bottom()

    def append_system_notice(self, notice: str) -> None:
        """Zeigt einen Systemhinweis (z.B. Abbruch oder Info) im Verlauf an."""
        escaped = html.escape(notice).replace("\n", "<br>")
        html_notice = (
            f'<div style="color: #666; font-style: italic; margin-bottom: 8px;">'
            f"[Hinweis: {escaped}]</div>"
        )
        self.chat_history_browser.append(html_notice)
        self._scroll_to_bottom()

    def append_error_message(self, error_message: str, error_code: str | None = None) -> None:
        """Zeigt eine Fehlermeldung mit optionalem Fehlercode im Verlauf an."""
        escaped_msg = html.escape(error_message).replace("\n", "<br>")
        code_suffix = f" ({html.escape(error_code)})" if error_code else ""
        html_err = (
            f'<div style="color: #d93025; margin-bottom: 8px;">'
            f"<b>Fehler{code_suffix}:</b> {escaped_msg}</div>"
        )
        self.chat_history_browser.append(html_err)
        self._scroll_to_bottom()

    def clear_chat(self) -> None:
        """Leert den Chatverlauf und das Eingabefeld."""
        self.chat_history_browser.clear()
        self.input_edit.clear()
        self._current_streaming_text = ""

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.chat_history_browser.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())
