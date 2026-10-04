# Handoff: T06 — FakeProvider über Hintergrundworker und Qt-Signale verbinden

## Status

DONE. Task-ID: T06, Agent, Datum: 2026-10-04, Contractstand: M2/M3

## Scope und Änderungen

- `src/jarves/ui/workers.py`: `InferenceWorker` implementiert. Dieser leitet den Stream des `FakeProvider` im QThread und sendet `ProviderEvent`s via Qt-Signal. Unerwartete Fehler werden abgefangen.
- `src/jarves/ui/event_bridge.py`: `EventBridge` implementiert. Verbindet `InferenceWorker`-Signale mit `ChatPanel`. Veraltete Events werden über die ID-Checks verworfen.
- `tests/ui/test_workers.py`: Tests für `InferenceWorker` (Events streamen, Cancel) und `EventBridge` (Event-Weiterleitung und Stale-Event-Check) implementiert.

## Akzeptanz

- Keine Widgetupdates vom Worker: Erfüllt. `InferenceWorker` sendet `ProviderEvent` über ein Qt-Signal `event_received`.
- Cancel sichtbar: Erfüllt. Wenn `cancel_token.is_cancelled()` aktiv ist, streamt der FakeProvider ein Cancel-Event und die UI verarbeitet dieses als System Notice.
- Fensterclose ohne Laufzeitcrash: Erfüllt. Worker fängt Exception ab, bricht sicher ab. Tests laufen mit QEventLoop stabil.
- Stale events verworfen: Erfüllt. `EventBridge` prüft `session_id` und `request_id`.

## Verifikation

| Befehl/Prüfung | Tatsächlich ausgeführt? | Ergebnis | Grenzen |
|---|---|---|---|
| `python -m ruff check .` | Ja | 0 Errors | - |
| `python -m ruff format --check .` | Ja | Formattiert | - |
| `python -m pytest -q` | Ja | 100% Passed (43 Tests) | Tests basieren auf FakeProvider |

## Risiken und Entscheidungen

- T05 SessionManager (parallel entwickelt): Die Implementation der `EventBridge` wurde bewusst entkoppelt, indem sie `set_active_ids` und einen Callback für `_on_request_finished` entgegennimmt. Es gibt keine harten Abhängigkeiten auf `SessionManager`.
- Testinfrastruktur: QApplication-Fixture wurde hinzugefügt, um headless Tests der Qt-Komponenten sauber zu unterstützen.

## Übergabe

- Die EventBridge und der InferenceWorker sind bereit, vom `MainController` initialisiert und mit der SessionManager-Klasse verknüpft zu werden (T07 oder weitere).
- Manuelle Prüfung des UI-Verhaltens (z.B. Abbruch) im Hauptfenster wird empfohlen, sobald der Controller integriert ist.
