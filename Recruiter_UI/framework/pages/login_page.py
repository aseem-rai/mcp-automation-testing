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
    def google_login_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"google|sign\s*in\s+with\s+google|continue\s+with\s+google", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"google|sign\s*in\s+with\s+google|continue\s+with\s+google", re.I))
        ).or_(self.page.get_by_text(re.compile(r"sign\s*in\s+with\s+google|continue\s+with\s+google", re.I))).first

    def load(self) -> None:
        self.page.goto(settings.BASE_URL, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=15_000)

    def is_login_page(self) -> bool:
        try:
            return "login" in (self.page.url or "").lower()
        except Exception:
            return False

    def is_dashboard_loaded(self) -> bool:
        """Return True if URL contains dashboard/recruiter/jobs (no welcome text in recruiter UI)."""
        try:
            return bool(re.search(r"/(dashboard|recruiter|jobs)", self.page.url or "", re.I))
        except Exception:
            return False

    def _fill_google_oauth_popup(self, popup: Page, timeout_ms: int) -> None:
        """
        In Google OAuth popup: type email from env → Continue → type password from env → Continue → consent if any.
        Reaches dashboard after successful sign-in.
        """
        popup.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        popup.wait_for_timeout(2000)
        email = (settings.TEST_EMAIL or "").strip()
        password = (settings.TEST_PASSWORD or "").strip()
        if not email:
            return
        popup.wait_for_url(re.compile(r"accounts\.google\.com", re.I), timeout=15_000)
        popup.wait_for_timeout(1500)

        # 1) If account chooser (list of accounts) is shown, click the one matching email
        try:
            account = popup.get_by_text(email, exact=True).first
            if account.is_visible():
                account.click(timeout=10_000)
                popup.wait_for_timeout(3000)
        except Exception:
            try:
                account = popup.locator(f'[data-email="{email}"], [data-identifier="{email}"]').first
                if account.count() > 0 and account.first.is_visible():
                    account.first.click(timeout=10_000)
                    popup.wait_for_timeout(3000)
            except Exception:
                pass

        # 2) Type email from env and click Continue
        try:
            email_input = popup.get_by_label(re.compile(r"email|phone|identifier", re.I)).or_(
                popup.locator('input[type="email"], input[name="identifier"]')
            ).first
            email_input.wait_for(state="visible", timeout=12_000)
            email_input.fill(email, timeout=10_000)
            popup.wait_for_timeout(500)
            next_btn = popup.get_by_role("button", name=re.compile(r"next|continue", re.I)).first
            next_btn.click(timeout=10_000)
            popup.wait_for_timeout(3500)
        except Exception:
            pass

        # 3) Type password from env and click Continue
        if password:
            try:
                pwd_input = popup.get_by_label(re.compile(r"password|passwd", re.I)).or_(
                    popup.locator('input[type="password"], input[name="password"]')
                ).first
                pwd_input.wait_for(state="visible", timeout=12_000)
                pwd_input.fill(password, timeout=10_000)
                popup.wait_for_timeout(500)
                next_btn = popup.get_by_role("button", name=re.compile(r"next|continue", re.I)).first
                next_btn.click(timeout=10_000)
                popup.wait_for_timeout(3500)
            except Exception:
                pass

        # 4) Consent: Continue / Allow (if shown)
        try:
            consent = popup.get_by_role("button", name=re.compile(r"continue|allow|accept", re.I)).first
            if consent.count() > 0 and consent.is_visible():
                consent.click(timeout=5_000)
                popup.wait_for_timeout(2000)
        except Exception:
            pass

    def do_google_sign_in_if_needed(self, timeout_ms: int = 30_000) -> bool:
        """
        If not on dashboard, click Sign in with Google. OAuth opens in popup —
        fill popup: select account (TEST_EMAIL), type password, wait for popup to close.
        """
        if self.is_dashboard_loaded():
            return True
        try:
            # Wait for login page / Google button to be visible (page may still be loading)
            try:
                self.google_login_button.first.wait_for(state="visible", timeout=15_000)
            except Exception:
                pass
            if self.google_login_button.count() > 0 and self.google_login_button.first.is_visible():
                with self.page.expect_popup(timeout=15_000) as popup_info:
                    self.google_login_button.first.click(timeout=10_000)
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
            try:
                self.page.wait_for_url(re.compile(r".*(dashboard|recruiter|jobs).*", re.I), timeout=min(30_000, timeout_ms))
                return True
            except Exception:
                pass
            elapsed = 0
            step_ms = 2000
            while elapsed < timeout_ms:
                if self.is_dashboard_loaded():
                    return True
                try:
                    self.page.wait_for_url(re.compile(r".*(dashboard|recruiter|jobs).*", re.I), timeout=step_ms)
                    return True
                except Exception:
                    pass
                try:
                    self.page.wait_for_timeout(step_ms)
                except Exception:
                    pass
                elapsed += step_ms
            return self.is_dashboard_loaded()
        except Exception:
            return self.is_dashboard_loaded()

    def take_screenshot(self, name: str) -> Path:
        _TEST_RESULTS.mkdir(parents=True, exist_ok=True)
        path = _TEST_RESULTS / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path
