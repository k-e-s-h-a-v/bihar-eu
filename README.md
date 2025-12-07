# BEU Results Fetcher

Small Python script to fetch student result payloads from BEU and save each payload as JSON and a combined CSV summary.

Usage (uv-only)

This project uses `uv` for dependency and environment management. The `pyproject.toml` declares `requests` so `uv` will install it for you when you run the project.

Quick start for first-time `uv` users

1) Install `uv` (macOS/Linux example):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```



2) Install `uv` on Windows

You can install `uv` on Windows using the standalone installer, a package manager, or PyPI. Example options:

PowerShell (standalone installer):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

WinGet:

```powershell
winget install --id=astral-sh.uv -e
```

Scoop:

```powershell
scoop install main/uv
```

PyPI (recommended via `pipx`):

```powershell
pipx install uv
# or
pip install uv
```

Notes:
- Running the standalone installer script may require adjusting PowerShell's execution policy; inspect the script before running if desired.
- If you used a package manager (WinGet/Scoop/Pipx), use that manager to upgrade `uv`.

3) Run the fetcher inside the project environment (recommended):

```bash
uv run python fetch_results.py --start 23105108001 --end 23105108060 --concurrency 12
```

Notes:
- The `--` separates `uv`/Python invocation from the script's arguments in some shells; if you prefer, `uv run -- python fetch_results.py --start ...` also works.
- `uv venv` creates a `.venv` using the requested Python version; `uv sync` installs the dependencies declared in `pyproject.toml` into that `.venv`.


Output

- Default output directory is `./results_json`.
- Each successful payload is saved as `{redg_no}_{name}.json` (contains the `data` object from the API).
- A CSV summary `results.csv` is written into the output folder. The CSV header is intentionally fixed (derived from the sample response) and includes columns for each theory/practical subject ESE and IA.
- Registration numbers for which no valid result was returned are appended to `results_json/not_found.txt` (one per line).

Tips

- The script sends a browser-like User-Agent and Referer header. If the remote endpoint requires cookies or more headers, modify `HEADERS` in `fetch_results.py`.
- Choose a respectful `--concurrency` value to avoid overloading the remote server.

If you want, I can add inline script metadata so the script can be run directly with `uv run --script fetch_results.py` (this will use the script's own inline dependencies rather than the project dependencies). I kept the current project-managed approach as you requested.
