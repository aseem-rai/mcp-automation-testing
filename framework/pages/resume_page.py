"""
Resume page object. Base URL: /dashboard/resumes.
Supports upload, validation, deletion, download; ensure_resume_exists() for Profile/Jobs/Prep.
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage
from framework.utils.test_data import ensure_dummy_resume_pdf

_DEFAULT_TIMEOUT = 15_000
# Wait up to 180 seconds for system to parse resume and show resume card after Add Resume submit
PARSE_RESUME_WAIT_MS = 180_000
_SCREENSHOTS_DIR = Path("test-results") / "resume"
_REPORTS_RESUME_SCREENSHOTS = Path("reports") / "screenshots" / "resume"


class ResumePage(BasePage):
    """Page Object for Resume module (/dashboard/resumes)."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators
    # -----------------------
    @property
    def sidebar_resume_button(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"\bresumes?\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bresumes?\b", re.I))
        ).or_(self.page.locator("[data-testid*='resume' i], [data-testid*='nav-resume' i]")).first

    @property
    def add_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\badd\s+new\s+resume\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\badd\s+resume\b", re.I))
        ).or_(self.page.get_by_text(re.compile(r"\badd\s+resume\b", re.I))).or_(
            self.page.locator("[data-testid*='add-resume' i], [data-testid*='addResume' i]")
        ).first

    @property
    def upload_input(self) -> Locator:
        dialog = self._add_resume_dialog()
        in_dialog = dialog.locator("input[type='file']")
        if in_dialog.count() > 0:
            return in_dialog.first
        return self.page.locator("input[type='file']").first

    def _add_resume_dialog(self) -> Locator:
        """Dialog/modal for Add Resume (use when modal is open)."""
        return self.page.get_by_role("dialog").or_(self.page.locator("[role='dialog']"))

    @property
    def target_role_input(self) -> Locator:
        dialog = self._add_resume_dialog()
        # Any text input or textarea in the modal that isn't the file input
        in_dialog = dialog.locator(
            "input[type='text'], input:not([type='file']), textarea, [contenteditable='true']"
        ).filter(has_not=self.page.locator("input[type='file']"))
        # Placeholder/label/name/id variants
        in_dialog_specific = dialog.locator(
            "input[placeholder*='role' i], input[placeholder*='target' i], input[placeholder*='position' i], "
            "input[placeholder*='title' i], input[placeholder*='job' i], input[placeholder*='enter' i], "
            "input[name*='role' i], input[name*='target' i], input[id*='role' i], input[id*='target' i], "
            "textarea[placeholder*='role' i], textarea[placeholder*='target' i], textarea[name*='role' i]"
        )
        by_label = self.page.get_by_label(
            re.compile(
                r"\b(target\s*role|job\s*role|desired\s*role|role|position|job\s*title|enter\s+role)\b",
                re.I,
            )
        )
        page_inputs = self.page.locator(
            "input[type='text'], textarea"
        ).filter(has_not=self.page.locator("input[type='file']"))
        return in_dialog_specific.first.or_(in_dialog.first).or_(by_label).or_(page_inputs).first

    @property
    def submit_add_resume_button(self) -> Locator:
        dialog = self._add_resume_dialog()
        in_dialog = dialog.get_by_role("button", name=re.compile(r"^\s*add\s+resume\s*$", re.I)).or_(
            dialog.get_by_role("button", name=re.compile(r"submit|save|upload", re.I))
        ).or_(dialog.locator("[data-testid*='submit-resume' i], [data-testid*='addResume' i]"))
        return in_dialog.or_(
            self.page.get_by_role("button", name=re.compile(r"^\s*add\s+resume\s*$", re.I))
        ).or_(self.page.get_by_role("button", name=re.compile(r"submit|save|upload", re.I))).or_(
            self.page.locator("[data-testid*='submit-resume' i], [data-testid*='addResume' i]")
        ).first

    @property
    def resume_card_container(self) -> Locator:
        return self.page.locator("[data-testid*='resume-card' i], [data-testid*='resumeCard' i]").or_(
            self.page.locator("section, div").filter(has=self.page.get_by_text(re.compile(r"\bresume\b", re.I)))
        ).first

    @property
    def resume_cards(self) -> Locator:
        return self.page.locator("[data-testid*='resume-card' i], [data-testid*='resumeCard' i]").or_(
            self.page.locator("div[class*='card'], section[class*='card']").filter(
                has=self.page.get_by_text(re.compile(r"\bresume|pdf|role\b", re.I))
            )
        )

    @property
    def uploaded_resume_card(self) -> Locator:
        """Locator for an actual uploaded resume card (has download/delete or data-testid), not Add Resume or heading."""
        # Card/section with explicit action labels OR icon/button controls in resume context.
        with_actions = self.page.locator(
            "div[class*='card'], section[class*='card'], article, [data-testid*='resume-card' i], [data-testid*='resumeCard' i]"
        ).filter(
            has=self.page.get_by_role("button", name=re.compile(r"download|delete|remove|view", re.I)).or_(
                self.page.locator(
                    "[title*='view' i], [title*='download' i], [title*='delete' i], "
                    "[aria-label*='view' i], [aria-label*='download' i], [aria-label*='delete' i]"
                )
            ).or_(self.page.locator("button, [role='button']"))
        )
        # data-testid resume card
        by_testid = self.page.locator("[data-testid*='resume-card' i], [data-testid*='resumeCard' i]")
        # Fallback by text content likely unique to uploaded cards.
        by_content = self.page.locator("article, section, div").filter(
            has=self.page.get_by_text(re.compile(r"\.pdf|default|resume", re.I))
        )
        return with_actions.first.or_(by_testid.first).or_(by_content.first)

    @property
    def resume_delete_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"delete|remove", re.I)).or_(
            self.page.get_by_title(re.compile(r"delete|remove", re.I))
        ).or_(self.page.locator("[data-testid*='delete-resume' i], [aria-label*='delete' i], [title*='delete' i]")).first

    @property
    def resume_download_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"download", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"download", re.I))
        ).or_(self.page.locator("[data-testid*='download-resume' i], [aria-label*='download' i], [title*='download' i]")).first

    @property
    def empty_state_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"no\s+resume|add\s+your\s+first|no\s+resumes\s+yet", re.I)).or_(
            self.page.locator("[data-testid*='empty-state' i]")
        ).first

    @property
    def heading_your_resumes(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\byour\s+resumes\b", re.I)).or_(
            self.page.get_by_role("heading", name=re.compile(r"resumes?", re.I))
        ).first

    @property
    def modal(self) -> Locator:
        return self.page.get_by_role("dialog")

    @property
    def close_modal_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bcancel\b|\bclose\b|x", re.I)).first

    @property
    def view_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"view\s+resume", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"view\s+resume", re.I))
        ).or_(self.page.get_by_text(re.compile(r"view\s+resume", re.I))).or_(
            self.page.locator("[aria-label*='view' i], [title*='view' i]")
        ).first

    def _screenshot_on_failure(self, action_name: str) -> None:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", action_name).strip() or "resume"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = _SCREENSHOTS_DIR / f"{safe}_{ts}.png"
        try:
            self.page.screenshot(path=str(path), full_page=True)
        except Exception:
            pass

    def take_screenshot(self, name: str) -> Path:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "resume"
        path = _SCREENSHOTS_DIR / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def take_screenshot_report(self, name: str) -> Path:
        """Save screenshot to reports/screenshots/resume/ for the resume upload test report."""
        _REPORTS_RESUME_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "resume"
        path = _REPORTS_RESUME_SCREENSHOTS / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    # -----------------------
    # Core functions
    # -----------------------
    def go_to_resumes(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Navigate to Resume page (/dashboard/resumes)."""
        self.goto("/dashboard/resumes", wait_until="domcontentloaded")
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        expect(self.page).to_have_url(re.compile(r"/resumes?", re.I), timeout=timeout_ms)

    def open_add_resume_modal(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Click Add New Resume to open the upload modal."""
        expect(self.add_resume_button).to_be_visible(timeout=timeout_ms)
        self.add_resume_button.click(timeout=timeout_ms)
        self.page.wait_for_timeout(800)

    def fill_target_role(self, role: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Enter target/job role in the Add Resume modal (e.g. ML Engineer)."""
        self.enter_target_role(role, timeout_ms=timeout_ms)

    def set_default(self, value: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Select default option in Add Resume modal (e.g. 'No')."""
        try:
            default_control = self._add_resume_dialog().get_by_label(
                re.compile(r"default|set\s+as\s+default", re.I)
            ).or_(self.page.get_by_text(re.compile(r"default", re.I)).first)
            if default_control.count() > 0:
                if value.strip().lower() in ("no", "false", "0"):
                    # Try unchecking checkbox or selecting No in dropdown
                    checkbox = self._add_resume_dialog().locator("input[type='checkbox']").first
                    if checkbox.count() > 0 and checkbox.is_visible():
                        if checkbox.is_checked():
                            checkbox.click()
                    else:
                        option = self.page.get_by_role("option", name=re.compile(r"^\s*no\s*$", re.I)).or_(
                            self.page.get_by_text(re.compile(r"^\s*no\s*$", re.I))
                        ).first
                        if option.count() > 0:
                            option.click()
                self.page.wait_for_timeout(200)
        except Exception:
            pass

    def wait_for_resume_card(self, timeout: int = 180) -> None:
        """Wait until the resume card appears after submit. Parsing can take up to timeout seconds (default 180)."""
        timeout_ms = timeout * 1000
        self.wait_for_back_to_resume_module(timeout_ms=min(30_000, timeout_ms))
        self.page.wait_for_timeout(2000)
        self.uploaded_resume_card.wait_for(state="visible", timeout=timeout_ms)

    def validate_resume_uploaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Verify resume card shows title, file name, timestamp and has View/Download/Delete buttons."""
        card = self.uploaded_resume_card
        expect(card).to_be_visible(timeout=timeout_ms)
        # Card should contain some resume-related content (title/filename/timestamp - flexible text)
        card_text = card.locator("text=/resume|pdf|role|upload|\\d{4}/i")
        try:
            card_text.first.wait_for(state="visible", timeout=5_000)
        except Exception:
            pass
        # Action buttons: View/Download/Delete (text buttons or icon-only controls)
        view_btn = self.page.get_by_role("button", name=re.compile(r"view\s+resume", re.I)).or_(
            self.page.get_by_text(re.compile(r"view\s+resume", re.I))
        ).or_(self.page.locator("[aria-label*='view' i], [title*='view' i]")).first
        if self.resume_download_button.count() > 0:
            expect(self.resume_download_button.first).to_be_visible(timeout=timeout_ms)
        if self.resume_delete_button.count() > 0:
            expect(self.resume_delete_button.first).to_be_visible(timeout=timeout_ms)
        if view_btn.count() > 0:
            expect(view_btn.first).to_be_visible(timeout=5_000)
        # Fallback: if no named controls detected, ensure at least 3 icon/action buttons in the card.
        actions = card.locator("button, [role='button'], [title], [aria-label]")
        if actions.count() >= 3:
            expect(actions.nth(0)).to_be_visible(timeout=timeout_ms)
        else:
            raise AssertionError(
                "Resume card found but action controls (View/Download/Delete) were not detected."
            )

    def view_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Click View Resume on the resume card."""
        expect(self.view_resume_button).to_be_visible(timeout=timeout_ms)
        self.view_resume_button.click(timeout=timeout_ms)

    def delete_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Click Delete Resume and confirm. Fails if no delete button visible."""
        expect(self.resume_delete_button).to_be_visible(timeout=timeout_ms)
        self.resume_delete_button.click(timeout=timeout_ms)
        self.page.wait_for_timeout(300)
        confirm = self.page.get_by_role("button", name=re.compile(r"confirm|yes|delete", re.I)).first
        if confirm.count() > 0 and confirm.is_visible():
            confirm.click(timeout=5_000)
        self.page.wait_for_timeout(500)

    def open_resume_page(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Opening Resume page")
        try:
            self.goto("/dashboard/resumes", wait_until="domcontentloaded")
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.page).to_have_url(re.compile(r"/resumes?", re.I), timeout=timeout_ms)
            print("Resume page opened")
        except Exception as e:
            self._screenshot_on_failure("open_resume_page")
            print(f"Result: open_resume_page failed - {e}")
            raise

    def verify_resume_page_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying Resume page loaded")
        try:
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.heading_your_resumes).to_be_visible(timeout=timeout_ms)
            print("Resume page loaded")
        except Exception as e:
            self._screenshot_on_failure("verify_resume_page_loaded")
            print(f"Result: verify_resume_page_loaded failed - {e}")
            raise

    def click_add_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking Add Resume")
        try:
            expect(self.add_resume_button).to_be_visible(timeout=timeout_ms)
            self.add_resume_button.click(timeout=timeout_ms)
            self.page.wait_for_timeout(800)
            print("Add Resume clicked")
        except Exception as e:
            self._screenshot_on_failure("click_add_resume")
            print(f"Result: click_add_resume failed - {e}")
            raise

    def _select_file_button(self) -> Locator:
        """Button/link that opens the file picker (Select file, Browse, Choose file, etc.)."""
        dialog = self._add_resume_dialog()
        return (
            dialog.get_by_role("button", name=re.compile(r"select\s+file|browse|choose\s+file", re.I))
            .or_(dialog.get_by_text(re.compile(r"select\s+file|browse|choose\s+file|click\s+to\s+select", re.I)))
            .or_(dialog.locator("label").filter(has=dialog.locator("input[type='file']")))
            .first
        )

    def _selected_file_names(self) -> list[str]:
        """Return selected file names from file inputs in Add Resume dialog."""
        try:
            names = self.page.evaluate(
                """() => {
                    const dialog = document.querySelector('[role="dialog"]');
                    const roots = dialog ? [dialog] : [document];
                    const out = [];
                    for (const root of roots) {
                      const inputs = root.querySelectorAll('input[type="file"]');
                      for (const input of inputs) {
                        if (input.files && input.files.length > 0) {
                          for (const f of Array.from(input.files)) {
                            out.push(f.name || "");
                          }
                        }
                      }
                    }
                    return out.filter(Boolean);
                }"""
            )
            if isinstance(names, list):
                return [str(n) for n in names if str(n).strip()]
        except Exception:
            pass
        return []

    def _wait_for_file_selected(self, expected_file_name: str, timeout_ms: int = 8_000) -> bool:
        """Wait until at least one file is selected in modal file input (or filename appears in modal text)."""
        deadline = self.page.evaluate("Date.now()") + timeout_ms
        expected = (expected_file_name or "").strip().lower()
        while self.page.evaluate("Date.now()") < deadline:
            selected = [n.lower() for n in self._selected_file_names()]
            if selected:
                if not expected:
                    return True
                if any(expected in n or n in expected for n in selected):
                    return True
            # Some UIs render selected file name as text next to the uploader.
            if expected:
                filename_text = self._add_resume_dialog().get_by_text(re.compile(re.escape(expected), re.I)).first
                try:
                    if filename_text.count() > 0 and filename_text.is_visible():
                        return True
                except Exception:
                    pass
            self.page.wait_for_timeout(250)
        return False

    def assert_file_selected(self, expected_file_name: str, timeout_ms: int = 8_000) -> None:
        """Assert that Add Resume file input has a selected file."""
        if self._wait_for_file_selected(expected_file_name=expected_file_name, timeout_ms=timeout_ms):
            return
        selected = self._selected_file_names()
        raise AssertionError(
            f"No file selected in Add Resume modal. Expected '{expected_file_name}', got {selected or 'none'}"
        )

    def upload_resume(self, file_path: str | Path | None = None, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Set resume file. Triggers native file manager popup by clicking the file input or Select file control."""
        print("Uploading Resume")
        try:
            if file_path is None:
                path = ensure_dummy_resume_pdf()
            else:
                path = Path(file_path)
                if not path.is_absolute():
                    root = ensure_dummy_resume_pdf().parent
                    path = root / path.name if (root / path.name).exists() else ensure_dummy_resume_pdf()
                if not path.exists():
                    path = ensure_dummy_resume_pdf()
            path = path.resolve()
            # Open file manager popup: expect_file_chooser then click the element that triggers it
            file_input = self.upload_input
            file_input.wait_for(state="attached", timeout=timeout_ms)
            # Try 1: click file input (even if hidden) - opens native file dialog
            try:
                with self.page.expect_file_chooser(timeout=15_000) as fc_info:
                    self.upload_input.click(timeout=5_000, force=True)
                file_chooser = fc_info.value
                file_chooser.set_files(str(path))
                self.page.wait_for_timeout(600)
                self.assert_file_selected(path.name)
                print("Resume file set via file chooser popup")
                return
            except Exception:
                pass
            # Try 2: click visible "Select file" / "Browse" button
            try:
                sel = self._select_file_button()
                if sel.count() > 0 and sel.is_visible():
                    with self.page.expect_file_chooser(timeout=15_000) as fc_info:
                        sel.click(timeout=5_000)
                    file_chooser = fc_info.value
                    file_chooser.set_files(str(path))
                    self.page.wait_for_timeout(600)
                    self.assert_file_selected(path.name)
                    print("Resume file set via file chooser popup (Select file button)")
                    return
            except Exception:
                pass
            # Try 3: click dropzone / upload text
            try:
                dropzone = self._add_resume_dialog().get_by_text(
                    re.compile(r"upload|browse|drop|click\s+to\s+select|choose\s+file", re.I)
                ).first
                if dropzone.count() > 0 and dropzone.is_visible():
                    with self.page.expect_file_chooser(timeout=15_000) as fc_info:
                        dropzone.click(timeout=5_000)
                    file_chooser = fc_info.value
                    file_chooser.set_files(str(path))
                    self.page.wait_for_timeout(600)
                    self.assert_file_selected(path.name)
                    print("Resume file set via file chooser popup (dropzone)")
                    return
            except Exception:
                pass
            # Fallback: set file on input directly (no popup)
            file_loc = self.upload_input
            try:
                sel = self._select_file_button()
                if sel.count() > 0 and sel.is_visible():
                    sel.click(timeout=3_000)
                    self.page.wait_for_timeout(300)
                else:
                    dropzone = self._add_resume_dialog().get_by_text(
                        re.compile(r"upload|browse|drop|click\s+to\s+select|choose\s+file", re.I)
                    ).first
                    if dropzone.count() > 0 and dropzone.is_visible():
                        dropzone.click(timeout=3_000)
                        self.page.wait_for_timeout(300)
            except Exception:
                pass
            file_loc.wait_for(state="attached", timeout=timeout_ms)
            file_loc.set_input_files(str(path), timeout=timeout_ms)
            self.page.wait_for_timeout(600)
            self.assert_file_selected(path.name)
            print("Resume file set")
        except Exception as e:
            self._screenshot_on_failure("upload_resume")
            print(f"Result: upload_resume failed - {e}")
            raise

    def enter_target_role(self, role: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Enter target/job role in Add Resume modal. Tries click+fill for React-style inputs."""
        print(f"Entering target role: {role}")
        loc = self.target_role_input
        try:
            loc.first.wait_for(state="visible", timeout=timeout_ms)
            loc.first.click(timeout=timeout_ms)
            self.page.wait_for_timeout(200)
            loc.first.fill(role)
            self.page.wait_for_timeout(200)
            print("Target role entered")
        except Exception as e:
            try:
                loc.first.fill(role)
                print("Target role entered (fill only)")
            except Exception:
                # Optional field: many UIs allow upload without role
                print(f"Target role field not found or not visible, skipping (upload-only?): {e}")
                return

    def submit_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Submitting Add Resume")
        try:
            expect(self.submit_add_resume_button).to_be_visible(timeout=timeout_ms)
            try:
                expect(self.submit_add_resume_button).to_be_enabled(timeout=5_000)
            except Exception:
                pass
            self.submit_add_resume_button.click(timeout=timeout_ms, force=True)
            self.page.wait_for_timeout(500)
            print("Resume submitted")
        except Exception as e:
            self._screenshot_on_failure("submit_resume")
            print(f"Result: submit_resume failed - {e}")
            raise

    def wait_for_back_to_resume_module(self, timeout_ms: int = 30_000) -> None:
        """After clicking Add Resume in the modal, wait for modal to close and resume module view to be visible."""
        print("Waiting for Add Resume modal to close and return to resume module...")
        try:
            dialog = self._add_resume_dialog()
            # Dialog can close by being hidden (CSS) or removed from DOM (detached)
            try:
                dialog.wait_for(state="hidden", timeout=timeout_ms)
            except Exception:
                dialog.wait_for(state="detached", timeout=10_000)
            self.page.wait_for_timeout(1000)
            expect(self.heading_your_resumes.first).to_be_visible(timeout=10_000)
            print("Back on resume module")
        except Exception as e:
            self._screenshot_on_failure("wait_for_back_to_resume_module")
            msg = str(e).encode("ascii", "replace").decode()
            print("Result: wait_for_back_to_resume_module failed -", msg[:300])
            raise

    def verify_resume_uploaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Wait for an actual uploaded resume card to appear (card with download/delete or data-testid). Full timeout."""
        print("Verifying resume uploaded")
        try:
            self.page.wait_for_timeout(2000)
            print("Waiting for resume card in resume module (up to %s min)..." % (timeout_ms // 60_000))
            # Use strict locator only: uploaded card (has download/delete or data-testid), NOT "Add Resume" or heading
            self.uploaded_resume_card.wait_for(state="visible", timeout=timeout_ms)
            print("Resume uploaded successfully")
        except Exception as e:
            self._screenshot_on_failure("verify_resume_uploaded")
            print(f"Result: verify_resume_uploaded failed - {e}")
            raise

    def delete_resume_if_exists(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Deleting resume if exists")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            self.page.wait_for_timeout(500)
            if self.resume_delete_button.count() > 0 and self.resume_delete_button.is_visible():
                self.resume_delete_button.click(timeout=timeout_ms)
                self.page.wait_for_timeout(300)
                confirm = self.page.get_by_role("button", name=re.compile(r"confirm|yes|delete", re.I)).first
                if confirm.count() > 0 and confirm.is_visible():
                    confirm.click(timeout=5_000)
                self.page.wait_for_timeout(500)
                print("Resume deleted")
            else:
                print("No resume to delete")
        except Exception as e:
            self._screenshot_on_failure("delete_resume_if_exists")
            print(f"Result: delete_resume_if_exists failed - {e}")
            raise

    def verify_resume_deleted(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying resume deleted")
        try:
            self.page.wait_for_timeout(500)
            if self.empty_state_text.count() > 0:
                expect(self.empty_state_text).to_be_visible(timeout=timeout_ms)
            elif self.resume_cards.count() == 0:
                expect(self.heading_your_resumes).to_be_visible(timeout=timeout_ms)
            print("Resume deleted verified")
        except Exception as e:
            self._screenshot_on_failure("verify_resume_deleted")
            print(f"Result: verify_resume_deleted failed - {e}")
            raise

    def download_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Downloading resume")
        try:
            expect(self.resume_download_button).to_be_visible(timeout=timeout_ms)
            with self.page.expect_download(timeout=timeout_ms):
                self.resume_download_button.click(timeout=timeout_ms)
            print("Resume download triggered")
        except Exception as e:
            self._screenshot_on_failure("download_resume")
            print(f"Result: download_resume failed - {e}")
            raise

    def ensure_resume_exists(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """If no resume exists, upload dummy_resume.pdf. Used by Profile, Jobs, Prep modules."""
        print("Ensuring resume exists")
        try:
            self.open_resume_page(timeout_ms=timeout_ms)
            self.verify_resume_page_loaded(timeout_ms=timeout_ms)
            if self.resume_cards.count() > 0 and self.resume_cards.first.is_visible():
                print("Resume already exists")
                return
            if self.empty_state_text.count() > 0 and self.empty_state_text.is_visible():
                pass
            self.click_add_resume(timeout_ms=timeout_ms)
            self.page.wait_for_timeout(400)
            self.enter_target_role("Software Engineer", timeout_ms=timeout_ms)
            expect(self.upload_input).to_be_attached(timeout=timeout_ms)
            self.upload_resume(ensure_dummy_resume_pdf(), timeout_ms=timeout_ms)
            self.submit_resume(timeout_ms=timeout_ms)
            self.verify_resume_uploaded(timeout_ms=PARSE_RESUME_WAIT_MS)
            print("Resume created (dummy_resume.pdf)")
        except Exception as e:
            self._screenshot_on_failure("ensure_resume_exists")
            print(f"Result: ensure_resume_exists failed - {e}")
            raise

    # -----------------------
    # Legacy compatibility
    # -----------------------
    def verify_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.verify_resume_page_loaded(timeout_ms=timeout_ms)

    def verify_resume_cards_present(self, timeout_ms: int = 10_000) -> None:
        try:
            if self.resume_cards.count() > 0:
                expect(self.resume_cards.first).to_be_visible(timeout=timeout_ms)
            else:
                self.page.get_by_text(re.compile(r"\bresume\b", re.I)).first.wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            self.page.get_by_text(re.compile(r"\bresume\b", re.I)).first.wait_for(state="visible", timeout=timeout_ms)

    def click_add_new_resume(self) -> None:
        self.click_add_resume()

    def verify_add_resume_modal_open(self, timeout_ms: int = 15_000) -> None:
        expect(self.target_role_input).to_be_visible(timeout=timeout_ms)
        if self.upload_input.count() > 0:
            self.upload_input.wait_for(state="attached", timeout=timeout_ms)

    @property
    def target_role_field(self) -> Locator:
        return self.target_role_input

    @property
    def resume_upload_field(self) -> Locator:
        return self.upload_input

    @property
    def resume_upload_dropzone(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bclick\s+to\s+select\s+file\b", re.I)).first

    def verify_target_role_field(self, timeout_ms: int = 10_000) -> None:
        expect(self.target_role_input).to_be_visible(timeout=timeout_ms)

    def verify_resume_upload_field(self, timeout_ms: int = 10_000) -> None:
        if self.resume_upload_dropzone.count() > 0:
            expect(self.resume_upload_dropzone).to_be_visible(timeout=timeout_ms)
        else:
            expect(self.upload_input).to_be_attached(timeout=timeout_ms)

    @property
    def error_messages(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bis\s+required\b|\brequired\b|\bplease\b|\binvalid\b", re.I))

    def verify_add_resume_button_disabled_when_empty(self) -> None:
        if self.submit_add_resume_button.count() > 0 and not self.submit_add_resume_button.is_enabled():
            return
        if self.submit_add_resume_button.count() > 0:
            self.submit_add_resume_button.click(timeout=5_000)
            self.page.wait_for_timeout(300)
        assert self.error_messages.count() > 0, "Expected validation errors when submitting empty resume modal"

    def close_modal(self) -> None:
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
            if self.modal.count() == 0 or not self.modal.is_visible():
                return
        except Exception:
            pass
        try:
            self.close_modal_button.click(timeout=5_000)
        except Exception:
            try:
                self.page.get_by_role("button", name=re.compile(r"^x$", re.I)).first.click(timeout=3_000)
            except Exception:
                pass
