@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Cannot find Python launcher "py". Install Python 3.11+ and try again.
  pause
  exit /b 1
)
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto failed
py -m pip install -r requirements.txt
if errorlevel 1 goto failed
set "PLAYWRIGHT_BROWSERS_PATH=0"
py -m playwright install chromium
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --onedir --console --name JUSTECH-Downloader-Test --distpath dist-exe-test --workpath build-exe-test --collect-all playwright --collect-all openpyxl --collect-all tzdata desktop_entry.py
if errorlevel 1 goto failed
echo.
if not exist "dist-exe-test\JUSTECH-Downloader-Test\_internal\playwright\driver\package\.local-browsers" (
  echo ERROR: bundled Chromium not found; build is incomplete.
  goto failed
)
echo Build complete: dist-exe-test\JUSTECH-Downloader-Test\JUSTECH-Downloader-Test.exe
echo IMPORTANT: Copy your existing device_names.json to the EXE folder.
echo Optional: copy enabled_devices.json, billing_periods.json and browser_profile directory.
pause
exit /b 0
:failed
echo Build failed. Read the error lines above.
pause
exit /b 1
