import json
import logging
import logging.config
from datetime import datetime, timezone


class JsonLogFormatter(logging.Formatter):
    """Format logs as one structured JSON object per line."""

    EXTRA_FIELDS = (
        "event",
        "request_id",
        "method",
        "path",
        "status_code",
        "duration_ms",
        "mode",
        "error_type",
        "stack_trace",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in self.EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def make_logging_config(*, production: bool) -> dict:
    formatter = (
        {"()": "app.core.logging_setup.JsonLogFormatter"}
        if production
        else {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}
    )
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"console": formatter},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "console",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
        "loggers": {
            "uvicorn": {"level": "INFO", "handlers": [], "propagate": True},
            "uvicorn.error": {"level": "INFO", "handlers": [], "propagate": True},
            # Request logs below include status, latency, and a request ID.
            "uvicorn.access": {
                "level": "CRITICAL" if production else "INFO",
                "handlers": [],
                "propagate": True,
            },
            "sqlalchemy.engine": {"level": "WARNING", "handlers": [], "propagate": True},
        },
    }


def configure_logging(*, production: bool) -> dict:
    config = make_logging_config(production=production)
    logging.config.dictConfig(config)
    return config
