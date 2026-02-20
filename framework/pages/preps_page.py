from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage


class PrepsPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators
    # -----------------------
    @property
    def heading_preps(self) -> Locator:
        return self.page.get_by_role("heading", name=re.compile(r"^\s*preps\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*preps\s*$", re.I))
        ).first

    @property
    def new_prep_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"new\s+prep|add\s+prep|create\s+jd|\+.*prep", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"new\s+prep|add\s+prep", re.I))
        ).or_(self.page.get_by_text(re.compile(r"new\s+prep|add\s+prep|\+\s*new\s+prep", re.I))).first

    @property
    def new_prep_modal(self) -> Locator:
        return self.page.get_by_role("dialog").or_(
            self.page.get_by_text(re.compile(r"create\s+jd|upload\s+jd", re.I)).first
        )

    @property
    def tab_create_jd(self) -> Locator:
        return self.page.get_by_role("tab", name=re.compile(r"create\s+jd", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*create\s+jd\s*$", re.I))
        ).first

    @property
    def tab_upload_jd(self) -> Locator:
        return self.page.get_by_role("tab", name=re.compile(r"upload\s+jd", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*upload\s+jd\s*$", re.I))
        ).first

    @property
    def role_field(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\brole\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\brole\b", re.I))
        ).first

    @property
    def skills_field(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\bskills?\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\bskills?\b", re.I))
        ).first

    @property
    def experience_field(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\bexperience\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\bexperience\b", re.I))
        ).first

    @property
    def additional_details_field(self) -> Locator:
        return self.page.get_by_label(re.compile(r"additional\s+details|details", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"additional|details", re.I))
        ).first

    @property
    def create_jd_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"create\s+jd", re.I)).first

    @property
    def next_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*next\s*$", re.I)).first

    @property
    def jd_upload_input(self) -> Locator:
        dialog = self.page.get_by_role("dialog")
        in_dialog = dialog.locator("input[type='file']")
        if in_dialog.count() > 0:
            return in_dialog.first
        return self.page.locator("input[type='file']").first

    @property
    def jd_cards(self) -> Locator:
        return self.page.get_by_text(re.compile(r"AI\s+Engineer|JD|job\s+description", re.I))

    @property
    def button_take_mock_interview(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"take\s+mock\s+interview|mock\s+interview", re.I)).or_(
            self.page.get_by_text(re.compile(r"take\s+mock\s+interview", re.I))
        ).first

    @property
    def button_enhance_resume(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"enhance\s+resume", re.I)).or_(
            self.page.get_by_text(re.compile(r"enhance\s+resume", re.I))
        ).first

    @property
    def button_delete(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*delete\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*delete\s*$", re.I))
        ).first

    # -----------------------
    # Actions
    # -----------------------
    @property
    def preps_sidebar_link(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"^\s*preps\s*$", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"^\s*preps\s*$", re.I))
        ).first

    def open_preps_page(self) -> None:
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

    def verify_prep_action_buttons(self) -> None:
        # Buttons may be in a card menu; verify at least one of each action is present on the page.
        take_interview = self.page.get_by_text(re.compile(r"take\s+mock\s+interview|mock\s+interview", re.I)).first
        enhance = self.page.get_by_text(re.compile(r"enhance\s+resume", re.I)).first
        delete = self.page.get_by_text(re.compile(r"^\s*delete\s*$", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"delete", re.I))
        ).first
        expect(take_interview).to_be_visible(timeout=10_000)
        expect(enhance).to_be_visible(timeout=10_000)
        expect(delete).to_be_visible(timeout=10_000)
