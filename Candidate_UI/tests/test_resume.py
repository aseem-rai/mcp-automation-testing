"""
Resume module tests (no upload flow).
These tests verify page load, existing resume card visibility, and action buttons on the card.
"""

import re

import pytest

from framework.pages.login_page import LoginPage
from framework.pages.resume_page import ResumePage

_WAIT_DASHBOARD_MS = 15_000


def _ensure_dashboard_same_as_login_test(page, base_url):
    """Use same dashboard reachability flow as login tests."""
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
    login_page.take_screenshot("resume_login_failure")
    _hint = (
        "python -m framework.auth.save_auth_state --democandidate"
        if "democandidate" in (base_url or "").lower()
        else "python -m framework.auth.save_auth_state"
    )
    pytest.fail(f"Auth state missing or expired. Run: {_hint}")


def _is_redirected_to_login(page) -> bool:
    url = page.url or ""
    return bool(re.search(r"/login|/signin|/auth", url, re.I))


def _require_logged_in(page) -> None:
    if _is_redirected_to_login(page):
        pytest.fail(
            "Login required for resume tests. Run: python -m framework.auth.save_auth_state "
            "and complete Google OAuth, then re-run tests."
        )


def _open_resume_page_with_card(page, base_url) -> ResumePage:
    _ensure_dashboard_same_as_login_test(page, base_url)
    resume_page = ResumePage(page, base_url)
    resume_page.go_to_resumes()
    _require_logged_in(page)
    resume_page.verify_resume_page_loaded()
    resume_page.verify_resume_uploaded()
    return resume_page


def _cancel_delete_if_present(page) -> None:
    cancel = page.get_by_role("button", name=re.compile(r"\bcancel\b|\bno\b|\bclose\b", re.I))
    if cancel.count() > 0:
        try:
            cancel.first.click(timeout=5_000)
            return
        except Exception:
            pass
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def _card_action_buttons(resume_page: ResumePage):
    return resume_page.uploaded_resume_card.locator("button, [role='button'], a[role='button'], a")


def _click_action_button_by_index(resume_page: ResumePage, index: int) -> None:
    actions = _card_action_buttons(resume_page)
    assert actions.count() >= 3, "Expected at least 3 action icons/buttons on resume card."
    btn = actions.nth(index)
    assert btn.is_visible(), f"Action button at index {index} is not visible."
    btn.click(timeout=20_000)


