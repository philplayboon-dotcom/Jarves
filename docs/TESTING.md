# Teststrategie

## Ebenen

Unit: Domain, ContextBuilder, Policies, Pfadprüfungen, CancellationToken.
Adapter: Ollama mit HTTP-Mock/NDJSON-Fakes, ProjectReader mit temporären Verzeichnissen.
UI: pytest-qt, FakeProvider und deterministische Workerereignisse; kein echtes Modell nötig.
Integration: lokale Ollama-Tests ausdrücklich opt-in, Marker `integration` und `ollama`.
Manuell: Windows-GUI, echte CPU-Inferenz, Ressourcenmessung, später Screenshot/DPI/OCR.

Default `pytest -q` führt keine echten Modell-/Netzwerk-/Bildschirmtests aus. T01 konfiguriert Marker und Skip-Regeln. Dokumentierte opt-in-Befehle für Integration erst bei vorhandenen Tests hinzufügen.

## Pflichtfälle und Zuständigkeit

| ID | Szenario | Verantwortlich |
|---|---|---|
| UT-01 | Budget, leere Quellen, lange Frage, Unicode | core |
| UT-02 | Start/Pause/Ende und veraltete Request-ID | core/ui |
| UT-03 | Path traversal, .env, Junction/Symlink, binär | core |
| AT-01 | NDJSON über Chunkgrenzen, leere/done Chunks | provider |
| AT-02 | Modell fehlt, Server fehlt, Timeout, Fehlerkörper | provider |
| AT-03 | Cancel vor Start/mittendrin, kein automatischer Retry | provider |
| UI-01 | Streaming ohne blockierte Oberfläche | ui |
| UI-02 | Abbruch, Fenster schließen, keine alten Deltas | ui |
| SEC-01 | Keine Inhalte in Logs | qa |
| SEC-02 | Remote-Endpoint/Redirect/Proxy blockiert | provider/qa |
| SEC-03 | Modelltext mit Shell/HTML wird nur dargestellt | ui/qa |
| E2E-01 | Frage + Fehlertext + kleine Datei | coordinator |
| OS-01 | Windows mit offenen Entwickleranwendungen | Nutzer/qa |

## Fixtures

Nur synthetische Daten unter tests/fixtures/. Keine echten Projektlogs/Secrets. Kleine Python-Datei mit falschem Typ, kurzer Python-Traceback, C++-Compilerfehler ohne notwendige Compilerinstallation, Unicode-Frage, synthetischer Geheimnismarker und injizierende README.

## Gates

M1: Fake-UI bedienbar; Unit-/UI-Tests bestanden.
M2: Provider-Mockfälle bestanden; echter Windows/Ollama-Smoke separat protokolliert.
M3/M4: Pfad-/Privacytests bestanden; E2E-Demo; kein Verstoß gegen nur-lesen.
M5: Qualitäts-/Ressourcenentscheidung mit echten Messdaten, sonst kein automatischer Übergang zu OCR.

Entwurfsziel Domain/Policy-Zweigabdeckung >=80 %, nicht bereits erreicht. Fokus auf Risikofälle statt Coverage allein. Tests dürfen nicht nur Implementierungsmocks mit sich selbst vergleichen.

## Ergebnisprotokoll

Befehl, Datum, Umgebung, Exitcode, Zahl Tests, Scope, Skipgründe und offene Befunde. Ein grüner Mocktest beweist keine echte OCR-/CPU-Leistung.
