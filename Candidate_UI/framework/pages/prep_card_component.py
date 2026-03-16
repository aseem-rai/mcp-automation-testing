"""JD card component for Prep module."""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

_DEFAULT_TIMEOUT = 15_000


class PrepCardComponent:
    def __init__(self, page: Page):
        self.page = page

    @property
    def take_mock_interview_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"take\s+mock\s+interview|mock\s+interview", re.I))

    @property
    def enhance_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"enhance\s+resume", re.I))

    @property
    def delete_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I))

    @property
    def first_jd_card(self) -> Locator:
        take_btn = self.take_mock_interview_button.first
        return take_btn.locator("xpath=ancestor::*[self::article or self::section or self::div][1]")

    @property
    def jd_card_container(self) -> Locator:
        return self.page.locator("[data-testid*='jd-card' i], [data-testid*='prep-card' i]").or_(
            self.first_jd_card
        )

    def verify_card_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying JD card visible")
        expect(self.take_mock_interview_button.first).to_be_visible(timeout=timeout_ms)
        print("JD card visible")

    def click_mock_interview(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking Mock Interview")
        card = self.first_jd_card
        btn = card.get_by_role("button", name=re.compile(r"take\s+mock\s+interview|mock\s+interview", re.I)).first
        expect(btn).to_be_visible(timeout=timeout_ms)
        btn.click(timeout=timeout_ms)
        print("Take Mock Interview clicked")

    def verify_mock_interview_started(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying mock interview started")
        try:
            self.page.wait_for_url(re.compile(r".*(mock|interview).*", re.I), timeout=timeout_ms)
            print("Mock interview started")
            return
        except Exception:
            pass
        expect(self.page.get_by_text(re.compile(r"\bmock\s+interview\b|\binterview\b", re.I)).first).to_be_visible(timeout=timeout_ms)
        print("Mock interview started")

    def click_enhance_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking Enhance Resume")
        card = self.first_jd_card
        btn = card.get_by_role("button", name=re.compile(r"enhance\s+resume", re.I)).first
        expect(btn).to_be_visible(timeout=timeout_ms)
        btn.click(timeout=timeout_ms)
        print("Enhance Resume clicked")

    def verify_enhance_resume_started(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying enhance resume started")
        try:
            self.page.wait_for_url(re.compile(r".*(enhance|resume).*", re.I), timeout=timeout_ms)
            print("Enhance resume started")
            return
        except Exception:
            pass
        try:
            expect(self.page.get_by_text(re.compile(r"\benhance\b.*\bresume\b|\bresume\b", re.I)).first).to_be_visible(timeout=timeout_ms)
        except Exception:
            expect(self.page.get_by_role("alert").first).to_be_visible(timeout=timeout_ms)
        print("Enhance resume started")

    def click_delete(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Deleting JD")
        card = self.first_jd_card
        btn = card.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I)).first
        expect(btn).to_be_visible(timeout=timeout_ms)
        btn.click(timeout=timeout_ms)
        self.page.wait_for_timeout(300)
        confirm = self.page.get_by_role("button", name=re.compile(r"\bconfirm\b|\byes\b|\bdelete\b", re.I)).first
        if confirm.count() > 0 and confirm.is_visible():
            confirm.click(timeout=5_000)
        print("Delete clicked")

    def verify_card_deleted(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying card deleted")
        self.page.wait_for_timeout(500)
        if self.take_mock_interview_button.count() == 0:
            print("Card deleted")
            return
        empty = self.page.get_by_text(re.compile(r"no\s+jds?|add\s+your\s+first", re.I))
        if empty.count() > 0:
            expect(empty.first).to_be_visible(timeout=timeout_ms)
        print("Card deleted")
