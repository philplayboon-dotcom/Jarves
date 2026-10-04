# Projektstatus

Stand: 04.10.2026. Phase: M2 abgeschlossen (Gate G2 erreicht).

## Tatsächlich vorhanden

- Grundgerüst mit `pyproject.toml`, `src/jarves/`, `tests/` und `scripts/check_links.py`.
- Domaenen-Vertraege (`models.py`, `ports.py`, `errors.py`, `cancellation.py`) in `src/jarves/domain/`.
- Deterministischer `FakeProvider` mit Streaming-, Abbruch- und Fehlerszenarien in `src/jarves/infrastructure/providers/fake.py`.
- Echter `OllamaProvider` mit NDJSON-Streaming, Loopback-Policy, Timeouts, Cancellation und Error-Mapping in `src/jarves/infrastructure/providers/ollama.py`.
- Session- und Request-Lifecycle (`SessionManager`) in `src/jarves/application/session.py`.
- PySide6-Chatlayout (`ChatPanel`, `MainWindow`) und Einstellungsdialog (`SettingsDialog`) mit Provider-/Modell-Umschaltung in `src/jarves/ui/`.
- Hintergrundworker (`InferenceWorker`) und Signal-Event-Bridge (`EventBridge`) in `src/jarves/ui/`.
- Composition Root in `src/jarves/app.py` und Einstiegspunkt `src/jarves/__main__.py`.
- 102 automatisierte Tests grün (Default-Suite: Offline-Unit-, Adapter- und UI-Tests).
- 1 Live-Integrationstest gegen lokalen Ollama-Dienst (`qwen2.5-coder:3b`) erfolgreich ausgeführt.
- Linkprüfung erfolgreich ausgeführt.

## Nächste Schritte

1. Wave 3 starten (Phase M3: Projekt- und Fehlerkontext).
2. T12 (ProjectReader mit Pfadsicherheit, Traversal-Schutz, Ausschlussregeln).
3. T13 (ContextBuilder mit Budgetierung, Prompt-Assembly, Priorisierung).
4. T14 (Kontextpanel, Dateiauswahl, Fehlertextfeld, Vorschau in UI).
5. T15 (Security- & Privacy-Tests für Pfade und Kontext).
6. T16 (M3-Integration & Gate G3 Abnahme).

## Gates

| Gate | Status | Nachweis |
|---|---|---|
| G0 Bootstrap/Contract Freeze | bestanden | T01 + T02 abgeschlossen; 10 Tests grün; keine Fremdabhängigkeiten in Domain |
| G1 Fake UI | bestanden | T03–T07 abgeschlossen; 47 Tests grün; Chat, Streaming, Cancel & Fehler ohne Ollama demonstriert |
| G2 Ollama | bestanden | T08–T11 abgeschlossen; 102 Adapter-/UI-Tests grün + Live-Ollama-Test mit qwen2.5-coder:3b bestanden |
| G3 Kontext/Privacy | offen | keiner |
| G4 MVP | offen | keiner |
| G5 Hardware/Qualität | offen | keiner |
| G6 OCR | optional/offen | keiner |
| G7 Integrationen | optional/offen | keiner |

## Aufgabenstatus

- T01: DONE (Bootstrap Grundgerüst, pytest, ruff, link-check validiert).
- T02: DONE (Contracts, Models, Protocols, Errors, CancellationToken implementiert & getestet).
- T03: DONE (FakeProvider mit deterministischem Streaming, Fehlern und Cancel).
- T04: DONE (ChatPanel, MainWindow, Signale & Zustandssteuerung).
- T05: DONE (SessionManager, Zustandsübergänge, UUID-Lifecycle).
- T06: DONE (InferenceWorker, EventBridge, Stale-Event-Filter).
- T07: DONE (Composition Root app.py, Gate G1 verifiziert).
- T08: DONE (Ollama list_models & Chat-NDJSON mit httpx).
- T09: DONE (Ollama Endpointpolicy, Timeouts, Cancellation, Error-Mapping).
- T10: DONE (SettingsDialog, Modellwahl, Verfügbarkeitsprüfung in UI).
- T11: DONE (Ollama-Integration & Windows Live-Smoke-Test bestanden).
- T12–T32: TODO.

## Risiken

8 GB RAM; noch unkonfiguriertes Entwicklungsmodell; unbekannte Geschwindigkeit; OCR-Backend ungeprüft; Desktop-API-Kompatibilität ungeprüft.
