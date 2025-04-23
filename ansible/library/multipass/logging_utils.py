"""Logging utilities for multipass Ansible module, compatible with ansible-execute CLI."""

import datetime
import json
import logging
import os
import pathlib
import time
from typing import Optional, Tuple


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for Vector or structured logging pipelines."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%S", time.localtime(record.created)
                ),
                "level": record.levelname,
                "filename": record.filename,
                "func": record.funcName,
                "line": record.lineno,
                "message": record.getMessage(),
            }
        )


def _verbosity_to_level(verbosity: int) -> int:
    if verbosity >= 2:
        return logging.DEBUG
    if verbosity == 1:
        return logging.INFO
    return logging.WARNING


def setup_logger() -> Tuple[logging.Logger, Optional[str]]:
    """
    Set up a logger for use in Ansible modules. Mirrors ansible-execute JSON log format.

    Reads:
        ANSIBLE_EXECUTE_LOG_DIR: where logs go (optional)
        ANSIBLE_EXECUTE_VERBOSITY: how verbose (default = 0)
    """
    verbosity = int(os.environ.get("ANSIBLE_EXECUTE_VERBOSITY", "0"))
    level = _verbosity_to_level(verbosity)

    logger = logging.getLogger("multipass")
    logger.setLevel(level)
    logger.debug("Logger setup")

    formatter = JSONFormatter()
    resolved_log_path = None

    # Log to file if instructed
    log_dir_env = os.environ.get("ANSIBLE_EXECUTE_LOG_DIR")
    if log_dir_env:
        log_dir = pathlib.Path(log_dir_env)
        log_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_filename = f"{date_str}_ansible-execute.log"
        resolved_log_path = log_dir / log_filename

        if not any(
            isinstance(h, logging.FileHandler)
            and h.baseFilename == str(resolved_log_path)
            for h in logger.handlers
        ):
            fh = logging.FileHandler(resolved_log_path, encoding="utf-8")
            fh.setFormatter(formatter)
            fh.setLevel(level)
            logger.addHandler(fh)

    # Only enable console logging in dev/debug if not run via ansible-playbook
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(level)
        logger.addHandler(sh)

    return logger, str(resolved_log_path) if resolved_log_path else None


# Shared logger instance for use inside multipass module
log, log_path = setup_logger()
