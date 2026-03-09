from __future__ import annotations

import datetime as _dt
import html
import logging
import os
import re
import sys
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from framework.config import settings as config_settings
from framework.utils.logger import logger as step_logger
from framework.utils.logger import set_current_test_name
from framework.utils.settings import settings as env_settings

_LOGGER = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent

# QA report folder: test-results/report.html, test.log, screenshots/
_TEST_RESULTS_DIR = _PROJECT_ROOT / "test-results"
_TEST_RESULTS_SCREENSHOTS = _TEST_RESULTS_DIR / "screenshots"
_REPORTS_LOG = _TEST_RESULTS_DIR / "test.log"
_HTML_REPORT_PATH = _TEST_RESULTS_DIR / "report.html"

# Google OAuth auth state (framework/auth/save_auth_state.py).
_AUTH_DIR = _PROJECT_ROOT / "framework" / "auth"
_STATE_PATH = _AUTH_DIR / "auth.json"
_LEGACY_STATE = _AUTH_DIR / "state.json"

_CURRENT_NODEID: ContextVar[str | None] = ContextVar("_CURRENT_NODEID", default=None)
_LAST_PAGE_URL_BY_NODEID: dict[str, str] = {}


class _PerTestLogHandler(logging.Handler):
    """
    Capture log records per-test so we can embed them into pytest-html Details.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.NOTSET)
        self._by_nodeid: dict[str, list[str]] = {}
        self._formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def emit(self, record: logging.LogRecord) -> None:
        nodeid = _CURRENT_NODEID.get()
        if not nodeid:
            return
        try:
            msg = self._formatter.format(record)
        except Exception:
            return
        self._by_nodeid.setdefault(nodeid, []).append(msg)

    def get_text(self, nodeid: str, *, max_lines: int = 400) -> str:
        lines = self._by_nodeid.get(nodeid, [])
        if not lines:
            return ""
        if len(lines) > max_lines:
            lines = ["... (truncated) ...", *lines[-max_lines:]]
        return "\n".join(lines)


_PER_TEST_LOG_HANDLER = _PerTestLogHandler()


@dataclass(frozen=True)
class RunConfig:
    base_url: str
    browser_name: str
    headless: bool
    slow_mo_ms: int
    ignore_https_errors: bool


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--base-url", action="store", default=env_settings.BASE_URL)
    parser.addoption("--browser", action="store", default=config_settings.browser_name)
    parser.addoption("--headless", action="store_true", default=config_settings.headless)
    parser.addoption("--headed", action="store_true", default=False)
    parser.addoption("--slowmo", action="store", default=str(config_settings.slow_mo_ms))
    parser.addoption("--ignore-https-errors", action="store_true", default=config_settings.ignore_https_errors)
    parser.addoption(
        "--use-mocks",
        action="store_true",
        default=False,
        help="Intercept API calls and return mock data (jobs, resumes, preps) so UI works without backend.",
    )
    parser.addoption(
        "--open-report",
        action="store_true",
        default=None,
        help="Open the HTML report (reports/report.html) after the test run completes.",
    )
    parser.addoption(
        "--open-report-chrome",
        action="store_true",
        default=False,
        help="Open the HTML report in Google Chrome after the test run.",
    )
    parser.addoption(
        "--no-open-report",
        action="store_true",
        default=False,
        help="Do not open the HTML report after the test run completes.",
    )
    parser.addoption(
        "--no-auth",
        action="store_true",
        default=False,
        help="Run without saved auth state (browser starts with no login session).",
    )
    parser.addoption(
        "--no-login",
        action="store_true",
        default=False,
        help="Do not run automatic Google sign-in before each test (page stays at base URL).",
    )


def pytest_configure(config: pytest.Config) -> None:
    _TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _TEST_RESULTS_SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    if not hasattr(config, "_metadata"):
        config._metadata = {}
    config._metadata["BASE_URL"] = env_settings.BASE_URL
    config._metadata["Browser"] = "Chromium"
    config._metadata["Tester Name"] = "Aseem Rai"

    root = logging.getLogger()
    if _PER_TEST_LOG_HANDLER not in root.handlers:
        root.addHandler(_PER_TEST_LOG_HANDLER)


def pytest_html_report_title(report) -> str:
    return "MeetAIVA Automation Report"


def pytest_html_results_summary(prefix, summary, postfix) -> None:
    prefix.append("<p><b>Environment:</b> BASE_URL, Browser: Chromium, Tester Name: Aseem Rai</p>")


def pytest_sessionstart(session: pytest.Session) -> None:
    _TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    _LOGGER.info("=== pytest session start ===")
    _LOGGER.info("python=%s", sys.version.replace("\n", " "))
    _LOGGER.info("platform=%s", sys.platform)
    _LOGGER.info("base_url=%s", getattr(session.config, "getoption", lambda *_: None)("--base-url"))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _LOGGER.info("=== pytest session finish (exitstatus=%s) ===", exitstatus)
    _maybe_open_html_report(session)


def _maybe_open_html_report(session: pytest.Session) -> None:
    config = session.config

    if getattr(session, "testscollected", 0) <= 0:
        return

    env = os.getenv("OPEN_REPORT")
    if env is not None:
        enabled = env.strip().lower() in {"1", "true", "t", "yes", "y", "on"}
    else:
        in_ci = os.getenv("CI") is not None
        enabled = bool(getattr(sys.stdout, "isatty", lambda: False)()) and not in_ci

    if config.getoption("--no-open-report", default=False):
        enabled = False
    if config.getoption("--open-report", default=None) is True:
        enabled = True
    open_in_chrome = config.getoption("--open-report-chrome", default=False)
    if open_in_chrome:
        enabled = True

    if not enabled:
        return

    report_path = _HTML_REPORT_PATH.resolve()
    if not report_path.exists():
        return

    try:
        if open_in_chrome:
            import subprocess
            chrome_paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
            opened = False
            for chrome in chrome_paths:
                if chrome and os.path.isfile(chrome):
                    subprocess.Popen([chrome, str(report_path)], shell=False)
                    opened = True
                    break
            if not opened:
                if os.name == "nt":
                    os.startfile(str(report_path))  # type: ignore[attr-defined]
                else:
                    import webbrowser
                    webbrowser.open(report_path.as_uri(), new=2)
        elif os.name == "nt":
            os.startfile(str(report_path))  # type: ignore[attr-defined]
        else:
            import webbrowser
            webbrowser.open(report_path.as_uri(), new=2)
    except Exception:
        _LOGGER.exception("Failed to open HTML report: %s", report_path)


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Log TEST STARTED before each test runs."""
    set_current_test_name(item.nodeid)
    step_logger.info("TEST STARTED: %s", item.nodeid)


