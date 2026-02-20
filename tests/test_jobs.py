import re

import pytest

from framework.pages.jobs_page import JobsPage
from framework.pages.login_page import LoginPage


def _open_jobs_or_skip(page, base_url) -> JobsPage:
    jobs = JobsPage(page, base_url)
    jobs.goto_jobs_page()

    # If auth is required, stub login UI and skip.
    if re.search(r"/login\b|/signin\b|/auth\b", page.url, re.I):
        LoginPage(page, base_url).assert_login_ui_present_stub()
        pytest.skip("Jobs page requires authentication; login UI verified (stub).")

    jobs.verify_jobs_page_loaded()
    return jobs


def test_navigate_to_jobs_page(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.take_screenshot("jobs_00_loaded")


def test_verify_jobs_page_elements(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.verify_total_jobs_card()
    jobs.verify_best_fit_job_card()
    jobs.verify_least_fit_job_card()
    jobs.verify_job_cards_visible()
    jobs.verify_job_titles_visible()
    jobs.verify_company_names_visible()
    jobs.verify_skills_tags_visible()
    jobs.click_first_job_card_and_verify_interaction()
    jobs.take_screenshot("jobs_01_elements_verified")


def test_take_mock_interview_button(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.add_job_if_none_exists()
    jobs.click_take_mock_interview()
    jobs.verify_mock_interview_started_or_modal()
    jobs.take_screenshot("jobs_02_mock_interview")


def test_enhance_resume_button(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.add_job_if_none_exists()
    jobs.click_enhance_resume()
    jobs.verify_enhance_resume_response()
    jobs.take_screenshot("jobs_03_enhance_resume")


def test_delete_job_button(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.add_job_if_none_exists()
    jobs.click_delete_job()
    jobs.verify_delete_confirmation()
    jobs.take_screenshot("jobs_04_delete_confirmation")


def test_search_job_modal_open(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()
    jobs.take_screenshot("jobs_05_search_modal_open")
    jobs.close_search_modal()


def test_search_job_input(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()
    jobs.verify_search_input_present()
    jobs.enter_search_text("data")
    jobs.take_screenshot("jobs_06_search_input")
    jobs.close_search_modal()


def test_search_job_filters(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()

    jobs.click_7_days_filter()
    jobs.verify_job_cards_visible()
    jobs.take_screenshot("jobs_07_filter_7_days")

    jobs.click_30_days_filter()
    jobs.verify_job_cards_visible()
    jobs.take_screenshot("jobs_08_filter_30_days")

    jobs.click_all_filter()
    jobs.verify_job_cards_visible()
    jobs.take_screenshot("jobs_09_filter_all")

    jobs.close_search_modal()


def test_search_job_results_visible(page, base_url):
    jobs = _open_jobs_or_skip(page, base_url)
    jobs.click_search_job_button()
    jobs.verify_search_modal_open()
    jobs.enter_search_text("engineer")
    jobs.verify_job_cards_visible()
    jobs.verify_job_titles_visible()
    jobs.verify_company_names_visible()
    jobs.verify_skills_tags_visible()
    jobs.take_screenshot("jobs_10_search_results")
    jobs.close_search_modal()

