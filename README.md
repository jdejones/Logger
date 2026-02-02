# Logger
Intended for creating, maintaining, and observing logs across repositories.

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
