# Roadmap — Jarves-AI

Stand: 04.10.2026. Alle Aufgaben TODO. Keine Kalendertermine oder bereits erreichten Ergebnisse. Meilensteine beschreiben Abnahmen, nicht nur Features.

## Strategie

Erst Fake und Verträge, dann lokales Modell, dann gezielter Kontext. G4 ist der erste brauchbare MVP. G5 entscheidet, ob der Laptop Modellqualität und Reaktionszeit trägt. OCR/Integrationen sind optionale Erweiterungen, keine Bootstrap-Voraussetzung.

## Meilensteine

| Phase | Ergebnis | Tasks | Gate | Abnahme |
|---|---|---|---|---|
| M0 | Bootstrap und Verträge | T01–T02 | G0 | Installierbares Grundgerüst; Contract Freeze; installierte OpenCode-Version/Profile geprüft. |
| M1 | Chat mit Fake-Provider | T03–T07 | G1 | Chat, Streaming, Cancel und Sitzungszustände ohne Ollama demonstriert. |
| M2 | Lokale Ollama-Inferenz | T08–T11 | G2 | Lokaler Endpunkt, Modellwahl, echte Anfrage und Fehlerfälle; keine Cloud. |
| M3 | Projekt- und Fehlerkontext | T12–T16 | G3 | Datei/Fehlertext/Vorschau/Quellen mit Policytests und E2E. |
| M4 | Sicherer MVP | T17–T21 | G4 | Cleanup, Logs, Shutdown, keine Aktionen; Nutzerabnahme. |
| M5 | Hardware und Qualität | T22–T24 | G5 | Echte Messdaten auf 8-GB-Laptop, Go/Scopeentscheidung. |
| M6 | Bildschirmtext per OCR | T25–T28 | G6 | Optional, nur nach G5; Backend getestet; explizite Aufnahme und editierbarer Text. |
| M7 | Strukturierte Integrationen | T29–T31 | G7 | Optional, nach G5; VS Code zuerst; Desktopapps nach Capability-Spike. |
| M8 | Proaktiven Modus planen | T32 | — | Nur Spezifikation, keine autonome Ausführung. |

## Kritischer Pfad

T01 -> T02 -> T03/T04/T05 -> T06 -> T07 -> T11 -> T16 -> T20 -> T21 -> T22 -> T23 -> T24.

T08/T09 und T12/T13 können nach T02 neben der UI vorbereitet werden. T11 benötigt T09/T10; T16 benötigt T14/T15; T20 benötigt T17/T18/T19. Abhängigkeiten pro Task sind maßgeblich, nicht allein die Kurzskizze.

## Größen und Planung

S: kleiner isolierter Task; M: mehrere Dateien/Negativfälle; L: Integration über Sprach-/Prozessgrenze. Keine belastbare Tagesabschätzung ohne Modell-/Tooltest. Größere Tasks in unabhängige Subtasks zerlegen, ohne Akzeptanz zu verlieren.

## Aufgaben mit Akzeptanz

### T01 — Installierbares src-Grundgerüst mit pytest/ruff/mypy und Windows-Einstieg anlegen

Phase M0; Owner coordinator; Größe S; Status TODO; Voraussetzungen: —.

Ziel: Installierbares src-Grundgerüst mit pytest/ruff/mypy und Windows-Einstieg anlegen. Keine OCR-/Cloudabhängigkeit.

Dateien: `pyproject.toml; src/jarves/__init__.py; src/jarves/__main__.py; tests/conftest.py; scripts/check_links.py`.

Abnahme: python -m jarves startet Platzhalter; Marker/Default-Skips konfiguriert; Dokumentlinks prüfen; tatsächliche Versionen und OpenCode-Profilkompatibilität notieren.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T02 — Contracts aus INTERFACES

Phase M0; Owner coordinator; Größe M; Status TODO; Voraussetzungen: T01.

Ziel: Contracts aus INTERFACES.md in Models/Protocols/Errors/Cancellation übersetzen; Settings/SelectionSpec/Metrics ergänzen.

Dateien: `src/jarves/domain/`.

