"""Upload JD component for Prep module."""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.utils.test_data import ensure_dummy_jd_pdf

_DEFAULT_TIMEOUT = 15_000


class PrepUploadJDComponent:
    def __init__(self, page: Page):
        self.page = page

    @property
    def upload_jd_tab(self) -> Locator:
        return self.page.get_by_role("tab", name=re.compile(r"upload\s+jd", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*upload\s+jd\s*$", re.I))
        ).or_(self.page.locator("[data-testid*='upload-jd' i]")).first

    @property
    def upload_input(self) -> Locator:
        dialog = self.page.get_by_role("dialog")
        in_dialog = dialog.locator("input[type='file']")
        if in_dialog.count() > 0:
            return in_dialog.first
        return self.page.locator("input[type='file']").first

    @property
    def next_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*next\s*$", re.I)).or_(
            self.page.locator("[data-testid*='next' i]")
        ).first

    @property
    def submit_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"submit|upload|create|add", re.I)).or_(
            self.page.locator("[data-testid*='submit' i]")
        ).first

    def open_upload_jd_tab(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Opening Upload JD tab")
        expect(self.upload_jd_tab).to_be_visible(timeout=timeout_ms)
        self.upload_jd_tab.click(timeout=timeout_ms)
        self.page.wait_for_timeout(300)
        print("Upload JD tab opened")

    def upload_jd_file(self, file_path: str | Path | None = None, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Uploading JD")
        path = Path(file_path) if file_path else ensure_dummy_jd_pdf()
        if not path.exists():
            path = ensure_dummy_jd_pdf()
        expect(self.upload_input).to_be_attached(timeout=timeout_ms)
        self.upload_input.set_input_files(str(path))
        self.page.wait_for_timeout(400)
        print("JD file set")

    def submit_upload(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Submitting upload")
        if self.next_button.count() > 0 and self.next_button.is_visible():
            expect(self.next_button).to_be_visible(timeout=timeout_ms)
            self.next_button.click(timeout=timeout_ms)
            self.page.wait_for_timeout(500)
        if self.submit_button.count() > 0 and self.submit_button.is_visible():
            expect(self.submit_button).to_be_visible(timeout=timeout_ms)
            self.submit_button.click(timeout=timeout_ms)
        self.page.wait_for_timeout(500)
        print("Upload submitted")

    def verify_upload_success(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying upload success")
        jd_indicator = self.page.get_by_text(re.compile(r"JD|job\s+description", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"take\s+mock\s+interview", re.I))
        )
        expect(jd_indicator.first).to_be_visible(timeout=timeout_ms)
        print("Upload success verified")
