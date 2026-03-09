"""
Prep module smoke tests (no upload flow).
These tests only verify:
1) Preps page loads
2) Existing prep card is visible
3) The 3 prep card action buttons are visible
"""

import pytest

from framework.pages.login_page import LoginPage
from framework.pages.preps_page import PrepsPage

_WAIT_DASHBOARD_MS = 15_000


def _ensure_dashboard_same_as_login_test(page, base_url) -> None:
    """Use same dashboard reachability flow as login/resume tests."""
    login_page = LoginPage(page, base_url)
    if not login_page.is_dashboard_loaded():
        base = (base_url or "").rstrip("/")
        page.goto(f"{base}/dashboard", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=15_000)
        try:
            page.wait_for_url("**/dashboard**", timeout=_WAIT_DASHBOARD_MS)
        except Exception:
            pass
        try:
            page.wait_for_load_state("networkidle", timeout=20_000)
        except Exception:
            page.wait_for_timeout(3000)
        page.wait_for_timeout(2000)
    if login_page.is_dashboard_loaded():
        return
    page.wait_for_timeout(5000)
    if login_page.is_dashboard_loaded():
        return
    login_page.take_screenshot("preps_login_failure")
    _hint = (
        "python -m framework.auth.save_auth_state --democandidate"
        if "democandidate" in (base_url or "").lower()
        else "python -m framework.auth.save_auth_state"
    )
    pytest.fail(f"Auth state missing or expired. Run: {_hint}")


def _open_preps_page_with_card(page, base_url) -> PrepsPage:
    _ensure_dashboard_same_as_login_test(page, base_url)
    preps_page = PrepsPage(page, base_url)
    preps_page.open_preps_page()
    preps_page.verify_first_jd_card_buttons(timeout_ms=30_000)
    preps_page.verify_first_three_action_buttons_clickable(timeout_ms=30_000)
    return preps_page


def _recover_to_preps(page, preps_page: PrepsPage, before_url: str) -> None:
    page.wait_for_timeout(1200)
    if (page.url or "") == before_url:
        preps_page.dismiss_open_panel_or_dialog(timeout_ms=5_000)
    if "/preps" not in (page.url or "").lower():
        preps_page.go_back_to_preps_page()


@pytest.mark.prep
@pytest.mark.smoke
def test_preps_page_load(page, base_url):
    """Prep page loads successfully."""
    print("Test: test_preps_page_load")
    _ensure_dashboard_same_as_login_test(page, base_url)
    preps_page = PrepsPage(page, base_url)
    preps_page.open_preps_page()
    preps_page.take_screenshot_report("preps_test_page_load")
    print("Result: test_preps_page_load passed")


@pytest.mark.prep
@pytest.mark.smoke
def test_prep_card_and_buttons_visible(page, base_url):
    """Existing prep card is visible and 3 action buttons are visible."""
    print("Test: test_prep_card_and_buttons_visible")
    _ensure_dashboard_same_as_login_test(page, base_url)
    preps_page = PrepsPage(page, base_url)
    preps_page.open_preps_page()
    preps_page.verify_first_jd_card_buttons(timeout_ms=30_000)
    preps_page.take_screenshot_report("preps_test_card_and_buttons_visible")
    print("Result: test_prep_card_and_buttons_visible passed")


@pytest.mark.prep
@pytest.mark.smoke
def test_prep_first_icon_click(page, base_url):
    """Click first prep card action icon and verify flow recovers to Preps page."""
    print("Test: test_prep_first_icon_click")
    preps_page = _open_preps_page_with_card(page, base_url)
    before = page.url or ""
    preps_page.click_first_card_action_by_index(0, timeout_ms=30_000)
    _recover_to_preps(page, preps_page, before)
    preps_page.take_screenshot_report("preps_test_action_button_1_clicked")
    print("Result: test_prep_first_icon_click passed")


@pytest.mark.prep
@pytest.mark.smoke
def test_prep_second_icon_click(page, base_url):
    """Click second prep card action icon and verify flow recovers to Preps page."""
    print("Test: test_prep_second_icon_click")
    preps_page = _open_preps_page_with_card(page, base_url)
    before = page.url or ""
    preps_page.click_first_card_action_by_index(1, timeout_ms=30_000)
    _recover_to_preps(page, preps_page, before)
    preps_page.take_screenshot_report("preps_test_action_button_2_clicked")
    print("Result: test_prep_second_icon_click passed")


@pytest.mark.prep
@pytest.mark.smoke
def test_prep_third_icon_click(page, base_url):
    """Click third prep card action icon and verify delete confirm is safely dismissed."""
    print("Test: test_prep_third_icon_click")
    preps_page = _open_preps_page_with_card(page, base_url)
    preps_page.click_first_card_action_by_index(2, timeout_ms=30_000)
    page.wait_for_timeout(800)
    preps_page.cancel_delete_if_present(timeout_ms=5_000)
    preps_page.dismiss_open_panel_or_dialog(timeout_ms=3_000)
    if "/preps" not in (page.url or "").lower():
        preps_page.go_back_to_preps_page()
    preps_page.take_screenshot_report("preps_test_action_button_3_clicked")
    print("Result: test_prep_third_icon_click passed")
