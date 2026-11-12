@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app.py
  goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python app.py
  goto end
)
echo Python 3 is not installed or is not on PATH.
echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
echo Select "Add python.exe to PATH", finish installation, and reopen VS Code.
pause
:end
endlocal
