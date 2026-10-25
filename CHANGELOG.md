# Changelog

## v1.1.0-refactor（2026-10-24，待本機回歸測試）
- 新建 `app.py`、`download_core.py`、`notifications.py`、`date_helpers.py`，正式批次入口 `batch_download.py`。
- GUI 固定共用瀏覽器，正式流程移除測試檔依賴。
- 更新文件；歷史版本暫不刪除。

## v1.0.2（本機測試成功）
- GUI 移除執行模式選擇。

## v1.0.1（本機測試成功）
- 正式對帳日期可儲存修改、臨時區間獨立匯出不記錄。

## v0.9（本機測試成功）
- 機台停用與每月結果 CSV。

## v0.8.1（本機測試成功）
- 登入按鈕、續跑、批次下載。

## v0.7（本機測試 7 台成功）
- 共用同一瀏覽器逐台下載。

## v0.6.3
- 改用實際下載路徑驗證成功。

## v0.1-dev（2026-10-22）
- 建立 `develop` 分支與初始原型。


## v1.2.0-rc（待 Windows 實測）
- 新增 `desktop_entry_v120.py`、`build_windows_v120.bat`。
- PyInstaller `--windowed`、獨立 `dist-v120` 輸出，保留既有測試版。
- 支援無主控台環境下登入／下載子程序輸出重新導向與錯誤檔。


## v1.3.0-dev（2026-10-25，尚待 Windows 實測）
- 圖形介面新增「從 JUSTECH 同步機台」，登入後可直接建立本機 device_names.json。
- 新增資料先顯示差異清單，取得使用者確認才更新；保留既有機台順序及停用設定。
- JUSTECH 查不到的舊機台預設保留，不直接刪除，降低既有 CSV 紀錄索引錯位風險。
- 新增 `app_desktop_v130.py`、`device_sync.py`、`desktop_entry_v130.py`、`build_windows_v130.bat`。
- v1.2.0 正式發布分支不修改。