Abnahme: Typen importierbar; Cancellation thread-safe getestet; keine Qt/HTTP-Imports; Consumer vor Wave 1 informieren.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T03 — Deterministischen FakeProvider mit Delta/Complete/Fehler/Cancel-Szenarien entwickeln

Phase M1; Owner provider; Größe S; Status TODO; Voraussetzungen: T02.

Ziel: Deterministischen FakeProvider mit Delta/Complete/Fehler/Cancel-Szenarien entwickeln.

Dateien: `src/jarves/infrastructure/providers/fake.py; tests/unit/test_fake_provider.py`.

Abnahme: Alle Events tragen IDs; ein terminales Event; keine Netzwerkzugriffe; Tests ohne Modell.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T04 — Chatlayout mit Modellstatus, Texteingabe, Streaminganzeige und Senden/Abbrechen bauen

Phase M1; Owner ui; Größe M; Status TODO; Voraussetzungen: T02.

Ziel: Chatlayout mit Modellstatus, Texteingabe, Streaminganzeige und Senden/Abbrechen bauen.

Dateien: `src/jarves/ui/main_window.py; src/jarves/ui/chat_panel.py; tests/ui/test_chat_panel.py`.

Abnahme: UI unabhängig vom konkreten Provider; Plain-Text-Ausgabe; leere Frage blockiert; Benutzertexte deutsch.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T05 — Session-/Requestzustände und UUID-Lifecycle implementieren

Phase M1; Owner core; Größe S; Status TODO; Voraussetzungen: T02.

Ziel: Session-/Requestzustände und UUID-Lifecycle implementieren.

Dateien: `src/jarves/application/session.py; tests/unit/test_session.py`.

Abnahme: Pause blockiert Aufnahme; Ende leert Sitzung; alte IDs erkennbar; zweite aktive Anfrage blockiert.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T06 — FakeProvider über Hintergrundworker und Qt-Signale verbinden

Phase M1; Owner ui; Größe M; Status TODO; Voraussetzungen: T03,T04,T05.

Ziel: FakeProvider über Hintergrundworker und Qt-Signale verbinden.

Dateien: `src/jarves/ui/workers.py; src/jarves/ui/event_bridge.py; tests/ui/test_workers.py`.

Abnahme: Keine Widgetupdates vom Worker; Cancel sichtbar; Fensterclose ohne Laufzeitcrash; stale events verworfen.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T07 — Fake-Demo im Composition Root verdrahten und Gate G1 prüfen

Phase M1; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T06.

Ziel: Fake-Demo im Composition Root verdrahten und Gate G1 prüfen.

Dateien: `src/jarves/app.py; src/jarves/__main__.py`.

Abnahme: Start ohne Ollama; UI-/Unitchecks nach Freigabe ausgeführt; keine erfundenen Integrationsnachweise.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T08 — Ollama list_models und Chat-NDJSON mit httpx implementieren

Phase M2; Owner provider; Größe M; Status TODO; Voraussetzungen: T02.

Ziel: Ollama list_models und Chat-NDJSON mit httpx implementieren.

Dateien: `src/jarves/infrastructure/providers/ollama.py; tests/adapters/test_ollama_stream.py`.

Abnahme: Chunkgrenzen/UTF-8/Restpuffer korrekt; done/Error-Mapping getestet; Optionen gemäß Contract; kein tools/images.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T09 — Endpointpolicy, Timeouts, Cancellation und Fehlerfälle härten

Phase M2; Owner provider; Größe M; Status TODO; Voraussetzungen: T08.

Ziel: Endpointpolicy, Timeouts, Cancellation und Fehlerfälle härten.

Dateien: `src/jarves/infrastructure/providers/ollama.py; tests/adapters/test_ollama_errors.py`.

Abnahme: Remote/Redirect/Proxy verhindert; Cancel vor/mittendrin; Server-/Modellfehler unterscheidbar; kein Retry nach Delta.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T10 — Modellwahl, Verfügbarkeitsprüfung und lokale Endpointanzeige in UI

Phase M2; Owner ui; Größe S; Status TODO; Voraussetzungen: T04,T08.

Ziel: Modellwahl, Verfügbarkeitsprüfung und lokale Endpointanzeige in UI.

