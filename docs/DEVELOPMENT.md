# Entwicklungsstandard

## Vorgesehene Basis

Python 3.12 x64 als zu prüfende Projektbaseline, src-Layout, setuptools als schlanker Build-Backend-Vorschlag. T01 erstellt pyproject.toml und validiert Installation auf Windows. Geplante Runtime-Abhängigkeiten: PySide6, httpx. mss und OCR kommen erst M6. Geplante Dev-Abhängigkeiten: pytest, pytest-qt, ruff, mypy. Versionen in T01 kompatibel wählen und dokumentieren; hier keine ungetesteten Pins behaupten.

## Struktur und Stil

- Englische Bezeichner, deutsche UI und Dokumente.
- Type Hints in allen öffentlichen Funktionen; Domain mit frozen dataclasses.
- pathlib statt Stringpfade; keine globalen Singletons für Provider oder Settings.
- Imports nach Layergrenzen; Composition Root in app.py.
- Fehler mit Code, sicherem Text und optional interner Ursache; keine Rohinhalte loggen.
- Keine stillen catch-all-Fallbacks oder automatischen Netzwerkretries bei Teilantworten.
- PySide6-Signale/Slots sind die Brücke zwischen Worker und UI.

## Abhängigkeiten

Coordinator allein pflegt pyproject.toml. Neue Abhängigkeit: Zweck, Alternative, Lizenzhinweis, Speicher-/Installationsfolgen und Test notieren. Keine Abhängigkeit nur für eine kleine Standardbibliotheksfunktion. Keine Lizenzentscheidung des Nutzers erfinden; Third-Party-Lizenzen vor Distribution prüfen.

## Geplante lokale Befehle

Nach T01 und Nutzerfreigabe:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m jarves
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy src/jarves
```

Kein Aktivierungsskript erforderlich. Bootstrap definiert den Einstieg `python -m jarves`. Vorher gibt es kein installierbares Projekt.

## Git und Review

Kleine diffs, keine automatischen Commits/Pushes. Keine Nutzerdaten im Repository. Branches optional `task/Txx-kurzname`. Worktrees optional, nicht automatisch anlegen. Gemeinsamer Working Tree nur mit eindeutiger Ownership und nicht gleichzeitig derselben Datei. Alle zentralen Integrationsdateien vom Coordinator ändern lassen.

## Definition of Done

Akzeptanzkriterien erfüllt; fachlich passende automatisierte Tests; dokumentierter manueller Test wenn OS/Modell betroffen; Typ-/Lintprüfung; keine Inhalte in Logs; Task-Handoff mit tatsächlich ausgeführten Prüfungen. Unausgeführte Tests sind offen, nicht grün.
