# GitHub Activity Events CLI

A command‑line tool to fetch and display GitHub user activity (events) using the GitHub REST API, built with [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich).

## About the Project

This CLI application lets you inspect a GitHub user’s recent activity—such as pushes, watches, issues, forks—right from your terminal. It handles pagination, rate‑limit errors, optional authentication, and lets you filter by event type or scope (public vs. all events).

### Key Features

- **Fetch Events:** Retrieve a user’s events (public or all) with a single command.  
- **Pagination Support:** Control how many items per page and how many pages to fetch.  
- **Filter by Type:** Narrow results to a specific event kind (e.g., `PushEvent`, `WatchEvent`).  
- **Auth-Friendly:** Supply a personal access token to raise rate limits and access private events.  
- **Rich Output:** Colorized and neatly formatted output powered by Rich.

### Tech Stack

- **Python 3.9+**  
- **Typer** for CLI parsing  
- **Rich** for colored, human‑friendly console output  
- **Requests** for HTTP interactions  
- **JSON** under the hood (no database required)

## Getting Started

### Prerequisites

- **Python 3.9+**  
- **pip** (usually bundled with Python)  
- (Optional) A **GitHub personal access token** if you plan to fetch private events or avoid stricter rate limits.

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/javierhwulin/Github-Activity-Events.git
   cd Github-Activity-Events
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

## Usage Examples

1. **Fetch all events for a user**  
   ```bash
   python cli.py octocat
   ```  
   _Shows the 30 most recent events (default per‑page), across all pages until exhausted or rate‑limit hits._

2. **Fetch only public events, 50 per page, max 2 pages**
   ```bash
   python cli.py octocat --public-only --per-page 50 --max-pages 2
   ```

3. **Filter by event type**  
   ```bash
   python cli.py octocat --type PushEvent
   ```

4. **Use a personal access token**  
   ```bash
   python cli.py octocat --token YOUR_TOKEN_HERE
   ```

5. **Help and options**  
   ```bash
   python cli.py --help
   ```

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

## Contact

**Javier Hengda** – [javier.hwulin.devtech@gmail.com](mailto:javier.hwulin.devtech@gmail.com)

## Acknowledgements

- [Typer](https://typer.tiangolo.com/) for the intuitive CLI framework  
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output  
- GitHub API team for a reliable REST interface  

## Support

If you encounter issues or have suggestions, please [open an issue](https://github.com/javierhwulin/github-activity-events/issues) or reach out via email.
