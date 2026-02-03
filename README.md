# Logger

Intended for creating, maintaining, and observing logs across repositories.

## Timing helpers
Use the `log_timing` context manager, `log_duration` decorator, or
`log_return_count` decorator to emit structured overview events with
`event="duration"` or `event="return_count"`. Duration events include
`duration_name`, `elapsed_ms`, and `run_id`. Return count events include
`return_count_name`, `count`, and `run_id`. These events are sent to the
`org_logging.overview` logger so handlers can route them to your overview log feed.

```python
import logging

from org_logging.timing import log_duration, log_return_count, log_timing

logging.basicConfig(level=logging.INFO)
overview_logger = logging.getLogger("org_logging.overview")

with log_timing("report.refresh", logger=overview_logger):
    # Do work here.
    ...

@log_duration(name="analytics.compute", logger=overview_logger)
def compute():
    # Do work here.
    ...

@log_return_count(name="analytics.load_items", logger=overview_logger)
def load_items():
    return [1, 2, 3]

compute()
load_items()
```
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
export LOG_DIR=/path/to/logs
export OVERVIEW_LOG_FILENAME=overview.log

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
| `LOG_DIR` | Base directory used when `OVERVIEW_LOG_PATH` is not set. | `./logs` |
| `OVERVIEW_LOG_FILENAME` | Overview log filename under `LOG_DIR` when path is unset. | `overview.log` |
| `LOG_MAX_ENTRIES` | Max number of log lines/entries returned per request. | `200` |

### Usage notes

- The overview feed polls the overview log and appends new lines every 2 seconds.
- If an overview line is JSON with `detail_log`, `detail_path`, `artifact_metadata`, `artifact_path`, or `id` fields, clicking the line will auto-fill the detail panel and fetch matching JSONL entries.
- You can always manually input a detail log path, artifact metadata path, and optional entry ID.
## Usage

```python
from org_logging import configure_logging, get_logger

run_id = configure_logging(app_name="billing-service", log_dir="logs")
logger = get_logger(__name__)

logger.info("Started service")
logger.debug("Loaded config", extra={"feature_flag": True})
```

The configuration writes:

- An overview text log at `logs/overview.log` (INFO and higher)
- A detail JSONL log at `logs/detail.jsonl` (DEBUG and higher)
- Console output with the overview formatter
