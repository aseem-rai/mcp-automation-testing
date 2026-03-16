from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip()


class _Settings:
    @property
    def BASE_URL(self) -> str:
        value = _env_str("BASE_URL")
        if not value:
            raise ValueError("BASE_URL is not set in Recruiter_UI/.env")
        return value.rstrip("/")

    @property
    def TEST_EMAIL(self) -> str:
        return _env_str("TEST_EMAIL")

    @property
    def TEST_PASSWORD(self) -> str:
        return _env_str("TEST_PASSWORD")

    @property
    def AUTH_STATE(self) -> str:
        return _env_str("AUTH_STATE", "framework/auth/auth.json")


settings = _Settings()
