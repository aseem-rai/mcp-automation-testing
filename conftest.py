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

from framework.config import settings

_LOGGER = logging.getLogger(__name__)

_RESULTS_DIR = Path("results")
_SCREENSHOTS_DIR = _RESULTS_DIR / "screenshots"
_LOGS_DIR = _RESULTS_DIR / "logs"
_CONSOLE_LOG_PATH = _LOGS_DIR / "test.log"
_HTML_REPORT_PATH = _RESULTS_DIR / "report.html"

_CURRENT_NODEID: ContextVar[str | None] = ContextVar("_CURRENT_NODEID", default=None)
_LAST_PAGE_URL_BY_NODEID: dict[str, str] = {}


class _PerTestLogHandler(logging.Handler):
    """
    Capture log records per-test so we can embed them into pytest-html Details.
    """

    def __init__(self) -> None:
        # Capture everything; filtering is handled by root/logger levels.
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
    parser.addoption("--base-url", action="store", default=settings.base_url)
    parser.addoption("--browser", action="store", default=settings.browser_name)
    parser.addoption("--headless", action="store_true", default=settings.headless)
    # Important: default must be False so passing nothing doesn't force headed mode.
    parser.addoption("--headed", action="store_true", default=False)
    parser.addoption("--slowmo", action="store", default=str(settings.slow_mo_ms))
    parser.addoption("--ignore-https-errors", action="store_true", default=settings.ignore_https_errors)
    parser.addoption(
        "--open-report",
        action="store_true",
        default=None,
        help="Open the HTML report (results/report.html) after the test run completes.",
    )
    parser.addoption(
        "--no-open-report",
        action="store_true",
        default=False,
        help="Do not open the HTML report after the test run completes.",
    )


def pytest_configure(config: pytest.Config) -> None:
    # Ensure output directories exist even on a fresh checkout / CI workspace.
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Capture logs per-test for embedding into pytest-html.
    root = logging.getLogger()
    if _PER_TEST_LOG_HANDLER not in root.handlers:
        root.addHandler(_PER_TEST_LOG_HANDLER)


def pytest_sessionstart(session: pytest.Session) -> None:
    # Ensure log directory exists even if pytest is invoked from a different CWD.
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    _LOGGER.info("=== pytest session start ===")
    _LOGGER.info("python=%s", sys.version.replace("\n", " "))
    _LOGGER.info("platform=%s", sys.platform)
    _LOGGER.info("base_url=%s", getattr(session.config, "getoption", lambda *_: None)("--base-url"))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _LOGGER.info("=== pytest session finish (exitstatus=%s) ===", exitstatus)
    _maybe_open_html_report(session)


def _maybe_open_html_report(session: pytest.Session) -> None:
    """
    Automatically open results/report.html after the run.

    Defaults:
    - enabled for interactive local runs
    - disabled in CI or when output isn't a TTY
    - can be overridden via:
      - `--open-report` / `--no-open-report`
      - `OPEN_REPORT=1|0` env var
    """
    config = session.config

    if getattr(session, "testscollected", 0) <= 0:
        return

    env = os.getenv("OPEN_REPORT")
    if env is not None:
        enabled = env.strip().lower() in {"1", "true", "t", "yes", "y", "on"}
    else:
        # Interactive default: don't pop browsers open in CI/non-interactive.
        in_ci = os.getenv("CI") is not None
        enabled = bool(getattr(sys.stdout, "isatty", lambda: False)()) and not in_ci

    if config.getoption("--no-open-report", default=False):
        enabled = False
    if config.getoption("--open-report", default=None) is True:
        enabled = True

    if not enabled:
        return

    report_path = _HTML_REPORT_PATH.resolve()
    if not report_path.exists():
        return

    try:
        # Windows: open in default browser (non-blocking).
        if os.name == "nt":
            os.startfile(str(report_path))  # type: ignore[attr-defined]
        else:
            import webbrowser

            webbrowser.open(report_path.as_uri(), new=2)
    except Exception:
        _LOGGER.exception("Failed to open HTML report: %s", report_path)


