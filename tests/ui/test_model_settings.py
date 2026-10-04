"""UI-Tests fuer den SettingsDialog und die Modellauswahl/Verfuegbarkeitspruefung."""

from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from jarves.app import JarvesApplication
from jarves.domain.errors import (
    PROVIDER_TIMEOUT,
    SERVER_UNAVAILABLE,
    DomainError,
)
from jarves.infrastructure.providers.fake import FakeProvider
from jarves.infrastructure.providers.ollama import OllamaProvider
from jarves.ui.main_window import MainWindow
from jarves.ui.settings_dialog import ModelSettings, SettingsDialog

os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Stellt sicher, dass eine QApplication-Instanz fuer Headless-Tests existiert."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["--platform", "offscreen"])
    return app  # type: ignore[return-value]


@pytest.mark.ui
def test_settings_dialog_initial_state_fake(qapp: QApplication) -> None:
    """Prueft die Initialisierung des Einstellungsdialogs im Fake-Modus."""
    dialog = SettingsDialog(
        settings=ModelSettings(
            provider_type="fake",
            endpoint="http://127.0.0.1:11434",
            model="fake-model",
        )
    )

    assert dialog.rb_fake.isChecked()
    assert not dialog.rb_ollama.isChecked()
    assert not dialog.edit_endpoint.isEnabled()
    assert dialog.edit_endpoint.text() == "http://127.0.0.1:11434"
    assert dialog.combo_model.currentText() == "fake-model"
    assert dialog.lbl_status.text() == ""


@pytest.mark.ui
def test_settings_dialog_initial_state_ollama(qapp: QApplication) -> None:
    """Prueft die Initialisierung des Einstellungsdialogs im Ollama-Modus."""
    dialog = SettingsDialog(
        settings=ModelSettings(
            provider_type="ollama",
            endpoint="http://127.0.0.1:11434",
            model="qwen2.5-coder:1.5b",
        )
    )

    assert dialog.rb_ollama.isChecked()
    assert not dialog.rb_fake.isChecked()
    assert dialog.edit_endpoint.isEnabled()
    assert dialog.combo_model.currentText() == "qwen2.5-coder:1.5b"


@pytest.mark.ui
def test_settings_dialog_toggle_provider_mode(qapp: QApplication) -> None:
    """Prueft die Umschaltung zwischen Demo-Modus und Ollama-Modus."""
    dialog = SettingsDialog()

    dialog.rb_ollama.setChecked(True)
    assert dialog.edit_endpoint.isEnabled()
    assert dialog.get_provider_type() == "ollama"

    dialog.rb_fake.setChecked(True)
    assert not dialog.edit_endpoint.isEnabled()
    assert dialog.get_provider_type() == "fake"


@pytest.mark.ui
def test_settings_dialog_check_connection_fake_success(qapp: QApplication) -> None:
    """Prueft Verbindungspruefung / Modell-Laden fuer FakeProvider."""
    fake_factory = lambda: FakeProvider(models=["demo-1", "demo-2"])  # noqa: E731
    dialog = SettingsDialog(fake_provider_factory=fake_factory)
    dialog.rb_fake.setChecked(True)

    success = dialog.check_connection()
    assert success is True
    assert "Demo-Modus aktiv" in dialog.lbl_status.text()
    assert dialog.combo_model.count() == 2
    assert dialog.combo_model.itemText(0) == "demo-1"
    assert dialog.combo_model.itemText(1) == "demo-2"


@pytest.mark.ui
def test_settings_dialog_check_connection_ollama_success(qapp: QApplication) -> None:
    """Prueft erfolgreiche Verbindungspruefung zu Ollama mit Modellabfrage."""
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.list_models.return_value = ("qwen2.5-coder:1.5b", "llama3.2:3b")
    ollama_factory = MagicMock(return_value=mock_provider)

    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434")

    success = dialog.check_connection()
    assert success is True
    ollama_factory.assert_called_once_with(endpoint="http://127.0.0.1:11434")
    assert "Verbindung erfolgreich" in dialog.lbl_status.text()
    assert "2 Modell(e)" in dialog.lbl_status.text()
    assert dialog.combo_model.count() == 2
    assert dialog.combo_model.itemText(0) == "qwen2.5-coder:1.5b"
    assert dialog.combo_model.itemText(1) == "llama3.2:3b"


