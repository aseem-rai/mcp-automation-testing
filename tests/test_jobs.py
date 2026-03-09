"""
Jobs module tests. Screenshots in test-results/jobs/ as jobs_<test_name>.png.
Skip if redirected to login.
Jira: JOB-001..JOB-015.
"""

import re
from pathlib import Path

import pytest

from framework.pages.jobs_page import JobsPage
from framework.pages.login_page import LoginPage
from framework.utils.settings import settings as env_settings


def _is_redirected_to_login(page) -> bool:
    url = page.url or ""
    return bool(re.search(r"/login|/signin|/auth", url, re.I))


def _skip_if_login_redirect(page, test_name: str) -> None:
    if _is_redirected_to_login(page):
        pytest.skip("Login required")


@pytest.fixture(scope="module")
def jobs_context(browser, run_config):
    """
    Shared Jobs browser context for whole module so login happens only once.
    """
    base_url = run_config.base_url
    auth_path = None
    if "democandidate" in (base_url or "").lower():
        demo = Path("D:/playwright-mcp/framework/auth/auth_democandidate.json")
        if demo.exists():
            auth_path = demo
    if auth_path is None:
        configured = Path(env_settings.AUTH_STATE) if env_settings.AUTH_STATE else Path("")
        if configured and not configured.is_absolute():
            configured = Path("D:/playwright-mcp") / configured
        if configured and configured.exists():
            auth_path = configured

    context_opts = {"ignore_https_errors": run_config.ignore_https_errors}
    if auth_path is not None:
        context_opts["storage_state"] = str(auth_path.resolve())
    context = browser.new_context(**context_opts)
    login_page_obj = context.new_page()
    login_page_obj.goto(base_url, wait_until="domcontentloaded")

    # Login once for entire jobs module.
    login_page = LoginPage(login_page_obj, base_url)
    login_page_obj.wait_for_load_state("domcontentloaded", timeout=15_000)
    try:
        login_page_obj.wait_for_url("**/dashboard**", timeout=15_000)
    except Exception:
        pass
    if not login_page.do_google_sign_in_if_needed(timeout_ms=90_000):
        if login_page.is_login_page():
            pytest.fail(
                "Google sign-in did not reach dashboard for jobs module. "
                "Run: python -m framework.auth.save_auth_state --democandidate"
            )

    # Keep logged-in storage/cookies in this context; close setup tab.
    try:
        login_page_obj.close()
    except Exception:
        pass

    yield context

    context.close()


@pytest.fixture(autouse=True)
def ensure_google_sign_in():
    """
    Override global per-test auto-login for this file.
    Login is handled once in the module-scoped page fixture above.
    """
    yield


@pytest.fixture
def page(jobs_context, base_url):
    """
    Fresh page per test from one already logged-in context.
    Prevents one failing test from closing page for all others.
    """
    p = jobs_context.new_page()
    p.goto(base_url, wait_until="domcontentloaded")
    yield p
    try:
        p.close()
    except Exception:
        pass


