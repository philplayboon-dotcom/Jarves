# Anforderungen

## MVP: M0 bis M5

| ID | Anforderung | Abnahme |
|---|---|---|
| FR-01 | Lokaler deutscher Chat | Anfrage und gestreamte Antwort sichtbar; keine Cloud-Anfrage |
| FR-02 | Fehlertext manuell übernehmen | Nutzer fügt Text ausdrücklich in eigenes Kontextfeld ein |
| FR-03 | Eine Datei auswählen | Datei liegt in freigegebenem Root, Vorschau und Zeilenbereich sichtbar |
| FR-04 | Kontext prüfen | Quellen aktivieren, entfernen und Kontext vor Versand ansehen |
| FR-05 | Sitzung steuern | Inaktiv/aktiv/pausiert; Aufnahme nur aktiv; Chat bei Pause weiterhin möglich |
| FR-06 | Anfrage abbrechen | Teilantwort markiert, UI bedienbar, alte Chunks ignoriert |
| FR-07 | Modellverfügbarkeit prüfen | Server fehlt/Modell fehlt klar unterscheidbar; kein stiller Download |
| FR-08 | Nur lesen | Keine Dateiänderung und keine Befehlsausführung im analysierten Projekt |
| FR-09 | Quellen anzeigen | Quellen-IDs vom Kontextpaket in der UI; unbekannte Modellreferenzen markieren |
| FR-10 | Kontext verwerfen | Neue Sitzung leert temporären Kontext und verwirft alte Events |

## Nach MVP

FR-11: Screenshot explizit auslösen, Vorschau anzeigen, nur lokal OCR verarbeiten.
FR-12: OCR-Text editierbar; nie als Originaldatei ausgeben.
FR-13: VS-Code-Brücke mit authentifizierter, lokaler Verbindung und manueller Exportgeste.
FR-14: OpenCode-Desktop-/Antigravity-Integrationen nur nach Capability-Spike.
FR-15: Proaktive Hinweise nur opt-in und erst nach separater Spezifikation.

## Nichtfunktionale Anforderungen

- NFR-01: Keine Inhaltsdaten im normalen Logging, keine Hintergrund-Cloudkommunikation.
- NFR-02: UI reagiert während Providerarbeit; Entwurfsziel für Abbruchbestätigung <= 1 s.
- NFR-03: Eine Anfrage, ein Modell, kleiner Kontext; keine permanente Bildschirmaufnahme.
- NFR-04: Unit-/Mocktests funktionieren ohne Ollama, Kamera, Bildschirm oder Internet.
- NFR-05: Ausschlussregeln und Pfadgrenzen werden vor Lesezugriff überprüft.
- NFR-06: Providerfehler erhalten technische Codes und verständliche deutsche Meldungen.
- NFR-07: Screenshots standardmäßig nicht persistieren; Chats nur RAM im MVP.
- NFR-08: Installation und Modellbeschaffung dürfen Internet brauchen; Runtime bleibt lokal.

## Nichtziele

Autonomes Coding, allgemeine PC-Steuerung, Hintergrundkeylogging, Voice, vollständiger Chatimport fremder Anwendungen, robuste Diagrammanalyse, Remote-Server, Repository-weites semantisches Gedächtnis, unbeaufsichtigte Shell.

## Offene Entscheidungen

OCR-Backend nach Spike; Code-Signing/Installer nach MVP; spätere Lizenzwahl durch Nutzer; Modellqualität und Latenz erst nach Hardwaretest. Diese Punkte blockieren M0–M5 nicht.
