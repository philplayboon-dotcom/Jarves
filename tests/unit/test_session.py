"""Unit tests for SessionManager."""

import pytest

from jarves.application.session import InvalidStateTransitionError, SessionManager


def test_initial_state():
    manager = SessionManager()
    assert manager.session_id is None
    assert manager.session_state == "inactive"
    assert manager.request_id is None
    assert manager.request_state == "idle"


def test_start_session():
    manager = SessionManager()
    session_id = manager.start_session()

    assert session_id is not None
    assert manager.session_id == session_id
    assert manager.session_state == "active"
    assert manager.request_state == "idle"


def test_start_session_ends_previous():
    manager = SessionManager()
    sid1 = manager.start_session()
    manager.start_request()

    sid2 = manager.start_session()
    assert sid1 != sid2
    assert manager.session_id == sid2
    assert manager.session_state == "active"
    assert manager.request_state == "idle"


def test_end_session():
    manager = SessionManager()
    manager.start_session()
    manager.start_request()

    manager.end_session()
    assert manager.session_id is None
    assert manager.session_state == "inactive"
    assert manager.request_id is None
    assert manager.request_state == "idle"


def test_pause_resume_session():
    manager = SessionManager()
    manager.start_session()

    manager.pause_session()
    assert manager.session_state == "paused"

    manager.resume_session()
    assert manager.session_state == "active"


def test_invalid_pause():
    manager = SessionManager()
    with pytest.raises(InvalidStateTransitionError):
        manager.pause_session()


def test_start_request():
    manager = SessionManager()
    manager.start_session()

    req_id, token = manager.start_request()
    assert req_id is not None
    assert manager.request_id == req_id
    assert manager.request_state == "running"
    assert not token.is_cancelled()


def test_start_request_without_session():
    manager = SessionManager()
    with pytest.raises(InvalidStateTransitionError):
        manager.start_request()


def test_second_request_blocks():
    manager = SessionManager()
    manager.start_session()
    manager.start_request()

    with pytest.raises(InvalidStateTransitionError):
        manager.start_request()


def test_cancel_request():
    manager = SessionManager()
    manager.start_session()
    _req_id, token = manager.start_request()

    manager.cancel_request()
    assert manager.request_state == "cancelling"
    assert token.is_cancelled()


def test_finish_request():
    manager = SessionManager()
    manager.start_session()
    manager.start_request()

    manager.finish_request()
    assert manager.request_state == "idle"
    assert manager.request_id is None
