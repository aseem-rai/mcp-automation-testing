"""
Save Google OAuth authentication state for use by tests.
Opens app in browser; log in manually with Google OAuth.
When URL contains /dashboard, state is saved to an env-specific file.

Usage:
  python -m framework.auth.save_auth_state              # use BASE_URL from .env
  python -m framework.auth.save_auth_state --democandidate   # save for democandidate (auth_democandidate.json)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from framework.utils.settings import settings

_AUTH_DIR = Path(__file__).resolve().parent
_DEMO_URL = "https://democandidate.meetaiva.in"
_LOG = logging.getLogger(__name__)


def _auth_state_path_for_base_url(base_url: str) -> Path:
    """Save to env-specific file so tests pick the right one by --base-url."""
    base_lower = (base_url or "").lower()
    if "democandidate" in base_lower:
        return _AUTH_DIR / "auth_democandidate.json"
    return _AUTH_DIR / "auth.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Save Google OAuth auth state. Log in manually in the browser; state is saved when dashboard loads."
    )
    parser.add_argument(
        "--democandidate",
        action="store_true",
        help="Open democandidate and save to framework/auth/auth_democandidate.json",
    )
    args = parser.parse_args()

    if args.democandidate:
        base_url = _DEMO_URL
        state_path = _AUTH_DIR / "auth_democandidate.json"
    else:
        base_url = settings.BASE_URL
        state_path = _auth_state_path_for_base_url(base_url)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    _AUTH_DIR.mkdir(parents=True, exist_ok=True)
    _LOG.info("Auth state will be saved to: %s", state_path.resolve())
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context()
        page = context.new_page()
        _LOG.info("Opening %s", base_url)
        page.goto(base_url)
        print("Login manually using Google OAuth")
        if args.democandidate:
            print("(Saving democandidate auth to auth_democandidate.json)")
        _LOG.info("Waiting for URL to contain /dashboard (timeout 5 min)")
        try:
            page.wait_for_url("**/dashboard", timeout=300_000)
        except Exception as e:
            _LOG.error("Timeout or error waiting for dashboard: %s", e)
            print(f"Timeout or error waiting for dashboard: {e}", file=sys.stderr)
            browser.close()
            return 1
        context.storage_state(path=str(state_path))
        _LOG.info("Auth state saved to %s", state_path.resolve())
        print("Auth state saved")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
