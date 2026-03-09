"""
Install Playwright route handlers that return mock API data.

Call install_mock_routes(page) when running with --use-mocks so the UI
works without a backend.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from framework.mocks.mock_data import (
    DASHBOARD_STATS_RESPONSE,
    JOBS_RESPONSE,
    PREPS_RESPONSE,
    RESUMES_RESPONSE,
    USER_RESPONSE,
)

if TYPE_CHECKING:
    from playwright.sync_api import Page

# URL path patterns (lowercase) -> (response_body, use_list_shape)
# Order matters: more specific first (e.g. "user/jobs" before "jobs")
_MOCK_GET_PATTERNS = [
    (re.compile(r"api[^/]*/.*job|/job"), JOBS_RESPONSE),
    (re.compile(r"api[^/]*/.*resume|/resume"), RESUMES_RESPONSE),
    (re.compile(r"api[^/]*/.*prep|/prep|/jd"), PREPS_RESPONSE),
    (re.compile(r"api[^/]*/.*stats|/stats|/dashboard"), DASHBOARD_STATS_RESPONSE),
    (re.compile(r"api[^/]*/.*user|/me|/profile"), USER_RESPONSE),
]

# Fallback: if path is just "jobs", "resumes", "preps" (common REST)
_MOCK_GET_PATH_EXACT = {
    "jobs": JOBS_RESPONSE,
    "resumes": RESUMES_RESPONSE,
    "preps": PREPS_RESPONSE,
    "prep": PREPS_RESPONSE,
    "jds": PREPS_RESPONSE,
}


def _pick_mock_response(url: str, method: str) -> dict | list | None:
    """Return mock payload for this request, or None to continue without mocking."""
    if method.upper() != "GET":
        # POST/PUT: return success + created resource for create flows
        if "resume" in url.lower():
            return {"data": RESUMES_RESPONSE["data"][0], "message": "Created"}
        if "job" in url.lower():
            return {"data": JOBS_RESPONSE["data"][0], "message": "Created"}
        if "prep" in url.lower() or "jd" in url.lower():
            return {"data": PREPS_RESPONSE["data"][0], "message": "Created"}
        return None

    url_lower = url.lower()
    path = ""
    try:
        path = url_lower.split("/api/")[-1] if "/api/" in url_lower else url_lower
        path = path.split("?")[0].strip("/")
    except Exception:
        pass

    for pattern, payload in _MOCK_GET_PATTERNS:
        if pattern.search(url_lower):
            return payload

    for segment in path.split("/"):
        if segment in _MOCK_GET_PATH_EXACT:
            return _MOCK_GET_PATH_EXACT[segment]

    return None


def _is_api_like_request(url: str) -> bool:
    """True if URL looks like an API endpoint (jobs, resumes, preps, user, etc.), not a document."""
    u = url.lower().split("?")[0]
    return any(
        segment in u
        for segment in ("/job", "/resume", "/prep", "/jd", "/user", "/me", "/profile", "/stats", "/dashboard", "/api/")
    )


def _handle_route(route) -> None:
    request = route.request
    url = request.url
    method = request.method
    # Only mock XHR/fetch, never document or other resource types
    resource_type = getattr(request, "resource_type", None)
    if resource_type not in ("xhr", "fetch"):
        route.continue_()
        return
    if not _is_api_like_request(url):
        route.continue_()
        return

    payload = _pick_mock_response(url, method)
    if payload is None:
        route.continue_()
        return

    body = json.dumps(payload) if not isinstance(payload, str) else payload
    route.fulfill(
        status=200,
        body=body,
        headers={"Content-Type": "application/json"},
    )


# 1) Match URLs containing /api/ (most common)
_API_GLOB = "**/api/**"
# 2) Catch-all for XHR/fetch only (handler checks URL and resource_type)
_CATCHALL_GLOB = "**/*"


def install_mock_routes(page: Page) -> None:
    """
    Intercept API calls on the given page and return mock data.

    Call this after creating the page and before navigating to the app.
    Intercepts only XHR/fetch requests whose URL looks like jobs/resumes/preps API.
    """
    def handler(route):
        _handle_route(route)

    page.route(_API_GLOB, handler)
    # Catch requests that don't use /api/ in path but are still API (e.g. /v1/jobs)
    page.route(_CATCHALL_GLOB, handler)
