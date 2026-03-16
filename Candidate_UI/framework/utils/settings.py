"""
Environment-based configuration for Playwright automation.

Loads BASE_URL, TEST_EMAIL, TEST_PASSWORD, AUTH_STATE from .env (project root).
Supports Dev, QA, and Production by changing only .env.

Usage:
    from framework.utils.settings import settings
    settings.BASE_URL   # required; raises if missing
    settings.TEST_EMAIL
    settings.TEST_PASSWORD
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root: conftest.py and .env live here (parent of framework/).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip()


def _get_base_url() -> str:
    value = _env_str("BASE_URL")
    if not value:
        raise ValueError(
            "BASE_URL is not set.\n\n"
            "Add BASE_URL to your .env file in the project root.\n"
            "Example for different environments:\n"
            "  # Development\n"
            "  BASE_URL=https://dev.example.com\n"
            "  # QA\n"
            "  BASE_URL=https://qa.example.com\n"
            "  # Production\n"
            "  BASE_URL=https://app.example.com\n"
        )
    return value.rstrip("/")


class _Settings:
    """Immutable settings from environment."""

    def __init__(self) -> None:
        self._base_url: str | None = None
        self._test_email: str | None = None
        self._test_password: str | None = None
        self._auth_state: str | None = None

    @property
    def BASE_URL(self) -> str:
        if self._base_url is None:
            self._base_url = _get_base_url()
        return self._base_url

    @property
    def TEST_EMAIL(self) -> str:
        if self._test_email is None:
            self._test_email = _env_str("TEST_EMAIL")
        return self._test_email

    @property
    def TEST_PASSWORD(self) -> str:
        if self._test_password is None:
            self._test_password = _env_str("TEST_PASSWORD")
        return self._test_password

    @property
    def AUTH_STATE(self) -> str:
        if self._auth_state is None:
            self._auth_state = _env_str("AUTH_STATE") or "framework/auth/auth.json"
        return self._auth_state


settings = _Settings()
