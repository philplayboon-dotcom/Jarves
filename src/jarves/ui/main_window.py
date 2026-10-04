"""Hauptfenster der Jarves-AI Desktop-Anwendung."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QWidget,
)

from jarves.ui.chat_panel import ChatPanel
from jarves.ui.settings_dialog import ModelSettings, SettingsDialog


class MainWindow(QMainWindow):
    """Hauptfenster von Jarves-AI.

    Layout (gemaess UX.md):
    - Oben: Menueleiste & Statusanzeige
    - Mitte: Splitter mit ChatPanel (zentral) und erweiterbaren Panels (Kontext/Sitzung)
    - Unten: QStatusBar fuer globale Statusmeldungen
    """

    settings_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._current_settings = ModelSettings()

        self.setWindowTitle("Jarves-AI — Lokaler Entwicklungsassistent")
        self.resize(1000, 700)
        self.setMinimumSize(640, 480)

        self._setup_ui()
        self._setup_menus()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # Haupt-Splitter (horizontal fuer spaetere Kontext-/Sitzungspanels)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)

        # Chat-Panel als zentrales Element
        self.chat_panel = ChatPanel(self.main_splitter)
        self.main_splitter.addWidget(self.chat_panel)

        main_layout.addWidget(self.main_splitter)

        # Statusleiste
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bereit")

    def _setup_menus(self) -> None:
        menu_bar = self.menuBar()

        # Datei-Menue
        file_menu = menu_bar.addMenu("&Datei")

        self.action_exit = QAction("&Beenden", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.triggered.connect(self.close)
        file_menu.addAction(self.action_exit)

        # Einstellungen-Menue
        settings_menu = menu_bar.addMenu("&Einstellungen")

        self.action_settings = QAction("&Einstellungen...", self)
        self.action_settings.setShortcut(QKeySequence.StandardKey.Preferences)
        self.action_settings.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(self.action_settings)

        # Hilfe-Menue
        help_menu = menu_bar.addMenu("&Hilfe")
        self.action_about = QAction("&Ueber Jarves-AI", self)
        help_menu.addAction(self.action_about)

    def get_settings(self) -> ModelSettings:
        """Gibt die aktuellen Modell- und Provider-Einstellungen zurueck."""
        return self._current_settings

    def set_settings(self, settings: ModelSettings) -> None:
        """Aktualisiert die hinterlegten Einstellungen."""
        self._current_settings = settings

    def open_settings_dialog(self) -> SettingsDialog | None:
        """Oeffnet den Einstellungsdialog modal und signalisiert Aenderungen."""
        dialog = SettingsDialog(self, settings=self._current_settings)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self._current_settings = new_settings
            self.settings_changed.emit(new_settings)
            return dialog
        return dialog
