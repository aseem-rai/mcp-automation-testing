from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Recruiter dashboard page. Assumes already on dashboard (post-login)."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    @property
    def stat_cards(self) -> Locator:
        """Locator for the 4 stat cards on dashboard/Jobs page (statistics widgets)."""
        return self.page.locator(
            "[class*='stat'], [class*='Stat'], [data-testid*='stat'], [data-testid*='Stat'], "
            "[aria-label*='stat' i], [id*='stat'], "
            "[class*='Paper'], [class*='MuiPaper'], [class*='card'], [class*='Card']"
        )

    @property
    def insight_cards(self) -> Locator:
        """Locator for insight/stat cards (dashboard metric widgets). Includes stat cards."""
        return self.page.locator(
            "[class*='insight'], [data-testid*='insight'], [aria-label*='insight' i], "
            "[id*='insight'], [class*='Insight'], "
            "[class*='card'], [data-testid*='card'], [class*='Card'], "
            "[class*='stat'], [class*='Stat'], [class*='metric'], [data-testid*='metric']"
        ).or_(
            self.page.get_by_role("region", name=re.compile(r"insight|stat", re.I))
        ).or_(
            self.page.get_by_role("figure")
        )

    def get_insight_card_count(self) -> int:
        """Return the number of visible insight cards."""
        return self.insight_cards.count()

    def get_stat_card_count(self) -> int:
        """Return the number of visible stat cards."""
        return self.stat_cards.count()

    def are_four_stat_cards_visible(self, timeout_ms: int = 20_000) -> bool:
        """Return True if 4 stat cards are present on the page (the 4 dashboard stat cards)."""
        try:
            self.stat_cards.first.wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            return False
        count = self.stat_cards.count()
        return count >= 4

    def are_four_insight_cards_visible(self, timeout_ms: int = 20_000) -> bool:
        """Return True if at least 4 insight/stat cards are visible. Prefers stat cards when present."""
        if self.are_four_stat_cards_visible(timeout_ms=timeout_ms):
            return True
        try:
            self.insight_cards.first.wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            return False
        count = self.insight_cards.count()
        if count < 4:
            return False
        visible = sum(1 for i in range(min(count, 10)) if self.insight_cards.nth(i).is_visible())
        return visible >= 4
