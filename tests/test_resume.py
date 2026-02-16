import re

import pytest

from framework.pages.dashboard_page import DashboardPage
from framework.pages.login_page import LoginPage
from framework.pages.resume_page import ResumePage


@pytest.mark.resume
@pytest.mark.smoke
def test_resumes_add_new_resume_modal_validation(page, base_url):
    """
    Flow:
    Dashboard -> Resumes -> Resume page -> Add New Resume modal
    Validates required fields and button disabled behavior.
    """
    dashboard = DashboardPage(page, base_url)
    dashboard.load()
    page.wait_for_timeout(1000)
    dashboard.take_screenshot("resume_00_dashboard_loaded")

    # If auth is required, stub login UI and skip (no real creds stored in framework).
    if re.search(r"/login\b|/signin\b|/auth\b", page.url, re.I):
        LoginPage(page, base_url).assert_login_ui_present_stub()
        pytest.skip("Resumes flow requires authentication; login UI verified (stub).")

    # Navigate to Resumes from sidebar.
    dashboard.verify_loaded()
    dashboard.verify_sidebar()
    dashboard.click_resumes_sidebar()
    page.wait_for_timeout(1200)

    resumes = ResumePage(page, base_url)
    resumes.verify_loaded()
    resumes.take_screenshot("resume_01_resumes_page_loaded")

    resumes.verify_resume_cards_present()
    resumes.take_screenshot("resume_02_resume_cards")

    resumes.click_add_new_resume()
    resumes.verify_add_resume_modal_open()
    resumes.take_screenshot("resume_03_add_resume_modal_open")

    # Validate mandatory fields presence.
    resumes.verify_target_role_field()
    resumes.verify_resume_upload_field()
    resumes.take_screenshot("resume_04_modal_fields_present")

    # Verify Add Resume disabled when empty (or validation triggers on click).
    resumes.verify_add_resume_button_disabled_when_empty()

    # Trigger validation messages (best effort) by focusing/blur fields.
    try:
        resumes.target_role_field.click()
        page.keyboard.press("Tab")
    except Exception:
        pass
    page.wait_for_timeout(300)

    # Ensure required/validation feedback exists (page shows "Target role is required", "Resume file is required", etc.)
    assert resumes.error_messages.count() > 0, "Expected validation/error messages to be visible"

    resumes.take_screenshot("resume_05_validation_state")

    resumes.close_modal()
    page.wait_for_timeout(500)
    resumes.take_screenshot("resume_06_modal_closed")

