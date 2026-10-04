# Oberfläche und Nutzerfluss

## Layout

Links Projekt/Sitzung und Modellstatus; Mitte Chat; rechts einklappbare Kontextliste. Unter Chat Texteingabe, Senden, Abbrechen. Oben Zustand: Inaktiv/Aktiv/Pausiert, lokale Verarbeitung, Modellname. Kein Overlay, kein Mikrofon, kein Tray-Autostart im MVP.

## Erststart

Modellserver prüfen, Modell auswählen, optionale Projektwurzel wählen. Fehlender Server verhindert nicht Fake-Demo oder Lesen der UI. Keine automatische Installation. Nutzer startet neue Sitzung; Aufnahme ist standardmäßig aus.

## Kontext

Eigenes Feld für Fehlertext, Button Datei wählen und Zeilenbereich. Checkbox pro Quelle, Quelle entfernen, Vorschau. Leere Kontextliste erlaubt normalen Chat. Senden zeigt das finale Kontextpaket; MVP verlangt ausdrückliche Bestätigung für hinzugefügte Quellen. Vorschau ist lokal.

Quellenkarte: Typ, Label, relative Datei/Zeilen, Erfassungszeit, Vollständigkeit. OCR separat als unsicher markieren. Nie ganze absolute Nutzerpfade in Standardlogs.

## Anfrage

Button wechselt Senden -> Abbrechen. Zweite Anfrage während RUNNING/CANCELLING blockiert. Delta-Text erscheint inkrementell. Quellenliste basiert auf tatsächlich gesendetem Packet. Modellbehauptungen sind keine geprüften Diagnosen.

## Pause und Ende

Pause: neue Aufnahme blockiert, vorhandenen Kontext sichtbar lassen; eigener Button Kontext löschen. Ende: Nachfrage bei ungesicherter Chatkopie, Cancel, Kontext löschen, alte Events ignorieren. Keine Speicherung ohne Opt-in.

## Fehler

Server nicht erreichbar: „Ollama ist nicht erreichbar. Starte den lokalen Dienst oder nutze den Demo-Modus.“
Modell fehlt: „Das ausgewählte Modell ist nicht installiert. Jarves lädt es nicht automatisch herunter.“
Timeout: „Die lokale Antwort dauert zu lange. Teilantwort bleibt sichtbar; du kannst abbrechen oder einen kleineren Kontext verwenden.“
Budget überschritten: Quelle/History-Kürzung explizit anzeigen; zu große Frage zum Kürzen zurückgeben.
