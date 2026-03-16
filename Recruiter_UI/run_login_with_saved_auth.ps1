# Run Recruiter login test with saved auth (headed). Skips login page, goes straight to dashboard.
Set-Location $PSScriptRoot
python -m pytest tests/test_login_rc.py -v
