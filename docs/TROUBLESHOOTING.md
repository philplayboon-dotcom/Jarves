# Fehlersuche

## OpenCode erkennt Profile nicht

Projektroot und .opencode/agents/ prüfen; installierte Version notieren; dokumentierte Frontmatter-Syntax mit tatsächlicher Version abgleichen. Modell im OpenCode-UI konfigurieren. Keine Profile in AGENTS.md hineinkopieren und keine Permissions blind entfernen.

## Python-/Testbefehle schlagen beim ersten Öffnen fehl

Das Paket ist Dokumentation. Zuerst T01 implementieren; erst danach existiert pyproject.toml. Python 3.12 x64 und passende Installation prüfen. Vollständige venv-Pythonpfade verwenden, statt PowerShell-ExecutionPolicy global zu ändern.

## Ollama nicht erreichbar

Dienst/App starten; Endpoint 127.0.0.1:11434 und Portkonflikt prüfen; UI darf Demo/Fake anbieten. Keinen Remote-Endpunkt als Ersatz verwenden.

## Modell fehlt

ollama list durch Nutzer ausführen; Tag abgleichen. Download nur explizit über Nutzerentscheidung, nicht auf Fehlerfallback.

## Antworten langsam oder System träge

Kontext/Antwortlänge reduzieren, einen Inferenzprozess verwenden, unnötige Anwendungen schließen, warm/kalt unterscheiden. Daten messen; keine GPU-Beschleunigung versprechen. Abbruchfunktion muss UI sofort freigeben, weitere Anfrage erst nach Workerende.

## OCR liest Code falsch

Originaldatei/Terminaltext bevorzugen, Region vergrößern und Vorschau korrigieren. OCR-Text bleibt als OCR markiert. Fehlender Backendcheck darf keine erfundenen Ergebnisse produzieren.

## Projektdatei blockiert

Root, Ausschlüsse, Zeilenbereich, Encoding und resolved Pfad prüfen. Sicherheitsregel nicht still umgehen. Es ist kein Bug, wenn .env oder Junction nach außen gesperrt wird.

## Sicherheitshinweis

Diagnosedaten vor Teilen prüfen; keine echten Keys oder vollständigen privaten Logs in Issues/Agentenprompts senden.
