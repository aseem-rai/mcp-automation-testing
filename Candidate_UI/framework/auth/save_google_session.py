"""
Save authenticated session for Google OAuth login using a persistent Chrome context.

Usage:
    1. Run: python -m framework.auth.save_google_session
    2. Complete Google sign-in in the opened browser.
    3. After redirect to dashboard, session is saved to framework/auth/state.json.
    4. Tests will use this session via conftest storage_state.

Requires: Playwright with Chrome channel (playwright install chromium).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Resolve paths relative to this file (framework/auth/).
_AUTH_DIR = Path(__file__).resolve().parent
_STATE_PATH = _AUTH_DIR / "state.json"
_USER_DATA_DIR = _AUTH_DIR / ".browser_data"
BASE_URL = "https://democandidate.meetaiva.in"


def main() -> int:
    _AUTH_DIR.mkdir(parents=True, exist_ok=True)

    url = BASE_URL.rstrip("/")
    print(f"Opening {url}")
    print("Complete Google sign-in in the browser. Session will be saved after redirect to dashboard.")
    print("(Waiting for URL to contain '/dashboard' or 'welcome' — up to 5 minutes.)\n")

    with sync_playwright() as p:
        # Real Chrome, persistent context so login state can be saved.
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(_USER_DATA_DIR),
            channel="chrome",
            headless=False,
            ignore_https_errors=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context.set_default_navigation_timeout(60_000)
        context.set_default_timeout(15_000)

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Wait for user to finish login (dashboard or welcome).
        try:
            page.wait_for_url(
                re.compile(r"/dashboard|/home|welcome", re.I),
                timeout=300_000,
            )
        except Exception as e:
            print(f"Timeout or error waiting for post-login URL: {e}", file=sys.stderr)
            context.close()
            return 1

        # Small settle before saving state.
        page.wait_for_timeout(2000)

        context.storage_state(path=str(_STATE_PATH))
        context.close()

    print(f"Session saved to: {_STATE_PATH.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
