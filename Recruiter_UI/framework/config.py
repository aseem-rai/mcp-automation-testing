from __future__ import annotations

import os
from dataclasses import dataclass

from framework.utils.settings import settings as env_settings


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


def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip()


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser_name: str
    headless: bool
    slow_mo_ms: int
    ignore_https_errors: bool
    default_timeout_ms: int
    navigation_timeout_ms: int


settings = Settings(
    base_url=env_settings.BASE_URL,
    browser_name=_env_str("BROWSER", "chromium"),
    headless=_env_bool("HEADLESS", False),
    slow_mo_ms=_env_int("SLOW_MO_MS", 0),
    ignore_https_errors=_env_bool("IGNORE_HTTPS_ERRORS", True),
    default_timeout_ms=_env_int("DEFAULT_TIMEOUT_MS", 15_000),
    navigation_timeout_ms=_env_int("NAVIGATION_TIMEOUT_MS", 60_000),
)
