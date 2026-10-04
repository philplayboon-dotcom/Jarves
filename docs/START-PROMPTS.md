# OpenCode-Startprompts

## 1. Bestand prüfen und Bootstrap planen

```text
@coordinator
Lies AGENTS.md, STATUS.md, QUICKSTART.md und Roadmap.md für M0.
Dieses Repository enthält anfangs nur Dokumentation. Prüfe den tatsächlichen Bestand.
Plane ausschließlich T01; implementiere noch nichts und führe keine Installationen aus.
Nenne Dateien, Abhängigkeiten, geplante Windowsbefehle und Akzeptanzprüfungen.
Prüfe, ob die .opencode-Agentprofile zur installierten OpenCode-Version passen.
OpenCode-Modell und Jarves-Runtimemodell sind getrennt. Keine Cloud konfigurieren.
Frage nach Freigabe, wenn du schreiben/installieren/Befehle ausführen möchtest.
```

## 2. Bootstrap nach Nutzerfreigabe

```text
@coordinator
Bearbeite nur T01 gemäß bestätigtem Plan. Halte AGENTS.md ein.
Erstelle minimalen installierbaren Python-3.12-src-Bootstrap mit PySide6/httpx und Testtools.
Noch keine OCR, Cloud, automatische Modelldownloads oder Überwachung.
Wenn Ausführung nicht freigegeben ist, liefere Änderungen und genaue offene Prüfungen.
Schließe mit HANDOFF-TEMPLATE.md ab; keine Testergebnisse erfinden.
```

## 3. Verträge einfrieren

```text
@coordinator
Bearbeite nur T02. Lies INTERFACES.md und ARCHITECTURE.md.
Implementiere Domainmodelle, Ports, Fehler und CancellationToken ohne Qt/HTTP-Abhängigkeiten.
Präzisiere Settings/SelectionSpec/Metrics minimal; melde nötige Vertragsänderungen.
Teste die Domain nach geltender Freigabe. Danach Contract Freeze dokumentieren.
Noch keine Consumer, keine Provider-/UI-Gesamtimplementierung.
```

## 4. UI-Lane starten

```text
@ui
Bearbeite T04, sofern T02 abgenommen ist. Lies UX.md und INTERFACES.md.
Arbeite nur in deinen UI-/UI-Testdateien. Verwende Ports/Fakes, keine echten Modellanfragen.
Kein app.py-/Domain-/pyproject-Edit; Integrationsbedarf an Coordinator melden.
Plain-Text-Antworten, deutsche Labels, nicht blockierende UI. Handoff liefern.
```

## 5. Provider-Lane starten

```text
@provider
Bearbeite ausschließlich T08 nach T02. Lies INTERFACES.md, SECURITY.md und TESTING.md.
Implementiere lokalen Ollama-Adapter mit NDJSON-Streaming und HTTP-Mocktests.
Keine automatische Installation, kein Cloudfallback, kein tools/images.
Eine echte Ollama-Anfrage ist ein separater freizugebender Smoke-Test.
T09 nicht ungefragt vorwegnehmen, aber nötige Endpoint-/Fehlerbasis einhalten.
```

## 6. Kontext-Lane starten

```text
@core
Bearbeite nur T12 nach T02. Lies SECURITY.md und den ProjectReader-Vertrag.
Projektroot/Ausschlüsse/Pfadgrenzen/Größe/Encoding/Zeilenbereiche zuerst testen.
Keine automatische Repositoryindexierung und keine fremden Projektänderungen.
Junction-/Symlinktests unter Windows nur mit passenden Voraussetzungen, Skipgründe dokumentieren.
```

## 7. Reviewer

```text
@reviewer
Prüfe den Diff des gerade abgeschlossenen Tasks und seine Kriterien in Roadmap.md.
Lies nur relevante Verträge und Sicherheitsregeln. Ändere keine Datei.
Priorisiere Bugs, Datenabfluss, Thread-/Cancelprobleme und fehlende Negativtests.
Unterscheide bestätigte Befunde von Vermutungen. Keine Tests ohne Freigabe ausführen.
Gib Go/No-Go für Integration mit begründeten offenen Punkten.
```

## 8. Wiederaufnahme einer Sitzung

```text
@coordinator
Lies AGENTS.md und STATUS.md, dann den nächsten offenen Task aus Roadmap.md.
Prüfe vorhandene Änderungen und letzte Handoffs. Beschreibe tatsächlichen Zustand.
Schlage genau einen nächsten Task vor. Keine gesamte Roadmap auf einmal implementieren.
```

## Lokales kleines Entwicklungsmodell

Falls @-Subagenten oder Toolaufrufe unzuverlässig sind: dieselben Aufgaben einzeln im normalen Chat verwenden, die Rolle ausdrücklich nennen und Code manuell prüfen. Keine automatische Cloudmigration oder pauschale Rechteausweitung.
