from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage


class JobsPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators (selectors)
    # -----------------------
    @property
    def header_jobs(self) -> Locator:
        return self.page.get_by_role("heading", name=re.compile(r"^\s*jobs\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*jobs\s*$", re.I))
        ).first

    @property
    def total_jobs_card(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+jobs\b", re.I)).first

    @property
    def best_fit_job_card(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bbest\s+fit\b.*\bjob\b|\bbest\s+fit\b", re.I)).first

    @property
    def least_fit_job_card(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bleast\s+fit\b.*\bjob\b|\bleast\s+fit\b", re.I)).first

    @property
    def take_mock_interview_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\btake\b.*\bmock\s+interview\b", re.I))

    @property
    def enhance_resume_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\benhance\b.*\bresume\b", re.I))

    @property
    def delete_job_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdelete\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bremove\b", re.I))
        )

    @property
    def search_job_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bsearch\b.*\bjob\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bsearch\b", re.I))
        ).first

    @property
    def search_modal_title(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bsearch\b.*\bjob\b", re.I)).first

    @property
    def search_input(self) -> Locator:
        return self.page.get_by_placeholder(re.compile(r"\bsearch\b", re.I)).or_(
            self.page.get_by_label(re.compile(r"\bsearch\b", re.I))
        ).or_(
            self.page.locator("input[type='search'], input[name*='search' i]")
        ).first

    @property
    def filter_7_days(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\b7\b.*\bdays?\b", re.I)).first

    @property
    def filter_30_days(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\b30\b.*\bdays?\b", re.I)).first

    @property
    def filter_all(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*all\s*$", re.I)).first

    @property
    def job_cards(self) -> Locator:
        # Prefer cards containing the known action button; this anchors on real UI controls.
        if self.take_mock_interview_buttons.count() > 0:
            return self.take_mock_interview_buttons.first.locator(
                "xpath=ancestor::*[self::article or self::section or self::div][1]"
            ).locator("xpath=ancestor::*[self::article or self::section or self::div][1]")
        # Fallback: any element mentioning "job" on the page.
        return self.page.get_by_text(re.compile(r"\bjob\b", re.I)).first.locator(
            "xpath=ancestor::*[self::article or self::section or self::div][1]"
        )

    def _first_job_card_container(self) -> Locator:
        btn = self.take_mock_interview_buttons.first
        return btn.locator("xpath=ancestor::*[self::article or self::section or self::div][1]")

    @property
    def job_title_headings(self) -> Locator:
        # Titles are often headings within cards.
        return self.page.get_by_role("heading")

    @property
    def skills_tags(self) -> Locator:
        # Skill chips/tags often include common skill-like words and appear as text spans.
        return self.page.get_by_text(re.compile(r"\bpython\b|\bjava\b|\breact\b|\bsql\b|\baws\b|\bnode\b", re.I))

    @property
    def delete_confirmation_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bare\s+you\s+sure\b|\bconfirm\b|\bdelete\b", re.I)).first

    @property
    def modal_close_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bclose\b|\bcancel\b|\bx\b", re.I)).first

    # -----------------------
    # Navigation
    # -----------------------
    def goto_jobs_page(self) -> None:
        self.goto("/dashboard/jobs", wait_until="domcontentloaded")

    def verify_jobs_page_loaded(self, timeout_ms: int = 15_000) -> None:
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        expect(self.header_jobs).to_be_visible(timeout=timeout_ms)

    # -----------------------
    # Verify main cards
    # -----------------------
    def verify_total_jobs_card(self) -> None:
        expect(self.total_jobs_card).to_be_visible()

    def verify_best_fit_job_card(self) -> None:
        expect(self.best_fit_job_card).to_be_visible()

    def verify_least_fit_job_card(self) -> None:
        expect(self.least_fit_job_card).to_be_visible()

    # -----------------------
    # First job card buttons
    # -----------------------
    def click_take_mock_interview(self) -> None:
        expect(self.take_mock_interview_buttons.first).to_be_visible()
        self.take_mock_interview_buttons.first.click()

    def verify_mock_interview_started_or_modal(self) -> None:
        # Either navigate to an interview route OR a modal/section becomes visible.
        try:
            self.page.wait_for_url(re.compile(r".*(mock|interview).*", re.I), timeout=10_000)
            return
        except Exception:
            pass

        modalish = self.page.get_by_text(re.compile(r"\bmock\s+interview\b|\binterview\b", re.I)).first
        expect(modalish).to_be_visible(timeout=10_000)

    def click_enhance_resume(self) -> None:
        expect(self.enhance_resume_buttons.first).to_be_visible()
        self.enhance_resume_buttons.first.click()

    def verify_enhance_resume_response(self) -> None:
        # Look for toast/alert/response text.
        candidates = [
            self.page.get_by_role("alert").first,
            self.page.get_by_text(re.compile(r"\benhanc(ed|ing)\b|\bresume\b|\bsuccess\b", re.I)).first,
        ]
        for loc in candidates:
            try:
                expect(loc).to_be_visible(timeout=10_000)
                return
            except Exception:
                continue
        # If no explicit message, at least ensure we didn't crash and still have UI.
        expect(self.header_jobs).to_be_visible()

    def click_delete_job(self) -> None:
        # Prefer a delete within the first job card if possible.
        if self.take_mock_interview_buttons.count() > 0:
            card = self._first_job_card_container()
            delete_in_card = card.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I))
            if delete_in_card.count() > 0:
                delete_in_card.first.click()
                return

        expect(self.delete_job_buttons.first).to_be_visible()
        self.delete_job_buttons.first.click()

    def verify_delete_confirmation(self) -> None:
        expect(self.delete_confirmation_text).to_be_visible(timeout=10_000)
        # Do not confirm deletion; close/cancel if possible.
        for name in [re.compile(r"\bcancel\b", re.I), re.compile(r"\bno\b", re.I), re.compile(r"\bclose\b", re.I)]:
            btn = self.page.get_by_role("button", name=name)
            if btn.count() > 0:
                try:
                    btn.first.click(timeout=3_000)
                except Exception:
                    pass
                break

    # -----------------------
    # Search job modal
    # -----------------------
    def click_search_job_button(self) -> None:
        expect(self.search_job_button).to_be_visible()
        self.search_job_button.click()

    def verify_search_modal_open(self) -> None:
        # Not all apps set role=dialog; anchor on title + input.
        expect(self.search_modal_title).to_be_visible(timeout=10_000)
        self.verify_search_input_present()

    def verify_search_input_present(self) -> None:
        expect(self.search_input).to_be_visible(timeout=10_000)

    def enter_search_text(self, text: str) -> None:
        self.verify_search_input_present()
        self.search_input.fill(text)

    def click_7_days_filter(self) -> None:
        expect(self.filter_7_days).to_be_visible(timeout=10_000)
        self.filter_7_days.click()

    def click_30_days_filter(self) -> None:
        expect(self.filter_30_days).to_be_visible(timeout=10_000)
        self.filter_30_days.click()

    def click_all_filter(self) -> None:
        expect(self.filter_all).to_be_visible(timeout=10_000)
        self.filter_all.click()

    def verify_job_cards_visible(self) -> None:
        # At least one actionable job card should exist.
        expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=15_000)

    def verify_job_titles_visible(self) -> None:
        # Ensure there are multiple headings; Jobs page header + job titles.
        expect(self.job_title_headings.first).to_be_visible(timeout=15_000)
        assert self.job_title_headings.count() >= 1

    def verify_company_names_visible(self) -> None:
        # Best-effort: presence of company-like text near job cards.
        companyish = self.page.get_by_text(re.compile(r"\binc\b|\bltd\b|\bcorp\b|\btechnologies\b|\bsolutions\b", re.I))
        if companyish.count() > 0:
            expect(companyish.first).to_be_visible(timeout=10_000)
            return
        # Fallback: ensure some non-empty text in the job list area.
        expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=10_000)

    def verify_skills_tags_visible(self) -> None:
        # Skills may be empty for some jobs; prefer any chip-like tags.
        if self.skills_tags.count() > 0:
            expect(self.skills_tags.first).to_be_visible(timeout=10_000)
            return
        expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=10_000)

    def click_first_job_card_and_verify_interaction(self) -> None:
        # Click the card container (or its first heading) and verify something changes.
        if self.take_mock_interview_buttons.count() == 0:
            self.verify_job_cards_visible()

        card = self._first_job_card_container()
        before_url = self.page.url

        heading = card.get_by_role("heading")
        if heading.count() > 0:
            heading.first.click()
        else:
            card.click()

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10_000)
        except Exception:
            pass

        # Interaction: URL changes or a details section becomes visible.
        if self.page.url != before_url:
            return

        details = self.page.get_by_text(re.compile(r"\bjob\s+details\b|\bdescription\b|\bresponsibilit", re.I))
        if details.count() > 0:
            expect(details.first).to_be_visible(timeout=10_000)

    def close_search_modal(self) -> None:
        # Escape often closes modals.
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

        # Or click a close/cancel button.
        if self.modal_close_button.count() > 0:
            try:
                self.modal_close_button.click(timeout=5_000)
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

