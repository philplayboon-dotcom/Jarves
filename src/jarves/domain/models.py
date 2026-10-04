"""Domaenenmodelle fuer Jarves-AI gemaess INTERFACES.md v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SourceKind = Literal["manual", "file", "terminal", "ocr", "ide"]
Completeness = Literal["full", "excerpt", "ocr_uncertain"]
ChatRole = Literal["system", "user", "assistant"]
EventKind = Literal["delta", "complete", "cancelled", "error"]
SessionState = Literal["inactive", "active", "paused"]
RequestState = Literal["idle", "running", "cancelling"]


@dataclass(frozen=True)
class ContextSource:
    """Repraesentiert eine explizit bereitgestellte Kontextquelle."""

    id: str
    kind: SourceKind
    label: str
    text: str
    captured_at: str
    project_relative_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    completeness: Completeness = "full"


@dataclass(frozen=True)
class ChatMessage:
    """Einzelne Nachricht im Chatverlauf."""

    role: ChatRole
    content: str


@dataclass(frozen=True)
class ContextPacket:
    """Vollstaendiges Kontextpaket fuer eine Modell-Anfrage."""

    session_id: str
    request_id: str
    sources: tuple[ContextSource, ...]
    messages: tuple[ChatMessage, ...]
    estimated_prompt_tokens: int
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ChatRequest:
    """Anfrageparameter fuer den ModelProvider."""

    packet: ContextPacket
    model: str
    num_ctx: int = 2048
    num_predict: int = 384
    temperature: float = 0.2


@dataclass(frozen=True)
class ProviderEvent:
    """Event aus dem gestreamten Inferenz-Prozess."""

    session_id: str
    request_id: str
    kind: EventKind
    text: str = ""
    error_code: str | None = None


@dataclass(frozen=True)
class SelectionSpec:
    """Spezifikation fuer Bildschirmausschnitte (ab M6)."""

    x: int
    y: int
    width: int
    height: int
    display_id: int = 0


@dataclass(frozen=True)
class RuntimeMetrics:
    """Metriken ohne Nutzerinhalte fuer Monitoring und Benchmarks."""

    prompt_eval_count: int | None = None
    eval_count: int | None = None
    total_duration_ms: float | None = None
    load_duration_ms: float | None = None
    prompt_eval_duration_ms: float | None = None
    eval_duration_ms: float | None = None


@dataclass(frozen=True)
class ProviderSettings:
    """Konfiguration fuer den lokalen Model-Provider."""

    endpoint: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5-coder:1.5b"
    num_ctx: int = 2048
    num_predict: int = 384
    temperature: float = 0.2
    keep_alive: str = "1m"
    timeout_seconds: float = 30.0
