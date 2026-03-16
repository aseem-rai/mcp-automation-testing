param(
    [string]$ProjectRoot = "D:\playwright-mcp",
    [string]$PythonExe = "D:\playwright-mcp\venv\Scripts\python.exe",
    [switch]$SkipEmail,
    [string]$PytestArgs = "tests -q"
)

$ErrorActionPreference = "Stop"

Write-Host "Project root: $ProjectRoot"
Write-Host "Python: $PythonExe"
Write-Host "Pytest args: $PytestArgs"

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

Set-Location $ProjectRoot

$pytestArgsList = @()
if ($PytestArgs -and $PytestArgs.Trim().Length -gt 0) {
    $pytestArgsList = $PytestArgs.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
}

& $PythonExe -m pytest @pytestArgsList
$pytestExit = $LASTEXITCODE
Write-Host "pytest exit code: $pytestExit"

$finalExit = $pytestExit

if (-not $SkipEmail) {
    $status = if ($pytestExit -eq 0) { "PASSED" } else { "FAILED" }
    $subject = "Daily Automation Report [$status] $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    $body = @"
Hi,

Please find attached the latest Playwright automation report.
Overall test status: $status

Regards,
Automation Scheduler
"@

    & $PythonExe "scripts/send_report_email.py" --subject $subject --body $body --attach-log
    $emailExit = $LASTEXITCODE
    Write-Host "email exit code: $emailExit"

    if ($emailExit -ne 0 -and $finalExit -eq 0) {
        $finalExit = $emailExit
    }
}

exit $finalExit
