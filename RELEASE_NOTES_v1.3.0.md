# JUSTECH Downloader v1.3.0

Windows 桌面版，在 v1.2.0 的登入、共用瀏覽器批次下載、續跑、日期區間、臨時匯出、機台停用及結果總表基礎上，新增 **「從 JUSTECH 同步機台」**。

使用者已實測：成功建立 `device_names.json`、同步數量與名稱正確、使用同步機台清單下載報表成功。

下載 `JUSTECH-Downloader-v1.3.0-Windows.zip`，解壓縮後保留整個資料夾，開啟 EXE，登入 JUSTECH 並關閉登入瀏覽器，再按「從 JUSTECH 同步機台」。新機台會先顯示差異供確認；既有機台順序與停用設定維持不變。

**注意：** ZIP 不包含登入資料、實際機台清單或銷售報表。更新安裝時，將原本 `enabled_devices.json`、`billing_periods.json`、`downloads/` 與必要的 `browser_profile/` 複製至 EXE 同層，才能保留設定與續跑紀錄。
