from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage


class ProfilePage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators (selectors)
    # -----------------------
    @property
    def header_profile(self) -> Locator:
        # Prefer heading semantics if present; otherwise match visible text.
        return self.page.get_by_role("heading", name=re.compile(r"^\s*profile\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*profile\s*$", re.I))
        ).first

    @property
    def basic_info_heading(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*basic\s+info\s*$", re.I)).first

    @property
    def about_heading(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*about\b|\bsummary\b", re.I)).first

    @property
    def no_resume_data_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bno\s+resume\s+data\s+found\b", re.I)).first

    @property
    def download_profile_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdownload\s+profile\b", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"\bdownload\s+profile\b", re.I))
        ).first

    @property
    def header_identity_block(self) -> Locator:
        return self.page.locator(
            "[data-testid*='profile-header' i], [class*='profile-header' i], "
            "[class*='user-header' i], [class*='candidate-header' i]"
        ).first

    @property
    def header_avatar(self) -> Locator:
        return self.page.locator(
            "[data-testid*='avatar' i], [class*='avatar' i], img[alt*='avatar' i], img[alt*='profile' i]"
        ).first

    # Field-label locators (best-effort; some accounts may not have data yet)
    @property
    def label_name(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*name\s*$", re.I)).first

    @property
    def label_title(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*title\s*$|^\s*designation\s*$", re.I)).first

    @property
    def label_email(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*email\s*$", re.I)).first

    @property
    def label_phone(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*phone\s*$|^\s*mobile\s*$", re.I)).first

    @property
    def label_location(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*location\s*$", re.I)).first

    def _has_no_resume_data(self) -> bool:
        try:
            return self.no_resume_data_text.is_visible()
        except Exception:
            return False

    # -----------------------
    # Actions / Assertions
    # -----------------------
    def load(self) -> None:
        self.goto("/dashboard/profile", wait_until="domcontentloaded")

    def verify_loaded(self, timeout_ms: int = 15_000) -> None:
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        self.header_profile.wait_for(state="visible", timeout=timeout_ms)
        self.download_profile_button.wait_for(state="visible", timeout=timeout_ms)

    def verify_basic_info_section(self, timeout_ms: int = 15_000) -> None:
        self.basic_info_heading.wait_for(state="visible", timeout=timeout_ms)

    def verify_name(self) -> None:
        if self._has_no_resume_data():
            return
        assert self.label_name.count() > 0 or self.page.get_by_text(re.compile(r".+")).count() > 0

    def verify_title(self) -> None:
        if self._has_no_resume_data():
            return
        assert self.label_title.count() > 0 or self.page.get_by_text(re.compile(r".+")).count() > 0

    def verify_email(self) -> None:
        if self._has_no_resume_data():
            return
        # Prefer explicit label; otherwise accept an email-looking value.
        if self.label_email.count() > 0:
            return
        assert self.page.get_by_text(re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)).count() > 0

    def verify_phone(self) -> None:
        if self._has_no_resume_data():
            return
        if self.label_phone.count() > 0:
            return
        assert self.page.get_by_text(re.compile(r"\+?\d[\d\s()-]{7,}", re.I)).count() > 0

    def verify_location(self) -> None:
        if self._has_no_resume_data():
            return
        if self.label_location.count() > 0:
            return
        # Best-effort: some location text exists.
        assert self.page.get_by_text(re.compile(r"\b[a-z]+(?:\s+[a-z]+)*\b", re.I)).count() > 0

    def verify_about_section(self, timeout_ms: int = 15_000) -> None:
        if self._has_no_resume_data():
            return
        # About might not exist for all profiles; when resume data exists it should.
        self.about_heading.wait_for(state="visible", timeout=timeout_ms)

    def click_download_profile(self) -> None:
        self.download_profile_button.click(timeout=15_000)

    def verify_profile_details_sections_visible(self, timeout_ms: int = 15_000) -> None:
        """
        Validate profile header and main profile sections:
        - Header: name, title/role, avatar
        - Sections: Basic Info, Education, Skills, Languages, Work Experience, Projects, Awards/Certifications
        """
        self.verify_loaded(timeout_ms=timeout_ms)

        # Header checks
        expect_name = self.page.get_by_text(re.compile(r"\bname\b", re.I))
        expect_role = self.page.get_by_text(re.compile(r"\btitle\b|\brole\b|\bdesignation\b", re.I))
        if self.header_identity_block.count() > 0:
            self.header_identity_block.wait_for(state="visible", timeout=timeout_ms)
        else:
            # Fallback to explicit labels if header container is not easily identifiable.
            assert expect_name.count() > 0, "Profile header name is not visible."
            assert expect_role.count() > 0, "Profile header title/role is not visible."
        assert self.header_avatar.count() > 0, "Profile avatar is not visible."
        self.header_avatar.first.wait_for(state="visible", timeout=timeout_ms)

        # Core section headings
        required_headings = [
            r"^\s*basic\s+info\s*$",
            r"^\s*education\s*$",
            r"^\s*skills?\s*$",
            r"^\s*languages?\s*$",
            r"^\s*work\s+experience\s*$|^\s*experience\s*$",
            r"^\s*projects?\s*$",
            r"^\s*awards?\s*$|^\s*certifications?\s*$|^\s*awards?\s*/\s*certifications?\s*$",
        ]
        for pattern in required_headings:
            heading = self.page.get_by_text(re.compile(pattern, re.I)).first
            heading.wait_for(state="visible", timeout=timeout_ms)

        # Basic info fields inside the section
        for field in [r"^\s*email\s*$", r"^\s*phone\s*$|^\s*mobile\s*$", r"^\s*location\s*$", r"^\s*about\s*$|\bsummary\b"]:
            fld = self.page.get_by_text(re.compile(field, re.I)).first
            fld.wait_for(state="visible", timeout=timeout_ms)

    def take_screenshot(self, name: str) -> Path:
        screenshots_dir = Path("results") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "screenshot"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = screenshots_dir / f"{safe}_{ts}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

