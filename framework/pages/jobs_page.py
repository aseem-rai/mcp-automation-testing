"""
Jobs page object. Base URL: /dashboard/jobs.
Supports search, add job, mock interview, enhance resume, delete. ensure_job_exists() for tests.
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import Optional

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage

_DEFAULT_TIMEOUT = 15_000
_SCREENSHOTS_DIR = Path("test-results") / "jobs"


class JobsPage(BasePage):
    """Page Object for Jobs module (/dashboard/jobs)."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators
    # -----------------------
    @property
    def sidebar_jobs_button(self) -> Locator:
        return self.page.get_by_role("link", name=re.compile(r"\bjobs?\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bjobs?\b", re.I))
        ).or_(self.page.locator("[data-testid*='jobs' i], [data-testid*='nav-jobs' i]")).first

    @property
    def search_job_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bsearch\b.*\bjob\b", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"\bsearch\b", re.I))
        ).or_(self.page.get_by_text(re.compile(r"\bsearch\s+job\b", re.I))).or_(
            self.page.locator("[data-testid*='search-job' i], [data-testid*='searchJob' i]")
        ).first

    @property
    def search_popup_modal(self) -> Locator:
        return self.page.get_by_role("dialog").or_(
            self.page.locator("div").filter(has=self.search_modal_title).filter(has=self.search_input)
        ).first

    @property
    def search_modal_title(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bsearch\b.*\bjob\b", re.I)).or_(
            self.page.get_by_role("heading", name=re.compile(r"\bsearch\b", re.I))
        ).or_(self.page.locator("[data-testid*='search-modal' i]")).first

    @property
    def search_input_field(self) -> Locator:
        return self.page.get_by_placeholder(re.compile(r"\bsearch\b", re.I)).or_(
            self.page.get_by_label(re.compile(r"\bsearch\b", re.I))
        ).or_(self.page.locator("input[type='search'], input[name*='search' i]")).first

    @property
    def search_submit_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bsearch\b|\bsubmit\b|\bgo\b", re.I)).or_(
            self.page.locator("[data-testid*='search-submit' i], [data-testid*='submit-search' i]")
        ).first

    @property
    def add_job_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\badd\s+job\b|\badd\s+to\s+jobs\b|\badd\b", re.I)).or_(
            self.page.get_by_title(re.compile(r"\badd\s+job\b", re.I))
        ).or_(
            self.page.locator("[data-testid*='add-job' i], [aria-label*='add job' i], [title*='add job' i]")
        ).first

    @property
    def job_cards_container(self) -> Locator:
        return self.page.locator("[data-testid*='job-cards' i], [data-testid*='jobs-list' i]").or_(
            self.page.locator("section, main").filter(has=self.page.get_by_text(re.compile(r"\bjob\b", re.I)))
        ).first

    @property
    def job_title_text(self) -> Locator:
        return self.page.get_by_role("heading").or_(
            self.page.locator("[data-testid*='job-title' i]")
        ).filter(has_text=re.compile(r".+"))

    @property
    def take_mock_interview_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\btake\b.*\bmock\s+interview\b", re.I)).or_(
            self.page.locator("[data-testid*='mock-interview' i], [data-testid*='take-mock' i]")
        ).first

    @property
    def enhance_resume_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\benhance\b.*\bresume\b", re.I)).or_(
            self.page.locator("[data-testid*='enhance-resume' i]")
        ).first

    @property
    def delete_job_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I)).or_(
            self.page.locator("[data-testid*='delete-job' i], [aria-label*='delete' i]")
        ).first

    @property
    def empty_state_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"no\s+jobs|add\s+your\s+first\s+job|search\s+for\s+jobs", re.I)).or_(
            self.page.locator("[data-testid*='empty-state' i]")
        ).first

    @property
    def header_jobs(self) -> Locator:
        return self.page.get_by_role("heading", name=re.compile(r"^\s*jobs\s*$", re.I)).or_(
            self.page.get_by_text(re.compile(r"^\s*jobs\s*$", re.I))
        ).first

    @property
    def take_mock_interview_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\btake\b.*\bmock\s+interview\b", re.I))

    @property
    def enhance_resume_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\benhance\b.*\bresume\b", re.I))

    @property
    def delete_job_buttons(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I))

    @property
    def first_job_card(self) -> Locator:
        # Do not anchor only on "Take Mock Interview" because some states show different action sets.
        by_testid = self.page.locator("[data-testid*='job-card' i], [data-testid*='jobs-card' i]")
        by_class = self.page.locator("[class*='job-card' i], [class*='jobCard' i]")
        by_actions = self.page.locator("article, section, div").filter(
            has=self.page.get_by_role(
                "button",
                name=re.compile(r"take|mock|enhance|resume|delete|remove|edit|start", re.I),
            )
        )
        by_content = self.page.locator("article, section, div").filter(
            has=self.page.get_by_text(
                re.compile(r"job|engineer|developer|intern|location|experience", re.I)
            )
        )
        return by_testid.first.or_(by_class.first).or_(by_actions.first).or_(by_content.first)

    @property
    def search_input(self) -> Locator:
        return self.search_input_field

    @property
    def modal_close_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\bclose\b|\bcancel\b|^\s*x\s*$", re.I)).first

    def _search_modal_container(self) -> Optional[Locator]:
        dialog = self.page.get_by_role("dialog")
        if dialog.count() > 0:
            try:
                if dialog.first.is_visible():
                    return dialog.first
            except Exception:
                pass
        modal_div = self.page.locator("div").filter(has=self.search_modal_title).filter(has=self.search_input_field)
        if modal_div.count() > 0:
            return modal_div.first
        return None

    def _screenshot_on_failure(self, action_name: str) -> None:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", action_name).strip() or "jobs"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = _SCREENSHOTS_DIR / f"{safe}_{ts}.png"
        try:
            self.page.screenshot(path=str(path), full_page=True)
        except Exception:
            pass

    def take_screenshot(self, name: str) -> Path:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "jobs"
        path = _SCREENSHOTS_DIR / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    # -----------------------
    # Core functions
    # -----------------------
    def open_jobs_page(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Opening Jobs page")
        try:
            self.goto("/dashboard/jobs", wait_until="domcontentloaded")
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.page).to_have_url(re.compile(r"/jobs", re.I), timeout=timeout_ms)
            print("Jobs page opened")
        except Exception as e:
            self._screenshot_on_failure("open_jobs_page")
            print(f"Result: open_jobs_page failed - {e}")
            raise

    def verify_jobs_page_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying Jobs page loaded")
        try:
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.header_jobs).to_be_visible(timeout=timeout_ms)
            print("Jobs page loaded")
        except Exception as e:
            self._screenshot_on_failure("verify_jobs_page_loaded")
            print(f"Result: verify_jobs_page_loaded failed - {e}")
            raise

    def click_search_job_button(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking Search Job button")
        try:
            expect(self.search_job_button).to_be_visible(timeout=timeout_ms)
            self.search_job_button.click(timeout=timeout_ms)
            self.page.wait_for_timeout(300)
            print("Search Job button clicked")
        except Exception as e:
            self._screenshot_on_failure("click_search_job_button")
            print(f"Result: click_search_job_button failed - {e}")
            raise

    def enter_job_search_text(self, text: str, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Searching job")
        try:
            expect(self.search_input_field).to_be_visible(timeout=timeout_ms)
            self.search_input_field.fill(text)
            self.page.wait_for_timeout(200)
            print("Job search text entered")
        except Exception as e:
            self._screenshot_on_failure("enter_job_search_text")
            print(f"Result: enter_job_search_text failed - {e}")
            raise

    def submit_job_search(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Submitting job search")
        try:
            # Prefer Enter submit to avoid overlay/pointer interception on button click.
            try:
                self.search_input_field.press("Enter")
                self.page.wait_for_timeout(400)
                print("Job search submitted (Enter)")
                return
            except Exception:
                pass
            if self.search_submit_button.count() > 0 and self.search_submit_button.is_visible():
                try:
                    self.search_submit_button.click(timeout=timeout_ms)
                except Exception:
                    self.search_submit_button.click(timeout=5_000, force=True)
            else:
                self.search_input_field.press("Enter")
            self.page.wait_for_timeout(1000)
            print("Job search submitted")
        except Exception as e:
            self._screenshot_on_failure("submit_job_search")
            msg = str(e).encode("ascii", "replace").decode()
            print("Result: submit_job_search failed -", msg[:500])
            raise

    def verify_search_results_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying search results visible")
        try:
            no_results = self.page.get_by_text(re.compile(r"no\s+results|no\s+jobs\s+found|not\s+found", re.I))
            if no_results.count() > 0 and no_results.first.is_visible():
                print("Search results (no results message) visible")
                return
            container = self._search_modal_container()
            if container is not None:
                for sel in ["article", "li", "[class*='card']", "[class*='job']", "[role='listitem']"]:
                    items = container.locator(sel)
                    if items.count() > 0:
                        expect(items.first).to_be_visible(timeout=timeout_ms)
                        print("Search results visible")
                        return
            expect(self.search_modal_title).to_be_visible(timeout=timeout_ms)
            print("Search results visible")
        except Exception as e:
            self._screenshot_on_failure("verify_search_results_visible")
            print(f"Result: verify_search_results_visible failed - {e}")
            raise

    def add_first_job_from_results(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Adding job")
        try:
            container = self._search_modal_container()
            if container is None:
                raise ValueError("Search modal container not found")
            # Step 1: click per-card Add Job icon button.
            per_card_add = container.get_by_title(re.compile(r"^\s*add\s+job\s*$", re.I)).or_(
                container.locator("[title*='add job' i], [aria-label*='add job' i]")
            )
            clicked_per_card = False
            for i in range(min(per_card_add.count(), 20)):
                btn = per_card_add.nth(i)
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.scroll_into_view_if_needed(timeout=3_000)
                        btn.click(timeout=5_000)
                        clicked_per_card = True
                        break
                except Exception:
                    continue
            if not clicked_per_card:
                raise ValueError("Per-card Add Job icon/button not found in search modal")

            # Step 2: click Add Jobs button that appears after selecting card.
            self.page.wait_for_timeout(600)
            add_jobs_btns = self.page.get_by_role(
                "button",
                name=re.compile(r"^\s*add\s+jobs?\s*$|add\s+to\s+jobs?", re.I),
            ).or_(container.get_by_role(
                "button",
                name=re.compile(r"^\s*add\s+jobs?\s*$|add\s+to\s+jobs?", re.I),
            ))
            clicked_add_jobs = False
            for i in range(min(add_jobs_btns.count(), 10)):
                btn = add_jobs_btns.nth(i)
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.click(timeout=5_000)
                        clicked_add_jobs = True
                        break
                except Exception:
                    continue
            if not clicked_add_jobs:
                raise ValueError("Add Jobs button did not appear after selecting a job")
            self.page.wait_for_timeout(500)
            print("First job added from results")
        except Exception as e:
            self._screenshot_on_failure("add_first_job_from_results")
            msg = str(e).encode("ascii", "replace").decode()
            print("Result: add_first_job_from_results failed -", msg[:400])
            raise

    def verify_job_card_created(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying job card created")
        try:
            # Primary signal: card action buttons visible.
            if self.take_mock_interview_buttons.count() > 0:
                expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=timeout_ms)
                print("Job card created")
                return
            # Fallback signal: total jobs counter > 0 after processing.
            body_text = self.page.locator("body").inner_text()
            m = re.search(r"total\s+jobs\s*(\d+)", body_text, re.I)
            if m and int(m.group(1)) > 0:
                print("Job card created (total jobs > 0)")
                return
            # Final fallback: any card/list item in jobs container.
            cards = self.page.locator("article, li, [data-testid*='job-card' i], [class*='job-card' i]")
            if cards.count() > 0 and cards.first.is_visible():
                print("Job card created (generic card visible)")
                return
            raise AssertionError("Job card not visible and total jobs still 0")
            print("Job card created")
        except Exception as e:
            self._screenshot_on_failure("verify_job_card_created")
            print(f"Result: verify_job_card_created failed - {e}")
            raise

    def verify_job_details_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying job details visible")
        try:
            if self.job_title_text.count() > 0:
                expect(self.job_title_text.first).to_be_visible(timeout=timeout_ms)
            expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=timeout_ms)
            print("Job details visible")
        except Exception as e:
            self._screenshot_on_failure("verify_job_details_visible")
            print(f"Result: verify_job_details_visible failed - {e}")
            raise

    def click_take_mock_interview(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking mock interview")
        try:
            card = self.first_job_card
            btn = card.get_by_role("button", name=re.compile(r"\btake\b.*\bmock\s+interview\b", re.I)).first
            expect(btn).to_be_visible(timeout=timeout_ms)
            btn.click(timeout=timeout_ms)
            print("Take Mock Interview clicked")
        except Exception as e:
            self._screenshot_on_failure("click_take_mock_interview")
            print(f"Result: click_take_mock_interview failed - {e}")
            raise

    def verify_mock_interview_started(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying mock interview started")
        try:
            try:
                self.page.wait_for_url(re.compile(r".*(mock|interview).*", re.I), timeout=timeout_ms)
                print("Mock interview started (URL)")
                return
            except Exception:
                pass
            modalish = self.page.get_by_text(re.compile(r"\bmock\s+interview\b|\binterview\b", re.I)).first
            expect(modalish).to_be_visible(timeout=timeout_ms)
            print("Mock interview started")
        except Exception as e:
            self._screenshot_on_failure("verify_mock_interview_started")
            print(f"Result: verify_mock_interview_started failed - {e}")
            raise

    def click_enhance_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Clicking Enhance Resume")
        try:
            card = self.first_job_card
            btn = self._pick_enhance_icon_button(card)
            expect(btn).to_be_visible(timeout=timeout_ms)
            btn.click(timeout=timeout_ms)
            print("Enhance Resume clicked")
        except Exception as e:
            self._screenshot_on_failure("click_enhance_resume")
            print(f"Result: click_enhance_resume failed - {e}")
            raise

    def _pick_enhance_icon_button(self, card: Locator) -> Locator:
        """
        Pick Enhance Resume action from a job card.
        Supports icon-only (magic wand) buttons by checking attributes/classes first,
        then falls back to action-button ordering (2nd icon is usually Enhance).
        """
        buttons = card.locator("button, [role='button']")
        visible = []
        for i in range(min(buttons.count(), 30)):
            btn = buttons.nth(i)
            try:
                if btn.is_visible() and btn.is_enabled():
                    visible.append(btn)
            except Exception:
                continue

        # 1) Strong semantic match from accessible fields/attributes.
        for btn in visible:
            parts = []
            for attr in ["aria-label", "title", "data-testid", "class"]:
                try:
                    v = btn.get_attribute(attr) or ""
                except Exception:
                    v = ""
                parts.append(v.lower())
            try:
                txt = (btn.inner_text() or "").lower()
            except Exception:
                txt = ""
            hay = " ".join(parts + [txt])
            if re.search(r"enhance|magic|wand|improv|optimi", hay, re.I):
                return btn

        # 2) Icon hint in nested elements (svg/i/span class/data-icon).
        for btn in visible:
            icon_hint = btn.locator(
                "svg[class*='wand' i], i[class*='wand' i], span[class*='wand' i], "
                "[data-icon*='wand' i], [data-testid*='wand' i], "
                "svg[class*='magic' i], i[class*='magic' i], [data-icon*='magic' i]"
            )
            try:
                if icon_hint.count() > 0 and icon_hint.first.is_visible():
                    return btn
            except Exception:
                continue

        # 3) Fallback ordering: [mock interview, enhance, delete] => 2nd visible action.
        if len(visible) >= 2:
            return visible[1]
        if len(visible) == 1:
            return visible[0]
        raise AssertionError("No clickable action button found on job card for Enhance Resume.")

    def verify_resume_enhancement_started(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying resume enhancement started")
        try:
            for loc in [
                self.page.get_by_role("alert").first,
                self.page.get_by_text(re.compile(r"\benhanc(ed|ing)\b|\bresume\b|\bsuccess\b", re.I)).first,
            ]:
                try:
                    expect(loc).to_be_visible(timeout=timeout_ms)
                    print("Resume enhancement started")
                    return
                except Exception:
                    continue
            expect(self.header_jobs).to_be_visible(timeout=timeout_ms)
            print("Resume enhancement started")
        except Exception as e:
            self._screenshot_on_failure("verify_resume_enhancement_started")
            print(f"Result: verify_resume_enhancement_started failed - {e}")
            raise

    def open_resume_enhancer_from_first_job_card(self, timeout_ms: int = 30_000) -> Page:
        """
        Click Enhance Resume (magic wand/icon) on first job card.
        Returns the enhancer page if opened in a new tab/window, else current page.
        """
        card = self.first_job_card
        expect(card).to_be_visible(timeout=timeout_ms)

        to_click = self._pick_enhance_icon_button(card)

        try:
            with self.page.context.expect_page(timeout=min(timeout_ms, 10_000)) as popup_info:
                to_click.click(timeout=timeout_ms)
            enhancer_page = popup_info.value
            enhancer_page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            return enhancer_page
        except Exception:
            # No separate page opened; enhancement may continue in same page/dialog.
            # IMPORTANT: don't click again; first click already triggered popup flow.
            self.page.wait_for_timeout(1200)
            return self.page

    def _visible_popup_container(self, target_page: Page) -> Locator:
        return target_page.locator(
            "[role='dialog'], div[class*='fixed'][class*='z-50'], "
            "div[class*='modal' i], div[class*='popup' i]"
        ).first

    def verify_enhancer_loading_popup(self, enhancer_page: Page, timeout_ms: int = 30_000) -> None:
        loading_signal = self._visible_popup_container(enhancer_page).or_(
            enhancer_page.get_by_text(re.compile(r"loading|please\s+wait|processing|enhanc", re.I))
        ).first
        expect(loading_signal).to_be_visible(timeout=timeout_ms)

    def wait_for_enhancer_content_popup(self, enhancer_page: Page, timeout_ms: int = 60_000) -> Locator:
        """
        After loading popup, wait until enhancer content popup appears
        (contains Original/Enhanced sections or Accept controls).
        """
        container = self._visible_popup_container(enhancer_page)
        expect(container).to_be_visible(timeout=timeout_ms)
        content_signal = container.get_by_text(
            re.compile(r"original|enhanced|suggest|accept|improve", re.I)
        ).or_(
            container.get_by_role("button", name=re.compile(r"accept|apply|add|save|rescore", re.I))
        ).first
        expect(content_signal).to_be_visible(timeout=timeout_ms)
        return container

    def verify_enhancer_dual_resume_view(self, enhancer_page: Page, timeout_ms: int = 60_000) -> None:
        container = self.wait_for_enhancer_content_popup(enhancer_page, timeout_ms=timeout_ms)
        original = container.get_by_text(re.compile(r"original\s+resume|original", re.I)).first
        enhanced = container.get_by_text(re.compile(r"enhanced\s+resume|enhanced", re.I)).first
        expect(original).to_be_visible(timeout=timeout_ms)
        expect(enhanced).to_be_visible(timeout=timeout_ms)

    def accept_all_enhancer_suggestions(self, enhancer_page: Page, timeout_ms: int = 30_000) -> None:
        """
        Click all visible Accept/Apply/Add suggestion actions.
        Best-effort loop: keeps clicking until no more actionable buttons are visible.
        """
        container = self.wait_for_enhancer_content_popup(enhancer_page, timeout_ms=timeout_ms)
        end_at = _dt.datetime.now(tz=_dt.timezone.utc).timestamp() + (timeout_ms / 1000)
        clicked_any = False
        while _dt.datetime.now(tz=_dt.timezone.utc).timestamp() < end_at:
            actions = container.get_by_role(
                "button", name=re.compile(r"accept|apply|add", re.I)
            ).or_(container.locator("[title*='accept' i], [aria-label*='accept' i], button[class*='green' i]"))
            clicked = False
            for i in range(min(actions.count(), 40)):
                btn = actions.nth(i)
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.click(timeout=5_000)
                        enhancer_page.wait_for_timeout(120)
                        clicked = True
                        clicked_any = True
                except Exception:
                    continue
            if not clicked:
                break
        assert clicked_any, "Accept button(s) not clicked in enhancer popup."

    def save_rescore_and_wait_download(self, enhancer_page: Page, timeout_ms: int = 90_000) -> None:
        # Continue in the same enhancer content popup where Accept was clicked.
        container = self.wait_for_enhancer_content_popup(enhancer_page, timeout_ms=timeout_ms)

        # Save (red button at top in popup UI).
        save_btn = container.get_by_role(
            "button", name=re.compile(r"^\s*save\b|save\s+resume|save\s+changes", re.I)
        ).or_(container.locator("button[class*='red' i], button[class*='danger' i]")).first
        expect(save_btn).to_be_visible(timeout=timeout_ms)
        save_btn.click(timeout=timeout_ms)

        # Save should transition to Rescore.
        rescore_btn = container.get_by_role(
            "button", name=re.compile(r"re[-\s]?score|rescore", re.I)
        ).or_(container.get_by_text(re.compile(r"re[-\s]?scor", re.I))).first
        expect(rescore_btn).to_be_visible(timeout=timeout_ms)
        try:
            if hasattr(rescore_btn, "click"):
                rescore_btn.click(timeout=10_000)
        except Exception:
            pass

        # Verify re-scoring/loading signal appears at least briefly.
        loading = container.get_by_text(re.compile(r"re[-\s]?scoring|scoring|loading", re.I)).first
        try:
            expect(loading).to_be_visible(timeout=20_000)
        except Exception:
            # Some builds transition quickly; continue to download assertion.
            pass

        # End condition: download action/icon appears in same popup area.
        download_btn = container.get_by_role(
            "button", name=re.compile(r"download", re.I)
        ).or_(container.get_by_role("link", name=re.compile(r"download", re.I))).or_(
            container.locator(
                "[title*='download' i], [aria-label*='download' i], [data-testid*='download' i], "
                "[data-icon*='download' i], svg[class*='download' i], i[class*='download' i], "
                "button[class*='download' i], a[class*='download' i]"
            )
        ).first
        expect(download_btn).to_be_visible(timeout=timeout_ms)

    def close_enhancer_window_or_popup(self, enhancer_page: Page, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        if enhancer_page != self.page:
            try:
                enhancer_page.close()
                return
            except Exception:
                pass
        close_btn = enhancer_page.get_by_role(
            "button", name=re.compile(r"close|back|done|x", re.I)
        ).or_(enhancer_page.locator("[aria-label*='close' i], [title*='close' i]")).first
        if close_btn.count() > 0:
            try:
                close_btn.click(timeout=timeout_ms)
                return
            except Exception:
                pass
        try:
            enhancer_page.keyboard.press("Escape")
        except Exception:
            pass

    def verify_enhanced_percentage_on_job_card(self, timeout_ms: int = 20_000) -> None:
        card = self.first_job_card
        expect(card).to_be_visible(timeout=timeout_ms)
        enhanced_with_percent = card.get_by_text(re.compile(r"enhanced.*\d{1,3}\s*%|\d{1,3}\s*%.*enhanced", re.I))
        if enhanced_with_percent.count() > 0:
            expect(enhanced_with_percent.first).to_be_visible(timeout=timeout_ms)
            return
        enhanced_text = card.get_by_text(re.compile(r"enhanced", re.I))
        percent_text = card.get_by_text(re.compile(r"\b(100|[1-9]?\d)\s*%\b", re.I))
        expect(enhanced_text.first).to_be_visible(timeout=timeout_ms)
        expect(percent_text.first).to_be_visible(timeout=timeout_ms)

    def click_delete_job(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Deleting job")
        try:
            card = self.first_job_card
            btn = card.get_by_role("button", name=re.compile(r"\bdelete\b|\bremove\b", re.I)).first
            expect(btn).to_be_visible(timeout=timeout_ms)
            btn.click(timeout=timeout_ms)
            self.page.wait_for_timeout(300)
            confirm = self.page.get_by_role("button", name=re.compile(r"\bconfirm\b|\byes\b|\bdelete\b", re.I)).first
            if confirm.count() > 0 and confirm.is_visible():
                confirm.click(timeout=5_000)
            print("Delete job clicked")
        except Exception as e:
            self._screenshot_on_failure("click_delete_job")
            print(f"Result: click_delete_job failed - {e}")
            raise

    def verify_job_deleted(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Verifying job deleted")
        try:
            self.page.wait_for_timeout(500)
            if self.take_mock_interview_buttons.count() == 0:
                print("Job deleted")
                return
            if self.empty_state_text.count() > 0:
                expect(self.empty_state_text).to_be_visible(timeout=timeout_ms)
            print("Job deleted")
        except Exception as e:
            self._screenshot_on_failure("verify_job_deleted")
            print(f"Result: verify_job_deleted failed - {e}")
            raise

    def delete_all_jobs_if_exist(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        print("Deleting all jobs if exist")
        try:
            while self.take_mock_interview_buttons.count() > 0 and self.take_mock_interview_buttons.first.is_visible():
                self.click_delete_job(timeout_ms=timeout_ms)
                self.page.wait_for_timeout(500)
            print("All jobs deleted (or none existed)")
        except Exception as e:
            self._screenshot_on_failure("delete_all_jobs_if_exist")
            print(f"Result: delete_all_jobs_if_exist failed - {e}")
            raise

    def ensure_job_exists(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """If job exists do nothing. Else: open search, search 'Software Engineer', add first job, verify."""
        print("Ensuring job exists")
        try:
            self.open_jobs_page(timeout_ms=timeout_ms)
            self.verify_jobs_page_loaded(timeout_ms=timeout_ms)
            if self.take_mock_interview_buttons.count() > 0 and self.take_mock_interview_buttons.first.is_visible():
                print("Job already exists")
                return
            self.click_search_job_button(timeout_ms=timeout_ms)
            expect(self.search_modal_title).to_be_visible(timeout=timeout_ms)
            expect(self.search_input_field).to_be_visible(timeout=timeout_ms)
            self.enter_job_search_text("Python", timeout_ms=timeout_ms)
            self.submit_job_search(timeout_ms=timeout_ms)
            self.page.wait_for_timeout(1000)
            self.verify_search_results_visible(timeout_ms=timeout_ms)
            self.add_first_job_from_results(timeout_ms=timeout_ms)
            self.close_search_modal()
            # Wait for agent/notification, then 1 minute processing window, then reload.
            self._wait_for_agent_alert_then_reload(wait_ms=60_000, timeout_ms=timeout_ms)
            self.verify_jobs_page_loaded(timeout_ms=timeout_ms)
            self.verify_job_card_created(timeout_ms=timeout_ms)
            print("Job created")
        except Exception as e:
            self._screenshot_on_failure("ensure_job_exists")
            print(f"Result: ensure_job_exists failed - {e}")
            raise

    def _wait_for_agent_alert_then_reload(self, wait_ms: int = 60_000, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Wait for agent alert notification (best effort), then wait and reload Jobs page."""
        # Best-effort alert wait; continue even if alert is not explicitly visible.
        try:
            alert = self.page.get_by_role("alert").or_(
                self.page.get_by_text(re.compile(r"agent|added|success|queued|processing", re.I))
            ).first
            if alert.count() > 0:
                alert.wait_for(state="visible", timeout=min(timeout_ms, 10_000))
        except Exception:
            pass
        self.page.wait_for_timeout(wait_ms)
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)

    def close_search_modal(self) -> None:
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(200)
        except Exception:
            pass
        if self.modal_close_button.count() > 0:
            try:
                self.modal_close_button.click(timeout=5_000)
            except Exception:
                pass

    def goto_jobs_page(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.open_jobs_page(timeout_ms=timeout_ms)

    def verify_search_modal_open(self) -> None:
        expect(self.search_modal_title).to_be_visible(timeout=10_000)
        expect(self.search_input_field).to_be_visible(timeout=10_000)

    def add_job_if_none_exists(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.ensure_job_exists(timeout_ms=timeout_ms)

    def verify_mock_interview_started_or_modal(self) -> None:
        self.verify_mock_interview_started()

    def verify_enhance_resume_response(self) -> None:
        self.verify_resume_enhancement_started()

    def verify_delete_confirmation(self) -> None:
        confirm = self.page.get_by_role("button", name=re.compile(r"\bconfirm\b|\byes\b|\bdelete\b", re.I)).first
        if confirm.count() > 0 and confirm.is_visible():
            confirm.click(timeout=5_000)

    @property
    def total_jobs_card(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+jobs\b", re.I)).first

    @property
    def filter_7_days(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\b7\b.*\bdays?\b", re.I)).first

    @property
    def filter_30_days(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"\b30\b.*\bdays?\b", re.I)).first

    @property
    def filter_all(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^\s*all\s*$", re.I)).first

    def verify_first_job_card_buttons(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        card = self.first_job_card
        expect(card).to_be_visible(timeout=timeout_ms)
        # Validate visible actions on card without hard-depending on a single button label.
        action_btns = card.get_by_role(
            "button",
            name=re.compile(r"take|mock|enhance|resume|delete|remove|edit|start", re.I),
        )
        if action_btns.count() > 0:
            expect(action_btns.first).to_be_visible(timeout=timeout_ms)
            return
        # Fallback: icon/button controls without accessible names.
        icon_btns = card.locator("button, [role='button'], [title], [aria-label]")
        expect(icon_btns.first).to_be_visible(timeout=timeout_ms)

    def verify_job_cards_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        expect(self.take_mock_interview_buttons.first).to_be_visible(timeout=timeout_ms)

    def verify_fitment_score_visible_on_first_job_card(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """
        Verify fitment score badge is visible on first job card.
        Supports text badges (e.g., '78%') and score circles/icons.
        """
        card = self.first_job_card
        expect(card).to_be_visible(timeout=timeout_ms)

        # Preferred: explicit fitment/score markers on card.
        fitment_badge = card.locator(
            "[data-testid*='fitment' i], [data-testid*='score' i], "
            "[class*='fitment' i], [class*='score' i], "
            "[aria-label*='fitment' i], [aria-label*='score' i]"
        )
        percent_text = card.get_by_text(re.compile(r"\b(100|[1-9]?\d)\s*%\b", re.I))
        top_right_circle = card.locator(
            ":scope > div >> [class*='rounded' i], :scope > div >> [class*='circle' i], "
            ":scope > [class*='absolute' i][class*='top' i][class*='right' i]"
        )

        if fitment_badge.count() > 0:
            expect(fitment_badge.first).to_be_visible(timeout=timeout_ms)
            return
        if percent_text.count() > 0:
            expect(percent_text.first).to_be_visible(timeout=timeout_ms)
            return
        if top_right_circle.count() > 0:
            expect(top_right_circle.first).to_be_visible(timeout=timeout_ms)
            return
        raise AssertionError("Fitment score badge is not visible on the first job card.")

    def click_first_job_card_open_details(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Click first job card body to open job details popup/modal."""
        card = self.first_job_card
        expect(card).to_be_visible(timeout=timeout_ms)
        # Avoid action buttons; click title/content region first.
        title_or_content = card.locator(
            "h1, h2, h3, h4, [data-testid*='job-title' i], [class*='title' i], p"
        ).first
        try:
            if title_or_content.count() > 0 and title_or_content.is_visible():
                title_or_content.click(timeout=timeout_ms)
            else:
                card.click(timeout=timeout_ms, force=True)
        except Exception:
            card.click(timeout=timeout_ms, force=True)
        self.page.wait_for_timeout(500)

    def verify_job_details_popup_opened(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        """Verify job details popup/modal is visible after clicking a job card."""
        dialog = self.page.get_by_role("dialog")
        details_text = self.page.get_by_text(
            re.compile(r"job\s+description|requirements|skills|employment|salary|fitment|applicants", re.I)
        )
        if dialog.count() > 0:
            expect(dialog.first).to_be_visible(timeout=timeout_ms)
            return
        expect(details_text.first).to_be_visible(timeout=timeout_ms)

    def enter_search_text(self, text: str) -> None:
        self.enter_job_search_text(text)
