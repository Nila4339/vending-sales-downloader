# JUSTECH 銷售報表下載器｜專案記憶

更新：2026-10-24。只修改 `develop`，不修改 `main` 或另一個正式 GAS 系統。

## 使用者實測成功
- v0.6.3 批次下載與實際下載路徑驗證。
- v0.7 同瀏覽器連續下載 7 台及續跑。
- v0.8.1 登入、批次與續跑。
- v0.9 機台停用與結果總表。
- v1.0.1 儲存自訂正式對帳日期、臨時區間匯出。
- v1.0.2 移除執行模式選擇，統一共用瀏覽器。

## 模組化重構（尚待本機回歸測試）
- `app.py` -> `batch_download.py` -> `download_core.py`。
- `notifications.py`、`date_helpers.py` 從測試模組提取，正式程式不再 import `test_*.py`。
- 仍保留 v1.0.2 穩定版供回退，尚未清除歷史檔。

## 資料和限制
- 本機 `device_names.json` 機台清單、`enabled_devices.json` 啟用設定、`billing_periods.json` 日期設定。
- `browser_profile/` 登入狀態；`downloads/YYYY-MM/` 月結及續跑記錄；`downloads/custom/` 臨時匯出，不影響月結。
- 預設上月 26 日 00:00 至本月 26 日 00:00（終點不包含當日之後）。
- 通知中心時間戳比對無法百分之百證明報表屬於某台機台；禁止同時競爭匯出。
- 技術債：續跑尚未完整比對已保存 Excel 的存在性；封存前應先回歸測試。

清理規劃見 `CLEANUP_AUDIT.md`。
