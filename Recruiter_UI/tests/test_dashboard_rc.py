"""
Recruiter dashboard tests. Require login (use auth or run after login test).
Login lands on https://demohire.meetaiva.in/Jobs — we check for 4 insight cards on that page.
"""

from __future__ import annotations

import pytest

from framework.pages.dashboard_page import DashboardPage
from framework.pages.login_page import LoginPage


@pytest.mark.dashboard
@pytest.mark.smoke
def test_dashboard_four_insight_cards_visible(logged_in_page, base_url):
    """
    Verify the page shows 4 insight cards. Login leads to /Jobs; we assert on the current page.
    Login runs before every test (ensure_google_sign_in, like Candidate_UI).
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_dashboard_rc is for demohire base_url. Current: {base_url!r}")

    # After login we are on /Jobs (https://demohire.meetaiva.in/Jobs). Do not navigate away.
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(3000)  # let insight cards render
    logged_in_page.evaluate("window.scrollTo(0, 0)")
    logged_in_page.wait_for_timeout(1000)

    dashboard = DashboardPage(logged_in_page, base_url)
    assert dashboard.are_four_insight_cards_visible(timeout_ms=20_000), (
        f"Expected 4 insight/stat cards on page (URL: {logged_in_page.url}); "
        f"stat cards: {dashboard.get_stat_card_count()}, other cards: {dashboard.get_insight_card_count()}."
    )
