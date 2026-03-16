# Playwright + pytest (Python) — Page Object Model

## Setup

Create a venv and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

## Run tests

```bash
pytest
```

## Results (reports, logs, screenshots)

This framework writes all test artifacts under `reports/`:

```bash
reports/
  report.html      # Pytest HTML report (test name, status, logs, error, screenshot on failure)
  test.log         # Step and test lifecycle logs (timestamp, test name, STEP / PASS / FAIL)
  screenshots/     # Failure screenshots (auto-captured)
```

The HTML report is **self-contained** and is generated via `pytest --html=reports/report.html --self-contained-html`. Step logging (from page objects and tests) appears in both `reports/test.log` and in the HTML report Details for each test.

The report can auto-open after the run (interactive sessions). Control it with:

```bash
pytest --open-report
pytest --no-open-report
set OPEN_REPORT=1
set OPEN_REPORT=0
```

Common options:

```bash
pytest --headed
pytest --headless
pytest --browser=chromium
pytest --base-url=https://example.com
pytest -m smoke
```

## Run specific suites (markers)

```bash
pytest -m smoke
pytest -m resume
pytest -m profile
pytest -m e2e
```

## Configurable test runner

You can also run via `run_tests.py`:

```bash
python run_tests.py --suite all
python run_tests.py --suite sanity
python run_tests.py --suite regression
python run_tests.py --markexpr "smoke and not negative"
```

## Schedule daily run + email report (Windows)

### 1) Add SMTP settings to `.env`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MAIL_TO=your_email@gmail.com
# Optional:
# SMTP_FROM=qa-bot@yourcompany.com
# SMTP_TLS=true
# SMTP_SSL=false
```

### 2) Run locally once (test + email)

```bash
powershell -ExecutionPolicy Bypass -File scripts/run_scheduled_tests.ps1
```

Python-only alternative:

```bash
venv\Scripts\python.exe scripts/run_scheduled_tests.py
```

For smoke-only:

```bash
powershell -ExecutionPolicy Bypass -File scripts/run_scheduled_tests.ps1 -PytestArgs "tests -m smoke -q"
```

### 3) Task Scheduler command

Create a Windows Task Scheduler task (daily trigger), and set:

- Program/script: `D:\playwright-mcp\venv\Scripts\python.exe`
- Add arguments:

```bash
scripts\run_scheduled_tests.py --project-root D:\playwright-mcp
```

This flow runs pytest first and then emails `test-results/report.html` (+ `test-results/test.log`).

## Project structure

- `framework/`: page objects + shared config
- `conftest.py`: pytest fixtures for Playwright (`browser`, `context`, `page`)
- `tests/`: tests (use Page Objects rather than raw selectors in tests)