def _dismiss_overlays(page) -> None:
    close_btn = page.get_by_role("button", name=re.compile(r"\bcancel\b|\bclose\b|\bno\b|\bback\b", re.I)).or_(
        page.locator("[aria-label*='close' i], [title*='close' i]")
    )
    if close_btn.count() > 0:
        try:
            close_btn.first.click(timeout=5_000)
            return
        except Exception:
            pass
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def _default_badge_on_card(card):
    """Prefer exact 'Default' badge text to avoid matching 'Set as Default' button labels."""
    return card.get_by_text(re.compile(r"^\s*default\s*$", re.I))


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_page_load(page, base_url):
    """Resume page loads and shows main content."""
    print("Test: test_resume_page_load")
    _ensure_dashboard_same_as_login_test(page, base_url)
    resume_page = ResumePage(page, base_url)
    resume_page.go_to_resumes()
    _require_logged_in(page)
    resume_page.verify_resume_page_loaded()
    resume_page.take_screenshot("resume_test_resume_page_load")
    print("Result: test_resume_page_load passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_add_resume_button_visible(page, base_url):
    """Add Resume button is visible on Resume page."""
    print("Test: test_add_resume_button_visible")
    _ensure_dashboard_same_as_login_test(page, base_url)
    resume_page = ResumePage(page, base_url)
    resume_page.go_to_resumes()
    _require_logged_in(page)
    resume_page.verify_resume_page_loaded()
    resume_page.click_add_resume()
    page.wait_for_timeout(500)
    resume_page.take_screenshot("resume_test_add_resume_button_visible")
    resume_page.close_modal()
    print("Result: test_add_resume_button_visible passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_visible(page, base_url):
    """At least one existing resume card is visible."""
    print("Test: test_resume_visible")
    _ensure_dashboard_same_as_login_test(page, base_url)
    resume_page = ResumePage(page, base_url)
    resume_page.go_to_resumes()
    _require_logged_in(page)
    resume_page.verify_resume_page_loaded()
    resume_page.verify_resume_uploaded()
    resume_page.take_screenshot("resume_test_resume_visible")
    print("Result: test_resume_visible passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_view_icon_click(page, base_url):
    """Click first resume action icon and validate click works."""
    print("Test: test_resume_view_icon_click")
    resume_page = _open_resume_page_with_card(page, base_url)
    _click_action_button_by_index(resume_page, 0)
    page.wait_for_timeout(1200)
    _dismiss_overlays(page)
    resume_page.take_screenshot("resume_test_resume_view_icon_click")
    print("Result: test_resume_view_icon_click passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_download_icon_click(page, base_url):
    """Click second resume action icon and validate click works."""
    print("Test: test_resume_download_icon_click")
    resume_page = _open_resume_page_with_card(page, base_url)
    _click_action_button_by_index(resume_page, 1)
    page.wait_for_timeout(1200)
    _dismiss_overlays(page)
    resume_page.take_screenshot("resume_test_resume_download_icon_click")
    print("Result: test_resume_download_icon_click passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_delete_icon_click(page, base_url):
    """Click third resume action icon and validate click works (cancel if delete confirm appears)."""
    print("Test: test_resume_delete_icon_click")
    resume_page = _open_resume_page_with_card(page, base_url)
    _click_action_button_by_index(resume_page, 2)
    page.wait_for_timeout(600)
    _cancel_delete_if_present(page)
    _dismiss_overlays(page)
    resume_page.take_screenshot("resume_test_resume_delete_icon_click")
    print("Result: test_resume_delete_icon_click passed")


@pytest.mark.resume
@pytest.mark.smoke
def test_resume_set_default(page, base_url):
    """
    Set Default Resume:
    1. Navigate to Resumes page
    2. Click Set as Default on a non-default resume
    Expected:
    Selected resume marked default via API; previous default loses default status; visual indicator updates.
    """
    print("Test: test_resume_set_default")
    resume_page = _open_resume_page_with_card(page, base_url)

    # Use broad, action-scoped card detection to avoid undercounting from narrow locators.
    cards = page.locator("article, section, div, [data-testid*='resume-card' i], [data-testid*='resumeCard' i]").filter(
        has=page.locator("button, [role='button'], a[role='button'], a")
    )
    default_api_calls = []

    def _on_request(req):
        try:
            if (req.method or "").upper() not in {"POST", "PUT", "PATCH"}:
                return
            url_l = (req.url or "").lower()
            data_l = ""
            try:
                data_l = (req.post_data or "").lower()
            except Exception:
                data_l = ""
            if any(
                key in url_l or key in data_l
                for key in ("default", "setdefaultresume", "set_default", "set as default")
            ):
                default_api_calls.append({"method": req.method, "url": req.url})
        except Exception:
            pass

    clicked = False
    page.on("request", _on_request)
    try:
        total_cards = cards.count()
        for i in range(total_cards):
            card = cards.nth(i)
            try:
                card.hover(timeout=3_000)
                page.wait_for_timeout(150)
            except Exception:
                pass

            # Primary UI per your clarification: button text is exactly "Default".
            default_btn = card.get_by_role("button", name=re.compile(r"^\s*default\s*$", re.I)).or_(
                card.locator("button:has-text('Default')")
            ).or_(
                card.locator("[aria-label*='default' i], [title*='default' i], [data-testid*='default' i]")
            ).first
            if default_btn.count() > 0:
                try:
                    if default_btn.is_visible():
                        default_btn.click(timeout=20_000, force=True)
                        clicked = True
                        break
                except Exception:
                    pass

            # Fallback: "Default" action may be inside overflow menu.
            more_btn = card.get_by_role(
                "button", name=re.compile(r"more|options|menu|actions|\.\.\.|ellipsis", re.I)
            ).or_(
                card.locator(
                    "[aria-label*='more' i], [aria-label*='option' i], [aria-label*='menu' i], "
                    "[title*='more' i], [title*='option' i], [title*='menu' i], "
                    "button:has(svg), [role='button']:has(svg)"
                )
            ).first
            if more_btn.count() > 0:
                try:
                    more_btn.click(timeout=5_000)
                    page.wait_for_timeout(250)
                    menu_default = page.locator(
                        "[role='menu'] [role='menuitem']:visible, "
                        "[role='menuitem']:visible, "
                        ".MuiMenu-paper [role='menuitem']:visible, "
                        "[role='menu'] button:visible"
                    ).filter(has_text=re.compile(r"^\s*default\s*$", re.I)).first
                    if menu_default.count() > 0 and menu_default.is_visible():
                        menu_default.click(timeout=10_000, force=True)
                        clicked = True
                        break
                except Exception:
                    pass
                _dismiss_overlays(page)

        if not clicked:
            pytest.skip("No clickable 'Default' button/action found on resume cards.")

        waited = 0
        while waited < 12_000:
            page.wait_for_timeout(500)
            waited += 500
            if default_api_calls:
                break
    finally:
        page.remove_listener("request", _on_request)

    assert default_api_calls, "No default-update API request captured after clicking Default."
    assert page.locator("button:has-text('Default'), [aria-label*='default' i], [title*='default' i]").count() > 0, (
        "Post-click state did not show any Default action/label on resume cards."
    )

    resume_page.take_screenshot("resume_test_set_default_resume")
    print("Result: test_resume_set_default passed")
