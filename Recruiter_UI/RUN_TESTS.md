## Recruiter_UI - how to run tests

### All tests

```bash
cd Recruiter_UI
python -m pytest
```

### Common options

- **Headed (see browser UI):**

```bash
python -m pytest --headed
```

- **Headless:**

```bash
python -m pytest --headless
```

### By module / feature

- **Login tests (Google / auth state):**

```bash
python -m pytest tests/test_login_rc.py -v
```

- **Dashboard tests:**

```bash
python -m pytest tests/test_dashboard_rc.py -v
```

- **Jobs tests:**

```bash
python -m pytest tests/test_jobs_rc.py -v
```

### Using markers

- **Only jobs tests:**

```bash
python -m pytest -m jobs -v
```

- **Only dashboard tests:**

```bash
python -m pytest -m dashboard -v
```

### Individual high-value test cases

- **Login with Google (main login test):**

```bash
python -m pytest tests/test_login_rc.py::test_login_with_google -v
```

- **Dashboard - 4 insight cards visible:**

```bash
python -m pytest tests/test_dashboard_rc.py::test_dashboard_four_insight_cards_visible -v
```

- **Jobs - Add New Job button clickable:**

```bash
python -m pytest tests/test_jobs_rc.py::test_add_new_job_button_clickable -v
```

- **Jobs - Create New Job button clickable:**

```bash
python -m pytest tests/test_jobs_rc.py::test_create_new_job_button_clickable -v
```

- **Jobs - Create New Job with sample data:**

```bash
python -m pytest tests/test_jobs_rc.py::test_create_new_job_fill_and_submit -v
```

- **Jobs - Click job card in My Jobs and verify center info:**

```bash
python -m pytest tests/test_jobs_rc.py::test_click_job_card_in_my_jobs_shows_info_in_center -v
```

- **Jobs - Upload one or more JDs via Add New Job:**

```bash
python -m pytest tests/test_jobs_rc.py::test_upload_jd_via_add_new_job -v
```

