# Handoff: T08 & T09 — OllamaProvider & Härtung

## Status

DONE. Task-IDs: T08, T09. Agent: provider. Datum: 04.10.2026. Verwendeter Contractstand: INTERFACES.md v0.1.

## Scope und Änderungen

### Bearbeitete Dateien
- `src/jarves/infrastructure/providers/ollama.py` (neu):
  - `validate_and_normalize_endpoint(endpoint: str) -> str`: Loopback-Validierung (nur `127.0.0.1`, `[::1]`, `localhost` -> normalisiert zu `127.0.0.1`), Abweisung von Remote-Hosts, Credentials, Proxies, HTTPS und ungültigen Ports; wirft `DomainError(INVALID_ENDPOINT)`.
  - `OllamaProvider`:
    - `list_models() -> tuple[str, ...]`: Ruft `GET /api/tags` ab, wandelt Verbindungs- und Protokollfehler in standardisierte DomainErrors (`SERVER_UNAVAILABLE`, `PROVIDER_TIMEOUT`, `PROVIDER_PROTOCOL_ERROR`).
    - `stream_chat(request: ChatRequest, cancel: CancellationToken) -> Iterator[ProviderEvent]`: Streamt POST `/api/chat` mit `stream=True`, NDJSON-Zeilenpufferung, Multi-Byte UTF-8 Dekodierung, Optionen `num_ctx`, `num_predict`, `temperature`, `keep_alive="1m"`. Keine `tools`/`images`/`think`-Felder.
    - Robuste Cancellation-Prüfung vor und während des Streamings.
    - Fehlerbehandlung (404 -> `MODEL_NOT_FOUND`, Verbindungsabbrüche -> `SERVER_UNAVAILABLE`, Timeouts -> `PROVIDER_TIMEOUT`, korrupte JSON-Zeilen -> `PROVIDER_PROTOCOL_ERROR`).
    - Garantiert genau ein terminales Event (`complete`, `cancelled`, `error`).
    - Kein automatischer Request-Retry nach bereits emittierten Deltas.
- `src/jarves/infrastructure/providers/__init__.py` (geändert):
  - Export von `OllamaProvider` und `validate_and_normalize_endpoint`.
- `tests/adapters/test_ollama_stream.py` (neu):
  - NDJSON-Streaming-Tests über mehrere Chunks, UTF-8-Grenzen, `done=True`, Leerzeilen, Cancellation und Payload-Prüfung.
- `tests/adapters/test_ollama_errors.py` (neu):
  - Endpoint-Policy-Tests (Loopback, Remote-Hosts, Credentials, Portbereiche, Params), `list_models()`-Fehlerfälle und `stream_chat()`-Fehlerfälle (404, 500, Stream-Abbrüche, JSON-Fehler, Timeouts, No-Retry-Invariante).

### Nicht bearbeitete / angrenzende Themen
- UI-Einstellungsdialog (Task T10 / ui-Agent)
- Echte Windows/Ollama-Smoke-Tests mit realem Server (Task T11 / coordinator)

## Akzeptanz

- **T08 / NDJSON-Streaming & list_models**: Erfüllt (`test_ollama_stream.py` prüft alle Aspekte offline via `httpx.MockTransport`).
- **T08 / Request-Format**: Erfüllt (keine tools/images/think; korrekte Options und keep_alive).
- **T08 / UTF-8 & Chunking**: Erfüllt (`test_stream_chat_utf8_split_across_chunks` teilt Mehrbyte-Zeichen über HTTP-Chunkgrenzen).
- **T09 / Endpoint-Policy**: Erfüllt (`test_endpoint_policy_rejections` weist Remote-Hosts, Credentials, HTTPS und ungültige Ports mit `INVALID_ENDPOINT` ab).
- **T09 / Timeouts & Errors**: Erfüllt (alle standardisierten Fehlercodes `SERVER_UNAVAILABLE`, `MODEL_NOT_FOUND`, `PROVIDER_TIMEOUT`, `PROVIDER_PROTOCOL_ERROR`, `INVALID_ENDPOINT` abgedeckt).
- **T09 / Cancellation & Terminal-Event**: Erfüllt (vor und während Stream, genau ein terminales Event, kein Retry nach Delta).

## Verifikation

| Befehl/Prüfung | Tatsächlich ausgeführt? | Ergebnis | Grenzen |
|---|---|---|---|
| `python -m pytest -v tests/adapters/` | Ja | 44 passed | Offline MockTransport |
| `python -m pytest -v` | Ja | 102 passed | Gesamte Testsuite grün |
| `python -m ruff check src/jarves/infrastructure/providers tests/adapters` | Ja | All checks passed | Linting sauber |
| `python -m ruff format --check src/jarves/infrastructure/providers tests/adapters` | Ja | 5 files formatted | Formatierung sauber |

## Risiken und Entscheidungen

- **IPv6-Loopback**: `[::1]` wird als gültige Loopback-Adresse unterstützt und korrekt normalisiert.
- **`httpx.MockTransport`**: Ermöglicht 100% deterministische und offline durchführbare Tests aller Netzwerk- und Streaming-Szenarien ohne echten Ollama-Server.
- **Port-Validierung**: `urllib.parse.SplitResult.port` fängt ungültige Portwerte sauber ab und übersetzt sie in `DomainError(INVALID_ENDPOINT)`.

## Übergabe

- Bereit für Task T11 (Integration und Windows/Ollama-Smoke mit echtem Server).
