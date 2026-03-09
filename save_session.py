"""
Save authenticated session to state.json for use by tests.

Loads TEST_EMAIL, TEST_PASSWORD, BASE_URL from .env, logs in, waits for dashboard,
then saves browser context state to state.json.

Run once before tests: python save_session.py
"""

import re
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).resolve().parent / ".env")

from framework.config import settings


def main() -> None:
    if not settings.test_email or not settings.test_password:
        raise SystemExit("Set TEST_EMAIL and TEST_PASSWORD in .env")

    state_path = Path("state.json")
    base_url = settings.base_url.rstrip("/")
    login_url = f"{base_url}/login"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        context.set_default_timeout(15_000)
        context.set_default_navigation_timeout(60_000)
        page = context.new_page()

        page.goto(login_url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        page.locator("input[type='email'], input[name='email'], input[placeholder*='email' i]").first.fill(settings.test_email)
        page.locator("input[type='password'], input[name='password']").first.fill(settings.test_password)
        page.get_by_role("button", name=re.compile(r"log\s*in|sign\s*in", re.I)).click()
        page.wait_for_timeout(3000)

        page.wait_for_url(re.compile(r"/dashboard", re.I), timeout=15_000)
        page.wait_for_load_state("domcontentloaded")

        context.storage_state(path=str(state_path))
        browser.close()

    print(f"Session saved to {state_path.resolve()}")


if __name__ == "__main__":
    main()
