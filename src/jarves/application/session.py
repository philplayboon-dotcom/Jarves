"""Session and request state management."""

import uuid

from jarves.domain.cancellation import CancellationToken
from jarves.domain.models import RequestState, SessionState


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


class SessionManager:
    """Manages the lifecycle of sessions and requests."""

    def __init__(self) -> None:
        self._session_id: str | None = None
        self._session_state: SessionState = "inactive"
        self._request_id: str | None = None
        self._request_state: RequestState = "idle"
        self._cancellation_token: CancellationToken | None = None

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def session_state(self) -> SessionState:
        return self._session_state

    @property
    def request_id(self) -> str | None:
        return self._request_id

    @property
    def request_state(self) -> RequestState:
        return self._request_state

    def start_session(self) -> str:
        """Start a new session, ending the previous one if active."""
        if self._session_state != "inactive":
            self.end_session()

        self._session_id = str(uuid.uuid4())
        self._session_state = "active"
        self._request_state = "idle"
        self._request_id = None
        self._cancellation_token = None
        return self._session_id

    def end_session(self) -> None:
        """End the current session, canceling any active request."""
        if self._request_state in ("running", "cancelling"):
            self.cancel_request()
            self.finish_request()

        self._session_id = None
        self._session_state = "inactive"
        self._request_id = None
        self._request_state = "idle"
        self._cancellation_token = None

    def pause_session(self) -> None:
        """Pause the current session."""
        if self._session_state != "active":
            raise InvalidStateTransitionError("Can only pause an active session.")
        self._session_state = "paused"

    def resume_session(self) -> None:
        """Resume a paused session."""
        if self._session_state != "paused":
            raise InvalidStateTransitionError("Can only resume a paused session.")
        self._session_state = "active"

    def start_request(self) -> tuple[str, CancellationToken]:
        """Start a new request in the current session."""
        if self._session_state not in ("active", "paused"):
            raise InvalidStateTransitionError(
                "Session must be active or paused to start a request."
            )

        if self._request_state != "idle":
            raise InvalidStateTransitionError("Another request is already active.")

        self._request_id = str(uuid.uuid4())
        self._request_state = "running"
        self._cancellation_token = CancellationToken()
        return self._request_id, self._cancellation_token

    def cancel_request(self) -> None:
        """Cancel the current request."""
        if self._request_state != "running":
            raise InvalidStateTransitionError("No running request to cancel.")

        if self._cancellation_token:
            self._cancellation_token.cancel()

        self._request_state = "cancelling"

    def finish_request(self) -> None:
        """Finish the current request."""
        if self._request_state not in ("running", "cancelling"):
            raise InvalidStateTransitionError("No active request to finish.")

        self._request_state = "idle"
        self._request_id = None
        self._cancellation_token = None