def pytest_runtest_call(item: pytest.Item) -> None:
    """Called when the test body runs. TEST STEP lines come from logger.info() in tests and page objects."""
    pass


def pytest_runtest_teardown(item: pytest.Item) -> None:
    """Clear test name after test (result logged in pytest_runtest_logreport)."""
    set_current_test_name(None)


def pytest_runtest_logstart(nodeid: str, location) -> None:
    _CURRENT_NODEID.set(nodeid)
    set_current_test_name(nodeid)
    _LOGGER.info("START %s", nodeid)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return

    if report.passed:
        step_logger.info("TEST PASSED: %s (%.3fs)", report.nodeid, report.duration)
    elif report.failed:
        step_logger.error("TEST FAILED: %s (%.3fs)", report.nodeid, report.duration)
    elif report.skipped:
        step_logger.warning("TEST SKIPPED: %s (%.3fs)", report.nodeid, report.duration)

    try:
        item = getattr(report, "_item", None)
        if item is not None and hasattr(item, "funcargs"):
            page = item.funcargs.get("page")
            if page is not None:
                _LAST_PAGE_URL_BY_NODEID[report.nodeid] = str(page.url)
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem):
    token = _CURRENT_NODEID.set(getattr(item, "nodeid", item.name))
    try:
        yield
    finally:
        _CURRENT_NODEID.reset(token)


