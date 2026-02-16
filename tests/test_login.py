import re

import pytest

from framework.pages.home_page import HomePage
from framework.pages.login_page import LoginPage


@pytest.mark.smoke
def test_democandidate_smoke_stub_login(page, base_url, tmp_path):
    """
    Smoke test (stub login):
    - Opens the site (base_url)
    - If redirected to login, asserts login UI is present (no credentials)
    - Captures a screenshot for debugging
    """
    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None, "No response object returned from navigation"
    assert response.status < 400, f"Unexpected HTTP status: {response.status}"

    # Let late resources settle a bit; don't over-wait.
    page.wait_for_timeout(1000)

    if re.search(r"/login\b|/signin\b|/auth\b", page.url, re.I):
        LoginPage(page, base_url).assert_login_ui_present_stub()
    else:
        HomePage(page, base_url).assert_rendered_something()

    page.screenshot(path=tmp_path / "democandidate.png", full_page=True)
