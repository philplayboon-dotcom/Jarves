# Schnittstellenvertrag — Version 0.1 (Soll)

Status: vor Implementierung einzufrieren in T02. Namen dürfen nur durch Coordinator geändert werden. Alle Zeitstempel UTC ISO-8601; Anzeige lokal. UUIDs als Strings. Typen in domain/models.py, Ports in domain/ports.py, Fehler in domain/errors.py.

## Modelle

```python
from dataclasses import dataclass
from typing import Literal

SourceKind = Literal["manual", "file", "terminal", "ocr", "ide"]

@dataclass(frozen=True)
class ContextSource:
    id: str
    kind: SourceKind
    label: str
    text: str
    captured_at: str
    project_relative_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    completeness: Literal["full", "excerpt", "ocr_uncertain"] = "full"

@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant"]
    content: str

@dataclass(frozen=True)
class ContextPacket:
    session_id: str
    request_id: str
    sources: tuple[ContextSource, ...]
    messages: tuple[ChatMessage, ...]
    estimated_prompt_tokens: int
    warnings: tuple[str, ...]

@dataclass(frozen=True)
class ChatRequest:
    packet: ContextPacket
    model: str
    num_ctx: int = 2048
    num_predict: int = 384
    temperature: float = 0.2

@dataclass(frozen=True)
class ProviderEvent:
    session_id: str
    request_id: str
    kind: Literal["delta", "complete", "cancelled", "error"]
    text: str = ""
    error_code: str | None = None
```

Modelle sind interne Verträge, kein bereits verfügbarer Python-Code. Erweiterungen: Settings, RuntimeMetrics und SelectionSpec in T02 konkretisieren. Metrics enthält ausschließlich Counts, Dauern und Speicherwerte, keine Inhalte.

## Providerport

```python
class ModelProvider(Protocol):
    def list_models(self) -> tuple[str, ...]: ...
    def stream_chat(self, request: ChatRequest,
                    cancel: CancellationToken) -> Iterator[ProviderEvent]: ...
```

CancellationToken.cancel() und is_cancelled() sind thread-safe. Pro Stream genau ein terminales Event complete/cancelled/error. Alle Events tragen beide IDs. Leeres delta ist erlaubt; UI muss es nicht rendern. Fehler vor Streambeginn werden vom Worker in ein error-Event übersetzt. list_models wirft DomainError.

## Projektport

```python
class ProjectReader(Protocol):
    def read_text(self, root: Path, relative_path: str,
                  line_start: int | None = None,
                  line_end: int | None = None) -> ContextSource: ...
```

Zeilen sind 1-basiert, line_end inklusiv. Root wird einmal ausdrücklich ausgewählt. Pfad muss nach Auflösung innerhalb Root liegen; externe Symlinks/Junctions blockieren. UNC-/Gerätepfade im MVP blockieren. Keine Binärdateien; initial UTF-8/UTF-8-BOM. Encodingfehler nicht still ersetzen. Maximale Dateigröße 256 KiB; größer ergibt FILE_TOO_LARGE, bevor vollständig gelesen wird. Untergrenze line_start=1; verkehrte Bereiche ergeben INVALID_SELECTION.

## Screenshot-/OCR-Ports (ab M6)

ScreenshotPort.capture(SelectionSpec) -> CapturedImage.
OcrPort.recognize(CapturedImage, language) -> OcrResult.
CapturedImage enthält Pixel/Bytes im RAM, Bereich, Zeitpunkt; kein Default-Dateipfad. OcrResult enthält Text, Backendname und Warnungen. Konfidenz optional, nicht künstlich erfinden. OCR-Port darf nicht das Sprachmodell aufrufen.

## Kontextbudget

Start: num_ctx=2048; reserve_output=384; reserve_overhead=256; target_prompt<=1408 Tokens. Das gesamte Kontextfenster umfasst Prompt und Ausgabe. Größere Einstellungen erst nach Evaluation.

MVP-Schätzung: UTF-8-Bytezahl des serialisierten Prompttexts als bewusst grober konservativer Proxy; keine Behauptung exakter Tokenisierung. Anzeige heißt Schätzung. Tags/Systemprompt/Chatrollen mitrechnen. Nicht auf Seitenzahl oder Zeichen/4 als Garantiewert verlassen.

Priorität: Systemregeln und Frage behalten; explizite aktuelle Quellen vor Historie. Über Budget: ältere Historie entfernen, danach Quelle mit sichtbarer Trunkierungsmarkierung kürzen; falls Frage/System allein nicht passen, INPUT_TOO_LARGE. Weder stumme Kürzung noch automatische Dateisuche. Ollama prompt_eval_count nach Anfrage zum Vergleich protokollieren, ohne Inhalte.

## Ollama-Mapping

POST http://127.0.0.1:11434/api/chat; stream=true; messages aus Packet; model aus Settings. options: num_ctx, num_predict, temperature; keep_alive="1m" als Startwert. Kein images, tools oder think im MVP. GET /api/tags für list_models.

NDJSON zeilenweise parsen; HTTP-Chunkgrenzen sind keine JSON-Grenzen. Leerzeilen, UTF-8 über mehrere Chunks, finaler Restpuffer, unvollständiges JSON, done=true ohne Text und error-Antworten testen. Kein automatischer Request-Retry nach bereits ausgegebenem delta.

## Fehlercodes

SERVER_UNAVAILABLE, MODEL_NOT_FOUND, PROVIDER_TIMEOUT, PROVIDER_PROTOCOL_ERROR, REQUEST_CANCELLED, INVALID_ENDPOINT, OUTSIDE_PROJECT, EXCLUDED_PATH, INVALID_SELECTION, FILE_TOO_LARGE, BINARY_FILE, UNSUPPORTED_ENCODING, INPUT_TOO_LARGE, CAPTURE_FAILED, OCR_UNAVAILABLE, OCR_FAILED.

Nur Loopback-IP-Endpoints (127.0.0.1 oder ::1), keine URL-Credentials, keine Redirects, kein Proxy für lokalen Provider. Endpointvalidierung vor jedem Clientaufbau. localhost kann bei Bedarf normalisiert werden; beliebige DNS-Namen nicht zulassen.

## Antwortdarstellung

UI zeigt tatsächliche Quellen aus Packet unabhängig von Modellzitaten. Prompt darf Referenzen [S1] verlangen, aber Referenzen sind keine Wahrheitsgarantie. Unbekannte Quellen-ID kennzeichnen. Niemals erfundene Dateipfade in klickbare Öffnungsaktionen übersetzen.
