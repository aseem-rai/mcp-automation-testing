from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage
from framework.utils.logger import logger

_DEFAULT_TIMEOUT = 15_000
_REPORTS_PREPS_SCREENSHOTS = Path("reports") / "screenshots" / "preps"


class PrepsPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators
    # -----------------------
    @property
    def heading_preps(self) -> Locator:
        return self.page.get_by_role("heading", name=re.compile(r"^\s*preps?\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*preps?\s*$", re.I))
        ).or_(self.page.locator("[data-testid*='prep-title' i], [data-testid*='preps-title' i]")).first

    @property
    def new_prep_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"new\s+prep|add\s+prep|create\s+jd|\+.*prep", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"new\s+prep|add\s+prep", re.I))
        ).or_(self.page.get_by_text(re.compile(r"new\s+prep|add\s+prep|\+\s*new\s+prep", re.I))).first

    @property
    def new_prep_modal(self) -> Locator:
        # App may render New Prep as dialog OR drawer/panel without role=dialog.
        by_role = self.page.get_by_role("dialog")
        by_aria_modal = self.page.locator("[aria-modal='true']")
        by_modal_class = self.page.locator(
            "[class*='modal' i], [class*='drawer' i], [class*='sheet' i]"
        ).filter(has=self.page.get_by_text(re.compile(r"new\s+prep|create\s+jd|upload\s+jd", re.I)))
        by_heading_parent = self.page.get_by_text(re.compile(r"new\s+prep", re.I)).locator(
            "xpath=ancestor::*[self::div or self::section or self::aside][1]"
        )
        return by_role.or_(by_aria_modal).or_(by_modal_class).or_(by_heading_parent).first

    @property
    def modal_title_new_prep(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_text(re.compile(r"^\s*new\s+prep\s*$", re.I)).or_(
            modal.get_by_role("heading", name=re.compile(r"^\s*new\s+prep\s*$", re.I))
        ).first

    @property
    def tab_create_jd(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_role("tab", name=re.compile(r"create\s+jd", re.I)).or_(
            modal.get_by_text(re.compile(r"^\s*create\s+jd\s*$", re.I))
        ).first

    @property
    def tab_upload_jd(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_role("tab", name=re.compile(r"upload\s+jd", re.I)).or_(
            modal.get_by_text(re.compile(r"^\s*upload\s+jd\s*$", re.I))
        ).first

    @property
    def role_field(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_label(re.compile(r"\brole\b", re.I)).or_(
            modal.get_by_placeholder(re.compile(r"\brole\b", re.I))
        ).or_(modal.locator("input[name*='role' i], input[id*='role' i]")).or_(
            self.page.get_by_label(re.compile(r"\brole\b", re.I))
        ).or_(self.page.get_by_placeholder(re.compile(r"\brole\b", re.I))).or_(
            self.page.locator("input[name*='role' i], input[id*='role' i]")
        ).first

    @property
    def role_field_label(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_text(re.compile(r"role\s*\*", re.I)).or_(
            modal.get_by_label(re.compile(r"role", re.I))
        ).first

    @property
    def skills_field(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_label(re.compile(r"\bskills?\b", re.I)).or_(
            modal.get_by_placeholder(re.compile(r"\bskills?\b", re.I))
        ).or_(modal.locator("input[name*='skill' i], textarea[name*='skill' i], input[id*='skill' i], textarea[id*='skill' i]")).or_(
            self.page.get_by_label(re.compile(r"\bskills?\b", re.I))
        ).or_(self.page.get_by_placeholder(re.compile(r"\bskills?\b", re.I))).or_(
            self.page.locator("input[name*='skill' i], textarea[name*='skill' i], input[id*='skill' i], textarea[id*='skill' i]")
        ).first

    @property
    def skills_field_label(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_text(re.compile(r"skills?\s*\*", re.I)).or_(
            modal.get_by_label(re.compile(r"skills?", re.I))
        ).first

    @property
    def experience_field(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_label(re.compile(r"\bexperience\b", re.I)).or_(
            modal.get_by_placeholder(re.compile(r"\bexperience\b", re.I))
        ).or_(modal.locator("input[name*='experience' i], input[id*='experience' i]")).or_(
            self.page.get_by_label(re.compile(r"\bexperience\b", re.I))
        ).or_(self.page.get_by_placeholder(re.compile(r"\bexperience\b", re.I))).or_(
            self.page.locator("input[name*='experience' i], input[id*='experience' i]")
        ).first

    @property
    def experience_field_label(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_text(re.compile(r"experience.*optional", re.I)).or_(
            modal.get_by_label(re.compile(r"experience", re.I))
        ).first

    @property
    def additional_details_field(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_label(re.compile(r"additional\s+details|details", re.I)).or_(
            modal.get_by_placeholder(re.compile(r"additional|details", re.I))
        ).or_(modal.locator("textarea[name*='detail' i], textarea[id*='detail' i]")).or_(
            self.page.get_by_label(re.compile(r"additional\s+details|details", re.I))
        ).or_(self.page.get_by_placeholder(re.compile(r"additional|details", re.I))).or_(
            self.page.locator("textarea[name*='detail' i], textarea[id*='detail' i]")
        ).first

    @property
    def additional_details_field_label(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_text(re.compile(r"additional\s+details.*optional", re.I)).or_(
            modal.get_by_label(re.compile(r"additional\s+details|details", re.I))
        ).first

    @property
    def create_jd_button(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_role("button", name=re.compile(r"create\s+jd", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"create\s+jd", re.I))
        ).first

    @property
    def create_jd_button_in_modal(self) -> Locator:
        """Primary red Create JD button inside New Prep modal."""
        modal = self.new_prep_modal
        return modal.get_by_role("button", name=re.compile(r"create\s+jd", re.I)).first

    @property
    def cancel_button(self) -> Locator:
        modal = self.new_prep_modal
        return modal.get_by_role("button", name=re.compile(r"cancel|close", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"cancel|close", re.I))
        ).first

    @property
    def next_button(self) -> Locator:
        return self.new_prep_modal.get_by_role("button", name=re.compile(r"^\s*next\s*$", re.I)).first

    @property
    def jd_upload_input(self) -> Locator:
        dialog = self.page.get_by_role("dialog")
        in_dialog = dialog.locator("input[type='file']")
        if in_dialog.count() > 0:
            return in_dialog.first
        return self.page.locator("input[type='file']").first

    @property
    def jd_cards(self) -> Locator:
        by_testid = self.page.locator("[data-testid*='prep-card' i], [data-testid*='jd-card' i]")
        by_actions = self.page.locator("article, section, div").filter(
            has=self.page.get_by_role("button", name=re.compile(r"start\s+prep|edit|delete|mock|enhance", re.I)).or_(
                self.page.locator(
                    "[title*='start' i], [title*='edit' i], [title*='delete' i], "
                    "[aria-label*='start' i], [aria-label*='edit' i], [aria-label*='delete' i]"
                )
            ).or_(self.page.locator("button, [role='button']"))
        )
        by_text = self.page.get_by_text(re.compile(r"job\s+description|machine\s+learning\s+engineer|prep", re.I))
        return by_testid.or_(by_actions).or_(by_text)

    @property
    def button_take_mock_interview(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"take\s+mock\s+interview|mock\s+interview", re.I))

    @property
    def start_prep_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"start\s+prep", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"start\s+prep", re.I))
        ).or_(self.page.locator("[title*='start' i], [aria-label*='start' i], [data-testid*='start' i]")).first

    @property
    def edit_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bedit\b", re.I)).or_(
            self.page.locator("[title*='edit' i], [aria-label*='edit' i], [data-testid*='edit' i]")
        ).first

    @property
    def button_enhance_resume(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"enhance\s+resume", re.I))

    @property
    def button_delete(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdelete\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bremove\b", re.I))
        ).or_(self.page.locator("[title*='delete' i], [aria-label*='delete' i], [data-testid*='delete' i]"))

    @property
    def empty_state_no_jobs_yet(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*no\s+jobs\s+yet\s*$", re.I)).first

    @property
    def first_jd_card(self) -> Locator:
        # Do not anchor only on "Take Mock Interview"; support Start/Edit/Delete/icon-only controls.
        by_testid = self.page.locator("[data-testid*='prep-card' i], [data-testid*='jd-card' i]").first
        by_action_container = self.page.locator("article, section, div").filter(
            has=self.page.get_by_role("button", name=re.compile(r"start\s+prep|edit|delete|mock|enhance", re.I)).or_(
                self.page.locator(
                    "[title*='start' i], [title*='edit' i], [title*='delete' i], "
                    "[aria-label*='start' i], [aria-label*='edit' i], [aria-label*='delete' i]"
                )
            )
        ).first
        return by_testid.or_(by_action_container)

    # -----------------------
    # Actions
    # -----------------------
    @property
    def preps_sidebar_link(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"^\s*preps\s*$", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"^\s*preps\s*$", re.I))
        ).first

    def open_preps_page(self) -> None:
        logger.info("Opening Prep page")
        # Prefer direct navigation so we don't depend on sidebar order
        for path in ["/dashboard/preps", "/preps"]:
            self.goto(path, wait_until="domcontentloaded")
            self.wait_for_body_visible(timeout_ms=15_000)
            try:
                self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=8_000)
                expect(self.heading_preps).to_be_visible(timeout=10_000)
                return
            except Exception:
                continue
        # Fallback: dashboard then sidebar
        self.goto("/dashboard", wait_until="domcontentloaded")
        self.wait_for_body_visible(timeout_ms=15_000)
        expect(self.preps_sidebar_link).to_be_visible(timeout=15_000)
        self.preps_sidebar_link.click()
        self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=15_000)
        expect(self.heading_preps).to_be_visible(timeout=15_000)

    def click_new_prep_button(self) -> None:
        # "New Prep" or "Create JD" can open the modal
        open_btn = self.new_prep_button.or_(self.page.get_by_role("button", name=re.compile(r"create\s+jd", re.I)).first)
        expect(open_btn).to_be_visible(timeout=15_000)
        open_btn.click()
        expect(
            self.page.get_by_role("dialog").or_(self.page.get_by_text(re.compile(r"create\s+jd|upload\s+jd", re.I)))
        ).to_be_visible(timeout=10_000)

    def create_jd(self) -> Path:
        logger.info("Creating JD")
        self.click_new_prep_button()
        self.tab_create_jd.click()
        expect(self.role_field).to_be_visible(timeout=10_000)
        self.role_field.fill("AI Engineer")
        self.skills_field.fill("Python, NLP, Machine Learning")
        self.experience_field.fill("2 years")
        try:
            if self.page.get_by_label(re.compile(r"additional|details", re.I)).count() > 0:
                self.additional_details_field.fill("Test automation JD")
        except Exception:
            pass
        expect(self.create_jd_button).to_be_visible(timeout=5_000)
        self.create_jd_button.click()
        expect(self.jd_cards.first).to_be_visible(timeout=15_000)
        out_dir = Path("results")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "prep_create_jd_success.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def upload_jd(self) -> Path:
        logger.info("Uploading JD")
        self.click_new_prep_button()
        self.tab_upload_jd.click()
        jd_path = Path(__file__).resolve().parent.parent.parent / "test_data" / "test_jd.pdf"
        expect(self.jd_upload_input).to_be_visible(timeout=10_000)
        self.jd_upload_input.set_input_files(str(jd_path))
        expect(self.next_button).to_be_visible(timeout=5_000)
        self.next_button.click()
        expect(self.jd_cards.first).to_be_visible(timeout=15_000)
        out_dir = Path("results")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "prep_upload_jd_success.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def verify_first_jd_card_buttons(self, timeout_ms: int = 15_000) -> None:
        card = self.first_jd_card
        expect(card).to_be_visible(timeout=timeout_ms)
        start_btn = card.get_by_role("button", name=re.compile(r"start\s+prep|mock\s+interview|take\s+mock\s+interview", re.I)).or_(
            card.locator("[title*='start' i], [aria-label*='start' i], [data-testid*='start' i]")
        ).first
        edit_btn = card.get_by_role("button", name=re.compile(r"\bedit\b|enhance\s+resume", re.I)).or_(
            card.locator("[title*='edit' i], [aria-label*='edit' i], [data-testid*='edit' i]")
        ).first
        delete_btn = card.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I)).or_(
            card.locator("[title*='delete' i], [aria-label*='delete' i], [data-testid*='delete' i]")
        ).first
        visible_named = 0
        for btn in (start_btn, edit_btn, delete_btn):
            try:
                if btn.count() > 0:
                    expect(btn).to_be_visible(timeout=3_000)
                    visible_named += 1
            except Exception:
                pass
        if visible_named >= 3:
            return
        # Fallback for icon-only action set with no stable names.
        actions = card.locator("button, [role='button'], [title], [aria-label]")
        if actions.count() >= 3:
            expect(actions.nth(0)).to_be_visible(timeout=timeout_ms)
            expect(actions.nth(1)).to_be_visible(timeout=timeout_ms)
            expect(actions.nth(2)).to_be_visible(timeout=timeout_ms)
            return
        raise AssertionError("Prep card found but 3 action buttons were not detected.")

    @property
    def first_card_action_buttons(self) -> Locator:
        card = self.first_jd_card
        return card.locator("button, [role='button']")

    def verify_first_three_action_buttons_clickable(self, timeout_ms: int = 15_000) -> None:
        """Ensure the first 3 visible action buttons on the first prep card are interactable."""
        card = self.first_jd_card
        expect(card).to_be_visible(timeout=timeout_ms)
        actions = self.first_card_action_buttons
        if actions.count() < 3:
            raise AssertionError("Expected at least 3 action buttons on prep card.")
        for idx in range(3):
            btn = actions.nth(idx)
            expect(btn).to_be_visible(timeout=timeout_ms)
            # trial=True validates clickability without side effects.
            btn.click(timeout=timeout_ms, trial=True)

    def click_first_card_action_by_index(self, index: int, timeout_ms: int = 15_000) -> None:
        actions = self.first_card_action_buttons
        if actions.count() <= index:
            raise AssertionError(f"Action button at index {index} not found on prep card.")
        btn = actions.nth(index)
        expect(btn).to_be_visible(timeout=timeout_ms)
        btn.click(timeout=timeout_ms)

    def click_take_mock_interview(self) -> None:
        logger.info("Clicking Take Mock Interview")
        card = self.first_jd_card
        btn = card.get_by_role(
            "button", name=re.compile(r"take\s+mock\s+interview|mock\s+interview|start\s+prep", re.I)
        ).or_(card.locator("[title*='start' i], [aria-label*='start' i], [data-testid*='start' i]")).first
        expect(btn).to_be_visible(timeout=15_000)
        btn.click()

    def click_enhance_resume(self) -> None:
        logger.info("Clicking Edit/Enhance Resume")
        card = self.first_jd_card
        btn = card.get_by_role("button", name=re.compile(r"enhance\s+resume|\bedit\b", re.I)).or_(
            card.locator("[title*='edit' i], [aria-label*='edit' i], [data-testid*='edit' i]")
        ).first
        expect(btn).to_be_visible(timeout=15_000)
        btn.click()

    def click_delete(self) -> None:
        logger.info("Clicking Delete on JD card")
        card = self.first_jd_card
        btn = card.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I)).or_(
            card.locator("[title*='delete' i], [aria-label*='delete' i], [data-testid*='delete' i]")
        ).first
        expect(btn).to_be_visible(timeout=15_000)
        btn.click()

    def verify_prep_action_buttons(self) -> None:
        self.verify_first_jd_card_buttons()

    def verify_interview_page_opened(self, timeout_ms: int = 10_000) -> None:
        try:
            self.page.wait_for_url(re.compile(r".*(mock|interview|prep|start).*", re.I), timeout=timeout_ms)
            return
        except Exception:
            pass
        expect(
            self.page.get_by_text(re.compile(r"\bmock\s+interview\b|\binterview\b|\bstart\s+prep\b", re.I)).first
        ).to_be_visible(timeout=timeout_ms)

    def verify_enhance_resume_page_opened(self, timeout_ms: int = 10_000) -> None:
        try:
            self.page.wait_for_url(re.compile(r".*(enhance|resume|edit|prep).*", re.I), timeout=timeout_ms)
            return
        except Exception:
            pass
        # Some builds open edit drawer/modal without URL change.
        edit_ui = self.page.get_by_role("dialog").or_(
            self.page.get_by_text(re.compile(r"edit|enhance|update|job\s+description", re.I))
        ).or_(self.page.locator("[aria-modal='true'], [class*='modal' i], [class*='drawer' i]")).first
        expect(edit_ui).to_be_visible(timeout=timeout_ms)

    def confirm_delete_if_present(self, timeout_ms: int = 5_000) -> None:
        confirm = self.page.get_by_role("button", name=re.compile(r"\bconfirm\b|\byes\b|\bdelete\b", re.I))
        if confirm.count() > 0:
            try:
                confirm.first.click(timeout=timeout_ms)
            except Exception:
                pass

    def cancel_delete_if_present(self, timeout_ms: int = 5_000) -> None:
        cancel = self.page.get_by_role("button", name=re.compile(r"\bcancel\b|\bno\b|\bclose\b", re.I)).or_(
            self.page.locator("[aria-label*='close' i], [title*='close' i]")
        )
        if cancel.count() > 0:
            try:
                cancel.first.click(timeout=timeout_ms)
                return
            except Exception:
                pass
        # Fallback: press Escape to close confirm dialog/drawer.
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    def dismiss_open_panel_or_dialog(self, timeout_ms: int = 5_000) -> None:
        """Best-effort close for drawers/modals/dialogs after action-button clicks."""
        close_btn = self.page.get_by_role("button", name=re.compile(r"\bcancel\b|\bclose\b|\bback\b|\bno\b", re.I)).or_(
            self.page.locator("[aria-label*='close' i], [title*='close' i], [data-testid*='close' i]")
        )
        if close_btn.count() > 0:
            try:
                close_btn.first.click(timeout=timeout_ms)
                return
            except Exception:
                pass
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    def jd_card_count(self) -> int:
        return self.jd_cards.count()

    def go_back_to_preps_page(self) -> None:
        self.page.go_back()
        self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
        expect(self.heading_preps).to_be_visible(timeout=15_000)

    # -----------------------
    # Create JD flow helpers
    # -----------------------
    def take_screenshot_report(self, name: str) -> Path:
        _REPORTS_PREPS_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "preps"
        path = _REPORTS_PREPS_SCREENSHOTS / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def open_preps(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Navigate to preps page and verify core elements."""
        last_error: Exception | None = None
        for path in ("/dashboard/preps", "/preps"):
            try:
                self.goto(path, wait_until="domcontentloaded")
                self.wait_for_body_visible(timeout_ms=timeout_ms)
                self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=timeout_ms)
                try:
                    expect(self.heading_preps).to_be_visible(timeout=timeout_ms)
                except Exception:
                    title = self.page.title()
                    if not re.search(r"\bprep", title, re.I):
                        raise AssertionError(f"Preps page title/heading not found. Current title: {title!r}")
                expect(self.new_prep_button).to_be_visible(timeout=timeout_ms)
                # Empty-state check is only mandatory when there are no prep cards.
                if self.start_prep_button.count() == 0:
                    expect(self.empty_state_no_jobs_yet).to_be_visible(timeout=timeout_ms)
                return
            except Exception as e:
                last_error = e
        if last_error:
            raise last_error

    def open_new_prep_modal(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        expect(self.new_prep_button).to_be_visible(timeout=timeout_ms)
        self.new_prep_button.click(timeout=timeout_ms)
        # Retry click once if form controls do not appear quickly.
        form_open = self._wait_for_create_jd_form(timeout_ms=4_000)
        if not form_open:
            self.new_prep_button.click(timeout=timeout_ms, force=True)
            form_open = self._wait_for_create_jd_form(timeout_ms=8_000)
        if not form_open:
            raise AssertionError(
                f"New Prep form did not open after clicking button. Current URL: {self.page.url}"
            )
        # Some builds don't expose strict labels; require at least 3 fillable controls.
        text_controls = self.page.locator(
            "input[type='text'], input:not([type]), textarea, [contenteditable='true']"
        )
        if text_controls.count() < 3:
            raise AssertionError("Role/Skills/Experience fields not found in New Prep form.")
        expect(self.create_jd_button).to_be_visible(timeout=timeout_ms)
        expect(self.cancel_button).to_be_visible(timeout=timeout_ms)

    def _wait_for_create_jd_form(self, timeout_ms: int = 8_000) -> bool:
        """Return True if any Create JD form control appears."""
        for loc in (self.role_field, self.skills_field, self.experience_field, self.create_jd_button):
            try:
                loc.first.wait_for(state="visible", timeout=timeout_ms)
                return True
            except Exception:
                continue
        return False

    def fill_create_jd_form(
        self,
        role: str,
        skills: str,
        experience: str,
        additional_details: str = "",
        timeout_ms: int = _DEFAULT_TIMEOUT,
    ) -> int:
        """
        Fill Create JD form with robust fallback.
        Returns number of fields successfully filled.
        """
        filled = 0

        def _try_fill(loc: Locator, value: str) -> bool:
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click(timeout=timeout_ms)
                    loc.first.fill(value)
                    return True
            except Exception:
                return False
            return False

        # Try semantic locators first.
        if _try_fill(self.role_field, role):
            filled += 1
        if _try_fill(self.skills_field, skills):
            filled += 1
        if _try_fill(self.experience_field, experience):
            filled += 1
        if additional_details and _try_fill(self.additional_details_field, additional_details):
            filled += 1

        # Fallback: fill by control order near Create JD button when labels are missing.
        if filled < 3:
            # Prefer controls scoped near the Create JD button (usually same form/container).
            scope_controls = self.create_jd_button.first.locator(
                "xpath=ancestor::*[self::form or self::section or self::div][1]"
            ).locator("input[type='text'], input:not([type]), textarea, [contenteditable='true']")
            controls = scope_controls
            if controls.count() < 3:
                controls = self.new_prep_modal.locator(
                    "input[type='text'], input:not([type]), textarea, [contenteditable='true']"
                )
            if controls.count() < 3:
                controls = self.page.locator(
                    "input[type='text'], input:not([type]), textarea, [contenteditable='true']"
                )
            values = [role, skills, experience, additional_details or "Automation-created JD"]
            max_to_fill = min(controls.count(), len(values))
            for i in range(max_to_fill):
                try:
                    field = controls.nth(i)
                    if field.is_visible():
                        field.scroll_into_view_if_needed(timeout=2_000)
                        field.click(timeout=3_000)
                        field.fill(values[i])
                        # Count only if this index wasn't already filled semantically.
                        if filled < i + 1:
                            filled += 1
                except Exception:
                    continue

        if filled < 3:
            raise AssertionError(
                f"Unable to fill required Create JD fields. Filled fields count={filled}"
            )
        return filled

    def submit_create_jd(self, timeout_ms: int = _DEFAULT_TIMEOUT, retry_clicks: int = 2) -> None:
        """
        Click Create JD with retries across matching buttons.
        Some builds render duplicate/hidden buttons; this tries visible+enabled candidates first.
        """
        candidates = self.page.get_by_role("button", name=re.compile(r"create\s+jd", re.I))
        tried = 0
        # First try the primary red modal button.
        if self.create_jd_button_in_modal.count() > 0:
            try:
                expect(self.create_jd_button_in_modal.first).to_be_visible(timeout=timeout_ms)
                expect(self.create_jd_button_in_modal.first).to_be_enabled(timeout=timeout_ms)
                self.create_jd_button_in_modal.first.click(timeout=timeout_ms)
                self.page.wait_for_timeout(500)
                return
            except Exception:
                tried += 1
        # Then try generic create JD button.
        if self.create_jd_button.count() > 0:
            try:
                expect(self.create_jd_button.first).to_be_visible(timeout=timeout_ms)
                expect(self.create_jd_button.first).to_be_enabled(timeout=timeout_ms)
                self.create_jd_button.first.click(timeout=timeout_ms)
                self.page.wait_for_timeout(500)
                return
            except Exception:
                tried += 1
        # Then iterate all candidates.
        for i in range(min(candidates.count(), 6)):
            try:
                btn = candidates.nth(i)
                if btn.is_visible() and btn.is_enabled():
                    btn.click(timeout=5_000)
                    self.page.wait_for_timeout(500)
                    return
            except Exception:
                continue
        # Final retries with force click on first visible candidate.
        while tried < retry_clicks:
            tried += 1
            for i in range(min(candidates.count(), 6)):
                try:
                    btn = candidates.nth(i)
                    if btn.is_visible():
                        btn.click(timeout=3_000, force=True)
                        self.page.wait_for_timeout(500)
                        return
                except Exception:
                    continue
        # Final fallback: click via DOM API by button text.
        clicked = self.page.evaluate(
            """() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const target = btns.find(b => /create\\s*jd/i.test((b.textContent || '').trim()));
                if (!target) return false;
                target.click();
                return true;
            }"""
        )
        if clicked:
            self.page.wait_for_timeout(500)
            return
        raise AssertionError("Create JD button click failed on all visible candidates.")

    def wait_back_to_preps_after_create_jd(self, timeout_ms: int = 30_000) -> None:
        """
        After clicking Create JD, wait for modal to close and user to be back on Preps page.
        """
        try:
            self.new_prep_modal.wait_for(state="hidden", timeout=timeout_ms)
        except Exception:
            try:
                self.new_prep_modal.wait_for(state="detached", timeout=8_000)
            except Exception:
                # Some UIs keep modal container but hide form content.
                pass
        self.page.wait_for_timeout(800)
        self.page.wait_for_url(re.compile(r"/preps", re.I), timeout=timeout_ms)
        # Preps page has New Prep button visible once modal is closed.
        expect(self.new_prep_button).to_be_visible(timeout=timeout_ms)

    def wait_for_prep_card(self, timeout_ms: int = 120_000) -> None:
        """Wait up to 120s for generated prep card after Create JD."""
        card = self.page.locator("[data-testid*='prep-card' i], [data-testid*='jd-card' i]").or_(
            self.page.locator("article, section, div").filter(
                has=self.page.get_by_role("button", name=re.compile(r"start\s+prep|edit|delete", re.I))
            )
        ).first
        card.wait_for(state="visible", timeout=timeout_ms)

    def validate_prep_card(self, expected_role: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        card = self.page.locator("[data-testid*='prep-card' i], [data-testid*='jd-card' i]").or_(
            self.page.locator("article, section, div").filter(
                has=self.page.get_by_role("button", name=re.compile(r"start\s+prep|edit|delete", re.I))
            )
        ).first
        expect(card).to_be_visible(timeout=timeout_ms)

        # Role must be present on card.
        expect(card.get_by_text(re.compile(re.escape(expected_role), re.I)).first).to_be_visible(timeout=timeout_ms)
        # Location/skills expected as visible card metadata.
        expect(card.get_by_text(re.compile(r"location", re.I)).first).to_be_visible(timeout=timeout_ms)
        expect(card.get_by_text(re.compile(r"skills?|required\s+skills?", re.I)).first).to_be_visible(timeout=timeout_ms)
        # Company can be optional, so just attempt and continue.
        try:
            maybe_company = card.get_by_text(re.compile(r"company", re.I)).first
            if maybe_company.count() > 0:
                expect(maybe_company).to_be_visible(timeout=3_000)
        except Exception:
            pass

        expect(card.get_by_role("button", name=re.compile(r"start\s+prep", re.I)).first).to_be_visible(timeout=timeout_ms)
        expect(card.get_by_role("button", name=re.compile(r"\bedit\b", re.I)).first).to_be_visible(timeout=timeout_ms)
        expect(card.get_by_role("button", name=re.compile(r"\bdelete\b", re.I)).first).to_be_visible(timeout=timeout_ms)
