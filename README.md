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
