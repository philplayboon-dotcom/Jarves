# Start mit OpenCode Desktop

## Paket einsetzen

1. ZIP in einen neuen Projektordner entpacken. README.md und AGENTS.md müssen direkt im Projektroot liegen.
2. Den gesamten Root einschließlich verstecktem .opencode-Ordner in OpenCode Desktop öffnen.
3. Vorhandene AGENTS.md behalten. /init ist nicht nötig; eine spätere Änderung zuerst prüfen.
4. OpenCode-Version und tatsächlich verfügbare Modelle notieren. Die Agentenprofile verwenden absichtlich keine model-ID und erben das in OpenCode gewählte Modell.
5. Zuerst den Plan-/Coordinator-Prompt aus START-PROMPTS.md senden.

## Zwei getrennte Modellkonfigurationen

Jarves-Runtime: der spätere Ollama-Adapter verwendet ein kleines lokales Modell für Projektfragen.
OpenCode-Entwicklung: OpenCode benötigt einen eigenen konfigurierten Provider/ein Modell zum Implementieren. Diese Markdown-Dateien stellen keinen Provider bereit und richten keinen API-Zugang ein. Falls auch OpenCode lokal arbeiten soll, Verbindung passend zur installierten Version konfigurieren und erst an einem Mini-Task prüfen.

Ein kleines Jarves-Chatmodell ist nicht automatisch ein zuverlässiges Tool-Calling-/Multi-Agent-Modell für OpenCode. Bei schwacher Qualität Aufgaben verkleinern, einzeln bearbeiten, Code manuell prüfen. Kein Cloud-Fallback ohne Nutzerentscheidung.

## Ollama separat vorbereiten

Installation über offizielle Windows-Dokumentation; Modellbefehle durch Nutzer, nicht still vom Agenten. Folgende Befehle benötigen keine Jarves-Implementierung, aber ein installiertes Ollama:

```powershell
ollama --version
ollama list
ollama pull qwen2.5-coder:1.5b
ollama run qwen2.5-coder:1.5b
```

pull benötigt zunächst Internet und Speicherplatz. Vorher lesen: MODEL-EVALUATION.md. Keine Echtzeit- oder RAM-Garantie. OpenCode nicht gleichzeitig mit mehreren lokalen Modellinstanzen belasten.

## Erster Implementierungsauftrag

T01 und T02 nacheinander, danach Contract Freeze. Zunächst Fake-Provider verwenden. Erst dann UI und Ollama-Adapter parallel oder sequenziell umsetzen. Keine Screenshot-/OCR-Installation beim Bootstrap.

## Wichtig

Dieses Paket enthält noch keine pyproject.toml und keinen Anwendungscode. Installations-/Testbefehle aus DEVELOPMENT.md sind Soll-Befehle ab T01. Agentenprofile sind gemäß dokumentierter OpenCode-Markdown-Syntax erstellt, aber nicht in deiner installierten Desktop-Version getestet. Bei Syntaxabweichung stoppen und Profile angepasst prüfen, nicht Berechtigungen entfernen.
