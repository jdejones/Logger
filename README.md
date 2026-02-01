# Logger

Intended for creating, maintaining, and observing logs across repositories.

## GUI (live log viewer)

A minimal Flask UI lives in `ui/` for tailing an overview log and pulling detail/artifact metadata.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ui/requirements.txt

# Configure log locations (adjust paths as needed)
export OVERVIEW_LOG_PATH=/path/to/overview.log
export DETAIL_LOG_PATH=/path/to/detail.jsonl
export ARTIFACT_METADATA_PATH=/path/to/artifacts.json

python -m flask --app ui/app.py run --host 0.0.0.0 --port 5000
```

Then open <http://localhost:5000>.

### Configuration

The UI reads logs from paths configured via environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `OVERVIEW_LOG_PATH` | Path to the overview log file (plain text or JSON lines). | `./logs/overview.log` |
| `DETAIL_LOG_PATH` | Optional default JSONL file for detail log entries. | unset |
| `ARTIFACT_METADATA_PATH` | Optional default JSON file for artifact metadata. | unset |
| `LOG_MAX_ENTRIES` | Max number of log lines/entries returned per request. | `200` |

### Usage notes

- The overview feed polls the overview log and appends new lines every 2 seconds.
- If an overview line is JSON with `detail_log`, `detail_path`, `artifact_metadata`, `artifact_path`, or `id` fields, clicking the line will auto-fill the detail panel and fetch matching JSONL entries.
- You can always manually input a detail log path, artifact metadata path, and optional entry ID.
