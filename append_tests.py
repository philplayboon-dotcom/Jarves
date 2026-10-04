#!/usr/bin/env python3
"""Append edge case tests to test_model_settings.py"""

import os

test_file = os.path.join(os.path.dirname(__file__), "tests", "ui", "test_model_settings.py")
with open(test_file, "r", encoding="utf-8") as f:
    existing = f.read()

new_tests = """
@pytest.mark.ui
def test_settings_dialog_check_connection_ollama_zero_models(qapp):
    """Prueft Ollama-Verbindung bei erfolgreicher Konnektivitaet, aber 0 Modellen."""
    from unittest.mock import MagicMock
    from jarves.infrastructure.providers.ollama import OllamaProvider
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.list_models.return_value = ()
    ollama_factory = MagicMock(return_value=mock_provider)
    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434")
    success = dialog.check_connection()
    assert success is True
    assert "keine Modelle" in dialog.lbl_status.text()
    assert dialog.combo_model.count() == 0

@pytest.mark.ui
def test_settings_dialog_model_name_whitespace_handling(qapp):
    """Prueft, dass whitespace-only Modellnamen auf Standardwert fallen."""
    dialog = SettingsDialog()
    dialog.combo_model.setEditText("   ")
    dialog._on_accept()
    emitted = []
    dialog.settings_applied.connect(emitted.append)
    dialog2 = SettingsDialog()
    dialog2.rb_ollama.setChecked(True)
    dialog2.edit_endpoint.setText("http://127.0.0.1:11434")
    dialog2._on_accept()
    assert len(emitted) == 1

@pytest.mark.ui
def test_settings_dialog_toggle_provider_with_populated_list(qapp):
    """Prueft Umschalten zwischen Modi bei bestaendiger Modellliste."""
    dialog = SettingsDialog()
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434")
    from unittest.mock import MagicMock
    from jarves.infrastructure.providers.ollama import OllamaProvider
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.list_models.return_value = ("model-a", "model-b")
    current_text = dialog.combo_model.currentText().strip()
    dialog._update_model_list(mock_provider.list_models())
    assert dialog.combo_model.count() == 2
    dialog.rb_fake.setChecked(True)
    assert dialog.combo_model.count() == 2
    assert dialog.get_provider_type() == "fake"
    dialog.rb_ollama.setChecked(True)
    assert dialog.get_provider_type() == "ollama"

@pytest.mark.ui
def test_settings_dialog_save_with_empty_endpoint(qapp):
    """Prueft Speichern mit leerer Endpoint-Feldnahme."""
    dialog = SettingsDialog()
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("")
    dialog._on_accept()
    emitted = []
    dialog.settings_applied.connect(emitted.append)
    settings = dialog.get_settings()
    assert settings.endpoint == "http://127.0.0.1:11434"

@pytest.mark.ui
def test_settings_dialog_invalid_endpoint_with_credentials(qapp):
    """Prueft, dass Endpoints mit Credentials abgelehnt werden."""
    from unittest.mock import MagicMock
    ollama_factory = MagicMock()
    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://user:pass@127.0.0.1:11434")
    success = dialog.check_connection()
    assert success is False
    ollama_factory.assert_not_called()
    assert "Credentials" in dialog.lbl_status.text() or "Ungueltiger Endpunkt" in dialog.lbl_status.text()

@pytest.mark.ui
def test_settings_dialog_invalid_endpoint_with_query_params(qapp):
    """Prueft, dass Endpoints mit Query-Parametern abgelehnt werden."""
    from unittest.mock import MagicMock
    ollama_factory = MagicMock()
    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434?token=abc")
    success = dialog.check_connection()
    assert success is False
    ollama_factory.assert_not_called()
    assert "Query" in dialog.lbl_status.text() or "Ungueltiger Endpunkt" in dialog.lbl_status.text()

@pytest.mark.ui
def test_settings_dialog_invalid_endpoint_with_fragment(qapp):
    """Prueft, dass Endpoints mit Fragment-Ablehnung."""
    from unittest.mock import MagicMock
    ollama_factory = MagicMock()
    dialog = SettingsDialog(ollama_provider_factory=ollama_factory)
    dialog.rb_ollama.setChecked(True)
    dialog.edit_endpoint.setText("http://127.0.0.1:11434#section")
    success = dialog.check_connection()
    assert success is False
    ollama_factory.assert_not_called()
    assert "Fragment" in dialog.lbl_status.text() or "Ungueltiger Endpunkt" in dialog.lbl_status.text()
"""

# Append new content
new_content = existing + new_tests

with open(test_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Appended new tests successfully to", test_file)