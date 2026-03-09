"""
Step logging for Playwright pytest automation.

Logs include timestamp, test name, step description, and PASS/FAIL.
Writes to test-results/test.log and propagates to root so pytest-html shows them.

Usage in tests and page objects:
    from framework.utils.logger import logger, log_step

    log_step("Opening Dashboard")
    log_step("Clicking Resume button")
    log_step("Verifying job card")
    logger.info("Creating JD")
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from pathlib import Path

# test-results dir for QA report
_TEST_RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "test-results"
_LOG_FILE = _TEST_RESULTS_DIR / "test.log"

_CURRENT_TEST_NAME: ContextVar[str | None] = ContextVar("current_test_name", default=None)


def set_current_test_name(name: str | None) -> None:
    """Set the current test name (called by conftest pytest hooks)."""
    _CURRENT_TEST_NAME.set(name)


def get_current_test_name() -> str:
    """Return current test name for log formatting."""
    return _CURRENT_TEST_NAME.get() or "—"


def log_step(description: str) -> None:
    """Log a step description so it appears in the report."""
    logger.info(description)


class _StepFormatter(logging.Formatter):
    """Format: timestamp [LEVEL] test_name | STEP: message (or message for INFO)."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(test_name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        record.test_name = get_current_test_name()
        if record.levelname == "INFO":
            msg = record.getMessage()
            if not msg.strip().upper().startswith("TEST "):
                record.msg = "STEP: " + msg
                record.args = ()
        return super().format(record)


def _setup_logger() -> logging.Logger:
    _TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log = logging.getLogger("framework.steps")
    if log.handlers:
        return log

    log.setLevel(logging.DEBUG)
    log.propagate = True

    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8", mode="a")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_StepFormatter())
    log.addHandler(handler)

    return log


logger = _setup_logger()


def step(msg: str, *args, **kwargs) -> None:
    """Log a test step (same as log_step; message appears as STEP in report)."""
    logger.info(msg, *args, **kwargs)


logger.step = step  # type: ignore[attr-defined]
