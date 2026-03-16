from __future__ import annotations

import logging
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from framework.utils.settings import settings

_AUTH_DIR = Path(__file__).resolve().parent
_LOG = logging.getLogger(__name__)


def main() -> int:
    base_url = settings.BASE_URL
    state_rel = settings.AUTH_STATE
    state_path = Path(state_rel)
    if not state_path.is_absolute():
        state_path = Path(__file__).resolve().parents[2] / state_path

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    _AUTH_DIR.mkdir(parents=True, exist_ok=True)
    _LOG.info("Auth state will be saved to: %s", state_path.resolve())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context()
        page = context.new_page()
        _LOG.info("Opening %s", base_url)
        page.goto(base_url)
        print("Login manually and complete verification.")
        _LOG.info("Waiting for URL to contain dashboard/recruiter/jobs (timeout 5 min)")
        try:
            page.wait_for_url("**/*dashboard*", timeout=300_000)
        except Exception:
            try:
                page.wait_for_url("**/*recruiter*", timeout=20_000)
            except Exception as e:
                _LOG.error("Timeout or error waiting for app landing: %s", e)
                print(f"Timeout or error waiting for app landing: {e}", file=sys.stderr)
                browser.close()
                return 1
        context.storage_state(path=str(state_path))
        _LOG.info("Auth state saved to %s", state_path.resolve())
        print("Auth state saved")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