Dateien: `src/jarves/ui/settings_dialog.py; tests/ui/test_model_settings.py`.

Abnahme: Kein Autodownload; Modell fehlt verständlich; Fake-Modus bleibt erreichbar; keine Cloudfelder.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T11 — Echten Provider integrieren; Windows/Ollama-Smoke gemeinsam mit Nutzer durchführen

Phase M2; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T07,T09,T10.

Ziel: Echten Provider integrieren; Windows/Ollama-Smoke gemeinsam mit Nutzer durchführen.

Dateien: `src/jarves/app.py; STATUS.md`.

Abnahme: Eine echte Frage streamt; Abbruch erprobt; Windowscheck separat protokolliert; Gate G2 nur mit Nachweis.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T12 — Projektroot, Exclusions und gezieltes Dateilesen implementieren

Phase M3; Owner core; Größe M; Status TODO; Voraussetzungen: T02.

Ziel: Projektroot, Exclusions und gezieltes Dateilesen implementieren.

Dateien: `src/jarves/infrastructure/filesystem/project_reader.py; tests/adapters/test_project_reader.py`.

Abnahme: Traversal/außenliegende Junction blockiert; .env ausgeschlossen; Größe/Encoding/Binär/Zeilenrange getestet.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T13 — Quellen, Prompt/Historie und sichtbare Budgetregeln zusammenstellen

Phase M3; Owner core; Größe M; Status TODO; Voraussetzungen: T02.

Ziel: Quellen, Prompt/Historie und sichtbare Budgetregeln zusammenstellen.

Dateien: `src/jarves/application/context_builder.py; tests/unit/test_context_builder.py`.

Abnahme: Frage/System behalten; Trunkierung/Warnungen; Unicodebudget; Source-IDs; keine automatische Suche.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T14 — Manuellen Fehlertext, Dateiauswahl, Quellencheckboxen und Vorschau bauen

Phase M3; Owner ui; Größe M; Status TODO; Voraussetzungen: T04,T12,T13.

Ziel: Manuellen Fehlertext, Dateiauswahl, Quellencheckboxen und Vorschau bauen.

Dateien: `src/jarves/ui/context_panel.py; tests/ui/test_context_panel.py`.

Abnahme: Nutzer bestimmt Quellen; entfernte Quelle nicht gesendet; OCR-/Dateityp unterscheidbar; keine Clipboard-Watcher.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T15 — Synthetische Sicherheits-/Kontextfixtures mit Geheimnismarker und Injection anlegen

Phase M3; Owner qa; Größe S; Status TODO; Voraussetzungen: T12,T13.

Ziel: Synthetische Sicherheits-/Kontextfixtures mit Geheimnismarker und Injection anlegen.

Dateien: `tests/fixtures/; tests/security/test_context_policy.py`.

Abnahme: Keine echten Nutzerdaten; Privacyfälle testen; Fixtureinhalt kann keine Aktionen auslösen.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T16 — Frage/Quellen/Provider in ApplicationController verdrahten

Phase M3; Owner coordinator; Größe M; Status TODO; Voraussetzungen: T11,T14,T15.

Ziel: Frage/Quellen/Provider in ApplicationController verdrahten.

Dateien: `src/jarves/application/controller.py; src/jarves/app.py`.

Abnahme: E2E mit Datei+Fehlertext; Vorschau stimmt mit Packet überein; nur ein Request; Gate G3.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T17 — Pause, Ende, Kontextverwerfen und neue Sitzung vervollständigen

Phase M4; Owner core; Größe S; Status TODO; Voraussetzungen: T05,T13.

Ziel: Pause, Ende, Kontextverwerfen und neue Sitzung vervollständigen.

Dateien: `src/jarves/application/session.py; tests/unit/test_session_cleanup.py`.

Abnahme: Kein alter Kontext in neuer Sitzung; Pause stoppt neue Erfassung; Ende cancelt und leert.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T18 — No-cloud/no-tools/logging-Invarianten unabhängig prüfen

Phase M4; Owner qa; Größe M; Status TODO; Voraussetzungen: T09,T16.

Ziel: No-cloud/no-tools/logging-Invarianten unabhängig prüfen.

Dateien: `tests/security/; scripts/check_invariants.py`.

