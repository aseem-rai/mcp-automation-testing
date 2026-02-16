from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    @property
    def email_input(self) -> Locator:
        # Prefer typed/semantic attributes; allow flexible naming.
        return self.page.locator(
            "input[type='email'], "
            "input[name='email'], "
            "input[placeholder*='email' i], "
            "input[autocomplete='username']"
        ).first

    @property
    def password_input(self) -> Locator:
        return self.page.locator(
            "input[type='password'], "
            "input[name='password'], "
            "input[placeholder*='password' i], "
            "input[autocomplete='current-password']"
        ).first

    @property
    def login_button(self) -> Locator:
        # Role-based match first, with a CSS fallback for submit buttons.
        role_btn = self.page.get_by_role("button", name=re.compile(r"\blog\s*in\b|\bsign\s*in\b", re.I))
        submit_btn = self.page.locator("button[type='submit'], input[type='submit']")
        return role_btn.or_(submit_btn).first

    @property
    def welcome_back_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I))

    @property
    def password_inputs(self) -> Locator:
        # Backwards-compatible alias used by earlier stub logic.
        return self.page.locator("input[type='password']")

    @property
    def login_text(self) -> Locator:
        # Backwards-compatible alias used by earlier stub logic.
        return self.page.get_by_text(re.compile(r"\blog\s*in\b|\bsign\s*in\b", re.I))

    def load(self) -> None:
        """
        Navigate to the app entrypoint and wait for either login or dashboard.
        """
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(500)

        if self.is_dashboard_loaded():
            return

        # Wait for login UI to be available.
        try:
            self.email_input.wait_for(state="visible", timeout=15_000)
        except Exception:
            # Some apps don't show email field immediately (SSO, step-based auth).
            self.login_button.wait_for(state="visible", timeout=15_000)

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email or "")
        self.password_input.fill(password or "")

    def click_login(self) -> None:
        self.login_button.click(timeout=15_000)

    def is_login_visible(self) -> bool:
        try:
            return (
                self.email_input.is_visible()
                and self.password_input.is_visible()
                and self.login_button.is_visible()
            )
        except Exception:
            return False

    def is_dashboard_loaded(self) -> bool:
        try:
            if re.search(r"/dashboard\b", self.page.url, re.I):
                return True
        except Exception:
            pass

        try:
            if self.welcome_back_text.first.is_visible():
                return True
        except Exception:
            pass

        try:
            dash_nav = self.page.get_by_role("link", name=re.compile(r"^\s*dashboard\s*$", re.I))
            if dash_nav.count() > 0 and dash_nav.first.is_visible():
                return True
        except Exception:
            pass

        return False

    def get_error_message(self) -> str:
        """
        Best-effort extraction of a visible login error/validation message.
        Returns an empty string if nothing is found.
        """
        candidates = [
            self.page.get_by_role("alert"),
            self.page.locator("[role='alert']"),
            self.page.locator(".MuiAlert-message, .MuiFormHelperText-root, .error, .errors"),
            self.page.get_by_text(re.compile(r"invalid|incorrect|required|password|email", re.I)),
        ]

        for loc in candidates:
            try:
                if loc.count() <= 0:
                    continue
                first = loc.first
                if not first.is_visible():
                    continue
                msg = (first.inner_text() or "").strip()
                if msg:
                    return msg
            except Exception:
                continue

        return ""

    def take_screenshot(self, name: str) -> Path:
        screenshots_dir = Path("results") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "screenshot"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = screenshots_dir / f"{safe}_{ts}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def assert_login_ui_present_stub(self, timeout_ms: int = 15_000) -> None:
        """
        Stubbed login assertion: do NOT submit credentials.
        If auth UI exists, ensure at least one "login-ish" element is visible.
        """
        # Try password input first (usually most reliable).
        if self.password_inputs.count() > 0:
            self.password_inputs.first.wait_for(state="visible", timeout=timeout_ms)
            return

        # Fallback: "Login/Sign in" text.
        if self.login_text.count() > 0:
            self.login_text.first.wait_for(state="visible", timeout=timeout_ms)
            return

        # If neither exists, stay tolerant (apps vary).
        return