def pytest_runtest_logstart(nodeid: str, location) -> None:
    _CURRENT_NODEID.set(nodeid)
    _LOGGER.info("START %s", nodeid)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return

    if report.passed:
        _LOGGER.info("PASS  %s (%.3fs)", report.nodeid, report.duration)
    elif report.failed:
        _LOGGER.error("FAIL  %s (%.3fs)", report.nodeid, report.duration)
    elif report.skipped:
        _LOGGER.warning("SKIP  %s (%.3fs)", report.nodeid, report.duration)

    # Store last known page URL for the report link (best effort).
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
    # Make the current test id available to the per-test log handler.
    token = _CURRENT_NODEID.set(getattr(item, "nodeid", item.name))
    try:
        yield
    finally:
        _CURRENT_NODEID.reset(token)


def _safe_filename(value: str, *, max_len: int = 180) -> str:
    # Keep it Windows-friendly (no <>:"/\|?*), stable and readable.
    value = re.sub(r"[<>:\"/\\\\|?*]+", "_", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > max_len:
        value = value[:max_len].rstrip("_ .")
    return value or "test"


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """
    On failure, take a Playwright screenshot (if the `page` fixture exists).
    Uses `pytest_runtest_makereport` so it works for setup/call/teardown phases.
    """
    outcome = yield
    report: pytest.TestReport = outcome.get_result()

    if report.when != "call":
        return

    # Attach full per-test logs + useful links into pytest-html Details (pass/fail).
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extra = getattr(report, "extra", [])

        logs_text = _PER_TEST_LOG_HANDLER.get_text(report.nodeid)
        if logs_text:
            pre = "<pre style='white-space:pre-wrap; word-break:break-word;'>" + html.escape(logs_text) + "</pre>"
            extra.append(pytest_html.extras.html(pre))

        # Also embed captured stdout/stderr (pytest capture), if any.
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

        # Embed any additional report sections (e.g., plugin-provided captured output).
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

        # Link to the final page URL for this test (if we have it).
        page_url = ""
        try:
            page = item.funcargs.get("page")
            if page is not None:
                page_url = str(page.url)
        except Exception:
            page_url = _LAST_PAGE_URL_BY_NODEID.get(report.nodeid, "")

        if page_url:
            extra.append(pytest_html.extras.url(page_url, name="Final page URL"))

        # Link to the run-wide log file (useful on CI / shareable artifacts).
        try:
            extra.append(pytest_html.extras.url(_CONSOLE_LOG_PATH.resolve().as_uri(), name="Run log file"))
        except Exception:
            extra.append(pytest_html.extras.url(str(_CONSOLE_LOG_PATH.resolve()), name="Run log file"))

        report.extra = extra

    if report.passed or report.skipped:
        return

    page: Optional[Page] = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    if page is None:
        return

    timestamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    nodeid = _safe_filename(getattr(item, "nodeid", item.name))
    path = _SCREENSHOTS_DIR / f"{nodeid}_{timestamp}.png"

    try:
        page.screenshot(path=str(path), full_page=True)
        _LOGGER.info("Saved failure screenshot: %s", path.as_posix())

        # Attach to pytest-html if available.
        if pytest_html is not None:
            extra = getattr(report, "extra", [])
            extra.append(pytest_html.extras.image(str(path)))
            try:
                extra.append(pytest_html.extras.url(path.resolve().as_uri(), name="Failure screenshot file"))
            except Exception:
                extra.append(pytest_html.extras.url(str(path.resolve()), name="Failure screenshot file"))
            report.extra = extra
    except Exception:
        _LOGGER.exception("Failed to capture screenshot for %s", getattr(item, "nodeid", item.name))


@pytest.fixture(scope="session")
def run_config(pytestconfig: pytest.Config) -> RunConfig:
    base_url = str(pytestconfig.getoption("--base-url"))
    browser_name = str(pytestconfig.getoption("--browser"))
    slow_mo_ms = int(pytestconfig.getoption("--slowmo"))

    # Allow either flag; --headed wins if both are passed.
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
    browser = browser_type.launch(headless=run_config.headless, slow_mo=run_config.slow_mo_ms)
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser, run_config: RunConfig) -> BrowserContext:
    context = browser.new_context(ignore_https_errors=run_config.ignore_https_errors)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    page = context.new_page()
    page.set_default_timeout(settings.default_timeout_ms)
    page.set_default_navigation_timeout(settings.navigation_timeout_ms)
    return page


@pytest.fixture(scope="session")
def base_url(run_config: RunConfig) -> str:
    return run_config.base_url

