from typing import Annotated, List, Optional

import typer
from rich import print as rprint

from github_events import Event, fetch_events

app = typer.Typer(help="Fetch and display Github user activity")


@app.command()
def fetch(
    username: Annotated[str, typer.Argument(help="Github username")],
    token: Annotated[
        Optional[str],
        typer.Option("--token", "-t", help="Github personal access token"),
    ] = None,
    public_only: Annotated[
        bool, typer.Option("--public_only", help="Only fetch public events")
    ] = False,
    per_page: Annotated[
        int,
        typer.Option(
            "--per-page",
            help="Items per page (1-100)",
            min=1,
            max=100,
            show_default=True,
        ),
    ] = 30,
    max_pages: Annotated[
        Optional[int], typer.Option("--max_pages", help="Maximum pages to fetch")
    ] = None,
    event_type: Annotated[
        Optional[str],
        typer.Option(
            "--type", help="Filter by event type (PushEvent, WatchEvent, ...)"
        ),
    ] = None,
):
    try:
        events = fetch_events(
            username,
            token=token,
            per_page=per_page,
            max_pages=max_pages,
            public_only=public_only,
        )
    except SystemExit as exc:
        raise typer.Exit(code=int(getattr(exc, "code", 1) or 1))
    if event_type:
        events = [ev for ev in events if ev.type == event_type]

    if not events:
        rprint("[yellow]No events found.[/yellow]")
        raise typer.Exit(0)

    _print_events(events)


def _print_events(events: List[Event]) -> None:
    for ev in events:
        rprint(f"{ev.created_at} - {ev.type:<12}: {ev.repo}")


if __name__ == "__main__":
    app()
