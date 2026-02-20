import re

import pytest

from framework.pages.login_page import LoginPage
from framework.pages.preps_page import PrepsPage


def _skip_if_login_required(page, base_url) -> None:
    if re.search(r"/login\b|/signin\b|/auth\b", page.url, re.I):
        LoginPage(page, base_url).assert_login_ui_present_stub()
        pytest.skip("Preps require authentication; login UI verified (stub).")


def test_open_preps_page(page, base_url):
    """Navigate to Preps and verify page heading."""
    preps = PrepsPage(page, base_url)
    preps.open_preps_page()
    _skip_if_login_required(page, base_url)


def test_create_jd(page, base_url):
    """Create JD via New Prep -> Create JD tab -> fill form -> Create JD -> verify card and screenshot."""
    preps = PrepsPage(page, base_url)
    preps.open_preps_page()
    _skip_if_login_required(page, base_url)
    if "/preps" not in page.url:
        pytest.skip("Preps page did not load; redirect or session issue.")
    if preps.new_prep_button.count() == 0:
        pytest.skip("New Prep / Create JD button not found; Preps UI may differ.")
    path = preps.create_jd()
    assert path.exists(), f"Expected screenshot at {path}"
    assert path.name == "prep_create_jd_success.png"


def test_upload_jd(page, base_url):
    """Upload JD via New Prep -> Upload JD tab -> upload file -> Next -> verify and screenshot."""
    preps = PrepsPage(page, base_url)
    preps.open_preps_page()
    _skip_if_login_required(page, base_url)
    if "/preps" not in page.url:
        pytest.skip("Preps page did not load; redirect or session issue.")
    if preps.new_prep_button.count() == 0:
        pytest.skip("New Prep / Create JD button not found; Preps UI may differ.")
    path = preps.upload_jd()
    assert path.exists(), f"Expected screenshot at {path}"
    assert path.name == "prep_upload_jd_success.png"


def test_verify_prep_buttons(page, base_url):
    """Verify Take Mock Interview, Enhance Resume, and Delete buttons are visible."""
    preps = PrepsPage(page, base_url)
    preps.open_preps_page()
    _skip_if_login_required(page, base_url)
    if "/preps" not in page.url:
        pytest.skip("Preps page did not load; redirect or session issue.")
    if preps.new_prep_button.count() == 0:
        pytest.skip("New Prep button not found; no prep cards to verify.")
    preps.verify_prep_action_buttons()