@pytest.mark.jobs
@pytest.mark.smoke
def test_jobs_page_load(page, base_url):
    """JOB-001: Jobs page load."""
    print("Test: test_jobs_page_load")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    _skip_if_login_redirect(page, "test_jobs_page_load")
    jobs.verify_jobs_page_loaded()
    jobs.take_screenshot("jobs_test_jobs_page_load")
    print("Result: test_jobs_page_load passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_search_job_popup(page, base_url):
    """JOB-002, JOB-003: Search button visible, Search popup opens."""
    print("Test: test_search_job_popup")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    _skip_if_login_redirect(page, "test_search_job_popup")
    jobs.verify_jobs_page_loaded()
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()
    jobs.take_screenshot("jobs_test_search_job_popup")
    jobs.close_search_modal()
    print("Result: test_search_job_popup passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_search_job_results(page, base_url):
    """JOB-004: Search results visible."""
    print("Test: test_search_job_results")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    _skip_if_login_redirect(page, "test_search_job_results")
    jobs.verify_jobs_page_loaded()
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()
    jobs.enter_job_search_text("Python")
    jobs.submit_job_search()
    jobs.verify_search_results_visible()
    jobs.take_screenshot("jobs_test_search_job_results")
    jobs.close_search_modal()
    print("Result: test_search_job_results passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_job_card_visible(page, base_url):
    """JOB-006, JOB-013: On Jobs page, job card and card buttons are visible."""
    print("Test: test_job_card_visible")
    _skip_if_login_redirect(page, "test_job_card_visible")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    jobs.verify_jobs_page_loaded()
    jobs.verify_job_card_created()
    jobs.verify_first_job_card_buttons()
    jobs.take_screenshot("jobs_test_job_card_visible")
    print("Result: test_job_card_visible passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_job_card_click_opens_details_popup(page, base_url):
    """Click job card and verify job details popup/modal opens."""
    print("Test: test_job_card_click_opens_details_popup")
    _skip_if_login_redirect(page, "test_job_card_click_opens_details_popup")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    jobs.verify_jobs_page_loaded()
    body_text = ""
    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        body_text = ""
    if re.search(r"total\s+jobs\s*0\b", body_text, re.I):
        pytest.skip("No job cards available (Total Jobs = 0) to validate details popup.")
    jobs.verify_job_card_created()
    jobs.click_first_job_card_open_details()
    jobs.verify_job_details_popup_opened()
    jobs.take_screenshot("jobs_test_job_card_click_opens_details_popup")
    print("Result: test_job_card_click_opens_details_popup passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_job_card_fitment_score_visible(page, base_url):
    """Fitment score badge is visible on top-right of first job card."""
    print("Test: test_job_card_fitment_score_visible")
    _skip_if_login_redirect(page, "test_job_card_fitment_score_visible")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    jobs.verify_jobs_page_loaded()
    # Fitment badge exists only on actual job cards; skip if no jobs are available.
    body_text = ""
    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        body_text = ""
    if re.search(r"total\s+jobs\s*0\b", body_text, re.I):
        pytest.skip("No job cards available (Total Jobs = 0) to validate fitment score badge.")
    jobs.verify_fitment_score_visible_on_first_job_card()
    jobs.take_screenshot("jobs_test_job_card_fitment_score_visible")
    print("Result: test_job_card_fitment_score_visible passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_take_mock_interview(page, base_url):
    """JOB-007: Mock interview visible and works."""
    print("Test: test_take_mock_interview")
    _skip_if_login_redirect(page, "test_take_mock_interview")
    jobs = JobsPage(page, base_url)
    jobs.ensure_job_exists()
    jobs.click_take_mock_interview()
    jobs.verify_mock_interview_started()
    jobs.take_screenshot("jobs_test_take_mock_interview")
    print("Result: test_take_mock_interview passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_enhance_resume(page, base_url):
    """JOB-008, JOB-009: Enhance resume visible and works."""
    print("Test: test_enhance_resume")
    _skip_if_login_redirect(page, "test_enhance_resume")
    jobs = JobsPage(page, base_url)
    jobs.ensure_job_exists()
    jobs.click_enhance_resume()
    jobs.verify_resume_enhancement_started()
    jobs.take_screenshot("jobs_test_enhance_resume")
    print("Result: test_enhance_resume passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_resume_enhancer_full_flow(page, base_url):
    """
    Full flow of Resume Enhancer:
    Jobs card -> Enhance Resume (magic wand) -> loading popup -> dual pane (original/enhanced)
    -> accept suggested additions -> save -> rescore/loading -> download visible
    (test ends when download icon/button appears).
    """
    print("Test: test_resume_enhancer_full_flow")
    _skip_if_login_redirect(page, "test_resume_enhancer_full_flow")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    jobs.verify_jobs_page_loaded()
    body_text = ""
    try:
        body_text = page.locator("body").inner_text()
    except Exception:
        body_text = ""
    if re.search(r"total\s+jobs\s*0\b", body_text, re.I):
        pytest.skip("No job cards available (Total Jobs = 0) for resume enhancer full flow.")
    jobs.verify_job_card_created()

    enhancer_page = jobs.open_resume_enhancer_from_first_job_card(timeout_ms=45_000)
    jobs.verify_enhancer_loading_popup(enhancer_page, timeout_ms=45_000)
    jobs.verify_enhancer_dual_resume_view(enhancer_page, timeout_ms=60_000)
    jobs.accept_all_enhancer_suggestions(enhancer_page, timeout_ms=45_000)
    jobs.save_rescore_and_wait_download(enhancer_page, timeout_ms=120_000)
    jobs.take_screenshot("jobs_test_resume_enhancer_full_flow")
    print("Result: test_resume_enhancer_full_flow passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_delete_job(page, base_url):
    """JOB-010, JOB-011: Delete button visible and delete job works."""
    print("Test: test_delete_job")
    _skip_if_login_redirect(page, "test_delete_job")
    jobs = JobsPage(page, base_url)
    jobs.ensure_job_exists()
    jobs.click_delete_job()
    jobs.verify_job_deleted()
    jobs.take_screenshot("jobs_test_delete_job")
    print("Result: test_delete_job passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_multiple_jobs_visible(page, base_url):
    """JOB-012: Multiple jobs visible (ensure at least one, verify cards)."""
    print("Test: test_multiple_jobs_visible")
    _skip_if_login_redirect(page, "test_multiple_jobs_visible")
    jobs = JobsPage(page, base_url)
    jobs.ensure_job_exists()
    jobs.verify_job_cards_visible()
    jobs.take_screenshot("jobs_test_multiple_jobs_visible")
    print("Result: test_multiple_jobs_visible passed")


@pytest.mark.jobs
@pytest.mark.smoke
def test_jobs_page_refresh(page, base_url):
    """JOB-014, JOB-015: Navigation and refresh works."""
    print("Test: test_jobs_page_refresh")
    jobs = JobsPage(page, base_url)
    jobs.open_jobs_page()
    _skip_if_login_redirect(page, "test_jobs_page_refresh")
    jobs.verify_jobs_page_loaded()
    page.reload()
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    jobs.verify_jobs_page_loaded()
    jobs.take_screenshot("jobs_test_jobs_page_refresh")
    print("Result: test_jobs_page_refresh passed")
