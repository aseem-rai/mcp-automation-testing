from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://democandidate.meetaiva.in")
    browser_name: str = os.getenv("BROWSER", "chromium")  # chromium|firefox|webkit
    headless: bool = _env_bool("HEADLESS", False)
    slow_mo_ms: int = _env_int("SLOW_MO_MS", 0)
    ignore_https_errors: bool = _env_bool("IGNORE_HTTPS_ERRORS", True)
    default_timeout_ms: int = _env_int("DEFAULT_TIMEOUT_MS", 15_000)
    navigation_timeout_ms: int = _env_int("NAVIGATION_TIMEOUT_MS", 60_000)


settings = Settings()