def _safe_filename(value: str, *, max_len: int = 180) -> str:
    value = re.sub(r"[<>:\"/\\\\|?*]+", "_", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > max_len:
        value = value[:max_len].rstrip("_ .")
    return value or "test"


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report: pytest.TestReport = outcome.get_result()

    if report.when != "call":
        return

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extra = getattr(report, "extra", [])

        docstring = (getattr(item.function, "__doc__", None) or "").strip()
        if docstring:
            desc_html = "<p><b>Test description:</b> " + html.escape(docstring) + "</p>"
            extra.append(pytest_html.extras.html(desc_html))

        logs_text = _PER_TEST_LOG_HANDLER.get_text(report.nodeid)
        if logs_text:
            pre = "<pre style='white-space:pre-wrap; word-break:break-word;'>" + html.escape(logs_text) + "</pre>"
            logs_section = "<details open><summary><b>Step-by-step logs</b></summary>" + pre + "</details>"
            extra.append(pytest_html.extras.html(logs_section))

        capstdout = getattr(report, "capstdout", "") or ""
        capstderr = getattr(report, "capstderr", "") or ""

        if capstdout.strip():
            pre = (
                "<details><summary><b>Captured stdout</b></summary>"
                "<pre style='white-space:pre-wrap; word-break:break-word;'>"
                + html.escape(capstdout)
                + "</pre></details>"
            )
            extra.append(pytest_html.extras.html(pre))

        if capstderr.strip():
            pre = (
                "<details><summary><b>Captured stderr</b></summary>"
                "<pre style='white-space:pre-wrap; word-break:break-word;'>"
                + html.escape(capstderr)
                + "</pre></details>"
            )
            extra.append(pytest_html.extras.html(pre))

        for name, content in getattr(report, "sections", []) or []:
            if not content or not str(content).strip():
                continue
            pre = (
                "<details><summary><b>"
                + html.escape(str(name))
                + "</b></summary>"
                "<pre style='white-space:pre-wrap; word-break:break-word;'>"
                + html.escape(str(content))
                + "</pre></details>"
            )
            extra.append(pytest_html.extras.html(pre))

        duration_html = "<p><b>Duration:</b> %.3fs</p>" % (report.duration or 0)
        extra.append(pytest_html.extras.html(duration_html))

        page_url = ""
        try:
            page = item.funcargs.get("page")
            if page is not None:
                page_url = str(page.url)
        except Exception:
            page_url = _LAST_PAGE_URL_BY_NODEID.get(report.nodeid, "")

        if page_url:
            extra.append(pytest_html.extras.url(page_url, name="Final page URL"))

        try:
            _TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            extra.append(pytest_html.extras.url(_REPORTS_LOG.resolve().as_uri(), name="Run log file"))
        except Exception:
            pass

        report.extra = extra

    page: Optional[Page] = None
    try:
        if hasattr(item, "funcargs"):
            page = item.funcargs.get("page")
    except Exception:
        pass

    timestamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nodeid = _safe_filename(getattr(item, "nodeid", item.name))
    path = _TEST_RESULTS_SCREENSHOTS / f"{nodeid}_{timestamp}.png"

    if page is not None:
        try:
            _TEST_RESULTS_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(path), full_page=True)
            _LOGGER.info("Saved screenshot: %s", path.as_posix())
            if pytest_html is not None:
                extra = getattr(report, "extra", [])
                extra.append(pytest_html.extras.image(str(path)))
                report.extra = extra
        except Exception:
            _LOGGER.exception("Failed to capture screenshot for %s", getattr(item, "nodeid", item.name))


# -----------------------------------------------------------------------------
# Fixtures: run_config, base_url, playwright_instance, browser, context, page
# -----------------------------------------------------------------------------


@pytest.fixture(scope="session")
def run_config(pytestconfig: pytest.Config) -> RunConfig:
    base_url = str(pytestconfig.getoption("--base-url"))
    browser_name = str(pytestconfig.getoption("--browser"))
    slow_mo_ms = int(pytestconfig.getoption("--slowmo"))

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
    launch_opts: dict = {
        "headless": run_config.headless,
        "slow_mo": run_config.slow_mo_ms,
    }
    if browser_name == "chromium":
        launch_opts["args"] = ["--disable-blink-features=AutomationControlled"]
    browser = browser_type.launch(**launch_opts)
    yield browser
    browser.close()


def _resolve_auth_state_path(base_url: str = "") -> Optional[Path]:
    """Return path to auth state file. Uses env-specific file when base_url matches (e.g. democandidate -> auth_democandidate.json)."""
    # Prefer env-specific file by base_url so --base-url=democandidate uses auth_democandidate.json.
    base_lower = (base_url or "").lower()
    if "democandidate" in base_lower:
        demo_path = _AUTH_DIR / "auth_democandidate.json"
        if demo_path.exists():
            return demo_path
    # Else use AUTH_STATE from .env or default auth.json
    auth_state = env_settings.AUTH_STATE.strip()
    if auth_state:
        path = Path(auth_state)
        if not path.is_absolute():
            path = _PROJECT_ROOT / path
        if path.exists():
            return path
    if _STATE_PATH.exists():
        return _STATE_PATH
    if _LEGACY_STATE.exists():
        import shutil
        shutil.copy(_LEGACY_STATE, _STATE_PATH)
        _LOGGER.info("Using auth state: copied %s -> %s", _LEGACY_STATE, _STATE_PATH)
        return _STATE_PATH
    return None


