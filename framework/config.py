from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


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


def _get_base_url_from_env() -> str:
    """Deferred import to avoid circular import and to use framework.utils.settings validation."""
    from framework.utils.settings import settings as env_settings
    return env_settings.BASE_URL


@dataclass(frozen=True)
class Settings:
    base_url: str  # From .env via framework.utils.settings (no hardcoded URL).
    browser_name: str
    headless: bool
    slow_mo_ms: int
    ignore_https_errors: bool
    default_timeout_ms: int
    navigation_timeout_ms: int
    test_email: str
    test_password: str


settings = Settings(
    base_url=_get_base_url_from_env(),
    browser_name=_env_str("BROWSER") or "chromium",
    headless=_env_bool("HEADLESS", False),
    slow_mo_ms=_env_int("SLOW_MO_MS", 0),
    ignore_https_errors=_env_bool("IGNORE_HTTPS_ERRORS", True),
    default_timeout_ms=_env_int("DEFAULT_TIMEOUT_MS", 15_000),
    navigation_timeout_ms=_env_int("NAVIGATION_TIMEOUT_MS", 60_000),
    test_email=_env_str("TEST_EMAIL"),
    test_password=_env_str("TEST_PASSWORD"),
)

