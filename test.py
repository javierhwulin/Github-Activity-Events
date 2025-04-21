"""
Run with:  pytest -q
"""

import time
from types import SimpleNamespace
from typing import Any, List

import pytest
import requests
from typer.testing import CliRunner

import cli
import github_events


# stubs
class _DummyResponse:
    def __init__(
        self,
        json_payload: Any,
        status: int = 200,
        *,
        headers: dict[str, str] | None = None,
        links: dict[str, Any] | None = None,
    ):
        self._payload = json_payload
        self.status_code = status
        self.headers = headers or {}
        self.links = links or {}
        self.text = (
            json_payload.get("message")
            if isinstance(json_payload, dict)
            else str(json_payload)
        )

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


class _DummySession:
    """Return queued responses in order every time `.get()` is called."""

    def __init__(self, responses: List[_DummyResponse]):
        self._responses = responses
        self.headers: dict[str, str] = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def get(self, url: str, *, timeout: int):
        try:
            return self._responses.pop(0)
        except IndexError:  # pragma: no cover
            raise RuntimeError("No more dummy responses queued") from None


# helpers
def _fake_requests(sess: _DummySession) -> SimpleNamespace:
    """Return a *minimal* stand‑in for the `requests` module."""
    return SimpleNamespace(Session=lambda: sess, HTTPError=requests.HTTPError)


def _patch_library(monkeypatch: pytest.MonkeyPatch, sess: _DummySession) -> None:
    """Patch **only** github_events.requests; cli uses the same module."""
    monkeypatch.setattr(github_events, "requests", _fake_requests(sess))


# library test
def test_fetch_events_happy(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = [
        {
            "created_at": "2025-04-20T12:00:00Z",
            "type": "PushEvent",
            "repo": {"name": "octocat/hello‑world"},
        }
    ]
    sess = _DummySession([_DummyResponse(payload)])
    _patch_library(monkeypatch, sess)

    events = github_events.fetch_events("octocat")
    assert len(events) == 1 and events[0].repo == "octocat/hello‑world"


def test_fetch_events_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(time.time()) + 60),
    }
    sess = _DummySession(
        [_DummyResponse({"message": "API rate limit exceeded"}, 403, headers=headers)]
    )
    _patch_library(monkeypatch, sess)

    with pytest.raises(SystemExit) as exc:
        github_events.fetch_events("octocat")

    assert exc.value.code == 1


def test_fetch_events_http_404(monkeypatch: pytest.MonkeyPatch) -> None:
    sess = _DummySession([_DummyResponse({"message": "Not Found"}, 404)])
    _patch_library(monkeypatch, sess)

    with pytest.raises(SystemExit) as exc:
        github_events.fetch_events("octocat")

    assert exc.value.code == 1


# cli test
runner = CliRunner()


def test_cli_fetch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = [
        {
            "created_at": "2025-04-20T12:00:00Z",
            "type": "WatchEvent",
            "repo": {"name": "octocat/spoon‑knife"},
        }
    ]
    sess = _DummySession([_DummyResponse(payload)])
    _patch_library(monkeypatch, sess)

    result = runner.invoke(cli.app, ["octocat"])
    assert result.exit_code == 0
    assert "WatchEvent" in result.stdout and "spoon‑knife" in result.stdout


def test_cli_fetch_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    sess = _DummySession([_DummyResponse({"message": "Not Found"}, 404)])
    _patch_library(monkeypatch, sess)

    result = runner.invoke(cli.app, ["nosuchuser"])
    assert result.exit_code == 1 and "HTTP 404" in result.stdout
