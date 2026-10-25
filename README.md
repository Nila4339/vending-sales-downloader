# JUSTECH 銷售報表下載器 v1.2.0

Windows 桌面版（正式發布內容）。本分支只保留 v1.2.0 所需程式碼與打包工具；舊版原始碼、測試及歷史資料保留在 `develop` 分支，不包含在本分支下載 ZIP。

## Windows 打包

1. 下載本 `release/v1.2.0` 分支的 ZIP 並解壓縮。
2. 安裝 Python（含 `py` 啟動器），連上網路。
3. 雙擊 `build_windows_v120.bat`。
4. 執行 `dist-v120\JUSTECH-Downloader-v120\JUSTECH-Downloader-v120.exe`。

PyInstaller 產生的是 **onedir 資料夾型態**；`JUSTECH-Downloader-v120.exe` 與 `_internal/` 必須一起保留。打包過程會下載 Playwright Chromium。

## 使用前準備

EXE 同層需要本機 `device_names.json`，可由舊版複製，或以開發環境執行 `discover_devices.py` 建立。

可選擇從舊資料夾複製：
- `enabled_devices.json`：停用機台設定
- `billing_periods.json`：每月自訂區間
- `browser_profile/`：登入工作階段（複製前關閉相關瀏覽器）
- `downloads/`：歷史 Excel 與續跑紀錄

不複製 `downloads/` 時，新版不會知道先前哪些機台已下載；如果要維持續跑，務必保留原資料。

## 功能

- GUI 開啟 JUSTECH 登入瀏覽器
- 共用瀏覽器逐台批次下載商品月銷售數量統計表
- 自動命名、檔案格式檢查、下載紀錄與續跑
- 機台啟用／停用、搜尋、下載結果總表
- 正式月結日期調整、臨時日期範圍匯出（不計入月結紀錄）
- 無黑色命令列主視窗；錯誤紀錄檔供診斷

## 本分支結構

- `desktop_entry_v120.py`：EXE 多模式入口
- `app_desktop.py`：圖形介面
- `batch_download.py`：批次下載與續跑
- `download_core.py`：逐台匯出核心
- `notifications.py`：通知辨識
- `date_helpers.py`：日期選擇
- `open_login_desktop.py`：登入瀏覽器
- `discover_devices.py`：建立機台清單輔助工具
- `build_windows_v120.bat`：Windows 打包腳本
- `requirements.txt`：依賴套件

## 安全提醒

本機 `browser_profile/`、`device_names.json`、`enabled_devices.json`、`billing_periods.json`、`downloads/` 與銷售報表不得提交 GitHub。避免其他人同時匯出相同報表，通知中心的時間戳並非機台歸屬的絕對證明。

Windows EXE 的登入、下載、續跑、臨時匯出、機台管理及結果總表均已由使用者驗收正常。
