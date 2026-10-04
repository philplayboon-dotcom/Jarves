# Projektstatus

Stand: 04.10.2026. Phase: M1 abgeschlossen (Gate G1 erreicht).

## Tatsächlich vorhanden

- Grundgerüst mit `pyproject.toml`, `src/jarves/`, `tests/` und `scripts/check_links.py`.
- Domaenen-Vertraege (`models.py`, `ports.py`, `errors.py`, `cancellation.py`) in `src/jarves/domain/`.
- Deterministischer `FakeProvider` mit Streaming-, Abbruch- und Fehlerszenarien in `src/jarves/infrastructure/providers/fake.py`.
- Session- und Request-Lifecycle (`SessionManager`) in `src/jarves/application/session.py`.
- PySide6-Chatlayout (`ChatPanel`, `MainWindow`) in `src/jarves/ui/`.
- Hintergrundworker (`InferenceWorker`) und Signal-Event-Bridge (`EventBridge`) in `src/jarves/ui/`.
- Composition Root in `src/jarves/app.py` und Einstiegspunkt `src/jarves/__main__.py`.
- 47 automatisierte Tests grün (Domain, Session, FakeProvider, UI ChatPanel, Workers, App Integration).
- Linkprüfung erfolgreich ausgeführt.

## Nächste Schritte

1. Wave 2 starten (Phase M2: Lokale Ollama-Inferenz).
2. T08 (Ollama list_models & Chat-NDJSON mit httpx).
3. T09 (Ollama Streaming, Timeouts, Cancel, Error-Mapping).
4. T10 (Modellauswahl & Endpunkt-Status in UI).
5. T11 (Ollama-Verdrahtung & Gate G2 Abnahme).

## Gates

| Gate | Status | Nachweis |
|---|---|---|
| G0 Bootstrap/Contract Freeze | bestanden | T01 + T02 abgeschlossen; 10 Tests grün; keine Fremdabhängigkeiten in Domain |
| G1 Fake UI | bestanden | T03–T07 abgeschlossen; 47 Tests grün; Chat, Streaming, Cancel & Fehler ohne Ollama demonstriert |
| G2 Ollama | offen | keiner |
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
- T08–T32: TODO.

## Risiken

8 GB RAM; noch unkonfiguriertes Entwicklungsmodell; unbekannte Geschwindigkeit; OCR-Backend ungeprüft; Desktop-API-Kompatibilität ungeprüft.
