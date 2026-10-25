# JUSTECH 銷售報表下載器

Windows Python + Playwright GUI。已實測穩定版為 v1.0.2；模組化重構版尚待 Windows 回歸測試。

## 啟動重構版

```powershell
.\.venv\Scripts\python.exe app.py
```

首次安裝需執行 `py -m venv .venv`、`.\.venv\Scripts\python.exe -m pip install -r requirements.txt` 和 `.\.venv\Scripts\python.exe -m playwright install chromium`。

先準備本機 `device_names.json`（若缺少，單獨執行 `discover_devices.py` 建立），在 GUI 按「開啟 JUSTECH 登入」，完成登入後關閉登入視窗，再開始下載。

## 功能

- 共用單一瀏覽器逐台匯出報表，自動命名、驗證與清除對應通知。
- 月結預設區間：上月 26 日 00:00 至本月 26 日 00:00；支援儲存自訂每月區間。
- 臨時區間匯出至 `downloads/custom/`，不參與月結下載紀錄或續跑。
- 機台搜尋、啟用停用、下載結果 CSV、成功略過、中途停止。

## 正式檔案

| 檔案 | 用途 |
| --- | --- |
| `app.py` | 圖形介面入口 |
| `batch_download.py` | 共用瀏覽器批次下載、續跑 |
| `download_core.py` | 逐台操作、格式驗證與保存 |
| `notifications.py` | 通知比對與單筆清除 |
| `date_helpers.py` | 日期區間與月曆操作 |
| `open_login_v081.py` | 登入視窗 |
| `discover_devices.py` | 機台清單擷取 |

穩定回退：`downloader_gui_v102.py`、`batch_download_v101.py`、`download_core_v101.py` 及其相依測試模組，回歸測試前不刪除。

## 安全與限制

`device_names.json`、`enabled_devices.json`、`billing_periods.json`、`browser_profile/`、`downloads/`、`.venv/` 不上傳 GitHub。通知僅以時間戳比對，避免其他使用者同時匯出相同報表。不要同時開登入視窗與下載程序。

清理詳見 [CLEANUP_AUDIT.md](CLEANUP_AUDIT.md)。

## 歷史版本

48 個早期測試與舊版程式已移至 [`archive/legacy/`](archive/legacy/)。v1.0.2 穩定回退組仍保留在根目錄；日常使用只需執行 `app.py`。


## Windows EXE 測試打包（實驗版）

從 GitHub `develop` 下載整包 ZIP 到**獨立的新資料夾**（不要覆蓋原本已正常的 Python 工作資料夾），在 Windows 雙擊 `build_windows.bat`。需事先安裝 Python 及網路下載依賴。

批次檔會安裝 PyInstaller、`requirements.txt`、Playwright Chromium 並執行 `--onedir --console` 打包，產生：

```text
dist/ JUSTECH-Downloader / JUSTECH-Downloader.exe
```

實際資料夾路徑沒有上列空格：`dist\JUSTECH-Downloader\JUSTECH-Downloader.exe`。

- 先將舊專案的 `device_names.json` 複製到 EXE **同層資料夾**。
- 可複製 `enabled_devices.json`、`billing_periods.json`，保留機台及日期偏好。
- 若要直接沿用登入狀態，必須在所有瀏覽器關閉後複製 `browser_profile/`；不複製也可以透過 EXE 重新登入。
- 如需沿用續跑結果，複製舊資料夾 `downloads/` 到 EXE 同層目錄；**不複製就不會知道過去成功的機台**。
- 此 EXE 為 `--onedir`，不要只移動 EXE 而留下旁邊的 `_internal/`，需要整個資料夾一起移動。
- 本版為驗證用 `--console`，會出現命令列視窗；驗收完成後才改成無主控台視窗的發行版。
- 不要同時執行原 Python GUI 與 EXE，尤其不要共用同一 `browser_profile/`。

**重要：** 這裡提供的是 Windows 本機打包腳本，而非已編譯好的 EXE。尚未在 Windows 完成 PyInstaller 打包／實際執行驗證。先確認登入、單台匯出、臨時匯出、續跑與結果總表，再評估發行。


## v1.2.0 Windows 無命令列視窗候選版

從 develop 下載 ZIP，在新的資料夾執行 `build_windows_v120.bat`（不是舊的 `build_windows.bat`）。打包後程式位於 `dist-v120/ JUSTECH-Downloader-v120/ JUSTECH-Downloader-v120.exe`（這裡用空格隔開路徑層級，實際名稱沒有額外空格）。

- PyInstaller 使用 `--windowed --onedir`，移除主視窗後方的命令列。
- 重要：不要覆蓋先前已測試成功的 `dist-exe-test`。
- 將 `device_names.json` 複製至新版 EXE 同層。要沿用停用設定、日期與續跑，請一併複製 `enabled_devices.json`、`billing_periods.json` 與 `downloads/`。
- 瀏覽器登入可在新版重新登入；如需帶入 `browser_profile/`，請先完全關閉舊版 EXE 與 Chromium。
- 測試登入、單台下載、進度、續跑、臨時區間、停用管理與 CSV。
- 錯誤診斷：`login_diagnostic.log`、`desktop_error.log`，下載輸出仍於 GUI 顯示。
- **此版本尚未在 Windows 測試；通過驗收後才可當作發行版。**
