"""Ollama ModelProvider Adapter fuer lokale LLM-Inferenz ueber HTTP/NDJSON."""

from __future__ import annotations

import json
import urllib.parse
from typing import TYPE_CHECKING

import httpx

from jarves.domain.errors import (
    INVALID_ENDPOINT,
    MODEL_NOT_FOUND,
    PROVIDER_PROTOCOL_ERROR,
    PROVIDER_TIMEOUT,
    SERVER_UNAVAILABLE,
    DomainError,
)
from jarves.domain.models import ProviderEvent

if TYPE_CHECKING:
    from collections.abc import Iterator

    from jarves.domain.cancellation import CancellationToken
    from jarves.domain.models import ChatRequest, ProviderSettings


def validate_and_normalize_endpoint(endpoint: str) -> str:
    """Validiert den Endpoint gemaess Sicherheitsrichtlinie und normalisiert ihn.

    Erlaubt sind ausschliesslich unverschluesselte HTTP-Loopback-Endpoints ohne Credentials:
    - http://127.0.0.1[:port]
    - http://[::1][:port]
    - http://localhost[:port] (wird zu http://127.0.0.1[:port] normalisiert)

    Wirft DomainError(INVALID_ENDPOINT), wenn der Endpoint ungueltig oder unsicher ist.
    """
    if not endpoint or not isinstance(endpoint, str):
        raise DomainError(
            INVALID_ENDPOINT,
            "Endpoint-URL darf nicht leer sein.",
        )

    try:
        parsed = urllib.parse.urlsplit(endpoint.strip())
    except Exception as exc:
        raise DomainError(
            INVALID_ENDPOINT,
            "Endpoint-URL konnte nicht geparst werden.",
            technical_detail=str(exc),
        ) from exc

    if parsed.scheme.lower() != "http":
        raise DomainError(
            INVALID_ENDPOINT,
            f"Ungueltiges Schema '{parsed.scheme}': "
            "Nur unverschluesseltes HTTP auf Loopback ist zulaessig.",
        )

    if parsed.username is not None or parsed.password is not None:
        raise DomainError(
            INVALID_ENDPOINT,
            "URL-Credentials (Benutzername/Passwort) sind im Endpoint nicht zulaessig.",
        )

    if parsed.query or parsed.fragment:
        raise DomainError(
            INVALID_ENDPOINT,
            "Query-Parameter oder Fragmente sind im Endpoint nicht zulaessig.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise DomainError(
            INVALID_ENDPOINT,
            "Endpoint enthaelt keinen gueltigen Hostnamen.",
        )

    host_lower = hostname.lower()
    if host_lower in ("localhost", "127.0.0.1"):
        normalized_host = "127.0.0.1"
    elif host_lower in ("::1", "[::1]"):
        normalized_host = "[::1]"
    else:
        raise DomainError(
            INVALID_ENDPOINT,
            f"Host '{hostname}' ist kein gueltiger lokaler Loopback-Endpunkt "
            "(nur 127.0.0.1, [::1], localhost).",
        )

    try:
        port = parsed.port
    except ValueError as exc:
        raise DomainError(
            INVALID_ENDPOINT,
            f"Ungueltiger Port im Endpoint: {exc}",
            technical_detail=str(exc),
        ) from exc

    if port is not None:
        if not (1 <= port <= 65535):
            raise DomainError(
                INVALID_ENDPOINT,
                f"Ungueltiger Port '{port}'. Erlaubt ist 1 bis 65535.",
            )
        netloc = f"{normalized_host}:{port}"
    else:
        netloc = normalized_host

    path = parsed.path.rstrip("/")
    return f"http://{netloc}{path}"


