from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import requests
from rich import print as rprint

BASE_URL = "https://api.github.com/users"
DEFAULT_TIMEOUT = 10


@dataclass(frozen=True, slots=True)
class Event:
    """Github user activity event"""

    created_at: str
    type: str
    repo: str

    @classmethod
    def from_api(cls, payload: Dict[str, Any]) -> "Event":
        """Convert raw API payload into an Event instance."""
        return cls(
            created_at=payload.get("created_at", "n/a"),
            type=payload.get("type", "n/a"),
            repo=payload.get("repo", {}).get("name", "n/a"),
        )


def _build_headers(token: Optional[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _paginate(
    session: requests.Session,
    url: str,
    *,
    max_pages: int | None,
) -> Iterable[dict[str, Any]]:
    """Yield all items across paginated Github API responses."""
    page = 0
    while url and (max_pages is None or page < max_pages):
        resp = session.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        yield from resp.json()
        page += 1
        url = resp.links.get("next", {}).get("url")


def _handle_http_error(err: requests.HTTPError) -> None:
    """Pretty-print an HTTP error and exit programmatically."""
    resp = err.response
    status = resp.status_code

    if resp.headers.get("X-RateLimit-Remaining") == "0":
        reset_ts = resp.headers.get("X-RateLimit-Reset")
        if reset_ts and reset_ts.isdigit():
            reset_dt = datetime.fromtimestamp(int(reset_ts), tz=timezone.utc)
            reset = reset_dt.astimezone().isoformat()
        else:
            reset = "unknown"
        rprint(f"[red]Rate-limit exceeded - resets at {reset}[/red]")
    else:
        try:
            message = resp.json().get("message", resp.text)
        except ValueError:
            message = resp.text or "Unknown error"
        rprint(f"[red]HTTP {status} Error:[/red] {message}")

    raise SystemExit(1)


def fetch_events(
    username: str,
    *,
    token: str | None = None,
    per_page: int = 30,
    max_pages: int | None = None,
    public_only: bool = False,
) -> List[Event]:
    """
    Retrieve Github events for *username* and return them as `Event` objects.
    This function raises `SystemExit` on fatal API errors.
    """
    endpoint = "events/public" if public_only else "events"
    url = f"{BASE_URL}/{username}/{endpoint}?per_page={per_page}"

    with requests.Session() as session:
        session.headers.update(_build_headers(token))
        try:
            raw: List[dict[str, Any]] = list(
                _paginate(session, url, max_pages=max_pages)
            )
            return [Event.from_api(ev) for ev in raw]
        except requests.HTTPError as e:
            _handle_http_error(e)
    return []