@pytest.mark.ui
def test_settings_dialog_check_connection_server_unavailable(qapp: QApplication) -> None:
    """Prueft Fehlerbehandlung bei nicht erreichbarem Ollama-Server."""
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.list_models.side_effect = DomainError(
        SERVER_UNAVAILABLE, "Ollama nicht erreichbar"
    )
    ollama_factory = MagicMock(return_value=mock_provider)

    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)

    success = dialog.check_connection()
    assert success is False
    assert (
        "Ollama ist nicht erreichbar. Starte den lokalen Dienst oder nutze den Demo-Modus."
        in dialog.lbl_status.text()
    )


@pytest.mark.ui
def test_settings_dialog_check_connection_timeout(qapp: QApplication) -> None:
    """Prueft Fehlerbehandlung bei Timeout."""
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.list_models.side_effect = DomainError(
        PROVIDER_TIMEOUT, "Zeitueberschreitung bei der Kommunikation mit dem Ollama-Server."
    )
    ollama_factory = MagicMock(return_value=mock_provider)

    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)

    success = dialog.check_connection()
    assert success is False
    assert "Zeitueberschreitung" in dialog.lbl_status.text()


@pytest.mark.ui
def test_settings_dialog_invalid_endpoint_validation(qapp: QApplication) -> None:
    """Prueft, dass externe/unsichere Endpoints vor dem Verbindungsaufbau abgewiesen werden."""
    ollama_factory = MagicMock()
    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://cloud-server.com:11434")

    success = dialog.check_connection()
    assert success is False
    ollama_factory.assert_not_called()
    assert "Ungueltiger Endpunkt" in dialog.lbl_status.text()


@pytest.mark.ui
def test_settings_dialog_save_and_emit(qapp: QApplication) -> None:
    """Prueft das Uebernehmen der Einstellungen und Signalisieren."""
    dialog = SettingsDialog()
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434")
    dialog.combo_model.setEditText("custom-model:latest")

    emitted_settings: list[ModelSettings] = []
    dialog.settings_applied.connect(emitted_settings.append)

    dialog._on_accept()

    assert len(emitted_settings) == 1
    settings = emitted_settings[0]
    assert settings.provider_type == "ollama"
    assert settings.endpoint == "http://127.0.0.1:11434"
    assert settings.model == "custom-model:latest"


@pytest.mark.ui
def test_main_window_settings_menu_and_signal(qapp: QApplication) -> None:
    """Prueft die Menueanbindung im MainWindow."""
    window = MainWindow()
    assert window.action_settings is not None

    emitted: list[ModelSettings] = []
    window.settings_changed.connect(emitted.append)

    new_settings = ModelSettings(
        provider_type="ollama",
        endpoint="http://127.0.0.1:11434",
        model="qwen2.5-coder:1.5b",
    )
    window.set_settings(new_settings)
    assert window.get_settings() == new_settings


@pytest.mark.ui
def test_app_integration_apply_settings(qapp: QApplication) -> None:
    """Prueft das Umschalten von Provider und Modell in der JarvesApplication."""
    window = MainWindow()
    app_instance = JarvesApplication(main_window=window)

    # Initial: Fake-Modus
    assert isinstance(app_instance.provider, FakeProvider)
    assert app_instance.settings.provider_type == "fake"

    # Umschalten auf Ollama
    ollama_settings = ModelSettings(
        provider_type="ollama",
        endpoint="http://127.0.0.1:11434",
        model="qwen2.5-coder:1.5b",
    )
    app_instance.apply_settings(ollama_settings)

    assert isinstance(app_instance.provider, OllamaProvider)
    assert app_instance.settings.model == "qwen2.5-coder:1.5b"
    assert app_instance.chat_panel.lbl_model_info.text() == "Modell: qwen2.5-coder:1.5b"

    # Zurueck auf Demo-Modus
    fake_settings = ModelSettings(
        provider_type="fake",
        model="fake-model",
    )
    app_instance.apply_settings(fake_settings)

    assert isinstance(app_instance.provider, FakeProvider)
    assert app_instance.settings.model == "fake-model"
    assert app_instance.chat_panel.lbl_model_info.text() == "Modell: fake-model"
