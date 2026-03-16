"""
Recruiter login test — same logic as Candidate_UI.
Uses saved auth state. Verifies dashboard load and JWT in storage/requests.
"""

from __future__ import annotations

import json
import re

import pytest

from framework.pages.login_page import LoginPage

_TEST_RESULTS = "test-results"
_WAIT_DASHBOARD_MS = 15_000

_TOKEN_KEYS = ("token", "accessToken", "access_token", "jwt", "id_token", "idToken", "bearer")


def _is_jwt_like(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    if value.startswith("Bearer "):
        value = value[7:].strip()
    return bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", value))


def _get_storage_with_jwt(page) -> dict:
    return page.evaluate("""() => {
        const out = { localStorage: {}, sessionStorage: {} };
        const jwtLike = (s) => typeof s === 'string' && /^[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+$/.test(s.replace(/^Bearer\\s+/i, '').trim());
        for (const storeName of ['localStorage', 'sessionStorage']) {
            const store = window[storeName];
            for (let i = 0; i < store.length; i++) {
                const key = store.key(i);
                if (!key) continue;
                try {
                    const val = store.getItem(key);
                    if (val && typeof val === 'string' && val.length > 50)
                        out[storeName][key] = val.length > 120 ? val.substring(0, 120) + '...' : val;
                } catch (e) {}
            }
        }
        return out;
    }""")


def _find_jwt_in_obj(obj, prefix: str = "") -> list[tuple[str, str]]:
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, str) and _is_jwt_like(v):
                found.append((path, v[:50] + "..." if len(v) > 50 else v))
            elif k.lower() in _TOKEN_KEYS and isinstance(v, str) and len(v) > 50:
                if _is_jwt_like(v):
                    found.append((path, v[:50] + "..." if len(v) > 50 else v))
            else:
                found.extend(_find_jwt_in_obj(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_find_jwt_in_obj(v, f"{prefix}[{i}]"))
    return found


def _get_storage_json_values(page, keys: list[str]) -> dict[str, str]:
    return page.evaluate(
        """(keys) => {
        const out = {};
        for (const k of keys) {
            try {
                const v = localStorage.getItem(k) || sessionStorage.getItem(k);
                if (v) out[k] = v;
            } catch (e) {}
        }
        return out;
    }""",
        keys,
    )


def _verify_jwt_after_login(page) -> tuple[bool, str]:
    try:
        data = _get_storage_with_jwt(page)
        for store_name, items in data.items():
            for key, value in items.items():
                if value and _is_jwt_like(str(value)):
                    return True, f"JWT found in {store_name}.{key} (login is passing JWT)"
        storage_keys = ["candidateInfo", "recruiterInfo", "user", "sessionData", "auth", "token"]
        raw = _get_storage_json_values(page, storage_keys)
        for key, value in raw.items():
            if not value:
                continue
            try:
                obj = json.loads(value)
                jwts = _find_jwt_in_obj(obj, key)
                if jwts:
                    return True, f"JWT found in {jwts[0][0]} (login is passing JWT)"
            except (json.JSONDecodeError, TypeError):
                if _is_jwt_like(value):
                    return True, f"JWT found in {key} (login is passing JWT)"
        keys_found = [f"{s}.{k}" for s, items in data.items() for k in items]
        return False, f"No JWT in storage. Keys: {keys_found or 'none'}."
    except Exception as e:
        return False, f"JWT check failed: {e!s}"


def _check_requests_pass_jwt(page) -> tuple[bool, str]:
    seen = []
    auth_header_found = []

    def on_request(req):
        try:
            auth = req.headers.get("authorization") or req.headers.get("Authorization")
            if auth and auth.startswith("Bearer ") and _is_jwt_like(auth[7:].strip()):
                auth_header_found.append((req.url[:80], "Bearer ..."))
            seen.append(req.url[:60])
        except Exception:
            pass

    page.on("request", on_request)
    try:
        try:
            page.wait_for_timeout(1500)
        except Exception:
            pass  # page may have closed
        if auth_header_found:
            return True, f"Login is passing JWT: saw Authorization Bearer on request to {auth_header_found[0][0]}"
        return False, f"No Authorization Bearer header in last {len(seen)} requests. URLs: {seen[:5]}"
    finally:
        try:
            page.remove_listener("request", on_request)
        except Exception:
            pass


@pytest.mark.login
@pytest.mark.smoke
def test_login_rc(page, base_url):
    """
    Same logic as Candidate_UI: verify auth session reaches dashboard.
    JWT verification in storage and requests. Screenshots on success/failure.
    """
    if "demohire" not in (base_url or "").lower():
        pytest.skip(f"test_login_rc is for demohire base_url. Current: {base_url!r}")

    login_page = LoginPage(page, base_url)
    base = (base_url or "").rstrip("/")

    if not login_page.is_dashboard_loaded():
        page.goto(f"{base}/dashboard", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=15_000)
        try:
            page.wait_for_url(re.compile(r".*(dashboard|recruiter|jobs).*", re.I), timeout=_WAIT_DASHBOARD_MS)
        except Exception:
            pass
        try:
            page.wait_for_load_state("networkidle", timeout=20_000)
        except Exception:
            try:
                page.wait_for_timeout(3000)
            except Exception:
                pass
        try:
            page.wait_for_timeout(2000)
        except Exception:
            pass

    print("Checking login state after Google sign-in")
    if login_page.is_dashboard_loaded():
        print("Dashboard loaded successfully")
        jwt_found, jwt_msg = _verify_jwt_after_login(page)
        print("JWT (storage): " + jwt_msg)
        req_found, req_msg = _check_requests_pass_jwt(page)
        print("JWT (requests): " + req_msg)
        login_page.take_screenshot("login_rc_success")
        return

    try:
        page.wait_for_timeout(5000)
    except Exception:
        pass  # page may have closed (auth failed, user closed browser)
    if login_page.is_dashboard_loaded():
        print("Dashboard loaded successfully")
        jwt_found, jwt_msg = _verify_jwt_after_login(page)
        print("JWT (storage): " + jwt_msg)
        req_found, req_msg = _check_requests_pass_jwt(page)
        print("JWT (requests): " + req_msg)
        login_page.take_screenshot("login_rc_success")
        return

    login_page.take_screenshot("login_rc_failure")
    pytest.fail(
        "Auth state missing or expired. Run: python -m framework.auth.save_auth_state (from Recruiter_UI)"
    )
