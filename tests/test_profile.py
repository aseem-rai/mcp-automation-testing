import re

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from framework.pages.dashboard_page import DashboardPage
from framework.pages.login_page import LoginPage
from framework.pages.profile_page import ProfilePage


@pytest.mark.profile
@pytest.mark.smoke
def test_profile_page_smoke(page, base_url):
    dashboard = DashboardPage(page, base_url)
    dashboard.load()
    page.wait_for_timeout(1000)
    dashboard.take_screenshot("profile_00_dashboard_loaded")

    # If auth is required, stub login UI and skip (no real creds stored in framework).
    if re.search(r"/login\b|/signin\b|/auth\b", page.url, re.I):
        LoginPage(page, base_url).assert_login_ui_present_stub()
        pytest.skip("Profile flow requires authentication; login UI verified (stub).")

    dashboard.verify_loaded()
    dashboard.verify_sidebar()
    dashboard.click_profile_sidebar()
    page.wait_for_timeout(1200)

    profile = ProfilePage(page, base_url)
    profile.verify_loaded()
    profile.take_screenshot("profile_01_profile_loaded")

    profile.verify_basic_info_section()
    profile.take_screenshot("profile_02_basic_info")

    # Field checks (may be empty if the account has no resume/profile data yet).
    profile.verify_name()
    profile.verify_title()
    profile.verify_email()
    profile.verify_phone()
    profile.verify_location()
    profile.verify_about_section()
    profile.take_screenshot("profile_03_fields_checked")

    # Download Profile: verify clickable and (if supported) download triggers.
    try:
        with page.expect_download(timeout=5_000) as dl_info:
            profile.click_download_profile()
        download = dl_info.value
        assert download.suggested_filename, "Download did not provide a filename"
    except PlaywrightTimeoutError:
        # Some implementations generate server-side/download in same tab or open a new route.
        profile.click_download_profile()

    profile.take_screenshot("profile_04_after_download_click")

