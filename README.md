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

This framework writes all test artifacts under `results/`:

```bash
results/
  report.html
  logs/test.log
  screenshots/
```

The HTML report is **self-contained** and is generated automatically via `pytest.ini`.

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
```

## Configurable test runner

You can also run via `run_tests.py`:

```bash
python run_tests.py --suite all
python run_tests.py --suite sanity
python run_tests.py --suite regression
python run_tests.py --markexpr "smoke and not negative"
```

## Project structure

- `framework/`: page objects + shared config
- `conftest.py`: pytest fixtures for Playwright (`browser`, `context`, `page`)
- `tests/`: tests (use Page Objects rather than raw selectors in tests)

