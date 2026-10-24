# 專案程式盤點與清理建議（2026-10-24）

> 範圍：GitHub `develop` 分支根目錄，靜態檢視與使用者提供的本機測試結果。**未執行 JUSTECH 登入後端到端測試，不能將舊檔都宣稱為失敗。** 本次不刪除檔案、不修改 main。

## 目前日常使用入口（新 GUI 待本機驗證）

- `downloader_gui_v102.py`：GUI；固定使用共用瀏覽器；登入、機台啟用、月結、臨時區間、月結 CSV 統計。
- `batch_download_v101.py`：批次與續跑紀錄；臨時匯出 `--adhoc` 不讀寫月結紀錄。
- `download_core_v101.py`：Playwright 逐台匯出、通知檢查、驗證下載及命名。
- `open_login_v081.py`：GUI 登入視窗。
- `test_auto_export_v063.py`：**雖有 test 前綴仍被 download_core_v101.py import**，提供通知比對、關閉通知和檔名清理。不得直接刪除。
- `test_date_range.py`：**雖有 test 前綴仍被 download_core_v101.py、GUI import**，提供日期月曆操作和預設對帳範圍。不得直接刪除。
- `discover_devices.py`：重新建立本機機台清單的輔助工具。
- `requirements.txt`、`.gitignore`：環境與安全忽略規則。

## 建議封存（而非立即刪除）

- 早期單台試驗：`test_auto_export_one.py`、`test_auto_export_v05.py`～`test_auto_export_v061.py`；保留 v063 作目前相依函式庫。
- 早期多台試驗：`test_batch_3.py`、`test_batch_v052.py`～`test_batch_v061.py`。
- DOM 檢視工具：`inspect_date_picker.py`、`inspect_notifications.py`、`inspect_notification_cards_v05.py`、`inspect_notification_close_v06.py`；可保留做網站改版除錯，不需放在使用者日常下載入口。
- 舊批次：`batch_download.py`、`batch_download_gui_runner.py`、`batch_download_v062.py`、`batch_download_v063.py`、`batch_download_v070.py`、`batch_download_v100.py`。
- 舊核心：`download_core_v07.py`、`download_core_v10.py`。
- 舊 GUI：`downloader_gui.py`、`downloader_gui_v07.py`、`downloader_gui_v071.py`、`downloader_gui_v072.py`、`downloader_gui_v080.py`、`downloader_gui_v081.py`、`downloader_gui_v090.py`、`downloader_gui_v101.py`。
- `downloader.py`、`machines.csv`、`config.example.json` 為早期 CSV／dry-run 原型，不是目前 `device_names.json` 工作流程的必要檔案。

## 確認過的歷史問題（不代表所有舊檔皆失敗）

- `downloader_gui_v071.py` 曾包含字面 `\\n` 導致 SyntaxError；已由後續版本修正。
- `batch_download_v062.py` 將資料夾前後檔名差集作為成功條件，曾出現 `exit_code=0, matching_new_files=0` 誤判；後改成 v063 的實際下載回報檢查。
- v0.5.7～v0.5.9 的通知 X 位置選取假設有誤；直到 v0.6.0 對 parent^3 按鈕的選取獲本機成功實測。
- `README.md`、`PROJECT_MEMORY.md`、`CHANGELOG.md` 的內容已落後現況，仍提到只可 dry-run 或功能尚未實作；需要更新。
- `batch_download_v101.py` 在既有設計下以 **月份＋機台序號／名稱** 記錄已完成，實際檔案存在性並未作為續跑判斷的一部分；如果手動刪除已下載 Excel，可能仍被略過。
- 通知的時間戳記比對只是一種關聯推測；若其他人同時匯出相同類型報表，仍可能無法唯一辨識機台。請避免同時操作。

## 建議下一輪重構（需要測試後才可以刪舊檔）

1. 建立正式名稱 `app.py`／`download_core.py`／`batch_download.py` 與 `date_helpers.py`、`notifications.py`，移除核心對 `test_*.py` 的 import；再做完整 GUI、日期、臨時匯出、續跑回歸測試。
2. 產出 `archive/legacy` 或 Git tag 標記歷史版本後，才將不使用的歷史檔移出根目錄，並確認沒有活躍程式 import。
3. 將使用指南、版本紀錄、登入限制、輸出資料夾結構更新為目前架構。
4. 最後才考慮刪除明確無依賴的歷史檔。現在保留在 Git 中，避免丟失除錯線索。

## 本機檔案不可納入 Git

`device_names.json`、`enabled_devices.json`、`billing_periods.json`、`browser_profile/`、`downloads/`、`config.json`、`.venv/` 應持續忽略。不要提交登入資料、機台敏感資訊或銷售報表。

## 2026-10-24 封存結果

已在 `develop` 分支以單一 Git commit 將 48 個舊版／實驗檔移至 `archive/legacy/`，不刪除檔案內容。保留 `app.py`、`batch_download.py`、`download_core.py`、`notifications.py`、`date_helpers.py`、登入與機台工具，並保留 v1.0.2 回退組（`downloader_gui_v102.py`、`batch_download_v101.py`、`download_core_v101.py`、`test_auto_export_v063.py`、`test_date_range.py`）。未修改 `main`。尚待使用者本機確認封存後正式入口仍能正常運行。
