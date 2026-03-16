from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from framework.config import settings as config_settings
from framework.pages.login_page import LoginPage
from framework.utils.logger import logger as step_logger
from framework.utils.logger import set_current_test_name
from framework.utils.settings import settings as env_settings

_PROJECT_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class RunConfig:
    base_url: str
    browser_name: str
    headless: bool
    slow_mo_ms: int
    ignore_https_errors: bool


def pytest_addoption(parser: pytest.Parser) -> None:
    def _safe_addoption(*args, **kwargs) -> None:
        try:
            parser.addoption(*args, **kwargs)
        except Exception as exc:
            msg = str(exc)
            if "already added" not in msg and "conflicting option string" not in msg:
                raise

    _safe_addoption("--base-url", action="store", default=env_settings.BASE_URL)
    _safe_addoption("--browser", action="store", default=config_settings.browser_name)
    # Default: headed (visible browser). Pass --headless to run without UI.
    _safe_addoption("--headless", action="store_true", default=False)
    _safe_addoption("--headed", action="store_true", default=False)
    _safe_addoption("--slowmo", action="store", default=str(config_settings.slow_mo_ms))
    _safe_addoption("--ignore-https-errors", action="store_true", default=config_settings.ignore_https_errors)
    _safe_addoption("--no-auth", action="store_true", default=False)
    _safe_addoption("--no-login", action="store_true", default=False)


def pytest_runtest_setup(item: pytest.Item) -> None:
    set_current_test_name(item.nodeid)
    step_logger.info("TEST STARTED: %s", item.nodeid)


def pytest_runtest_teardown(item: pytest.Item) -> None:
    set_current_test_name(None)


@pytest.fixture(scope="session")
def run_config(pytestconfig: pytest.Config) -> RunConfig:
    def _normalize_scalar_option(value) -> str:
        if isinstance(value, (list, tuple)):
            return str(value[0]) if value else ""
        text = str(value).strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, (list, tuple)):
                    return str(parsed[0]) if parsed else ""
            except Exception:
                pass
        return text

    base_url = _normalize_scalar_option(pytestconfig.getoption("--base-url"))
    browser_name = _normalize_scalar_option(pytestconfig.getoption("--browser"))
    slow_mo_ms = int(_normalize_scalar_option(pytestconfig.getoption("--slowmo")) or 0)
    headless = bool(pytestconfig.getoption("--headless"))
    if bool(pytestconfig.getoption("--headed")):
        headless = False
    ignore_https_errors = bool(pytestconfig.getoption("--ignore-https-errors"))
    return RunConfig(
        base_url=base_url,
        browser_name=browser_name,
        headless=headless,
        slow_mo_ms=slow_mo_ms,
        ignore_https_errors=ignore_https_errors,
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, run_config: RunConfig) -> Browser:
    browser_name = run_config.browser_name.lower().strip()
    if browser_name not in {"chromium", "firefox", "webkit"}:
        raise ValueError(f"Unsupported --browser={run_config.browser_name!r}. Use chromium|firefox|webkit.")
    browser_type = getattr(playwright_instance, browser_name)
    launch_opts = {"headless": run_config.headless, "slow_mo": run_config.slow_mo_ms}
    if browser_name == "chromium":
        launch_opts["args"] = ["--disable-blink-features=AutomationControlled"]
    br = browser_type.launch(**launch_opts)
    yield br
    br.close()


def _resolve_auth_state_path() -> Path | None:
    auth_state = (env_settings.AUTH_STATE or "").strip()
    if not auth_state:
        return None
    path = Path(auth_state)
    if not path.is_absolute():
        path = _PROJECT_ROOT / auth_state
    return path if path.exists() else None


@pytest.fixture
def context(browser: Browser, run_config: RunConfig, request: pytest.FixtureRequest) -> BrowserContext:
    opts = {"ignore_https_errors": run_config.ignore_https_errors}
    use_auth = not request.config.getoption("--no-auth", False)
    auth_path = _resolve_auth_state_path() if use_auth else None
    if auth_path:
        opts["storage_state"] = str(auth_path.resolve())
    ctx = browser.new_context(**opts)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext, base_url: str) -> Page:
    pg = context.new_page()
    pg.set_default_timeout(config_settings.default_timeout_ms)
    pg.set_default_navigation_timeout(config_settings.navigation_timeout_ms)
    pg.goto(base_url, wait_until="domcontentloaded")
    pg.wait_for_timeout(7000)  # wait 7s after opening URL for page to settle
    return pg


@pytest.fixture(autouse=True)
def ensure_google_sign_in(page: Page, base_url: str, request: pytest.FixtureRequest) -> None:
    """
    Like Candidate_UI: run before every test that uses page.
    Ensures user is on dashboard (saved auth or full Google sign-in with email/password from .env).
    Skip with --no-login.
    """
    if request.config.getoption("--no-login", False):
        return
    # With --no-auth: no saved session; run full Google sign-in (click button, fill popup).
    # Without --no-auth: use saved session; only run sign-in if dashboard not loaded.
    lp = LoginPage(page, base_url)
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    if lp.is_dashboard_loaded():
        return
    if not lp.do_google_sign_in_if_needed(timeout_ms=90_000) and lp.is_login_page():
        pytest.fail("Could not reach recruiter app landing page. Re-save auth state and retry.")


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Page after login (ensure_google_sign_in runs first via autouse). Use like Candidate_UI."""
    return page


@pytest.fixture(scope="session")
def base_url(run_config: RunConfig) -> str:
    return run_config.base_url
