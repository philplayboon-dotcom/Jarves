"""Einstellungsdialog fuer Modell- und Inferenz-Provider in Jarves-AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from jarves.domain.errors import SERVER_UNAVAILABLE, DomainError
from jarves.infrastructure.providers.fake import FakeProvider
from jarves.infrastructure.providers.ollama import (
    OllamaProvider,
    validate_and_normalize_endpoint,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

ProviderType = Literal["fake", "ollama"]


@dataclass(frozen=True)
class ModelSettings:
    """Konfiguration fuer Modell und Inferenz-Provider."""

    provider_type: ProviderType = "fake"
    endpoint: str = "http://127.0.0.1:11434"
    model: str = "fake-model"


class SettingsDialog(QDialog):
    """Einstellungsdialog zur Auswahl des Inferenz-Providers, Endpoints und Modells."""

    settings_applied = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        settings: ModelSettings | None = None,
        ollama_provider_factory: Any | None = None,
        fake_provider_factory: Any | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Einstellungen — Modell & Inferenz")
        self.setMinimumWidth(500)

        self._current_settings = settings or ModelSettings()
        self._ollama_provider_factory = ollama_provider_factory or OllamaProvider
        self._fake_provider_factory = fake_provider_factory or FakeProvider

        self._setup_ui()
        self.load_settings(self._current_settings)

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # 1. Provider-Auswahl
        self.group_provider = QGroupBox("Inferenz-Provider / Modus", self)
        provider_layout = QVBoxLayout(self.group_provider)

        self.rb_fake = QRadioButton(
            "Demo-Modus (Fake-Provider, ohne Netzwerk)", self.group_provider
        )
        self.rb_ollama = QRadioButton("Lokales Ollama (Ollama-Provider)", self.group_provider)

        self.provider_btn_group = QButtonGroup(self)
        self.provider_btn_group.addButton(self.rb_fake)
        self.provider_btn_group.addButton(self.rb_ollama)

        self.rb_fake.toggled.connect(self._on_provider_mode_changed)
        self.rb_ollama.toggled.connect(self._on_provider_mode_changed)

        provider_layout.addWidget(self.rb_fake)
        provider_layout.addWidget(self.rb_ollama)
        main_layout.addWidget(self.group_provider)

        # 2. Ollama-Endpoint
        self.group_endpoint = QGroupBox("Lokaler Ollama-Endpunkt", self)
        endpoint_layout = QVBoxLayout(self.group_endpoint)

        endpoint_row = QHBoxLayout()
        self.lbl_endpoint = QLabel("Endpunkt-URL:", self.group_endpoint)
        self.edit_endpoint = QLineEdit(self.group_endpoint)
        self.edit_endpoint.setPlaceholderText("http://127.0.0.1:11434")
        endpoint_row.addWidget(self.lbl_endpoint)
        endpoint_row.addWidget(self.edit_endpoint)
        endpoint_layout.addLayout(endpoint_row)

        self.lbl_endpoint_hint = QLabel(
            "Hinweis: Ausschliesslich unverschluesselte lokale Loopback-Adressen "
            "(127.0.0.1, [::1] oder localhost) zulaessig. Keine Cloud-Dienste, keine API-Keys.",
            self.group_endpoint,
        )
        self.lbl_endpoint_hint.setWordWrap(True)
        self.lbl_endpoint_hint.setStyleSheet("color: #666; font-size: 11px;")
        endpoint_layout.addWidget(self.lbl_endpoint_hint)

        main_layout.addWidget(self.group_endpoint)

        # 3. Verbindungspruefung & Modell-Laden
        check_layout = QHBoxLayout()
        self.btn_check_connection = QPushButton(
            "Verbindung pruefen / Modelle laden",
            self,
        )
        self.btn_check_connection.clicked.connect(self.check_connection)
        check_layout.addWidget(self.btn_check_connection)
        check_layout.addStretch()
        main_layout.addLayout(check_layout)

        # Statusanzeige fuer Pruefung
        self.lbl_status = QLabel("", self)
        self.lbl_status.setWordWrap(True)
        main_layout.addWidget(self.lbl_status)

        # 4. Modellauswahl
        self.group_model = QGroupBox("Modellauswahl", self)
        model_layout = QVBoxLayout(self.group_model)

        model_row = QHBoxLayout()
        self.lbl_model = QLabel("Modellname:", self.group_model)
        self.combo_model = QComboBox(self.group_model)
        self.combo_model.setEditable(True)
        model_row.addWidget(self.lbl_model)
        model_row.addWidget(self.combo_model, stretch=1)
        model_layout.addLayout(model_row)

        self.lbl_model_hint = QLabel(
            "Waehle ein verfuegbares Modell aus der Liste oder gib den "
            "Modellbezeichner manuell ein.",
            self.group_model,
        )
        self.lbl_model_hint.setWordWrap(True)
        self.lbl_model_hint.setStyleSheet("color: #666; font-size: 11px;")
        model_layout.addWidget(self.lbl_model_hint)

        main_layout.addWidget(self.group_model)

        main_layout.addStretch()

        # 5. Dialog-Buttons (Speichern / Abbrechen)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal,
            self,
        )
        save_btn = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        if save_btn is not None:
            save_btn.setText("Speichern")
        cancel_btn = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn is not None:
            cancel_btn.setText("Abbrechen")

        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _on_provider_mode_changed(self) -> None:
        is_ollama = self.rb_ollama.isChecked()
        self.edit_endpoint.setEnabled(is_ollama)
        self.lbl_endpoint.setEnabled(is_ollama)
        self.lbl_endpoint_hint.setEnabled(is_ollama)

        # Bei Umschalten Liste mit Standardwerten vorbesetzen, falls leer
        if not is_ollama and self.combo_model.count() == 0:
            self._update_model_list(["fake-model", "qwen2.5-coder:1.5b"])

    def load_settings(self, settings: ModelSettings) -> None:
        """Laedt bestehende Einstellungen in die UI-Elemente."""
        self._current_settings = settings
        if settings.provider_type == "ollama":
            self.rb_ollama.setChecked(True)
        else:
            self.rb_fake.setChecked(True)

        self.edit_endpoint.setText(settings.endpoint or "http://127.0.0.1:11434")

        # Modellauswahl vorbesetzen
        self.combo_model.clear()
        if settings.model:
            self.combo_model.addItem(settings.model)
            self.combo_model.setCurrentText(settings.model)

        self._on_provider_mode_changed()
        self._set_status("", is_error=False)

    def get_provider_type(self) -> ProviderType:
        """Gibt den aktuell ausgewaehlten Provider-Typ zurueck."""
        return "ollama" if self.rb_ollama.isChecked() else "fake"

    def get_settings(self) -> ModelSettings:
        """Erzeugt ein ModelSettings-Objekt aus den aktuellen UI-Eingaben."""
        provider_type = self.get_provider_type()
        endpoint = self.edit_endpoint.text().strip() or "http://127.0.0.1:11434"
        model_text = self.combo_model.currentText().strip()

        if not model_text:
            model_text = "qwen2.5-coder:1.5b" if provider_type == "ollama" else "fake-model"

        return ModelSettings(
            provider_type=provider_type,
            endpoint=endpoint,
            model=model_text,
        )

    def check_connection(self) -> bool:
        """Prueft den konfigurierten Endpunkt und aktualisiert die Modellliste."""
        provider_type = self.get_provider_type()

        if provider_type == "fake":
            try:
                provider = self._fake_provider_factory()
                models = provider.list_models()
                self._update_model_list(models)
                self._set_status(
                    f"Demo-Modus aktiv. {len(models)} Test-Modell(e) verfuegbar.",
                    is_error=False,
                )
                return True
            except DomainError as err:
                self._set_status(err.user_message, is_error=True)
                return False
            except Exception as exc:
                self._set_status(f"Unerwarteter Fehler: {exc}", is_error=True)
                return False

        # Ollama-Modus
        raw_endpoint = self.edit_endpoint.text().strip()
        try:
            norm_endpoint = validate_and_normalize_endpoint(raw_endpoint)
        except DomainError as err:
            self._set_status(f"Ungueltiger Endpunkt: {err.user_message}", is_error=True)
            return False

        try:
            provider = self._ollama_provider_factory(endpoint=norm_endpoint)
            models = provider.list_models()
            self._update_model_list(models)
            count = len(models)
            if count == 0:
                self._set_status(
                    "Verbindung erfolgreich, aber keine Modelle auf Ollama gefunden. "
                    "Bitte lade ein Modell via 'ollama pull <modell>'.",
                    is_error=False,
                )
            else:
                self._set_status(
                    f"Verbindung erfolgreich. {count} Modell(e) verfuegbar.",
                    is_error=False,
                )
            return True
        except DomainError as err:
            if err.code == SERVER_UNAVAILABLE:
                msg = (
                    "Ollama ist nicht erreichbar. Starte den lokalen Dienst "
                    "oder nutze den Demo-Modus."
                )
            else:
                msg = err.user_message
            self._set_status(msg, is_error=True)
            return False
        except Exception as exc:
            self._set_status(f"Verbindungsfehler: {exc}", is_error=True)
            return False

    def _update_model_list(self, models: Sequence[str]) -> None:
        """Aktualisiert die ComboBox-Liste und behaelt die aktuelle Auswahl bei."""
        current_text = self.combo_model.currentText().strip()
        self.combo_model.clear()
        for model_name in models:
            self.combo_model.addItem(model_name)

        if current_text:
            idx = self.combo_model.findText(current_text)
            if idx >= 0:
                self.combo_model.setCurrentIndex(idx)
            else:
                self.combo_model.setEditText(current_text)
        elif self.combo_model.count() > 0:
            self.combo_model.setCurrentIndex(0)

    def _set_status(self, message: str, *, is_error: bool) -> None:
        """Setzt die Statusmeldung mit farblicher Unterscheidung."""
        self.lbl_status.setText(message)
        if not message:
            self.lbl_status.setStyleSheet("")
        elif is_error:
            self.lbl_status.setStyleSheet("color: #d93025; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: #188038; font-weight: bold;")

    def _on_accept(self) -> None:
        """Validiert und uebernimmt die Einstellungen."""
        settings = self.get_settings()
        self._current_settings = settings
        self.settings_applied.emit(settings)
        self.accept()
