from __future__ import annotations

import argparse
import shlex
import sys
from typing import List, Optional

import pytest


def _build_args(ns: argparse.Namespace) -> List[str]:
    args: List[str] = []

    # Suite selection via markers.
    suite: str = ns.suite
    markexpr: Optional[str] = ns.markexpr
    if markexpr:
        args += ["-m", markexpr]
    elif suite != "all":
        args += ["-m", suite]

    # Forward our Playwright framework CLI options (defined in conftest.py).
    if ns.base_url:
        args += ["--base-url", ns.base_url]
    if ns.browser:
        args += ["--browser", ns.browser]
    if ns.headless:
        args += ["--headless"]
    if ns.headed:
        args += ["--headed"]
    if ns.slowmo is not None:
        args += ["--slowmo", str(ns.slowmo)]

    # Pass-through pytest args.
    if ns.pytest_args:
        args += ns.pytest_args

    if ns.pytest_args_str:
        args += shlex.split(ns.pytest_args_str)

    return args


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="run_tests.py",
        description="Configurable test runner for the Playwright+pytest framework.",
    )

    parser.add_argument(
        "--suite",
        choices=["sanity", "regression", "all"],
        default="all",
        help="Test suite to run. Uses pytest markers (sanity/regression).",
    )
    parser.add_argument(
        "--markexpr",
        default=None,
        help='Custom pytest -m expression (overrides --suite), e.g. "sanity and not flaky".',
    )

    parser.add_argument("--base-url", default=None, help="Override BASE_URL.")
    parser.add_argument("--browser", default=None, help="chromium|firefox|webkit.")

    headless_group = parser.add_mutually_exclusive_group()
    headless_group.add_argument("--headless", action="store_true", help="Run browser headless.")
    headless_group.add_argument("--headed", action="store_true", help="Run browser headed.")

    parser.add_argument("--slowmo", type=int, default=None, help="Slow motion delay (ms).")

    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional pytest args, e.g. tests/test_x.py -k login",
    )
    parser.add_argument(
        "--pytest-args",
        dest="pytest_args_str",
        default=None,
        help='Additional pytest args as a single string, e.g. \'--maxfail=1 -k "smoke"\'.',
    )

    # Allow arbitrary pytest flags without needing a special separator:
    # unknown args are treated as pytest args and forwarded.
    ns, unknown = parser.parse_known_args(argv)
    if unknown:
        ns.pytest_args = list(ns.pytest_args) + unknown
    args = _build_args(ns)
    return int(pytest.main(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
