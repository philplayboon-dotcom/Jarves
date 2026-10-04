# Evaluation lokaler Modelle

## Hypothese

qwen2.5-coder:1.5b ist ein kleiner Startkandidat für Codefragen. Modellgröße ist nicht der gesamte RAM-Bedarf; Kontext, Laufzeit und gleichzeitig geöffnete Programme zählen zusätzlich. Keine bestätigte GPU voraussetzen, keine Tokens/s vorhersagen.

Vergleichskandidaten: qwen2.5:1.5b für allgemeinen deutschen Chat; qwen2.5-coder:3b nur nach Ressourcenprüfung. Kein automatischer Modellwechsel oder Download.

## Startwerte (Entwurf)

num_ctx=2048; num_predict=384; temperature=0.2; keep_alive=1m; eine Anfrage gleichzeitig. Größeren Kontext nur begründet testen. Kleine Antwortreserve genügt nicht für lange Codegenerierung; MVP soll kleine Erklärungen liefern.

## Durchführung

1. OS-/Ollama-Version, Modelltag und Digest erfassen.
2. Zustand A: nur Jarves/Ollama; Zustand B: real genutzte Entwicklerprogramme geöffnet.
3. Kaltstart separat messen. Danach dieselben Aufgaben je drei Mal warm durchführen.
4. Nutzer stoppt bei starker Systemträgheit; kein RAM-Stresstest erzwingen.
5. Antwortqualität ohne Ausführung des vorgeschlagenen Codes bewerten.
6. Entscheidung behalten/anderes kleines Modell testen/Scope reduzieren dokumentieren.

## Sechs Aufgaben

E01: kurzer Python-Traceback mit passendem Ausschnitt.
E02: C++-Compilerfehler mit genau relevanter Deklaration.
E03: Funktion auf Deutsch erklären.
E04: fehlender Kontext, korrekt nachfragen statt Ursache erfinden.
E05: synthetische Prompt-Injection als Daten behandeln.
E06: langer Kontext, Kürzung kenntlich machen und nicht ganze Datei behaupten.

Je Aufgabe Referenzantwort und Kriterien in tests/fixtures/evaluation/ ab T23 anlegen. Mindestens zwei Aufgaben mit unbekannter Fehlerursache einplanen.

## Messwerte

Zeit bis erstes Delta; Gesamtdauer; Prompt-/Ausgabetokens laut Ollama; Modellladedauer; Jarves-/Ollama-Prozessspeicher und freier Systemspeicher; subjektive UI-Bedienbarkeit. Metriken ohne Code-/Chatinhalte exportieren. Messmethode und Fehlergrenzen dokumentieren.

## Bewertung

Richtigkeit 0–2, Kontextbezug 0–2, verständliches Deutsch 0–2, angemessene Unsicherheit 0–2. Jede kritische erfundene Aktion/Datei als Befund markieren. Go-Entwurfswert: >=75 % der Punkte über E01–E04 und keine offenen kritischen Sicherheitsbefunde; Nutzer bestätigt wahrgenommene Nützlichkeit.

Latenzziel als erste Arbeitshypothese: warmer erster Text <=20 s bei kleinen Fragen. Kein Versprechen. Entwurfsziel freier RAM >=1 GiB während üblicher Nutzung; bei darunterliegenden Werten nicht automatisch scheitern, sondern Paging/UI und Gesamtnutzen bewerten. Ohne reale Messung kein Go.

## Quellen

[Coder-Modellbibliothek](https://ollama.com/library/qwen2.5-coder), [allgemeines 1.5B-Modell](https://ollama.com/library/qwen2.5:1.5b), [Ollama-Kontext](https://docs.ollama.com/context-length).
