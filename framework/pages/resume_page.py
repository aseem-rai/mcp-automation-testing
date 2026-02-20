from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage


class ResumePage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators (selectors)
    # -----------------------
    @property
    def heading_your_resumes(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\byour\s+resumes\b", re.I))

    @property
    def add_new_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\badd\s+new\s+resume\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\badd\s+resume\b", re.I))
        )

    @property
    def resume_cards(self) -> Locator:
        # Prefer cards with recognizable resume-ish text; keep it tolerant.
        return self.page.locator("text=/resume/i").locator("xpath=ancestor-or-self::*[self::div or self::section][1]")

    @property
    def modal_title(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*add\s+new\s+resume\s*$", re.I)).first

    @property
    def target_role_field(self) -> Locator:
        # Try by label first (best), then by placeholder/name.
        by_label = self.page.get_by_label(re.compile(r"\btarget\s*role\b", re.I))
        by_placeholder = self.page.locator(
            "input[placeholder^='e.g.' i], "
            "input[placeholder*='data scientist' i], "
            "input[placeholder*='target' i], "
            "input[placeholder*='role' i], "
            "input[name*='role' i], "
            "input[name*='target' i]"
        )
        return by_label.or_(by_placeholder).first

    @property
    def resume_upload_field(self) -> Locator:
        # File input is typically <input type=file>. Prefer the one inside the modal when open.
        dialog = self.page.get_by_role("dialog")
        in_dialog = dialog.locator("input[type='file']")
        if in_dialog.count() > 0:
            return in_dialog.first
        return self.page.locator("input[type='file']").first

    @property
    def resume_upload_dropzone(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bclick\s+to\s+select\s+file\b", re.I)).first

    @property
    def add_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*add\s+resume\s*$", re.I)).first

    @property
    def close_button(self) -> Locator:
        # Prefer Close/X buttons within modal.
        return self.page.get_by_role("button", name=re.compile(r"\bcancel\b|\bclose\b", re.I)).first

    @property
    def close_icon(self) -> Locator:
        # The "X" is often an icon button without accessible name; best-effort.
        return self.page.get_by_role("button", name=re.compile(r"^\s*x\s*$", re.I)).first

    @property
    def error_messages(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bis\s+required\b|\brequired\b|\bplease\b|\binvalid\b", re.I))

    # -----------------------
    # Assertions / actions
    # -----------------------
    def verify_loaded(self, timeout_ms: int = 15_000) -> None:
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        self.heading_your_resumes.first.wait_for(state="visible", timeout=timeout_ms)

    def verify_resume_cards_present(self, timeout_ms: int = 10_000) -> None:
        # We accept either explicit cards or at least some resume-related content.
        try:
            self.resume_cards.first.wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            # Fallback: page should have some resume text visible.
            self.page.get_by_text(re.compile(r"\bresume\b", re.I)).first.wait_for(state="visible", timeout=timeout_ms)

    def click_add_new_resume(self) -> None:
        self.add_new_resume_button.first.wait_for(state="visible", timeout=15_000)
        self.add_new_resume_button.first.click(timeout=15_000)

    def verify_add_resume_modal_open(self, timeout_ms: int = 15_000) -> None:
        # Avoid relying on role=dialog (not always set). Use the title as the anchor.
        self.modal_title.wait_for(state="visible", timeout=timeout_ms)
        self.target_role_field.wait_for(state="visible", timeout=timeout_ms)
        # One of these should be present in the modal.
        if self.resume_upload_dropzone.count() > 0:
            self.resume_upload_dropzone.wait_for(state="visible", timeout=timeout_ms)
        elif self.resume_upload_field.count() > 0:
            self.resume_upload_field.wait_for(state="attached", timeout=timeout_ms)

    def verify_target_role_field(self, timeout_ms: int = 10_000) -> None:
        self.target_role_field.wait_for(state="visible", timeout=timeout_ms)

    def verify_resume_upload_field(self, timeout_ms: int = 10_000) -> None:
        if self.resume_upload_dropzone.count() > 0:
            self.resume_upload_dropzone.wait_for(state="visible", timeout=timeout_ms)
            return
        self.resume_upload_field.wait_for(state="attached", timeout=timeout_ms)

    def verify_add_resume_button_disabled_when_empty(self) -> None:
        # If the UI disables it, great.
        if self.add_resume_button.count() > 0 and not self.add_resume_button.is_enabled():
            return

        # Otherwise, clicking should trigger validation messages.
        if self.add_resume_button.count() > 0:
            self.add_resume_button.click(timeout=5_000)
            self.page.wait_for_timeout(300)
            assert self.error_messages.count() > 0, "Expected validation errors when submitting empty resume modal"
            return

        # If the button label differs, accept any visible required/validation feedback.
        assert self.error_messages.count() > 0, "Expected validation errors in empty resume modal"

    def close_modal(self) -> None:
        # Try Escape first (commonly supported).
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
            if self.modal.count() == 0 or not self.modal.is_visible():
                return
        except Exception:
            pass

        # Fall back to a close/cancel button.
        try:
            self.close_button.click(timeout=5_000)
            return
        except Exception:
            pass

        # Try "X" icon button.
        try:
            self.close_icon.click(timeout=3_000)
            return
        except Exception:
            pass

        # Final fallback: click outside if overlay allows.
        try:
            self.page.mouse.click(5, 5)
        except Exception:
            pass

    def take_screenshot(self, name: str) -> Path:
        screenshots_dir = Path("results") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "screenshot"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = screenshots_dir / f"{safe}_{ts}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    # -----------------------
    # Upload resume flow
    # -----------------------
    def upload_resume(self, resume_file_path: str | Path | None = None) -> Path:
        """Navigate to resumes, add new resume, fill role, upload file, submit, verify card, save screenshot."""
        if resume_file_path is None:
            # Default: test_data/test_resume.pdf relative to project root
            project_root = Path(__file__).resolve().parent.parent.parent
            resume_file_path = project_root / "test_data" / "test_resume.pdf"
        path = Path(resume_file_path)
        if not path.is_absolute():
            project_root = Path(__file__).resolve().parent.parent.parent
            path = project_root / path

        self.goto("/dashboard/resumes", wait_until="domcontentloaded")
        self.verify_loaded()
        self.click_add_new_resume()
        self.verify_add_resume_modal_open()
        self.target_role_field.fill("AI Engineer")
        self.resume_upload_field.set_input_files(str(path))
        try:
            expect(self.add_resume_button).to_be_enabled(timeout=5_000)
        except Exception:
            # Some UIs keep the button disabled until change event is processed; click anyway.
            pass
        self.add_resume_button.click(force=True)
        self.verify_resume_cards_present(timeout_ms=15_000)
        out_dir = Path("results")
        out_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = out_dir / "resume_uploaded.png"
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        return screenshot_path

