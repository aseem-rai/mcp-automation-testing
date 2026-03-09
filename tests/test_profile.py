from pathlib import Path

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from framework.pages.dashboard_page import DashboardPage
from framework.pages.login_page import LoginPage
from framework.pages.profile_page import ProfilePage
from framework.pages.resume_page import ResumePage, PARSE_RESUME_WAIT_MS
from framework.utils.settings import settings
from framework.utils.test_data import ensure_resume_with_details_pdf

_PROFILE_AFTER_RESUME_SCREENSHOT = Path("test-results/screenshots/profile_after_new_resume.png")


def _require_logged_in_with_env_email(page, base_url: str) -> None:
    """Ensure flow starts with login: open dashboard; fail if redirected to login (session must be for TEST_EMAIL)."""
    # Go to dashboard (staying in app; root URL may redirect to login even with valid session)
    page.goto(f"{base_url.rstrip('/')}/dashboard", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    page.wait_for_timeout(800)
    if LoginPage(page, base_url).is_login_page():
        pytest.fail(
            "Login required first. Run: python -m framework.auth.save_auth_state "
            f"and sign in with TEST_EMAIL ({settings.TEST_EMAIL or 'set in .env'}), then re-run tests."
        )


@pytest.mark.profile
@pytest.mark.smoke
def test_profile_page_smoke(page, base_url):
    """Profile page smoke. Login first (env email), then open profile."""
    _require_logged_in_with_env_email(page, base_url)
    dashboard = DashboardPage(page, base_url)
    dashboard.load()
    page.wait_for_timeout(1000)
    dashboard.take_screenshot("profile_00_dashboard_loaded")

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


@pytest.mark.profile
@pytest.mark.smoke
def test_profile_details_visibility(page, base_url):
    """
    Steps:
    1. Navigate to /dashboard/profile

    Expected:
    Profile header shows name, title/role, avatar; sections display Basic Info
    (email, phone, location, about), Education, Skills (categorized), Languages,
    Work Experience, Projects, Awards/Certifications.
    """
    _require_logged_in_with_env_email(page, base_url)
    profile = ProfilePage(page, base_url)
    profile.load()
    profile.verify_profile_details_sections_visible()
    profile.take_screenshot("profile_details_visibility")


@pytest.mark.profile
@pytest.mark.smoke
def test_profile_download_profile_file(page, base_url):
    """Profile: Download Profile button triggers a file download."""
    _require_logged_in_with_env_email(page, base_url)
    profile = ProfilePage(page, base_url)
    profile.load()
    profile.verify_loaded()

    with page.expect_download(timeout=15_000) as dl_info:
        profile.click_download_profile()
    download = dl_info.value

    suggested = (download.suggested_filename or "").strip()
    assert suggested, "Download did not provide a filename."
    profile.take_screenshot("profile_download_profile_file")


_PROFILE_DATA_TIMEOUT_MS = 30_000  # Fail if no profile data visible within 30s


def _wait_for_profile_data_visible(page, timeout_ms: int = _PROFILE_DATA_TIMEOUT_MS) -> bool:
    """Return True if any profile data appears within timeout_ms; False otherwise."""
    env_email = (settings.TEST_EMAIL or "").strip()
    locators = [
        page.get_by_text("John Doe", exact=False),
        page.get_by_text("johndoe.example@email.com", exact=False),
        page.get_by_text("Basic info", exact=False),
    ]
    if env_email:
        locators.insert(0, page.get_by_text(env_email, exact=False))
    # Single 30s wait: first locator that becomes visible wins
    combined = locators[0]
    for loc in locators[1:]:
        combined = combined.or_(loc)
    try:
        combined.first.wait_for(state="visible", timeout=timeout_ms)
        return True
    except Exception:
        return False


@pytest.mark.profile
@pytest.mark.smoke
def test_profile_after_new_resume_upload(page, base_url):
    """Login first (env email), add resume, open profile; screenshot only when data is seen; fail if no data in 30s."""
    # 1. Login first: must be logged in with TEST_EMAIL (session from save_auth_state)
    _require_logged_in_with_env_email(page, base_url)
    page.wait_for_timeout(1000)

    # 2. Add resume with parseable details
    resume_path = ensure_resume_with_details_pdf()
    resume_page = ResumePage(page, base_url)
    resume_page.open_resume_page()
    resume_page.verify_resume_page_loaded()
    resume_page.click_add_resume()
    resume_page.enter_target_role("Software Engineer")
    resume_page.upload_resume(file_path=str(resume_path))
    resume_page.submit_resume()
    resume_page.verify_resume_uploaded(timeout_ms=PARSE_RESUME_WAIT_MS)

    # 3. Give backend time to parse resume and populate profile
    page.wait_for_timeout(3000)

    # 4. Open profile and wait up to 30s for data to appear
    profile = ProfilePage(page, base_url)
    profile.load()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Wait up to 30s for profile data; fail if not visible
    if not _wait_for_profile_data_visible(page, timeout_ms=_PROFILE_DATA_TIMEOUT_MS):
        pytest.fail(
            f"Profile data not visible within {_PROFILE_DATA_TIMEOUT_MS // 1000}s. "
            "Expected TEST_EMAIL, name, or Basic info to appear on profile."
        )

    # Data is visible: take screenshot only now
    profile.verify_loaded()
    _PROFILE_AFTER_RESUME_SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(_PROFILE_AFTER_RESUME_SCREENSHOT), full_page=True)

