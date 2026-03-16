"""
Dashboard page object. Base URL: /dashboard.
Uses robust selectors: get_by_role, get_by_text, data-testid, aria-label.
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from framework.pages.base_page import BasePage
from framework.utils.logger import logger

_DEFAULT_TIMEOUT = 15_000
_SCREENSHOTS_DIR = Path("test-results") / "dashboard"


class DashboardPage(BasePage):
    """Page Object for /dashboard."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    # -----------------------
    # Locators (robust: role, text, data-testid, aria-label)
    # -----------------------
    @property
    def welcome_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I)).or_(
            self.page.get_by_role("heading", name=re.compile(r"welcome\s+back", re.I))
        ).or_(self.page.locator("[data-testid='welcome-text']")).or_(
            self.page.locator("[aria-label*='welcome' i]")
        ).first

    @property
    def stats_total_activities(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+activities\b", re.I)).or_(
            self.page.locator("[data-testid*='total-activities' i], [data-testid*='totalActivities' i]")
        ).or_(self.page.locator("[aria-label*='total activities' i]")).first

    @property
    def stats_total_preps(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+preps?\b", re.I)).or_(
            self.page.locator("[data-testid*='total-preps' i], [data-testid*='totalPreps' i]")
        ).or_(self.page.locator("[aria-label*='total preps' i]")).first

    @property
    def stats_total_interviews(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\btotal\s+interviews?\b", re.I)).or_(
            self.page.locator("[data-testid*='total-interviews' i], [data-testid*='totalInterviews' i]")
        ).or_(self.page.locator("[aria-label*='total interviews' i]")).first

    @property
    def stats_job_applications(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\b(applied\s+jobs?|job\s+applications?)\b", re.I)).or_(
            self.page.locator(
                "[data-testid*='applied-jobs' i], [data-testid*='job-applications' i], [data-testid*='jobs-count' i]"
            )
        ).or_(self.page.locator("[aria-label*='job applications' i], [aria-label*='applied jobs' i]")).first

    @property
    def stats_resume(self) -> Locator:
        by_resume_card = self.page.locator("article, section, div").filter(
            has=self.page.get_by_text(re.compile(r"^\s*resumes?\s*$", re.I))
        ).filter(
            has=self.page.get_by_role("button", name=re.compile(r"add\s+resume", re.I)).or_(
                self.page.get_by_role("link", name=re.compile(r"add\s+resume", re.I))
            )
        )
        return by_resume_card.first.or_(
            self.page.get_by_text(re.compile(r"\b(total\s+resumes?|resume\s+stats?|resumes?\s+enhanced|resumes?)\b", re.I))
        ).or_(
            self.page.locator("[data-testid*='resume-stats' i], [data-testid*='total-resumes' i], [data-testid*='resume-count' i]")
        ).or_(self.page.locator("[aria-label*='resume stats' i], [aria-label*='total resumes' i], [aria-label*='resumes enhanced' i]")).first

    @property
    def stats_goals(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\b(total\s+goals?|goals?)\b", re.I)).or_(
            self.page.locator("[data-testid*='total-goals' i], [data-testid*='goals-count' i], [data-testid*='goals-stats' i]")
        ).or_(self.page.locator("[aria-label*='goals' i], [aria-label*='total goals' i]")).first

    @property
    def button_find_jobs(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"find\s+jobs", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"find\s+jobs", re.I))
        ).or_(self.page.get_by_text(re.compile(r"find\s+jobs", re.I))).or_(
            self.page.locator("[data-testid*='find-jobs' i], [data-testid*='findJobs' i]")
        ).first

    @property
    def button_add_resume(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"add\s+resume", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"add\s+resume", re.I))
        ).or_(self.page.get_by_text(re.compile(r"add\s+resume", re.I))).or_(
            self.page.locator("[data-testid*='add-resume' i], [data-testid*='addResume' i]")
        ).first

    def _sidebar_item(self, name_regex: re.Pattern[str]) -> Locator:
        return self.page.get_by_role("link", name=name_regex).or_(
            self.page.get_by_role("button", name=name_regex)
        ).first

    @property
    def sidebar_dashboard(self) -> Locator:
        return self._sidebar_item(re.compile(r"^\s*dashboard\s*$", re.I))

    @property
    def sidebar_profile(self) -> Locator:
        return self._sidebar_item(re.compile(r"^\s*profile\s*$", re.I))

    @property
    def sidebar_resume(self) -> Locator:
        return self._sidebar_item(re.compile(r"\bresumes?\b", re.I))

    @property
    def sidebar_jobs(self) -> Locator:
        return self._sidebar_item(re.compile(r"\bjobs?\b", re.I))

    @property
    def sidebar_prep(self) -> Locator:
        return self._sidebar_item(re.compile(r"\bpreps?\b", re.I))

    @property
    def profile_icon(self) -> Locator:
        return self.page.locator("[data-testid*='profile' i], [data-testid*='user-menu' i], [aria-label*='profile' i], [aria-label*='user menu' i]").or_(
            self.page.get_by_role("button", name=re.compile(r"profile|account|user", re.I))
        ).first

    @property
    def logout_option(self) -> Locator:
        return self.page.get_by_role("menuitem", name=re.compile(r"logout|sign\s*out", re.I)).or_(
            self.page.get_by_role("button", name=re.compile(r"logout|sign\s*out", re.I))
        ).or_(self.page.get_by_text(re.compile(r"logout|sign\s*out", re.I))).first

    @property
    def sidebar(self) -> Locator:
        return self.page.locator("aside, nav").first

    @property
    def sidebar_profile_email(self) -> Locator:
        return self.page.get_by_text(
            re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
        ).first

    @property
    def sidebar_profile_phone(self) -> Locator:
        return self.page.get_by_text(
            re.compile(r"(\+?\d[\d\-\s]{6,}|\bn/?a\b)", re.I)
        ).first

    @property
    def sidebar_profile_location(self) -> Locator:
        return self.page.get_by_text(
            re.compile(
                r"\b(india|usa|uk|uae|canada|australia|singapore|germany|france|location)\b",
                re.I,
            )
        ).first

    @property
    def sidebar_toggle_button(self) -> Locator:
        return self.page.locator(
            "[data-testid*='sidebar-toggle' i], [data-testid*='collapse' i], "
            "[aria-label*='collapse' i], [aria-label*='expand' i], "
            "[title*='collapse' i], [title*='expand' i]"
        ).or_(
            self.sidebar.locator("button").first
        ).first

    @property
    def recent_activity_heading(self) -> Locator:
        return self.page.get_by_text(re.compile(r"^\s*recent\s+activity\s*$", re.I)).or_(
            self.page.get_by_role("heading", name=re.compile(r"recent\s+activity", re.I))
        ).first

    @property
    def recent_activity_section(self) -> Locator:
        return self.recent_activity_heading.locator(
            "xpath=ancestor::*[self::section or self::div][1]"
        )

    @property
    def stats_cards_generic(self) -> Locator:
        return self.page.locator("section >> text=/total|activities|preps|interviews/i")

    @property
    def welcome_back_text(self) -> Locator:
        return self.page.get_by_text(re.compile(r"\bwelcome\s+back\b", re.I))

    @property
    def dashboard_menu_item(self) -> Locator:
        return self.sidebar_dashboard

    # -----------------------
    # Helpers
    # -----------------------
    def _screenshot_on_failure(self, action_name: str) -> None:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", action_name).strip() or "dashboard"
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = _SCREENSHOTS_DIR / f"{safe}_{ts}.png"
        try:
            self.page.screenshot(path=str(path), full_page=True)
            logger.info("Screenshot on failure: %s", path)
        except Exception:
            pass

    def take_screenshot(self, name: str) -> Path:
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[<>:\"/\\\\|?*]+", "_", name).strip() or "screenshot"
        path = _SCREENSHOTS_DIR / f"{safe}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    # -----------------------
    # Actions (expect, timeout, screenshot on failure, log)
    # -----------------------
    def open_dashboard(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: open_dashboard")
        try:
            self.goto("/dashboard", wait_until="domcontentloaded")
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.page).to_have_url(re.compile(r"/dashboard", re.I), timeout=timeout_ms)
            logger.info("Result: dashboard opened")
        except Exception as e:
            self._screenshot_on_failure("open_dashboard")
            logger.error("Result: open_dashboard failed - %s", e)
            raise

    def verify_dashboard_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_dashboard_loaded")
        try:
            self.wait_for_body_visible(timeout_ms=timeout_ms)
            expect(self.welcome_text).to_be_visible(timeout=timeout_ms)
            logger.info("Result: dashboard loaded")
        except Exception as e:
            self._screenshot_on_failure("verify_dashboard_loaded")
            logger.error("Result: verify_dashboard_loaded failed - %s", e)
            raise

    def verify_welcome_message(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_welcome_message")
        try:
            expect(self.welcome_text).to_be_visible(timeout=timeout_ms)
            logger.info("Result: welcome message visible")
        except Exception as e:
            self._screenshot_on_failure("verify_welcome_message")
            logger.error("Result: verify_welcome_message failed - %s", e)
            raise

    def verify_stats_cards_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_stats_cards_visible")
        try:
            if self.stats_total_activities.count() > 0:
                expect(self.stats_total_activities).to_be_visible(timeout=timeout_ms)
            if self.stats_total_preps.count() > 0:
                expect(self.stats_total_preps).to_be_visible(timeout=timeout_ms)
            if self.stats_total_interviews.count() > 0:
                expect(self.stats_total_interviews).to_be_visible(timeout=timeout_ms)
            if self.stats_total_activities.count() == 0 and self.stats_total_preps.count() == 0 and self.stats_total_interviews.count() == 0:
                expect(self.stats_cards_generic.first).to_be_visible(timeout=timeout_ms)
            logger.info("Result: stats cards visible")
        except Exception as e:
            self._screenshot_on_failure("verify_stats_cards_visible")
            logger.error("Result: verify_stats_cards_visible failed - %s", e)
            raise

    def verify_total_activities_stats_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_total_activities_stats_visible")
        try:
            expect(self.stats_total_activities).to_be_visible(timeout=timeout_ms)
            logger.info("Result: total activities stat visible")
        except Exception as e:
            self._screenshot_on_failure("verify_total_activities_stats_visible")
            logger.error("Result: verify_total_activities_stats_visible failed - %s", e)
            raise

    def verify_job_applications_stats_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_job_applications_stats_visible")
        try:
            expect(self.stats_job_applications).to_be_visible(timeout=timeout_ms)
            logger.info("Result: job applications stat visible")
        except Exception as e:
            self._screenshot_on_failure("verify_job_applications_stats_visible")
            logger.error("Result: verify_job_applications_stats_visible failed - %s", e)
            raise

    def verify_resume_stats_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_resume_stats_visible")
        try:
            expect(self.stats_resume).to_be_visible(timeout=timeout_ms)
            logger.info("Result: resume stat visible")
        except Exception as e:
            self._screenshot_on_failure("verify_resume_stats_visible")
            logger.error("Result: verify_resume_stats_visible failed - %s", e)
            raise

    def verify_goals_stats_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_goals_stats_visible")
        try:
            expect(self.stats_goals).to_be_visible(timeout=timeout_ms)
            logger.info("Result: goals stat visible")
        except Exception as e:
            self._screenshot_on_failure("verify_goals_stats_visible")
            logger.error("Result: verify_goals_stats_visible failed - %s", e)
            raise

    def verify_recent_activity_visible_and_updated(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_recent_activity_visible_and_updated")
        try:
            expect(self.recent_activity_heading).to_be_visible(timeout=timeout_ms)
            self.recent_activity_heading.scroll_into_view_if_needed(timeout=timeout_ms)
            expect(self.recent_activity_section).to_be_visible(timeout=timeout_ms)

            # "Updated" signal: relative time text on activity entries (e.g., "3 minutes ago").
            relative_time = self.recent_activity_section.get_by_text(
                re.compile(
                    r"(less\s+than\s+a\s+minute\s+ago|\bjust\s+now\b|\b\d+\s+(seconds?|minutes?|hours?|days?|weeks?)\s+ago\b)",
                    re.I,
                )
            )
            if relative_time.count() > 0:
                expect(relative_time.first).to_be_visible(timeout=timeout_ms)
            else:
                # Fallback for builds with generic "ago" strings.
                ago_text = self.recent_activity_section.get_by_text(re.compile(r"\bago\b", re.I))
                expect(ago_text.first).to_be_visible(timeout=timeout_ms)
            logger.info("Result: recent activity visible and updated")
        except Exception as e:
            self._screenshot_on_failure("verify_recent_activity_visible_and_updated")
            logger.error("Result: verify_recent_activity_visible_and_updated failed - %s", e)
            raise

    def verify_sidebar_collapse_successful(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_sidebar_collapse_successful")
        try:
            expect(self.sidebar).to_be_visible(timeout=timeout_ms)
            before_box = self.sidebar.bounding_box() or {}
            before_width = float(before_box.get("width") or 0)
            before_profile_visible = False
            try:
                before_profile_visible = self.sidebar_profile.count() > 0 and self.sidebar_profile.first.is_visible()
            except Exception:
                before_profile_visible = False

            expect(self.sidebar_toggle_button).to_be_visible(timeout=timeout_ms)
            self.sidebar_toggle_button.click(timeout=timeout_ms)
            self.page.wait_for_timeout(900)

            after_box = self.sidebar.bounding_box() or {}
            after_width = float(after_box.get("width") or 0)
            after_profile_visible = False
            try:
                after_profile_visible = self.sidebar_profile.count() > 0 and self.sidebar_profile.first.is_visible()
            except Exception:
                after_profile_visible = False

            # Optional persisted state signal if implemented by UI.
            collapsed_flag = None
            try:
                collapsed_flag = self.page.evaluate("() => window.localStorage.getItem('sidebarCollapsed')")
            except Exception:
                collapsed_flag = None

            width_collapsed = before_width > 0 and after_width > 0 and after_width <= (before_width - 20)
            label_hidden = before_profile_visible and (not after_profile_visible)
            storage_collapsed = str(collapsed_flag).lower() in {"true", "1"}

            if not (width_collapsed or label_hidden or storage_collapsed):
                raise AssertionError(
                    f"Sidebar did not appear collapsed. before_width={before_width}, after_width={after_width}, "
                    f"before_profile_visible={before_profile_visible}, after_profile_visible={after_profile_visible}, "
                    f"sidebarCollapsed={collapsed_flag!r}"
                )
            logger.info("Result: sidebar collapse successful")
        except Exception as e:
            self._screenshot_on_failure("verify_sidebar_collapse_successful")
            logger.error("Result: verify_sidebar_collapse_successful failed - %s", e)
            raise

    def verify_sidebar_profile_details_visible(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_sidebar_profile_details_visible")
        try:
            expect(self.sidebar).to_be_visible(timeout=timeout_ms)

            # If sidebar is collapsed (persisted state), expand once before validating details.
            text_now = (self.sidebar.inner_text() or "").strip()
            looks_collapsed = len(text_now) < 40 or self.sidebar_profile_email.count() == 0
            if looks_collapsed:
                try:
                    # Persist expanded state and reload (more reliable than guessing toggle button selector).
                    self.page.evaluate("() => window.localStorage.setItem('sidebarCollapsed', 'false')")
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_timeout(900)
                except Exception:
                    # Fallback: try clicking known toggle if localStorage path fails.
                    if self.sidebar_toggle_button.count() > 0:
                        try:
                            self.sidebar_toggle_button.click(timeout=5_000)
                            self.page.wait_for_timeout(700)
                        except Exception:
                            pass

            visible_contact_parts = 0
            for loc in (self.sidebar_profile_phone, self.sidebar_profile_email, self.sidebar_profile_location):
                try:
                    if loc.count() > 0 and loc.first.is_visible():
                        visible_contact_parts += 1
                except Exception:
                    continue

            if visible_contact_parts < 2:
                raise AssertionError(
                    "Sidebar top-left profile details are not clearly visible. "
                    f"Visible contact parts={visible_contact_parts} (expected >=2 among phone/email/location)."
                )
            logger.info("Result: sidebar profile details visible")
        except Exception as e:
            self._screenshot_on_failure("verify_sidebar_profile_details_visible")
            logger.error("Result: verify_sidebar_profile_details_visible failed - %s", e)
            raise

    def click_find_jobs(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: click_find_jobs")
        try:
            expect(self.button_find_jobs).to_be_visible(timeout=timeout_ms)
            self.button_find_jobs.click(timeout=timeout_ms)
            logger.info("Result: find jobs clicked")
        except Exception as e:
            self._screenshot_on_failure("click_find_jobs")
            logger.error("Result: click_find_jobs failed - %s", e)
            raise

    def click_add_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: click_add_resume")
        try:
            expect(self.button_add_resume).to_be_visible(timeout=timeout_ms)
            self.button_add_resume.click(timeout=timeout_ms)
            logger.info("Result: add resume clicked")
        except Exception as e:
            self._screenshot_on_failure("click_add_resume")
            logger.error("Result: click_add_resume failed - %s", e)
            raise

    def navigate_to_profile(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: navigate_to_profile")
        try:
            expect(self.sidebar_profile).to_be_visible(timeout=timeout_ms)
            self.sidebar_profile.click(timeout=timeout_ms)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            logger.info("Result: navigated to profile")
        except Exception as e:
            self._screenshot_on_failure("navigate_to_profile")
            logger.error("Result: navigate_to_profile failed - %s", e)
            raise

    def navigate_to_resume(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: navigate_to_resume")
        try:
            expect(self.sidebar_resume).to_be_visible(timeout=timeout_ms)
            self.sidebar_resume.click(timeout=timeout_ms)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            logger.info("Result: navigated to resume")
        except Exception as e:
            self._screenshot_on_failure("navigate_to_resume")
            logger.error("Result: navigate_to_resume failed - %s", e)
            raise

    def navigate_to_jobs(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: navigate_to_jobs")
        try:
            expect(self.sidebar_jobs).to_be_visible(timeout=timeout_ms)
            self.sidebar_jobs.click(timeout=timeout_ms)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            logger.info("Result: navigated to jobs")
        except Exception as e:
            self._screenshot_on_failure("navigate_to_jobs")
            logger.error("Result: navigate_to_jobs failed - %s", e)
            raise

    def navigate_to_prep(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: navigate_to_prep")
        try:
            expect(self.sidebar_prep).to_be_visible(timeout=timeout_ms)
            self.sidebar_prep.click(timeout=timeout_ms)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            logger.info("Result: navigated to prep")
        except Exception as e:
            self._screenshot_on_failure("navigate_to_prep")
            logger.error("Result: navigate_to_prep failed - %s", e)
            raise

    def open_profile_menu(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: open_profile_menu")
        try:
            if self.profile_icon.count() > 0:
                expect(self.profile_icon).to_be_visible(timeout=timeout_ms)
                self.profile_icon.click(timeout=timeout_ms)
            else:
                self.sidebar_profile.click(timeout=timeout_ms)
            self.page.wait_for_timeout(300)
            logger.info("Result: profile menu opened")
        except Exception as e:
            self._screenshot_on_failure("open_profile_menu")
            logger.error("Result: open_profile_menu failed - %s", e)
            raise

    def click_logout(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: click_logout")
        try:
            expect(self.logout_option).to_be_visible(timeout=timeout_ms)
            self.logout_option.click(timeout=timeout_ms)
            logger.info("Result: logout clicked")
        except Exception as e:
            self._screenshot_on_failure("click_logout")
            logger.error("Result: click_logout failed - %s", e)
            raise

    def verify_redirect_to_login(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        logger.info("Action: verify_redirect_to_login")
        try:
            expect(self.page).to_have_url(re.compile(r"/login|/signin|/auth", re.I), timeout=timeout_ms)
            logger.info("Result: redirected to login")
        except Exception as e:
            self._screenshot_on_failure("verify_redirect_to_login")
            logger.error("Result: verify_redirect_to_login failed - %s", e)
            raise

    # -----------------------
    # Legacy compatibility
    # -----------------------
    def load(self) -> None:
        logger.info("Loading dashboard")
        self.goto("/dashboard", wait_until="domcontentloaded")

    def verify_loaded(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.wait_for_body_visible(timeout_ms=timeout_ms)
        expect(self.welcome_back_text.first).to_be_visible(timeout=timeout_ms)
        self.stats_cards_generic.first.wait_for(state="visible", timeout=timeout_ms)

    def verify_sidebar(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.sidebar.wait_for(state="visible", timeout=timeout_ms)
        expect(self.dashboard_menu_item.first).to_be_visible(timeout=timeout_ms)

    def verify_stats_cards(self, timeout_ms: int = _DEFAULT_TIMEOUT) -> None:
        self.verify_stats_cards_visible(timeout_ms=timeout_ms)

    def safe_click(self, locator: Locator, timeout_ms: int = 10_000) -> None:
        locator.first.wait_for(state="visible", timeout=timeout_ms)
        try:
            locator.first.scroll_into_view_if_needed(timeout=timeout_ms)
        except Exception:
            pass
        before_url = self.page.url
        try:
            locator.first.click(timeout=timeout_ms)
        except Exception:
            locator.first.click(timeout=timeout_ms, force=True)
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass
        if self.page.url == before_url:
            self.page.wait_for_timeout(500)

    def click_resumes_sidebar(self) -> None:
        logger.info("Clicking Resumes in sidebar")
        self.safe_click(self.sidebar_resume)

    def click_preps_sidebar(self) -> None:
        logger.info("Clicking Preps in sidebar")
        self.safe_click(self.sidebar_prep)

    def click_profile_sidebar(self) -> None:
        self.safe_click(self.sidebar_profile)
