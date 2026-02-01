# Logger
Intended for creating, maintaining, and observing logs across repositories.

## Timing helpers
Use the `log_timing` context manager or `log_duration` decorator to emit a
structured overview event with `event="duration"`, `name`, `elapsed_ms`, and
`run_id` fields. These events are sent to the `org_logging.overview` logger so
handlers can route them to your overview log feed.

```python
import logging

from org_logging.timing import log_duration, log_timing

logging.basicConfig(level=logging.INFO)
overview_logger = logging.getLogger("org_logging.overview")

with log_timing("report.refresh", logger=overview_logger):
    # Do work here.
    ...

@log_duration(name="analytics.compute", logger=overview_logger)
def compute():
    # Do work here.
    ...

compute()
```
