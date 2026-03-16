# Run Recruiter login test (headed). Uses --no-auth so you see: click "Sign in with Google", select account, type password.
Set-Location $PSScriptRoot
python -m pytest tests/test_login_rc.py -v --no-auth
