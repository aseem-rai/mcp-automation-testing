"""
Login test using Google OAuth saved auth state. No email/password or Google form automation.
Verifies dashboard load and whether login is passing a JWT token (in storage or in request headers).
BASE_URL and AUTH_STATE from .env. Screenshots in test-results/.
"""

import json
import re

import pytest

from framework.pages.login_page import LoginPage

_TEST_RESULTS = "test-results"
_WAIT_DASHBOARD_MS = 15_000  # allow time for redirect when session is valid (democandidate)

# Keys that often hold a JWT (in JSON)
_TOKEN_KEYS = ("token", "accessToken", "access_token", "jwt", "id_token", "idToken", "bearer")


def _is_jwt_like(value: str) -> bool:
    """True if value looks like a JWT (three base64 segments separated by dots)."""
    if not value or not isinstance(value, str):
        return False
    value = value.strip()
    if value.startswith("Bearer "):
        value = value[7:].strip()
    return bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", value))


def _get_storage_with_jwt(page) -> dict:
    """Return localStorage + sessionStorage; all keys with string values (for JWT scan)."""
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
    """Recursively find JWT-like string values in dict/list. Returns list of (path, value_snippet)."""
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
    """Get full localStorage values for given keys (for JSON parsing)."""
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
    """
    Check if login is passing a JWT: look in storage (raw and inside candidateInfo/user/sessionData JSON).
    Returns (found: bool, message: str).
    """
    try:
        # 1) Raw storage values (top-level JWT)
        data = _get_storage_with_jwt(page)
        for store_name, items in data.items():
            for key, value in items.items():
                if value and _is_jwt_like(str(value)):
                    return True, f"JWT found in {store_name}.{key} (login is passing JWT)"
        # 2) Parse candidateInfo, user, sessionData as JSON and look for nested token
        storage_keys = ["candidateInfo", "user", "sessionData", "auth", "token"]
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
        return False, f"No JWT in storage or in candidateInfo/user/sessionData. Keys with long values: {keys_found or 'none'}."
    except Exception as e:
        return False, f"JWT check failed: {e!s}"


def _check_requests_pass_jwt(page, num_requests: int = 10) -> tuple[bool, str]:
    """
    Capture outgoing requests and check if any include Authorization: Bearer <JWT>.
    Returns (found: bool, message: str). Call after dashboard load; triggers a small action to generate requests.
    """
    seen = []
    auth_header_found = []

    def on_request(req):
        try:
            headers = req.headers
            auth = headers.get("authorization") or headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                token = auth[7:].strip()
                if _is_jwt_like(token):
                    auth_header_found.append((req.url[:80], "Bearer ..."))
            seen.append(req.url[:60])
        except Exception:
            pass

    page.on("request", on_request)
    try:
        page.wait_for_timeout(1500)
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
def test_login_with_google_auth_state(page, base_url):
    """
    Verify Google sign-in flow: ensure_google_sign_in (conftest) gets us to dashboard with saved auth.
    We stay on dashboard (no goto to root) and verify; going to base_url would load the landing page.
    """
    # We are already on dashboard after ensure_google_sign_in. Do NOT goto(base_url) here —
    # that loads the root/landing page ("Sign in with Google") and makes the test fail.
    # If we're not on dashboard yet, navigate to /dashboard directly (session already applied).
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
    print("Checking login state after Google sign-in")
    if login_page.is_dashboard_loaded():
        print("Dashboard loaded successfully")
        jwt_found, jwt_msg = _verify_jwt_after_login(page)
        if jwt_found:
            print("JWT (storage): " + jwt_msg)
        else:
            print("JWT (storage): " + jwt_msg)
        req_found, req_msg = _check_requests_pass_jwt(page)
        if req_found:
            print("JWT (requests): " + req_msg)
        else:
            print("JWT (requests): " + req_msg)
        login_page.take_screenshot("login_success")
        return
    page.wait_for_timeout(5000)
    if login_page.is_dashboard_loaded():
        print("Dashboard loaded successfully")
        jwt_found, jwt_msg = _verify_jwt_after_login(page)
        if jwt_found:
            print("JWT (storage): " + jwt_msg)
        else:
            print("JWT (storage): " + jwt_msg)
        req_found, req_msg = _check_requests_pass_jwt(page)
        if req_found:
            print("JWT (requests): " + req_msg)
        else:
            print("JWT (requests): " + req_msg)
        login_page.take_screenshot("login_success")
        return
    login_page.take_screenshot("login_failure")
    _hint = "python -m framework.auth.save_auth_state --democandidate" if "democandidate" in (base_url or "").lower() else "python -m framework.auth.save_auth_state"
    pytest.fail(
        f"Auth state missing or expired. Run: {_hint}",
    )
