"""Logging set-up shared by the services."""

import logging
import os
import sys

LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


def setup_logging(service: str) -> logging.Logger:
    """Configure the root logger once and return the logger of ``service``.

    The level comes from ``$LOG_LEVEL`` (default ``INFO``). Logs go to
    standard error, which is not buffered, so they show up immediately in
    ``docker compose logs``.
    """
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format=LOG_FORMAT, stream=sys.stderr)
    return logging.getLogger(service)
