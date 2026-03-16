# Mock QA environment

API mocks for running Playwright UI tests **without a backend**. Uses `page.route()` to intercept requests and return static JSON for jobs, resumes, and preps.

## Usage

```bash
pytest tests/ --use-mocks
```

With mocks:

- **Jobs**: list and search responses use `framework/mocks/mock_data.py` → `JOBS_RESPONSE`
- **Resumes**: list/create responses use `RESUMES_RESPONSE`
- **Preps**: list/create responses use `PREPS_RESPONSE`
- **User/Profile/Dashboard**: optional `USER_RESPONSE` and `DASHBOARD_STATS_RESPONSE` for auth/stats

Only XHR/fetch requests whose URL looks like an API (e.g. contains `/api/`, `job`, `resume`, `prep`) are mocked; document navigations are unchanged.

## Layout

- **mock_data.py** – JSON-serializable payloads for jobs, resumes, preps, user, dashboard stats.
- **routes.py** – `install_mock_routes(page)` registers route handlers that fulfill with mock data.

## Conftest

When `--use-mocks` is set, the `page` fixture calls `install_mock_routes(page)` so every test receives a page with API interception enabled. Three job tests that rely on the live app’s job card dropdown menu are skipped when using mocks (run without `--use-mocks` to exercise the menu).
