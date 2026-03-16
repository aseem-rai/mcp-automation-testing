from __future__ import annotations

import logging
from contextvars import ContextVar
from pathlib import Path

_TEST_RESULTS_DIR = Path(__file__).resolve().parents[2] / "test-results"
_LOG_FILE = _TEST_RESULTS_DIR / "test.log"

_CURRENT_TEST_NAME: ContextVar[str | None] = ContextVar("current_test_name", default=None)


def set_current_test_name(name: str | None) -> None:
    _CURRENT_TEST_NAME.set(name)


def get_current_test_name() -> str:
    return _CURRENT_TEST_NAME.get() or "-"


class _StepFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(test_name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        record.test_name = get_current_test_name()
        return super().format(record)


def _setup_logger() -> logging.Logger:
    _TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("recruiter.steps")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    log.propagate = True

    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8", mode="a")
    handler.setFormatter(_StepFormatter())
    log.addHandler(handler)
    return log


logger = _setup_logger()
