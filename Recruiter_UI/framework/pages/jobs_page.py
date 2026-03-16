from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.pages.base_page import BasePage


class JobsPage(BasePage):
    """Recruiter Jobs page (/Jobs). Provides access to Add New Job / Create New Job buttons."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page=page, base_url=base_url)

    @property
    def add_new_job_button(self) -> Locator:
        """Locator for 'Add New Job' / 'Add Job' button/link."""
        return self.page.get_by_role("button", name=re.compile(r"add\s+(new\s+)?job", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"add\s+(new\s+)?job", re.I))
        ).or_(self.page.get_by_text(re.compile(r"add\s+(new\s+)?job", re.I))).or_(
            self.page.locator("[data-testid*='add-job'], [aria-label*='add' i][aria-label*='job' i]")
        ).first

    @property
    def create_new_job_button(self) -> Locator:
        """Locator for 'Create New Job' / 'Create Job' button/link."""
        return self.page.get_by_role("button", name=re.compile(r"create\s+(new\s+)?job", re.I)).or_(
            self.page.get_by_role("link", name=re.compile(r"create\s+(new\s+)?job", re.I))
        ).or_(self.page.get_by_text(re.compile(r"create\s+(new\s+)?job", re.I))).or_(
            self.page.locator("[data-testid*='create-job'], [aria-label*='create' i][aria-label*='job' i]")
        ).first

    @property
    def search_box(self) -> Locator:
        """Locator for the search box on the left side of /Jobs page."""
        return self.page.get_by_role("searchbox").or_(
            self.page.get_by_placeholder(re.compile(r"search", re.I))
        ).or_(
            self.page.locator("[aria-label*='search' i], [data-testid*='search'], input[type='search']")
        ).first

    def goto_jobs(self) -> None:
        """Navigate to /Jobs explicitly."""
        self.goto("/Jobs")

    def is_search_clickable(self, timeout_ms: int = 10_000) -> bool:
        """Return True if the search box (left side) is visible and clickable/focusable."""
        search = self.search_box
        try:
            search.wait_for(state="visible", timeout=timeout_ms)
            return search.is_enabled()
        except Exception:
            return False

    def is_add_new_job_clickable(self, timeout_ms: int = 10_000) -> bool:
        """Return True if Add New Job is visible and enabled (clickable)."""
        btn = self.add_new_job_button
        try:
            btn.wait_for(state="visible", timeout=timeout_ms)
            return btn.is_enabled()
        except Exception:
            return False

    def is_create_new_job_clickable(self, timeout_ms: int = 10_000) -> bool:
        """Return True if Create New Job is visible and enabled (clickable)."""
        btn = self.create_new_job_button
        try:
            btn.wait_for(state="visible", timeout=timeout_ms)
            return btn.is_enabled()
        except Exception:
            return False

    def upload_jd_via_add_new_job(self, file_paths: str | list[str], timeout_ms: int = 15_000) -> None:
        """
        Click Add New Job (opens native file manager), select one or multiple files and confirm (Open).
        If `file_paths` is a list, all provided files are selected in a single popup.
        """
        if isinstance(file_paths, str):
            files = [file_paths]
        else:
            files = list(file_paths)
        self.add_new_job_button.wait_for(state="visible", timeout=timeout_ms)
        with self.page.expect_file_chooser(timeout=timeout_ms) as fc_info:
            self.add_new_job_button.click(timeout=timeout_ms)
        file_chooser = fc_info.value
        file_chooser.set_files(files)
        self.page.wait_for_timeout(1500)

    def is_on_jobs_page(self, timeout_ms: int = 5_000) -> bool:
        """Return True if the current URL is the Jobs page and Add New Job is visible."""
        try:
            self.page.wait_for_url(re.compile(r"/Jobs", re.I), timeout=timeout_ms)
            return self.add_new_job_button.is_visible()
        except Exception:
            return False

    # --- My Jobs (left side): job cards and center job info ---

    def first_my_jobs_job_card(self) -> Locator:
        """First visible job card in My Jobs list (left side). Cards have ID written on them."""
        # Prefer elements that have "ID" text on them (the job card displays an ID)
        cards_with_id = self.page.locator(
            "[class*='card'], [class*='Card'], [role='listitem']"
        ).filter(has=self.page.get_by_text(re.compile(r"\bID\b", re.I)))
        fallback = self.page.get_by_role("listitem").or_(
            self.page.locator("[class*='JobCard'], [data-testid*='job-card'], a[href*='job']")
        )
        return cards_with_id.or_(fallback).first

    def click_first_job_card_in_my_jobs(self, timeout_ms: int = 10_000) -> None:
        """Click the first job card in the My Jobs list (left side). Pauses so the click is visible."""
        card = self.first_my_jobs_job_card()
        card.wait_for(state="visible", timeout=timeout_ms)
        self.page.wait_for_timeout(1500)  # Pause so user sees the Jobs page and left list
        card.click(timeout=timeout_ms)
        self.page.wait_for_timeout(2500)  # Pause so user sees job info appear in center

    def is_job_info_visible_in_center(self, timeout_ms: int = 10_000) -> bool:
        """Return True if job information is visible in the center content area after selecting a job."""
        try:
            self.page.wait_for_timeout(2000)
            main = self.page.get_by_role("main")
            if main.count() > 0 and main.first.is_visible():
                return True
            # Any visible block in center that has substantial text (job details)
            center = self.page.locator("[class*='content'], [class*='Content'], [class*='detail'], [class*='Detail']")
            for i in range(min(center.count(), 5)):
                loc = center.nth(i)
                if loc.is_visible() and loc.get_by_text(re.compile(r".{10,}")).count() > 0:
                    return True
            return False
        except Exception:
            return False

    # --- Create New Job popup (visible modal/dialog with form) ---

    def _create_job_form_container(self) -> Locator:
        """Visible dialog/modal that contains the create job form (exclude hidden menus)."""
        return self.page.locator("[role='dialog']").filter(
            has=self.page.get_by_text(re.compile(r"create\s*(new\s+)?job|job\s*role", re.I))
        ).or_(
            self.page.locator("[class*='Modal']").filter(
                has=self.page.locator("input, textarea")
            ).filter(has_not=self.page.locator("[aria-hidden='true']"))
        ).first

    def _job_role_field(self) -> Locator:
        """Job role input in the create job popup."""
        return self.page.get_by_label(re.compile(r"job\s*role|role|title", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"job\s*role|role|title", re.I))
        ).or_(self.page.locator("input[name*='role'], input[id*='role'], input[name*='title']")).first

    def _required_skills_field(self) -> Locator:
        """Required skills input in the create job popup."""
        return self.page.get_by_label(re.compile(r"skill|required", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"skill|required", re.I))
        ).or_(self.page.locator("input[name*='skill'], input[id*='skill'], textarea[name*='skill']")).first

    def _experience_field(self) -> Locator:
        """Experience input in the create job popup."""
        return self.page.get_by_label(re.compile(r"experience", re.I)).or_(
            self.page.get_by_placeholder(re.compile(r"experience|years", re.I))
        ).or_(self.page.locator("input[name*='experience'], input[id*='experience']")).first

    def _create_job_submit_button(self) -> Locator:
        """Create Job button at the bottom of the popup."""
        return self.page.get_by_role("button", name=re.compile(r"create\s*job", re.I)).or_(
            self.page.get_by_text(re.compile(r"^create\s*job$", re.I))
        ).first

    def open_create_job_popup(self, timeout_ms: int = 15_000) -> None:
        """Click Create New Job (or menu item if it opens a menu) and wait for the form popup."""
        self.create_new_job_button.click(timeout=10_000)
        self.page.wait_for_timeout(1500)
        # If a menu opened, click the "Create New Job" / "Create Job" menu item to open the form
        menu_item = self.page.get_by_role("menuitem", name=re.compile(r"create\s+(new\s+)?job", re.I)).or_(
            self.page.get_by_role("option", name=re.compile(r"create\s+(new\s+)?job", re.I))
        ).or_(self.page.get_by_text(re.compile(r"create\s+(new\s+)?job", re.I)).first)
        if menu_item.count() > 0:
            try:
                menu_item.first.click(timeout=5000)
                self.page.wait_for_timeout(2000)
            except Exception:
                pass
        # Wait for the form: job role field or any visible input in a dialog
        try:
            self._job_role_field().wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            self.page.locator("[role='dialog'] input, [class*='Modal'] input").first.wait_for(
                state="visible", timeout=timeout_ms
            )

    def _visible_editable_dialog_inputs(self):
        """First 3 visible, editable input/textarea elements in the create job dialog (for fallback fill)."""
        all_in = self.page.locator(
            "[role='dialog'] input:not([readonly]):not([aria-hidden='true']), "
            "[role='dialog'] textarea:not([readonly]):not([aria-hidden='true'])"
        ).or_(
            self.page.locator("[class*='Modal'] input:not([readonly]), [class*='Modal'] textarea:not([readonly])")
        )
        visible = []
        for i in range(min(all_in.count(), 10)):
            loc = all_in.nth(i)
            try:
                if loc.is_visible():
                    visible.append(loc)
                    if len(visible) >= 3:
                        break
            except Exception:
                pass
        return visible

    def fill_create_job_form(
        self,
        job_role: str,
        required_skills: str,
        experience: str,
        timeout_ms: int = 10_000,
    ) -> None:
        """Fill job role, required skills and experience in the Create New Job popup."""
        self.page.wait_for_timeout(1000)
        # Try labeled/placeholder fields first
        try:
            self._job_role_field().wait_for(state="visible", timeout=3000)
            self._job_role_field().fill(job_role, timeout=timeout_ms)
            self._required_skills_field().fill(required_skills, timeout=timeout_ms)
            self._experience_field().fill(experience, timeout=timeout_ms)
        except Exception:
            # Fallback: fill first three visible, editable inputs in the dialog
            inputs = self._visible_editable_dialog_inputs()
            if len(inputs) >= 3:
                inputs[0].fill(job_role, timeout=timeout_ms)
                self.page.wait_for_timeout(300)
                inputs[1].fill(required_skills, timeout=timeout_ms)
                self.page.wait_for_timeout(300)
                inputs[2].fill(experience, timeout=timeout_ms)
            else:
                raise
        self.page.wait_for_timeout(300)

    def click_create_job_in_popup(self, timeout_ms: int = 10_000) -> None:
        """Click the Create Job button at the bottom of the popup."""
        self._create_job_submit_button().click(timeout=timeout_ms)

