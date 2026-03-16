"""
Create JD workflow test for Prep module.
Validates New Prep -> Create JD -> prep card creation.
"""

import random
import string
import json
from pathlib import Path

import pytest

from framework.pages.login_page import LoginPage
from framework.pages.preps_page import PrepsPage
from framework.utils.logger import log_step

_WAIT_DASHBOARD_MS = 15_000
_CREATE_JD_WAIT_MS = 120_000


def _random_suffix(length: int = 5) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _watch_create_jd_backend(page):
    """Capture backend calls related to Create JD/Prep generation."""
    events = {"requests": [], "responses": []}
    mutation_methods = {"POST", "PUT", "PATCH"}

    def _is_target(req) -> bool:
        method = (req.method or "").upper()
        if method not in mutation_methods:
            return False
        # Accept broad mutation traffic so we don't miss unknown endpoint naming.
        try:
            rtype = (req.resource_type or "").lower()
        except Exception:
            rtype = ""
        return rtype in {"xhr", "fetch"} or "/api" in (req.url or "").lower() or "/graphql" in (req.url or "").lower()

    def on_request(req):
        try:
            if _is_target(req):
                headers = req.headers or {}
                pdata = ""
                try:
                    pdata = (req.post_data or "")[:600]
                except Exception:
                    pdata = ""
                events["requests"].append(
                    {
                        "method": req.method,
                        "url": req.url,
                        "resource_type": getattr(req, "resource_type", ""),
                        "content_type": headers.get("content-type", ""),
                        "post_data": pdata,
                    }
                )
        except Exception:
            pass

    def on_response(resp):
        try:
            req = resp.request
            if _is_target(req):
                body = ""
                try:
                    body = (resp.text() or "").strip()
                except Exception:
                    body = ""
                events["responses"].append(
                    {
                        "method": req.method,
                        "url": req.url,
                        "status": resp.status,
                        "body": body[:1000],
                    }
                )
        except Exception:
            pass

    page.on("request", on_request)
    page.on("response", on_response)
    return events, on_request, on_response


def _write_backend_capture(events: dict, suffix: str) -> Path:
    out_dir = Path("test-results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"prep_create_jd_backend_capture_{suffix}.json"
    out_path.write_text(json.dumps(events, indent=2), encoding="utf-8")
    return out_path


def _ensure_dashboard_same_as_login_test(page, base_url):
    """Use same dashboard reachability flow as login/resume tests."""
    login_page = LoginPage(page, base_url)
    if not login_page.is_dashboard_loaded():
        base = (base_url or "").rstrip("/")
        page.goto(f"{base}/dashboard", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=15_000)
        try:
            page.wait_for_url("**/dashboard**", timeout=_WAIT_DASHBOARD_MS)
        except Exception:
            pass
        try:
            page.wait_for_load_state("networkidle", timeout=20_000)
        except Exception:
            page.wait_for_timeout(3000)
        page.wait_for_timeout(2000)
    if login_page.is_dashboard_loaded():
        return
    page.wait_for_timeout(5000)
    if login_page.is_dashboard_loaded():
        return
    login_page.take_screenshot("prep_login_failure")
    _hint = (
        "python -m framework.auth.save_auth_state --democandidate"
        if "democandidate" in (base_url or "").lower()
        else "python -m framework.auth.save_auth_state"
    )
    pytest.fail(f"Auth state missing or expired. Run: {_hint}")


@pytest.mark.prep
@pytest.mark.smoke
def test_create_prep_jd_and_validate_card(page, base_url):
    _ensure_dashboard_same_as_login_test(page, base_url)
    preps_page = PrepsPage(page, base_url)

    suffix = _random_suffix()
    role_value = f"Machine Learning Engineer {suffix}"
    skills_value = f"Python, ML, NLP, {suffix}"
    experience_value = f"{random.randint(1, 6)} years"

    log_step("Opening Preps Page")
    preps_page.open_preps()
    preps_page.take_screenshot_report("preps_page_loaded")

    log_step("Clicking New Prep Button")
    log_step("Opening Create JD Modal")
    preps_page.open_new_prep_modal()
    preps_page.take_screenshot_report("create_jd_modal_open")

    log_step("Filling JD Form Fields")
    filled_count = preps_page.fill_create_jd_form(
        role=role_value,
        skills=skills_value,
        experience=experience_value,
        additional_details="Created by Playwright automation test",
    )
    if filled_count < 3:
        pytest.fail("Role/Skills/Experience fields were not filled in Create JD form.")
    preps_page.take_screenshot_report("create_jd_form_filled")

    log_step("Submitting JD Creation")
    backend_events, on_request, on_response = _watch_create_jd_backend(page)
    try:
        preps_page.submit_create_jd()
        # Required behavior: after clicking red Create JD, modal should close and return to Preps page.
        preps_page.wait_back_to_preps_after_create_jd(timeout_ms=30_000)
        # Check whether create-JD backend request is sent after returning to preps.
        waited_ms = 0
        while waited_ms < 20_000 and not backend_events.get("requests"):
            page.wait_for_timeout(1000)
            waited_ms += 1000
    finally:
        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)

    capture_path = _write_backend_capture(backend_events, suffix)
    print(f"Create JD backend capture saved: {capture_path.as_posix()}")
    print(f"Create JD backend requests: {backend_events.get('requests', [])[:8]}")
    print(f"Create JD backend responses: {backend_events.get('responses', [])[:8]}")
    if not backend_events.get("requests"):
        pytest.fail(
            "After clicking Create JD and returning to Preps page, no backend mutation call was captured "
            "(POST/PUT/PATCH xhr/fetch). "
            f"See capture: {capture_path.as_posix()}"
        )

    log_step("Waiting for Prep Card")
    preps_page.wait_for_prep_card(timeout_ms=_CREATE_JD_WAIT_MS)

    log_step("Validating Prep Card")
    preps_page.validate_prep_card(expected_role=role_value)
    preps_page.take_screenshot_report("prep_card_created")