Abnahme: Synthetischer Marker fehlt in Logs; Endpointpolicy; Modelltext wird nie ausgeführt; Befunde dokumentiert.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T19 — Fehlerzustände, Abbruch und Shutdown in echter Controlleranbindung prüfen

Phase M4; Owner ui; Größe S; Status TODO; Voraussetzungen: T06,T16,T17.

Ziel: Fehlerzustände, Abbruch und Shutdown in echter Controlleranbindung prüfen.

Dateien: `src/jarves/ui/main_window.py; src/jarves/ui/event_bridge.py; tests/ui/test_shutdown.py`.

Abnahme: Kein zweiter Worker; Teilantwort markiert; alte Deltas ignoriert; read-timeout begrenzt Shutdown.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T20 — Optionale Settingspersistenz und inhaltsfreies Logging integrieren

Phase M4; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T17,T18,T19.

Ziel: Optionale Settingspersistenz und inhaltsfreies Logging integrieren.

Dateien: `src/jarves/infrastructure/config/settings.py; src/jarves/infrastructure/logging_setup.py`.

Abnahme: Atomische validierte JSON-Settings; keine Chat-/Screenshotpersistenz; Default bleibt lokal.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T21 — MVP-Smoke und komplette Abnahme mit Nutzer; Dokumente an echten Code anpassen

Phase M4; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T20.

Ziel: MVP-Smoke und komplette Abnahme mit Nutzer; Dokumente an echten Code anpassen.

Dateien: `README.md; QUICKSTART.md; STATUS.md`.

Abnahme: G4-Nachweise; tatsächlich vorhandene Befehle stimmen; offene Tests/Risiken klar; keine Releasebehauptung.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T22 — Metrikexport für kalte/warme Läufe und Speicherzustand entwickeln

Phase M5; Owner qa; Größe M; Status TODO; Voraussetzungen: T21.

Ziel: Metrikexport für kalte/warme Läufe und Speicherzustand entwickeln.

Dateien: `scripts/benchmark.py; tests/unit/test_benchmark.py`.

Abnahme: Keine Inhalte im Export; Modell/Ollama-Version; TTFT und Dauer getrennt; Messmethode dokumentiert.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T23 — Sechs kleine Qualitätsaufgaben mit Referenzkriterien erstellen

Phase M5; Owner qa; Größe S; Status TODO; Voraussetzungen: T22.

Ziel: Sechs kleine Qualitätsaufgaben mit Referenzkriterien erstellen.

Dateien: `tests/fixtures/evaluation/`.

Abnahme: Python/C++/Deutsch/Unsicherheit/Injection/Budget abgedeckt; keine notwendigen Fremdcompiler.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T24 — Echte Hardware-/Qualitätsevaluation gemeinsam mit Nutzer bewerten

Phase M5; Owner coordinator; Größe M; Status TODO; Voraussetzungen: T23.

Ziel: Echte Hardware-/Qualitätsevaluation gemeinsam mit Nutzer bewerten.

Dateien: `MODEL-EVALUATION.md; STATUS.md`.

Abnahme: Messdaten mit offenen Apps; Go/Reduce-Scope/Modellwechsel dokumentiert; kein Gate ohne reale Messung.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T25 — OCR-Backend-Spike inklusive Windows-/Python-/Packaginganforderungen

Phase M6; Owner core; Größe S; Status TODO; Voraussetzungen: T24 + Go.

Ziel: OCR-Backend-Spike inklusive Windows-/Python-/Packaginganforderungen.

Dateien: `docs/spikes/ocr-backend.md`.

Abnahme: Ein geeignetes Backend mit echtem Screenshot getestet; Footprint/Lizenz/Fehlerfälle; OCR-Port unverändert.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T26 — Explizite Bereichsaufnahme mit mss implementieren

Phase M6; Owner core; Größe M; Status TODO; Voraussetzungen: T25.

Ziel: Explizite Bereichsaufnahme mit mss implementieren.

Dateien: `src/jarves/infrastructure/capture/; tests/adapters/test_capture.py`.

Abnahme: Keine Loopaufnahme; RAM-only; Rand/DPI/Mehrmonitorfälle prüfen; Vorschau vor OCR.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T27 — Gewähltes OCR-Backend an Port anbinden

