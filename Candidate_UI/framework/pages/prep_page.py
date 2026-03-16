"""
Prep page object. Base URL: /dashboard/preps.
Uses PrepCreateJDComponent, PrepUploadJDComponent, PrepCardComponent.
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage
from framework.pages.prep_card_component import PrepCardComponent
from framework.pages.prep_create_jd_component import PrepCreateJDComponent
from framework.pages.prep_upload_jd_component import PrepUploadJDComponent

_DEFAULT_TIMEOUT = 15_000
_SCREENSHOTS_DIR = Path("test-results") / "prep"


class PrepPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)
        self.create_jd = PrepCreateJDComponent(page)
        self.upload_jd = PrepUploadJDComponent(page)
        self.card = PrepCardComponent(page)

    @property
    def prep_sidebar_button(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"\bpreps?\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bpreps?\b", re.I))
        ).or_(self.page.locator("[data-testid*='prep' i], [data-testid*='nav-prep' i]")).first

    @property
    def new_prep_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"new\s+prep|add\s+prep|create\s+jd", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"new\s+prep|add\s+prep", re.I))
        ).or_(self.page.get_by_text(re.compile(r"new\s+prep|add\s+prep", re.I))).or_(
            self.page.locator("[data-testid*='new-prep' i]")
        ).first

    @property
    def prep_page_heading(self) -> Locator:
        return self.page.get_by_role("heading", name=re.compile(r"^\s*preps?\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*preps?\s*$", re.I))
        ).first

    @property
    def jd_cards_container(self) -> Locator:
        return self.page.locator("[data-testid*='jd-cards' i], [data-testid*='prep-cards' i]").or_(
            self.page.locator("section, main").filter(has=self.card.take_mock_interview_button)
        ).first

    @property
    def empty_state_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"no\s+jds?|add\s+your\s+first|search\s+for", re.I)).or_(
            self.page.locator("[data-testid*='empty-state' i]")
        ).first

    def _screenshot_on_failure(self, action_name: str) -> None:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", action_name).strip() or "prep"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = _SCREENSHOTS_DIR / f"{safe}_{ts}.png"
        try:
            self.page.screenshot(path=str(path), full_page=True)
        except Exception:
            pass

    def take_screenshot(self, name: str) -> Path:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "prep"
        path = _SCREENSHOTS_DIR / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def open_prep_page(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Opening Prep page")
        try:
            for path in ["/dashboard/preps", "/preps"]:
                self.goto(path, wait_until="domcontentloaded")
                self.wait_for_body_visible(timeout_ms=timeout_ms)
                try:
                    self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=8_000)
                    expect(self.prep_page_heading).to_be_visible(timeout=timeout_ms)
                    print("Prep page opened")
                    return
                except Exception:
                    continue
            self.goto("/dashboard", wait_until="domcontentloaded")
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.prep_sidebar_button).to_be_visible(timeout=timeout_ms)
            self.prep_sidebar_button.click(timeout=timeout_ms)
            self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=timeout_ms)
            expect(self.prep_page_heading).to_be_visible(timeout=timeout_ms)
            print("Prep page opened")
        except Exception as e:
            self._screenshot_on_failure("open_prep_page")
            print(f"Result: open_prep_page failed - {e}")
            raise

    def verify_prep_page_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying Prep page loaded")
        try:
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.prep_page_heading).to_be_visible(timeout=timeout_ms)
            print("Prep page loaded")
        except Exception as e:
            self._screenshot_on_failure("verify_prep_page_loaded")
            print(f"Result: verify_prep_page_loaded failed - {e}")
            raise

    def click_new_prep(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking New Prep")
        try:
            expect(self.new_prep_button).to_be_visible(timeout=timeout_ms)
            self.new_prep_button.click(timeout=timeout_ms)
            self.page.wait_for_timeout(500)
            expect(
                self.page.get_by_role("dialog").or_(self.page.get_by_text(re.compile(r"create\s+jd|upload\s+jd", re.I)))
            ).to_be_visible(timeout=timeout_ms)
            print("New Prep clicked")
        except Exception as e:
            self._screenshot_on_failure("click_new_prep")
            print(f"Result: click_new_prep failed - {e}")
            raise

    def verify_jd_cards_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying JD cards visible")
        try:
            expect(self.card.take_mock_interview_button.first).to_be_visible(timeout=timeout_ms)
            print("JD cards visible")
        except Exception as e:
            self._screenshot_on_failure("verify_jd_cards_visible")
            print(f"Result: verify_jd_cards_visible failed - {e}")
            raise

    def delete_all_preps_if_exist(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Deleting all preps if exist")
        try:
            while self.card.take_mock_interview_button.count() > 0 and self.card.take_mock_interview_button.first.is_visible():
                self.card.click_delete(timeout_ms=timeout_ms)
                self.page.wait_for_timeout(500)
            print("All preps deleted (or none existed)")
        except Exception as e:
            self._screenshot_on_failure("delete_all_preps_if_exist")
            print(f"Result: delete_all_preps_if_exist failed - {e}")
            raise

    def ensure_prep_exists(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """If JD exists do nothing. Else: Click New Prep, Create JD using component, verify JD created."""
        print("Ensuring prep exists")
        try:
            self.open_prep_page(timeout_ms=timeout_ms)
            self.verify_prep_page_loaded(timeout_ms=timeout_ms)
            if self.card.take_mock_interview_button.count() > 0 and self.card.take_mock_interview_button.first.is_visible():
                print("Prep already exists")
                return
            self.click_new_prep(timeout_ms=timeout_ms)
            self.create_jd.open_create_jd_tab(timeout_ms=timeout_ms)
            self.create_jd.enter_role("Software Engineer", timeout_ms=timeout_ms)
            self.create_jd.enter_skills("Python, SQL", timeout_ms=timeout_ms)
            self.create_jd.enter_experience("2", timeout_ms=timeout_ms)
            self.create_jd.click_create_jd(timeout_ms=timeout_ms)
            self.create_jd.verify_jd_created(timeout_ms=timeout_ms)
            print("Prep created")
        except Exception as e:
            self._screenshot_on_failure("ensure_prep_exists")
            print(f"Result: ensure_prep_exists failed - {e}")
            raise
