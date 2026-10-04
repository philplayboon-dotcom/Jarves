# Entscheidungen und offene Punkte

## D001 — Python statt kompletter C++-Implementierung

Status: geplant/angenommen für MVP. Python 3.12 + PySide6; C++ später nur bei nachgewiesenem Bedarf. Folge: leichter Prototyp, trotzdem Tests für Ressourcen notwendig.

## D002 — Lokal zuerst

Status: Nutzerentscheidung. Keine Keys, kein Cloudadapter im MVP. Ollama auf Loopback, kleines Textmodell. Konsequenz: begrenzte Qualität und Rechenleistung müssen gemessen werden.

## D003 — Strukturierter Text vor Bildern

Status: Entwurf. Dateien/Fehlerausgaben zuerst; Screenshot später über OCR. Kein Bildverständnis mit Textmodell behaupten.

## D004 — Keine Aktionen im MVP

Status: Entwurf passend zum gewünschten On-Demand-Start. Kein Shell-/Schreibtool in Jarves. Entwicklungsagenten sind separat berechtigt.

## D005 — RAM-only Kontext

Status: Entwurf. Keine Chatdatenbank im MVP; Einstellungen später JSON. Erinnerung/SQLite erst bei tatsächlichem Bedarf.

## D006 — Ports/Contracts vor Parallelität

Status: Entwurf. T02 Freeze; Coordinator alleiniger Owner zentraler Dateien. Ein aktiver Schreibagent als Default auf 8 GB.

## D007 — Fake vor echtem Modell

Status: Entwurf. UI muss offline ohne Ollama testbar sein. Providerintegration erst nach UI-/Domainbasis.

## D008 — Entwicklungsmodell separat

Status: offen in Toolkonfiguration. Jarves-Modellkandidat richtet OpenCode nicht ein. Lokales OpenCode-Modell muss Tool-/Taskqualität separat demonstrieren.

## Noch offen

OCR-Backend und Packaginganforderungen; installierte OpenCode-Version; tatsächlich freier RAM; License/Distribution; genaue Antigravity-/OpenCode-Capabilities; Nutzen proaktiver Hinweise. Kein Punkt blockiert T01/T02.

## Änderungen

Datum, Entscheidung, Grund, Auswirkungen, Nutzerfreigabe falls Datenschutz/Scope betroffen. Nicht aus Bequemlichkeit lokale Netzwerkrichtlinien oder Nur-Lesen aufweichen.