class OllamaProvider:
    """Ollama ModelProvider Adapter fuer lokale Inferenz ueber HTTP/NDJSON.

    Implementiert das ModelProvider Protocol. Kommuniziert ausschliesslich ueber
    Loopback-Endpoints ohne Proxies oder Redirects.
    """

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 30.0,
        settings: ProviderSettings | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if settings is not None:
            self._endpoint = settings.endpoint
            self._timeout_seconds = settings.timeout_seconds
        else:
            self._endpoint = endpoint
            self._timeout_seconds = timeout_seconds
        self._transport = transport

    def list_models(self) -> tuple[str, ...]:
        """Fragt verfuegbare Modelle ueber GET /api/tags ab."""
        base_url = validate_and_normalize_endpoint(self._endpoint)
        url = f"{base_url}/api/tags"

        try:
            with httpx.Client(
                timeout=httpx.Timeout(self._timeout_seconds, connect=10.0),
                follow_redirects=False,
                trust_env=False,
                transport=self._transport,
            ) as client:
                response = client.get(url)
        except (httpx.ConnectError, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            raise DomainError(
                SERVER_UNAVAILABLE,
                "Ollama-Server ist nicht erreichbar.",
                technical_detail=str(exc),
            ) from exc
        except httpx.TimeoutException as exc:
            raise DomainError(
                PROVIDER_TIMEOUT,
                "Zeitueberschreitung bei der Kommunikation mit dem Ollama-Server.",
                technical_detail=str(exc),
            ) from exc

        if response.status_code != 200:
            raise DomainError(
                PROVIDER_PROTOCOL_ERROR,
                f"Ollama-Server meldet HTTP-Status {response.status_code}.",
                technical_detail=response.text,
            )

        try:
            data = response.json()
        except Exception as exc:
            raise DomainError(
                PROVIDER_PROTOCOL_ERROR,
                "Antwort von /api/tags ist kein gueltiges JSON.",
                technical_detail=str(exc),
            ) from exc

        if (
            not isinstance(data, dict)
            or "models" not in data
            or not isinstance(data["models"], list)
        ):
            raise DomainError(
                PROVIDER_PROTOCOL_ERROR,
                "Antwortstruktur von /api/tags enthaelt kein gueltiges 'models'-Array.",
            )

        models: list[str] = []
        for item in data["models"]:
            if isinstance(item, dict) and "name" in item and isinstance(item["name"], str):
                models.append(item["name"])
            elif isinstance(item, str):
                models.append(item)

        return tuple(models)

    def stream_chat(
        self,
        request: ChatRequest,
        cancel: CancellationToken,
    ) -> Iterator[ProviderEvent]:
        """Streamt Antwort-Events fuer die gegebene Chat-Anfrage ueber POST /api/chat.

        Garantiert genau ein terminales Event ('complete', 'cancelled' oder 'error').
        """
        session_id = request.packet.session_id
        request_id = request.packet.request_id

        if cancel.is_cancelled():
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="cancelled",
                text="Anfrage vor Beginn abgebrochen.",
            )
            return

        try:
            base_url = validate_and_normalize_endpoint(self._endpoint)
        except DomainError as err:
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=err.code,
                text=err.user_message,
            )
            return

        url = f"{base_url}/api/chat"
        payload = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.packet.messages],
            "stream": True,
            "options": {
                "num_ctx": request.num_ctx,
                "num_predict": request.num_predict,
                "temperature": request.temperature,
            },
            "keep_alive": "1m",
        }

        client = httpx.Client(
            timeout=httpx.Timeout(self._timeout_seconds, connect=10.0),
            follow_redirects=False,
            trust_env=False,
            transport=self._transport,
        )

        try:
            with client.stream("POST", url, json=payload) as response:
                if response.status_code == 404:
                    yield ProviderEvent(
                        session_id=session_id,
                        request_id=request_id,
                        kind="error",
                        error_code=MODEL_NOT_FOUND,
                        text=(
                            f"Modell '{request.model}' wurde auf dem Ollama-Server nicht gefunden."
                        ),
                    )
                    return

                if response.status_code != 200:
                    try:
                        err_body = response.read().decode("utf-8", errors="replace")
                    except Exception:
                        err_body = ""
                    yield ProviderEvent(
                        session_id=session_id,
                        request_id=request_id,
                        kind="error",
                        error_code=PROVIDER_PROTOCOL_ERROR,
                        text=f"Ollama meldet HTTP {response.status_code}: {err_body}",
                    )
                    return

                got_done = False
                for line in response.iter_lines():
                    if cancel.is_cancelled():
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="cancelled",
                            text="Anfrage waehrend Stream abgebrochen.",
                        )
                        return

                    line_str = line.strip()
                    if not line_str:
                        continue

                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError as exc:
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="error",
                            error_code=PROVIDER_PROTOCOL_ERROR,
                            text=f"Ungueltiges JSON im NDJSON-Stream: {exc}",
                        )
                        return

                    if not isinstance(data, dict):
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="error",
                            error_code=PROVIDER_PROTOCOL_ERROR,
                            text="Ungueltiges JSON-Objekt im Stream empfangen.",
                        )
                        return

                    if "error" in data:
                        err_text = str(data["error"])
                        err_code = (
                            MODEL_NOT_FOUND
                            if "not found" in err_text.lower()
                            else PROVIDER_PROTOCOL_ERROR
                        )
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="error",
                            error_code=err_code,
                            text=err_text,
                        )
                        return

                    message = data.get("message")
                    if isinstance(message, dict):
                        delta_text = message.get("content", "")
                        if delta_text:
                            yield ProviderEvent(
                                session_id=session_id,
                                request_id=request_id,
                                kind="delta",
                                text=delta_text,
                            )

                    if data.get("done") is True:
                        got_done = True
                        if cancel.is_cancelled():
                            yield ProviderEvent(
                                session_id=session_id,
                                request_id=request_id,
                                kind="cancelled",
                                text="Anfrage nach Stream abgebrochen.",
                            )
                        else:
                            yield ProviderEvent(
                                session_id=session_id,
                                request_id=request_id,
                                kind="complete",
                            )
                        return

                if not got_done:
                    if cancel.is_cancelled():
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="cancelled",
                            text="Anfrage abgebrochen.",
                        )
                    else:
                        yield ProviderEvent(
                            session_id=session_id,
                            request_id=request_id,
                            kind="error",
                            error_code=PROVIDER_PROTOCOL_ERROR,
                            text="Stream vorzeitig geschlossen ohne done=true.",
                        )
                    return

        except (httpx.ConnectError, httpx.NetworkError, httpx.RemoteProtocolError):
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=SERVER_UNAVAILABLE,
                text="Ollama-Server nicht erreichbar oder Verbindung abgebrochen.",
            )
        except httpx.TimeoutException:
            yield ProviderEvent(
                session_id=session_id,
                request_id=request_id,
                kind="error",
                error_code=PROVIDER_TIMEOUT,
                text="Zeitueberschreitung bei Anfrage an Ollama.",
            )
        finally:
            client.close()
