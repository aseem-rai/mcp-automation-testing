from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object for /dashboard.

    Notes:
    - Selectors are intentionally resilient (role/text-first, limited CSS).
    - Methods verify *visible UI signals* rather than brittle DOM structure.
    """

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators (selectors)
    # -----------------------
    def _sidebar_item(self, name_regex: re.Pattern[str]) -> Locator:
        # Sidebar items are usually links; allow button-based nav too.
        return self.page.get_by_role("link", name=name_regex).or_(
            self.page.get_by_role("button", name=name_regex)
        )

    @property
    def welcome_back_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I))

    @property
    def sidebar(self) -> Locator:
        # Try common semantic containers first, then fall back to a left-side nav-ish region.
        return self.page.locator("aside, nav").first

    @property
    def dashboard_menu_item(self) -> Locator:
        # Prefer role-based matching if the app uses links/buttons.
        link = self.page.get_by_role("link", name=re.compile(r"^\s*dashboard\s*$", re.I))
        btn = self.page.get_by_role("button", name=re.compile(r"^\s*dashboard\s*$", re.I))
        return link.or_(btn)

    @property
    def stats_total_activities(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+activities\b", re.I))

    @property
    def stats_cards_generic(self) -> Locator:
        # Generic "card-like" blocks; used as a fallback if exact labels differ.
        return self.page.locator(
            "section >> text=/total|activities|candidates|applied|shortlisted|interviews/i"
        )

    @property
    def stats_cards(self) -> Locator:
        # Prefer explicit label, else any stats-like content on the dashboard.
        explicit = self.stats_total_activities
        return explicit.or_(self.stats_cards_generic)

    # -----------------------
    # Actions / Assertions
    # -----------------------
    def load(self) -> None:
        self.goto("/dashboard", wait_until="domcontentloaded")

    def verify_loaded(self, timeout_ms: int = 15_000) -> None:
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        self.welcome_back_text.first.wait_for(state="visible", timeout=timeout_ms)
        # Ensure we have some stats cards visible.
        self.stats_cards.first.wait_for(state="visible", timeout=timeout_ms)

    def verify_sidebar(self, timeout_ms: int = 15_000) -> None:
        self.sidebar.wait_for(state="visible", timeout=timeout_ms)
        # Ensure the sidebar includes a Dashboard nav item.
        self.dashboard_menu_item.first.wait_for(state="visible", timeout=timeout_ms)

    def verify_stats_cards(self, timeout_ms: int = 15_000) -> None:
        # Prefer explicit "Total Activities", otherwise accept any stats-like signals.
        if self.stats_total_activities.count() > 0:
            self.stats_total_activities.first.wait_for(state="visible", timeout=timeout_ms)
            return

        # Fallback: look for some common stats-ish text on the dashboard.
        self.stats_cards_generic.first.wait_for(state="visible", timeout=timeout_ms)

    def safe_click(self, locator: Locator, timeout_ms: int = 10_000) -> None:
        """
        Click a locator safely:
        - wait visible
        - scroll into view
        - click
        - wait briefly for navigation / UI stabilization
        """
        locator.first.wait_for(state="visible", timeout=timeout_ms)
        try:
            locator.first.scroll_into_view_if_needed(timeout=timeout_ms)
        except Exception:
            pass

        before_url = self.page.url
        try:
            locator.first.click(timeout=timeout_ms)
        except Exception:
            # If a click is intercepted by overlays, try force as last resort.
            locator.first.click(timeout=timeout_ms, force=True)

        # Try to detect navigation; SPAs may not trigger full load events.
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass

        # If URL didn't change, still allow short settle for UI updates.
        if self.page.url == before_url:
            self.page.wait_for_timeout(500)

    def click_resumes_sidebar(self) -> None:
        self.safe_click(self._sidebar_item(re.compile(r"\bresumes?\b", re.I)))

    def click_profile_sidebar(self) -> None:
        self.safe_click(self._sidebar_item(re.compile(r"^\s*profile\s*$", re.I)))

    def take_screenshot(self, name: str) -> Path:
        screenshots_dir = Path("results") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "screenshot"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = screenshots_dir / f"{safe}_{ts}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