Phase M6; Owner core; Größe M; Status TODO; Voraussetzungen: T25,T26.

Ziel: Gewähltes OCR-Backend an Port anbinden.

Dateien: `src/jarves/infrastructure/ocr/; tests/adapters/test_ocr.py`.

Abnahme: OCR_UNAVAILABLE sauber; lokale Verarbeitung; unsicherer Text gekennzeichnet; keine Fake-Konfidenz.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T28 — Bereichsauswahl, Bildvorschau und editierbaren OCR-Text integrieren

Phase M6; Owner ui; Größe M; Status TODO; Voraussetzungen: T14,T27.

Ziel: Bereichsauswahl, Bildvorschau und editierbaren OCR-Text integrieren.

Dateien: `src/jarves/ui/capture_dialog.py; tests/ui/test_capture_dialog.py`.

Abnahme: Sitzung aktiv nötig; keine heimliche Aufnahme; Nutzer übernimmt Text ausdrücklich; G6-Nutzerprüfung.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T29 — Lokale IDE-Brücke spezifizieren: Handshake, Auth, Größe, Herkunft und Consent

Phase M7; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T24 + Go.

Ziel: Lokale IDE-Brücke spezifizieren: Handshake, Auth, Größe, Herkunft und Consent.

Dateien: `docs/spikes/ide-bridge.md; INTERFACES.md`.

Abnahme: Keine beliebige Prozessinjektion; Schema/Token/Loopback; manuelle Exportgeste; Scopefreigabe.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T30 — Kleine TypeScript-VS-Code-Erweiterung mit Datei/Auswahl/Diagnoseexport

Phase M7; Owner ui; Größe L; Status TODO; Voraussetzungen: T29.

Ziel: Kleine TypeScript-VS-Code-Erweiterung mit Datei/Auswahl/Diagnoseexport.

Dateien: `extensions/vscode/; tests/integration/test_vscode_bridge.py`.

Abnahme: Kein unbedingtes Terminal-Abgreifen; Größenlimit/Auth; Herkunft stimmt; Nutzer-Smoke; Pythonkern bleibt.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T31 — OpenCode Desktop und Antigravity-App/IDE auf dokumentierte Capabilities untersuchen

Phase M7; Owner provider; Größe S; Status TODO; Voraussetzungen: T29.

Ziel: OpenCode Desktop und Antigravity-App/IDE auf dokumentierte Capabilities untersuchen.

Dateien: `docs/spikes/desktop-integrations.md`.

Abnahme: Tatsächliche Versionen; erreichbare API nicht voraussetzen; Ergebnis API/Export/OCR begründet; kein Chat-Scraping.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

### T32 — Opt-in-Begleitmodus nur spezifizieren, noch nicht implementieren

Phase M8; Owner coordinator; Größe S; Status TODO; Voraussetzungen: T24 + Nutzerentscheidung.

Ziel: Opt-in-Begleitmodus nur spezifizieren, noch nicht implementieren.

Dateien: `docs/spikes/proactive-mode.md`.

Abnahme: Trigger/Debounce/Quiet-Time/Consent/Kosten/Ressourcen formuliert; keine dauerhafte Bildanalyse.

Verifikation: passende Fälle aus TESTING.md; Handoff mit wirklich ausgeführten Prüfungen.

## Stop- und Änderungsregeln

- Kein nächstes Gate mit kritischem Privacy-/Cancellationbefund.
- Kein OCR-Start ohne reale G5-Entscheidung.
- Schwaches Modell: erst kleinere Aufgaben/Kontext; dann anderer kleiner Kandidat nach Nutzerfreigabe.
- Mehr RAM oder Cloud sind spätere Optionen, keine Voraussetzung erzwingen.
- Cloud, Schreibaktionen und Proaktivität benötigen eigene Spezifikation und Nutzerentscheidung.

## Gatebericht

Gate-ID, Datum, Tasks, Testnachweise, manueller Windowsnachweis, offene Risiken, Go/No-Go und Nutzerbestätigung für G4/G5/G6. Ablage/Status durch Coordinator; keine falschen Häkchen.
