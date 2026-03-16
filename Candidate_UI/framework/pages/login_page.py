"""
Login page for Google OAuth auth state flow. No email/password form filling.
Uses BASE_URL from .env via framework.utils.settings.
"""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage
from framework.utils.settings import settings

_TEST_RESULTS = Path("test-results")


class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    @property
    def welcome_back_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I))

    @property
    def google_login_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"google|sign\s+in\s+with\s+google", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"google|sign\s+in\s+with\s+google", re.I))
        ).or_(self.page.get_by_text(re.compile(r"sign\s+in\s+with\s+google|continue\s+with\s+google", re.I))).first

    def load(self) -> None:
        """Open BASE_URL and wait for redirect to dashboard or login."""
        url = settings.BASE_URL
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
        # Wait for app redirect (dashboard or login)
        try:
            self.page.wait_for_url("**/dashboard**", timeout=10_000)
        except Exception:
            try:
                self.page.wait_for_url("**/*login*", timeout=3_000)
            except Exception:
                pass
        self.page.wait_for_timeout(500)

    def is_login_page(self) -> bool:
        """Return True if URL contains 'login'."""
        try:
            return "login" in (self.page.url or "").lower()
        except Exception:
            return False

    def _dashboard_welcome_locator(self) -> Locator:
        """Locator for dashboard welcome (multiple fallbacks so we catch heading/data-testid/aria-label)."""
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I)).or_(
            self.page.get_by_role("heading", name=re.compile(r"welcome\s+back", re.I))
        ).or_(self.page.locator("[data-testid='welcome-text']")).or_(
            self.page.locator("[aria-label*='welcome' i]")
        ).first

    def is_dashboard_loaded(self) -> bool:
        """Return True if URL contains 'dashboard' OR welcome text visible."""
        try:
            if "dashboard" in (self.page.url or "").lower():
                return True
        except Exception:
            pass
        try:
            # Wait for welcome text to appear (don't require count() > 0 first; DOM may still be loading)
            self._dashboard_welcome_locator().wait_for(state="visible", timeout=15_000)
            return True
        except Exception:
            pass
        try:
            if self._dashboard_welcome_locator().is_visible():
                return True
        except Exception:
            pass
        return False

    def click_google_login_button(self) -> None:
        """Click the app's Google sign-in button (does not automate Google form)."""
        if self.google_login_button.count() > 0:
            self.google_login_button.click(timeout=10_000)

    def _fill_google_oauth_popup(self, popup: Page, timeout_ms: int) -> None:
        """
        In the Google OAuth popup: find and select demoaiva.test@gmail.com (from env),
        then enter password from TEST_PASSWORD and submit.
        """
        popup.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        popup.wait_for_timeout(2500)
        email = (settings.TEST_EMAIL or "").strip()
        password = (settings.TEST_PASSWORD or "").strip()
        if not email:
            return
        # 1) Account chooser: wait for and find demoaiva.test@gmail.com, then click it
        try:
            # Wait for Google account list / chooser to be present
            popup.wait_for_url(re.compile(r"accounts\.google\.com", re.I), timeout=15_000)
            popup.wait_for_timeout(1500)
            # Find the account by exact text (demoaiva.test@gmail.com)
            account = popup.get_by_text(email, exact=True).first
            account.wait_for(state="visible", timeout=12_000)
            account.click(timeout=10_000)
            popup.wait_for_timeout(3000)
        except Exception:
            try:
                # Fallback: partial text match (e.g. email inside a div)
                account = popup.get_by_text(re.escape(email), exact=False).first
                account.wait_for(state="visible", timeout=8_000)
                account.click(timeout=10_000)
                popup.wait_for_timeout(3000)
            except Exception:
                try:
                    # Fallback: link or div with data-email (Google sometimes uses this)
                    account = popup.locator(f'[data-email="{email}"], [data-identifier="{email}"]').first
                    if account.count() > 0:
                        account.click(timeout=10_000)
                        popup.wait_for_timeout(3000)
                except Exception:
                    pass
        # 2) If we're on email input page (no account list), fill email and Next
        try:
            email_input = popup.get_by_label(re.compile(r"email|phone|identifier", re.I)).or_(
                popup.locator('input[type="email"], input[name="identifier"]')
            ).first
            if email_input.count() > 0 and email_input.is_visible():
                email_input.fill(email, timeout=10_000)
                popup.wait_for_timeout(500)
                next_btn = popup.get_by_role("button", name=re.compile(r"next|continue", re.I)).first
                if next_btn.count() > 0:
                    next_btn.click(timeout=10_000)
                popup.wait_for_timeout(3000)
        except Exception:
            pass
        # 3) Password: fill TEST_PASSWORD and Next
        if password:
            try:
                pwd_input = popup.get_by_label(re.compile(r"password|passwd", re.I)).or_(
                    popup.locator('input[type="password"], input[name="password"]')
                ).first
                if pwd_input.count() > 0 and pwd_input.is_visible():
                    pwd_input.fill(password, timeout=10_000)
                    popup.wait_for_timeout(500)
                    next_btn = popup.get_by_role("button", name=re.compile(r"next|continue", re.I)).first
                    if next_btn.count() > 0:
                        next_btn.click(timeout=10_000)
                    popup.wait_for_timeout(3000)
            except Exception:
                pass
        # 4) Consent: Continue / Allow
        try:
            consent = popup.get_by_role("button", name=re.compile(r"continue|allow|accept", re.I)).first
            if consent.count() > 0 and consent.is_visible():
                consent.click(timeout=5_000)
                popup.wait_for_timeout(2000)
        except Exception:
            pass

    def do_google_sign_in_if_needed(self, timeout_ms: int = 30_000) -> bool:
        """
        If not on dashboard, click Sign in with Google (when visible). OAuth opens in a popup —
        fill popup: select demoaiva.test@gmail.com (from env), type password, then wait for popup to close.
        """
        if self.is_dashboard_loaded():
            return True
        try:
            if self.google_login_button.count() > 0 and self.google_login_button.first.is_visible():
                # OAuth opens in a popup: capture it, fill account + password, then wait for close
                with self.page.expect_popup(timeout=15_000) as popup_info:
                    self.click_google_login_button()
                popup = popup_info.value
                try:
                    self._fill_google_oauth_popup(popup, timeout_ms=30_000)
                except Exception:
                    pass
                try:
                    popup.wait_for_event("close", timeout=timeout_ms)
                except Exception:
                    try:
                        popup.close()
                    except Exception:
                        pass
                self.page.wait_for_timeout(2000)
            # Main page should now show dashboard (or redirect to it)
            try:
                self.page.wait_for_url(re.compile(r".*dashboard.*", re.I), timeout=min(30_000, timeout_ms))
                return True
            except Exception:
                pass
            elapsed = 0
            step_ms = 2000
            while elapsed < timeout_ms:
                if self.is_dashboard_loaded():
                    return True
                try:
                    self.page.wait_for_url(re.compile(r".*dashboard.*", re.I), timeout=step_ms)
                    return True
                except Exception:
                    pass
                self.page.wait_for_timeout(step_ms)
                elapsed += step_ms
            return self.is_dashboard_loaded()
        except Exception:
            return self.is_dashboard_loaded()

    def take_screenshot(self, name: str) -> Path:
        _TEST_RESULTS.mkdir(parents=True, exist_ok=True)
        path = _TEST_RESULTS / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path
