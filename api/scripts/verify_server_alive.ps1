param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [string]$LaunchCommand = "uvicorn",
    [string[]]$LaunchArguments = @("app.main:app", "--host", "127.0.0.1", "--port", "8000"),
    [string]$WorkingDirectory = (Get-Location).Path,
    [int]$StartupDelaySeconds = 3
)

# Verification/CI helper only.
# For active local development, keep Uvicorn in a foreground terminal so you can watch logs and process lifetime directly.

$ErrorActionPreference = "Stop"

$process = Start-Process `
    -FilePath $LaunchCommand `
    -ArgumentList $LaunchArguments `
    -WorkingDirectory $WorkingDirectory `
    -PassThru `
    -WindowStyle Hidden

Start-Sleep -Seconds $StartupDelaySeconds

$alive = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
if (-not $alive) {
    Write-Host "FAIL: Uvicorn process not found after launch - process died or never started (lifecycle failure, not an app bug). Check launch method (foreground vs. background/detached) before investigating application code."
    exit 1
}

$healthUrl = "http://$Host`:$Port/health"
$healthStatus = curl.exe -s -o NUL -w "%{http_code}" $healthUrl

if ($healthStatus -ne "200") {
    Write-Host "FAIL: Uvicorn process is alive (PID found) but GET /health did not return 200 - this points to an application/runtime issue (config, DB connection, startup exception, or route error), not a process-lifecycle problem. Check app logs next."
    exit 1
}

Write-Host "PASS: Uvicorn is alive and /health returned 200."
exit 0
