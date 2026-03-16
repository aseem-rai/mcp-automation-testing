from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run scheduled pytest execution and optionally email HTML report."
    )
    parser.add_argument(
        "--project-root",
        default=str(PROJECT_ROOT),
        help="Project root directory (default: repo root).",
    )
    parser.add_argument(
        "--skip-email",
        action="store_true",
        help="Skip sending the email report.",
    )
    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Arguments passed to pytest. Example: --pytest-args tests -m smoke -q",
    )
    return parser.parse_args()


def run_pytest(pytest_args: list[str], cwd: Path) -> int:
    cmd = [sys.executable, "-m", "pytest", *pytest_args]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(cwd))
    return int(result.returncode)


def send_email(cwd: Path, pytest_exit: int) -> int:
    status = "PASSED" if pytest_exit == 0 else "FAILED"
    subject = f"Daily Automation Report [{status}] {datetime.now():%Y-%m-%d %H:%M}"
    body = (
        "Hi,\n\n"
        "Please find attached the latest Playwright automation report.\n"
        f"Overall test status: {status}\n\n"
        "Regards,\n"
        "Automation Scheduler\n"
    )
    cmd = [
        sys.executable,
        "scripts/send_report_email.py",
        "--subject",
        subject,
        "--body",
        body,
        "--attach-log",
    ]
    print("Running:", " ".join(cmd[:3]), "...")  # avoid noisy body echo
    result = subprocess.run(cmd, cwd=str(cwd))
    return int(result.returncode)


def main() -> int:
    ns = parse_args()
    project_root = Path(ns.project_root).resolve()
    pytest_args = ns.pytest_args if ns.pytest_args else ["tests", "-q"]

    if not project_root.exists():
        print(f"Project root not found: {project_root}")
        return 2

    pytest_exit = run_pytest(pytest_args, project_root)
    print(f"pytest exit code: {pytest_exit}")

    final_exit = pytest_exit
    if not ns.skip_email:
        email_exit = send_email(project_root, pytest_exit)
        print(f"email exit code: {email_exit}")
        if email_exit != 0 and final_exit == 0:
            final_exit = email_exit

    return final_exit


if __name__ == "__main__":
    raise SystemExit(main())
