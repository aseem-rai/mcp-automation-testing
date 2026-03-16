"""
Recruiter Jobs tests.
Verify that 'Add New Job', 'Create New Job' buttons and the search box (left side) are clickable.
"""

from __future__ import annotations

import os
import pytest

from framework.pages.jobs_page import JobsPage


@pytest.mark.jobs
@pytest.mark.smoke
def test_add_new_job_button_clickable(logged_in_page, base_url):
    """
    Verify 'Add New Job' button is visible and clickable on Jobs page.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_add_new_job_button_clickable is for demohire base_url. Current: {base_url!r}")

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(2000)

    assert jobs_page.is_add_new_job_clickable(), "'Add New Job' button is not clickable on Jobs page."


@pytest.mark.jobs
@pytest.mark.smoke
def test_create_new_job_button_clickable(logged_in_page, base_url):
    """
    Verify 'Create New Job' button is visible and clickable on Jobs page.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_create_new_job_button_clickable is for demohire base_url. Current: {base_url!r}")

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(2000)

    assert jobs_page.is_create_new_job_clickable(), "'Create New Job' button is not clickable on Jobs page."


@pytest.mark.jobs
@pytest.mark.smoke
def test_search_box_clickable(logged_in_page, base_url):
    """
    Verify the search box on the left side of /Jobs page is visible and clickable.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_search_box_clickable is for demohire base_url. Current: {base_url!r}")

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(2000)

    assert jobs_page.is_search_clickable(), "Search box on /Jobs page (left side) is not clickable."


# Sample data for Create New Job form (required fields)
_CREATE_JOB_ROLE = "Software Engineer"
_CREATE_JOB_SKILLS = "Python, API, Playwright"
_CREATE_JOB_EXPERIENCE = "2-5 years"


@pytest.mark.jobs
@pytest.mark.smoke
def test_create_new_job_fill_and_submit(logged_in_page, base_url):
    """
    Click Create New Job -> popup opens -> fill job role, required skills, experience -> click Create Job.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_create_new_job_fill_and_submit is for demohire base_url. Current: {base_url!r}")

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(2000)

    jobs_page.open_create_job_popup()
    jobs_page.fill_create_job_form(
        job_role=_CREATE_JOB_ROLE,
        required_skills=_CREATE_JOB_SKILLS,
        experience=_CREATE_JOB_EXPERIENCE,
    )
    jobs_page.click_create_job_in_popup()

    # Popup may close or show success; allow a moment for navigation/update
    logged_in_page.wait_for_timeout(3000)


# JD folder and count for "Add New Job" upload test (file manager popup).
# All PDFs in this folder are candidates; the first N (sorted by name) are used.
_JD_FOLDER = r"D:\JD"
_JD_UPLOAD_COUNT = 5  # Change this number to upload N files from _JD_FOLDER


@pytest.mark.jobs
@pytest.mark.smoke
def test_upload_jd_via_add_new_job(logged_in_page, base_url):
    """
    Click Add New Job -> file manager popup opens -> select JD PDF(s) -> Open -> back on Jobs page.
    Uses the first `_JD_UPLOAD_COUNT` PDF files from `_JD_FOLDER`.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_upload_jd_via_add_new_job is for demohire base_url. Current: {base_url!r}")

    if not os.path.isdir(_JD_FOLDER):
        pytest.skip(f"JD folder not found: {_JD_FOLDER!r}")

    pdf_files = sorted(
        os.path.join(_JD_FOLDER, name)
        for name in os.listdir(_JD_FOLDER)
        if name.lower().endswith(".pdf")
    )
    if not pdf_files:
        pytest.skip(f"No PDF files found in JD folder: {_JD_FOLDER!r}")

    count = max(0, int(_JD_UPLOAD_COUNT))
    if count < 1:
        pytest.skip(f"_JD_UPLOAD_COUNT is < 1 (current value: {_JD_UPLOAD_COUNT!r})")
    if len(pdf_files) < count:
        pytest.skip(
            f"Requested {_JD_UPLOAD_COUNT} JD uploads but only {len(pdf_files)} PDF files are present in {_JD_FOLDER!r}"
        )

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(2000)

    # Select multiple PDFs in a single file chooser popup
    files_to_upload = pdf_files[:count]
    jobs_page.upload_jd_via_add_new_job(files_to_upload)
    logged_in_page.wait_for_timeout(2000)

    assert jobs_page.is_on_jobs_page(timeout_ms=10_000), (
        "After uploading JD via Add New Job, expected to be back on Jobs page."
    )


@pytest.mark.jobs
@pytest.mark.smoke
def test_click_job_card_in_my_jobs_shows_info_in_center(logged_in_page, base_url):
    """
    Click a job card in My Jobs (left side) and verify job information appears in the center.
    Run with headed browser to see the click and center update (default is headed).
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test is for demohire base_url. Current: {base_url!r}")

    jobs_page = JobsPage(logged_in_page, base_url)
    jobs_page.goto_jobs()
    logged_in_page.wait_for_load_state("domcontentloaded", timeout=15_000)
    logged_in_page.wait_for_timeout(3000)  # So you can see the Jobs page and My Jobs list

    jobs_page.click_first_job_card_in_my_jobs()  # Includes pauses so click and center update are visible
    assert jobs_page.is_job_info_visible_in_center(), (
        "After clicking a job card in My Jobs, job information did not appear in the center."
    )

