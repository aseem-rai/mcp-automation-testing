# Run the "click job card in My Jobs / info in center" test with visible browser (headed).
# You should see: Jobs page -> click a job card on the left -> job info appears in the center.
Set-Location $PSScriptRoot
python -m pytest tests/test_jobs_rc.py::test_click_job_card_in_my_jobs_shows_info_in_center -v
