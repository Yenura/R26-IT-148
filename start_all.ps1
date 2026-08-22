# ===============================================================================
#                RECRUITAI - MASTER 1-CLICK POWERSHELL LAUNCHER
# ===============================================================================

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$PyPath = if (Test-Path "$Root\.venv\Scripts\python.exe") {
    "$Root\.venv\Scripts\python.exe"
} elseif (Test-Path "$Root\.venv312\Scripts\python.exe") {
    "$Root\.venv312\Scripts\python.exe"
} else {
    "python"
}

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "               RECRUITAI - MASTER 1-CLICK SYSTEM LAUNCHER                      " -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "Executing launcher with Python: $PyPath`n" -ForegroundColor Yellow

& $PyPath "$Root\start_all.py"