@pytest.fixture
def context(browser: Browser, run_config: RunConfig, request: pytest.FixtureRequest) -> BrowserContext:
    use_auth = not request.config.getoption("--no-auth", False)
    auth_path = _resolve_auth_state_path(run_config.base_url) if use_auth else None
    opts = {"ignore_https_errors": run_config.ignore_https_errors}
    if auth_path is not None:
        opts["storage_state"] = str(auth_path.resolve())
        _LOGGER.info("Using saved auth state: %s", auth_path.resolve())
        ctx = browser.new_context(**opts)
    else:
        if use_auth:
            _hint = "python -m framework.auth.save_auth_state --democandidate" if "democandidate" in (run_config.base_url or "").lower() else "python -m framework.auth.save_auth_state"
            _LOGGER.warning(
                "No auth state found. Browser will start without saved session. "
                "To save Google OAuth state run: %s",
                _hint,
            )
        else:
            _LOGGER.info("Running without login (--no-auth). Browser will start with no saved session.")
        ctx = browser.new_context(**opts)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext, request: pytest.FixtureRequest, base_url: str) -> Page:
    from framework.mocks.routes import install_mock_routes

    page = context.new_page()
    page.set_default_timeout(config_settings.default_timeout_ms)
    page.set_default_navigation_timeout(config_settings.navigation_timeout_ms)

    use_mocks = request.config.getoption("--use-mocks", default=False)
    if use_mocks:
        install_mock_routes(page)

    # Start at app root (login page). Use base_url fixture so --base-url is respected.
    page.goto(base_url, wait_until="domcontentloaded")
    return page


@pytest.fixture(autouse=True)
def ensure_google_sign_in(page: Page, base_url: str, request: pytest.FixtureRequest) -> None:
    """For each test: if on login page, click Sign in with Google and wait for dashboard (uses saved auth state)."""
    if request.config.getoption("--no-auth", False):
        return
    if request.config.getoption("--no-login", False):
        return
    from framework.pages.login_page import LoginPage

    login_page = LoginPage(page, base_url)
    page.wait_for_load_state("domcontentloaded", timeout=15_000)
    # Wait for app to redirect to dashboard when session is valid (avoids triggering login every test)
    try:
        page.wait_for_url("**/dashboard**", timeout=15_000)
    except Exception:
        pass
    page.wait_for_timeout(1000)
    if not login_page.do_google_sign_in_if_needed(timeout_ms=90_000):
        if login_page.is_login_page():
            pytest.fail(
                "Google sign-in did not reach dashboard. Run: python -m framework.auth.save_auth_state "
                "and complete sign-in, then re-run tests."
            )
    # democandidate can keep stale candidateInfo in saved auth state (resumeList cached as empty).
    # Clear only candidateInfo so dashboard/resume data refreshes from backend.
    try:
        if "democandidate" in (base_url or "").lower():
            stale_candidate_info = page.evaluate(
                """() => {
                    try {
                        const raw = window.localStorage.getItem("candidateInfo");
                        if (!raw) return false;
                        const parsed = JSON.parse(raw);
                        const list = parsed?.resumeList;
                        return Array.isArray(list) && list.length === 0;
                    } catch (_) {
                        return false;
                    }
                }"""
            )
            if stale_candidate_info:
                page.evaluate("() => window.localStorage.removeItem('candidateInfo')")
                base = (base_url or "").rstrip("/")
                page.goto(f"{base}/dashboard", wait_until="domcontentloaded")
                page.wait_for_load_state("domcontentloaded", timeout=15_000)
                try:
                    page.wait_for_load_state("networkidle", timeout=20_000)
                except Exception:
                    pass
                _LOGGER.info("Cleared stale localStorage.candidateInfo to refresh resume data.")
    except Exception:
        pass


@pytest.fixture(scope="session")
def base_url(run_config: RunConfig) -> str:
    return run_config.base_url
