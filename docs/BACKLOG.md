# Backlog nach MVP

MVP-Aufgaben stehen ausschließlich in Roadmap.md/Parallel-Tasks.md. Diese Liste ist nicht automatisch freigegeben.

| ID | Thema | Voraussetzung | Warum später |
|---|---|---|---|
| B01 | Lokales bildfähiges Modell | G5 und neuer Ressourcencheck | Textmodell/OCR zuerst |
| B02 | SQLite-Projektgedächtnis | Explizite Speicherregeln | RAM-only MVP genügt |
| B03 | Semantische Suche/Embeddings | Mehrprojektbedarf und Messung | Zusätzlicher RAM/Komplexität |
| B04 | Cloudadapter | Modell/Budget/Consent-Entscheidung | Noch keine Keys, lokal gewünscht |
| B05 | Patchvorschläge mit Diff | Qualitätsgate | Keine automatische Änderung |
| B06 | Genehmigte Dateiänderungen | Eigene Action-Security-Spezifikation | Nicht MVP |
| B07 | Test-/Build-Ausführung | Sandbox/Consent/Projektvertrauen | Führt fremden Code aus |
| B08 | Proaktive Hinweise | T32 + Nutzerentscheidung | Unterbrechungen/Ressourcen prüfen |
| B09 | Sprache | Neuer Nutzerwunsch | Mikrofon nicht benötigt |
| B10 | Installer/Signierung | Stabile MVP-Version und Lizenzcheck | Entwicklung zuerst |
| B11 | Native C++-Optimierung | Gemessener Engpass | Kein vorzeitiger Rewrite |
| B12 | Mehrere Projekte | Bedarf und Kontexttrennung | Ein Root zuerst |

Priorität wird später entschieden. Keine Backlogfunktion während kleiner MVP-Tasks als Bonus implementieren.
