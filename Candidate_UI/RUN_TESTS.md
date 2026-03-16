## Candidate_UI - how to run tests

### All tests

```bash
cd Candidate_UI
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

- **Only smoke tests:**

```bash
python -m pytest -m smoke
```

### By module / feature

- **Dashboard tests:**

```bash
python -m pytest tests/test_dashboard.py -v
```

- **Login tests:**

```bash
python -m pytest tests/test_login.py -v
```

- **Resume module tests:**

```bash
python -m pytest tests/test_resume.py -v
```

- **Profile tests (includes resume→profile flow):**

```bash
python -m pytest tests/test_profile.py -v
```

- **Jobs / prep tests:**

```bash
python -m pytest tests/test_jobs.py -v
python -m pytest tests/test_preps.py -v
```

### Individual high-value test cases

- **Resume upload then verify profile data populated:**

```bash
python -m pytest tests/test_profile.py::test_profile_after_new_resume_upload -v
```

- **Profile smoke:**

```bash
python -m pytest tests/test_profile.py::test_profile_page_smoke -v
```

- **Profile download file:**

```bash
python -m pytest tests/test_profile.py::test_profile_download_profile_file -v
```

- **Resume page loads and shows content:**

```bash
python -m pytest tests/test_resume.py::test_resume_page_load -v
```

- **Resume card visible:**

```bash
python -m pytest tests/test_resume.py::test_resume_visible -v
```

