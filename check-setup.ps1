$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3 --version
    if ($LASTEXITCODE -eq 0) { Write-Host 'Python is ready. Run .\run-roadwatch.bat from the RoadWatch folder.' -ForegroundColor Green; exit 0 }
}
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python --version
    if ($LASTEXITCODE -eq 0) { Write-Host 'Python is ready. Run .\run-roadwatch.bat from the RoadWatch folder.' -ForegroundColor Green; exit 0 }
}
Write-Host 'Python 3 is not installed or is not available in PATH.' -ForegroundColor Red
Write-Host 'Install Python 3.11 or newer from https://www.python.org/downloads/windows/'
Write-Host 'In the installer, enable Add python.exe to PATH. Then close and reopen VS Code.'
exit 1
