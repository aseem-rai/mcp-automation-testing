"""Create JD component for Prep module."""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

_DEFAULT_TIMEOUT = 15_000


class PrepCreateJDComponent:
    def __init__(self, page: Page):
        self.page = page

    @property
    def create_jd_tab(self) -> Locator:
        return self.page.get_by_role("tab", name=re.compile(r"create\s+jd", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*create\s+jd\s*$", re.I))
        ).or_(self.page.locator("[data-testid*='create-jd' i]")).first

    @property
    def role_input(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\brole\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\brole\b", re.I))
        ).or_(self.page.locator("input[name*='role' i]")).first

    @property
    def skills_input(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\bskills?\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\bskills?\b", re.I))
        ).or_(self.page.locator("input[name*='skill' i], textarea[name*='skill' i]")).first

    @property
    def experience_input(self) -> Locator:
        return self.page.get_by_label(re.compile(r"\bexperience\b", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"\bexperience\b", re.I))
        ).or_(self.page.locator("input[name*='experience' i]")).first

    @property
    def create_jd_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"create\s+jd", re.I)).or_(
            self.page.locator("[data-testid*='create-jd' i]")
        ).first

    def open_create_jd_tab(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Opening Create JD tab")
        expect(self.create_jd_tab).to_be_visible(timeout=timeout_ms)
        self.create_jd_tab.click(timeout=timeout_ms)
        self.page.wait_for_timeout(300)
        print("Create JD tab opened")

    def enter_role(self, role: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Entering role")
        expect(self.role_input).to_be_visible(timeout=timeout_ms)
        self.role_input.fill(role)
        print("Role entered")

    def enter_skills(self, skills: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Entering skills")
        expect(self.skills_input).to_be_visible(timeout=timeout_ms)
        self.skills_input.fill(skills)
        print("Skills entered")

    def enter_experience(self, exp: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Entering experience")
        expect(self.experience_input).to_be_visible(timeout=timeout_ms)
        self.experience_input.fill(exp)
        print("Experience entered")

    def click_create_jd(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Creating JD")
        expect(self.create_jd_button).to_be_visible(timeout=timeout_ms)
        self.create_jd_button.click(timeout=timeout_ms)
        self.page.wait_for_timeout(500)
        print("Create JD clicked")

    def verify_jd_created(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying JD created")
        jd_cards = self.page.get_by_text(re.compile(r"software\s+engineer|JD|job\s+description", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"take\s+mock\s+interview", re.I))
        )
        expect(jd_cards.first).to_be_visible(timeout=timeout_ms)
        print("JD created verified")
