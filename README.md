# Jarves-AI — Entwicklungsstart

Stand: 04.10.2026. Status: Dokumentations- und Planungspaket; noch kein implementierter Anwendungscode.

Jarves ist ein lokaler, auf Wunsch aktivierter Entwicklungsassistent für Windows 11. Er beantwortet Fragen zu ausdrücklich bereitgestellten Python-/C++-Dateien und Fehlerausgaben. Später ergänzt er Bildschirmtexte mittels OCR und strukturierte IDE-Daten. Er verändert im MVP keine Projektdateien und führt keine Modellbefehle aus.

## Ausgangslage

- Windows 11; Intel Core i5-1135G7; 8 GB RAM. Eine dedizierte GPU ist nicht bestätigt.
- Werkzeuge: VS Code, OpenCode Desktop, Perplexity und Antigravity als App/IDE.
- Anwendungskern: Python; Oberfläche: PySide6; Inferenz: lokales Ollama.
- Modellkandidat: qwen2.5-coder:1.5b. Ein Kandidat, keine garantierte Qualitäts- oder Leistungsaussage.
- Keine API-Keys vorhanden. Cloud ist eine spätere Option, nicht Teil des MVP.

## Lesen und starten

1. QUICKSTART.md: Paket verwenden und Voraussetzungen prüfen.
2. AGENTS.md: verbindliche Regeln für Entwicklungsagenten.
3. Roadmap.md: Meilensteine, Abhängigkeiten und Abnahme.
4. Parallel-Tasks.md: Arbeitspakete und Datei-Ownership.
5. START-PROMPTS.md: konkrete Prompts für OpenCode.
6. INTERFACES.md und SECURITY.md: Verträge vor Implementierung lesen.

Weitere Dateien werden nur passend zur Aufgabe geladen; nicht sämtliche Dokumentation in den kleinen Modellkontext kopieren.

## Was geliefert wird

- Konkrete Spezifikation, Schnittstellen, Backlog und Testszenarien.
- OpenCode-Agentenprofile unter .opencode/agents/.
- Keine fertige Anwendung, kein installiertes Modell, keine vorab bestandenen Tests.
- Kein opencode.json: bewusst keine ungeprüfte Providerkonfiguration oder pauschale Toolfreigabe.

## Erste nutzbare Version

Chatfenster + Fake-Provider + Ollama-Streaming + manuell eingefügter Fehlertext + ausgewählte Datei + Kontextvorschau + Abbruch. OCR und IDE-Integration folgen erst nach einer erfolgreichen Qualitäts-/Ressourcenprüfung.

## Quellen

Siehe SOURCES.md für die verwendeten öffentlichen Schnittstellendokumentationen. Entwurfswerte und Produktentscheidungen sind keine Herstellerzusagen.
