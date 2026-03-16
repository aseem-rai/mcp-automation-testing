from __future__ import annotations

import argparse
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def _required_env(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        raise ValueError(f"Missing required environment variable: {name}")
    return val


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send automation report via SMTP.")
    parser.add_argument(
        "--report-path",
        default="test-results/report.html",
        help="Path to HTML report file (default: test-results/report.html).",
    )
    parser.add_argument(
        "--subject",
        default=f"Daily Playwright Automation Report - {datetime.now().strftime('%Y-%m-%d')}",
        help="Email subject line.",
    )
    parser.add_argument(
        "--body",
        default="Hi,\n\nPlease find attached the latest automation report.\n",
        help="Email body text.",
    )
    parser.add_argument(
        "--attach-log",
        action="store_true",
        help="Attach test-results/test.log if present.",
    )
    return parser.parse_args()


def main() -> int:
    project_env = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=project_env)
    args = parse_args()

    report_path = Path(args.report_path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")

    smtp_host = _required_env("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = _required_env("SMTP_USER")
    smtp_pass = _required_env("SMTP_PASS")
    mail_to = _required_env("MAIL_TO")
    smtp_from = os.getenv("SMTP_FROM", smtp_user).strip() or smtp_user

    recipients = [item.strip() for item in mail_to.split(",") if item.strip()]
    if not recipients:
        raise ValueError("MAIL_TO must contain at least one recipient email address.")

    msg = EmailMessage()
    msg["Subject"] = args.subject
    msg["From"] = smtp_from
    msg["To"] = ", ".join(recipients)
    msg.set_content(args.body)

    with report_path.open("rb") as fp:
        msg.add_attachment(
            fp.read(),
            maintype="text",
            subtype="html",
            filename=report_path.name,
        )

    if args.attach_log:
        log_path = Path("test-results/test.log")
        if log_path.exists():
            with log_path.open("rb") as fp:
                msg.add_attachment(
                    fp.read(),
                    maintype="text",
                    subtype="plain",
                    filename=log_path.name,
                )

    use_ssl = _env_bool("SMTP_SSL", False)
    use_tls = _env_bool("SMTP_TLS", True)

    if use_ssl:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

    print(f"Email sent to: {', '.join(recipients)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
