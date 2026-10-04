# Architektur

## Entscheidung

Eine lokale Desktop-App, ein Prozess, ein Qt-Hauptthread und höchstens ein Provider-Worker. Ports-and-Adapters mit schlanker Domain, kein Agentenframework. Ollama läuft als separater lokaler Dienst. Das Modell ist nicht Teil des UI-Prozesses.

```text
Qt UI -> ApplicationController -> ContextBuilder -> PrivacyPolicy
                               -> ModelProvider port -> Ollama HTTP worker
                               -> ProjectReader port
                               -> Screenshot/OCR ports (später)
```

## Geplante Struktur

```text
pyproject.toml
src/jarves/
  __init__.py
  __main__.py
  app.py
  domain/
    models.py
    ports.py
    errors.py
    cancellation.py
  application/
    controller.py
    context_builder.py
    session.py
  infrastructure/
    providers/fake.py
    providers/ollama.py
    filesystem/project_reader.py
    capture/mss_capture.py
    ocr/
    config/settings.py
    logging_setup.py
  ui/
    main_window.py
    chat_panel.py
    context_panel.py
    settings_dialog.py
    workers.py
    event_bridge.py
  prompts/system.de.txt
extensions/vscode/                 # erst M7
scripts/benchmark.py               # M5
scripts/check_links.py             # M0
scripts/check_invariants.py        # M4
tests/
```

## Abhängigkeiten

- domain: nur Standardbibliothek; frozen dataclasses für Werte, Protocols für Ports.
- application: domain; keine Imports aus ui oder konkreten Adaptern.
- infrastructure: domain plus konkrete Bibliotheken.
- ui: application/domain; Adapter werden nur im Composition Root verdrahtet.
- app.py: alleiniger Composition Root; keine Fachlogik.

## Threading

Worker verwendet synchrones HTTP-Streaming im Hintergrundthread. Er sendet Qt-Signale mit Domain-Events; keine Widgetzugriffe. CancellationToken ist thread-safe. UI bestätigt Abbruch sofort, sperrt Folgeanfrage aber bis Workerende. Nach Sitzungsschluss verwirft event_bridge Events mit alter session_id/request_id.

Keine QThread.terminate()-Abbruchstrategie. Connect-Timeout 3 s, Read-Timeout zunächst 5 s, Gesamtlaufzeit maximal 120 s als konfigurierbare Entwurfswerte. Bei CPU-Inferenz prüfen, ob der Read-Timeout zu knapp ist. I/O-Ende ist nicht identisch mit sofortigem Ende der Serverinferenz.

## Sitzungslogik

SessionState: INACTIVE, ACTIVE, PAUSED. RequestState: IDLE, RUNNING, CANCELLING. Aufnahme ist nur ACTIVE zulässig. Chat benötigt eine existierende Sitzung, aber keine laufende Aufnahme. Pausieren blockiert neue Erfassung, leert nicht automatisch Kontext. Sitzung beenden cancelt Anfrage, entfernt Kontext und deaktiviert Aufnahme. Neue Sitzung erhält neue UUID.

## Persistenz

MVP: keine Chat-/Kontextdatenbank. Optional ab M4 nur geprüfte Einstellungen als lokale JSON-Datei unter LocalAppData/Jarves-AI; atomisch schreiben, keine Secrets. SQLite und langfristige Erinnerungen bleiben Backlog. Screenshots nur kurzlebig im RAM.

## Fehlergrenzen

Provider, ProjectReader und OCR übersetzen technische Ausnahmen in Domain-Fehler. UI zeigt Codes und Hilfetext. Modelloutput niemals als HTML mit Remote-Ressourcen rendern; zunächst Plain Text, keine automatisch geöffneten Links.

## Grenze

Jarves hat keine Aktionswerkzeuge im MVP. Dies wird durch fehlende Tool-Registrierung und fehlende Ausführungspfade abgesichert, nicht nur durch einen Prompt.
