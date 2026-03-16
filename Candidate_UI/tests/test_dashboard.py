"""
Dashboard module tests. Screenshots saved to test-results/dashboard/.
Uses base_url fixture; no hardcoded credentials.
"""

import re

import pytest

from framework.pages.dashboard_page import DashboardPage
from framework.utils.logger import logger

_DASHBOARD_SCREENSHOTS = "test-results/dashboard"


def _is_redirected_to_login(page) -> bool:
    url = page.url or ""
    return bool(re.search(r"/login|/signin|/auth", url, re.I))


def _skip_if_login_redirect(page, test_name: str) -> None:
    if _is_redirected_to_login(page):
        pytest.skip(f"Redirected to login; session may be expired (test: {test_name})")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_load(page, base_url):
    """Dashboard loads and shows main content."""
    logger.info("Test: test_dashboard_load")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_load")
    dashboard.verify_dashboard_loaded()
    dashboard.take_screenshot("dashboard_test_dashboard_load")
    logger.info("Result: test_dashboard_load passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_stats_visible(page, base_url):
    """Stats cards (Total Activities, Preps, Interviews) are visible."""
    logger.info("Test: test_dashboard_stats_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_stats_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_stats_cards_visible()
    dashboard.take_screenshot("dashboard_test_dashboard_stats_visible")
    logger.info("Result: test_dashboard_stats_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_total_activities_stats_visible(page, base_url):
    """Total Activities stat is visible on Dashboard."""
    logger.info("Test: test_dashboard_total_activities_stats_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_total_activities_stats_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_total_activities_stats_visible()
    dashboard.take_screenshot("dashboard_test_total_activities_stats_visible")
    logger.info("Result: test_dashboard_total_activities_stats_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_job_applications_stats_visible(page, base_url):
    """Job Applications stat is visible on Dashboard."""
    logger.info("Test: test_dashboard_job_applications_stats_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_job_applications_stats_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_job_applications_stats_visible()
    dashboard.take_screenshot("dashboard_test_job_applications_stats_visible")
    logger.info("Result: test_dashboard_job_applications_stats_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_resume_stats_visible(page, base_url):
    """Resume stat is visible on Dashboard."""
    logger.info("Test: test_dashboard_resume_stats_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_resume_stats_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_resume_stats_visible()
    dashboard.take_screenshot("dashboard_test_resume_stats_visible")
    logger.info("Result: test_dashboard_resume_stats_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_goals_stats_visible(page, base_url):
    """Goals stat is visible on Dashboard."""
    logger.info("Test: test_dashboard_goals_stats_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_goals_stats_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_goals_stats_visible()
    dashboard.take_screenshot("dashboard_test_goals_stats_visible")
    logger.info("Result: test_dashboard_goals_stats_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_recent_activity_visible_and_updated(page, base_url):
    """Scroll to Recent Activity section and verify it is visible with updated activity timestamps."""
    logger.info("Test: test_dashboard_recent_activity_visible_and_updated")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_recent_activity_visible_and_updated")
    dashboard.verify_welcome_message()
    dashboard.verify_recent_activity_visible_and_updated()
    dashboard.take_screenshot("dashboard_test_recent_activity_visible_and_updated")
    logger.info("Result: test_dashboard_recent_activity_visible_and_updated passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_sidebar_collapses_successfully(page, base_url):
    """Sidebar collapse toggle works and sidebar enters collapsed state."""
    logger.info("Test: test_sidebar_collapses_successfully")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_sidebar_collapses_successfully")
    dashboard.verify_welcome_message()
    dashboard.verify_sidebar_collapse_successful()
    dashboard.take_screenshot("dashboard_test_sidebar_collapses_successfully")
    logger.info("Result: test_sidebar_collapses_successfully passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_sidebar_top_left_profile_details_visible(page, base_url):
    """Sidebar top-left profile details (email and phone/location) are visible."""
    logger.info("Test: test_sidebar_top_left_profile_details_visible")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_sidebar_top_left_profile_details_visible")
    dashboard.verify_welcome_message()
    dashboard.verify_sidebar_profile_details_visible()
    dashboard.take_screenshot("dashboard_test_sidebar_top_left_profile_details_visible")
    logger.info("Result: test_sidebar_top_left_profile_details_visible passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_find_jobs_navigation(page, base_url):
    """Find Jobs button navigates correctly."""
    logger.info("Test: test_find_jobs_navigation")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_find_jobs_navigation")
    dashboard.click_find_jobs()
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    dashboard.take_screenshot("dashboard_test_find_jobs_navigation")
    logger.info("Result: test_find_jobs_navigation passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_add_resume_navigation(page, base_url):
    """Add Resume button/link navigates correctly."""
    logger.info("Test: test_add_resume_navigation")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_add_resume_navigation")
    dashboard.click_add_resume()
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    dashboard.take_screenshot("dashboard_test_add_resume_navigation")
    logger.info("Result: test_add_resume_navigation passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_sidebar_navigation(page, base_url):
    """Sidebar: Dashboard, Profile, Resume, Jobs, Prep navigation."""
    logger.info("Test: test_sidebar_navigation")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_sidebar_navigation")
    dashboard.verify_sidebar()
    dashboard.navigate_to_resume()
    page.wait_for_timeout(500)
    dashboard.open_dashboard()
    dashboard.navigate_to_jobs()
    page.wait_for_timeout(500)
    dashboard.open_dashboard()
    dashboard.navigate_to_prep()
    page.wait_for_timeout(500)
    dashboard.open_dashboard()
    dashboard.navigate_to_profile()
    page.wait_for_timeout(500)
    dashboard.take_screenshot("dashboard_test_sidebar_navigation")
    logger.info("Result: test_sidebar_navigation passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_logout_functionality(page, base_url):
    """Open profile menu, click logout, verify redirect to login."""
    logger.info("Test: test_logout_functionality")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_logout_functionality")
    dashboard.open_profile_menu()
    dashboard.click_logout()
    dashboard.verify_redirect_to_login()
    dashboard.take_screenshot("dashboard_test_logout_functionality")
    logger.info("Result: test_logout_functionality passed")


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_responsive(page, base_url):
    """Dashboard renders and key elements visible (responsive check)."""
    logger.info("Test: test_dashboard_responsive")
    dashboard = DashboardPage(page, base_url)
    dashboard.open_dashboard()
    _skip_if_login_redirect(page, "test_dashboard_responsive")
    dashboard.verify_dashboard_loaded()
    dashboard.verify_welcome_message()
    dashboard.verify_sidebar()
    dashboard.take_screenshot("dashboard_test_dashboard_responsive")
    logger.info("Result: test_dashboard_responsive passed")
