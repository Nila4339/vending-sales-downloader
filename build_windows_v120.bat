@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found.
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
py -m PyInstaller --noconfirm --clean --onedir --windowed --name JUSTECH-Downloader-v120 --distpath dist-v120 --workpath build-v120 --collect-all playwright --collect-all openpyxl --collect-all tzdata desktop_entry_v120.py
if errorlevel 1 goto failed
if not exist "dist-v120\JUSTECH-Downloader-v120\_internal\playwright\driver\package\.local-browsers" (
 echo ERROR: bundled Chromium missing.
 goto failed
)
echo.
echo Build complete: dist-v120\JUSTECH-Downloader-v120\JUSTECH-Downloader-v120.exe
echo Copy device_names.json into the EXE folder.
echo Copy enabled_devices.json billing_periods.json and downloads if you want to retain settings and resume.
echo Close older EXE and browser instances before launch.
pause
exit /b 0
:failed
echo Build FAILED. Review the error above.
pause
exit /b 1
