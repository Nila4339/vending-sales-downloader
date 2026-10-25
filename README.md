# JUSTECH 銷售報表下載器

**Windows 桌面工具｜最新穩定版本 v1.3.0**

JUSTECH 銷售報表下載器是協助販賣機營運與對帳人員批次匯出銷售資料的桌面程式。過去需要登入 JUSTECH 後台、逐台選擇機台、設定日期並下載報表；現在可以一次指定多台機器，交由程式依序下載並整理結果。

> 本專案為第三方自動化輔助工具，非 JUSTECH 官方軟體。使用時需要有權限登入 JUSTECH 的帳號，匯出後仍應核對報表內容與對帳期間。

## ⬇️ 下載 Windows 正式版

**[下載 JUSTECH 銷售報表下載器 v1.3.0（GitHub Release）](https://github.com/Nila4339/vending-sales-downloader/releases/tag/v1.3.0)**

在 Release 頁面的 **Assets** 下載 `JUSTECH-Downloader-v1.3.0-Windows.zip`，解壓縮後開啟 `JUSTECH-Downloader-v1.3.0.exe`。正式 ZIP 已包含 Windows 執行程式及所需元件，使用者**不需要安裝 Python**。

**請保留整個解壓縮資料夾**，不要只複製 EXE；程式還需要旁邊的 `_internal/`。

## ✨ 主要功能

| 功能 | 說明 |
| --- | --- |
| 批次下載銷售報表 | 指定全部或部分機台，共用瀏覽器依序下載，檔案依機台名稱標示 |
| 同步 JUSTECH 機台 | 登入後可同步設備清單，首次使用不必自行建立 `device_names.json` |
| 月結區間設定 | 預設上月 26 日 00:00 至本月 26 日 00:00（結束日不包含），可自行調整及儲存 |
| 臨時區間匯出 | 查詢特定起訖日期，不影響正式月結下載紀錄 |
| 中斷續跑 | 依成功紀錄略過已完成機台，並可選擇重新下載 |
| 管理機台 | 搜尋、指定、啟用與停用機台 |
| 下載結果總表 | 檢視每月進度，產生結果總表 CSV |

## 🚀 第一次使用

1. 下載上述 Windows ZIP，完整解壓縮。
2. 開啟 `JUSTECH-Downloader-v1.3.0.exe`。
3. 點選 **「開啟 JUSTECH 登入」**，在開啟的瀏覽器完成登入；關閉登入瀏覽器後返回下載器。
4. 點選 **「從 JUSTECH 同步機台」**，核對數量和名稱，確認後建立本機清單。
5. 選擇對帳年月、日期區間與下載機台，按 **「開始下載」**。
6. 完成後使用 **「開啟下載資料夾」** 查看報表，也可以匯出本月結果總表。

同步機台時會保留原有機台順序與停用設定，不會因為某台設備暫時沒出現在 JUSTECH 清單裡就直接刪除。

## 💾 升級與本機資料

若從舊版升級、希望延續之前的設定及紀錄，可以在**關閉舊版程式與相關瀏覽器後**，視需要將下列資料複製到新版 EXE 同層：

| 本機項目 | 用途 |
| --- | --- |
| `device_names.json` | 原有機台清單；v1.3.0 亦可從 JUSTECH 重新同步 |
| `enabled_devices.json` | 機台啟用／停用設定 |
| `billing_periods.json` | 已儲存的各月份對帳期間 |
| `downloads/` | 已下載報表及續跑紀錄 |
| `browser_profile/` | 瀏覽器登入狀態；也可以在新版重新登入 |

這些是**使用者本機資料**，不包含在公開的 GitHub Release ZIP 中，也**不應提交到 GitHub**。其中登入狀態與銷售報表可能含敏感資訊，請妥善保管。

**續跑提醒：** 沒有搬移原本 `downloads/` 紀錄，新版就無法判斷之前哪些報表已完成。

## 🛠️ 開發與版本管理

| 位置 | 用途 |
| --- | --- |
| [`main`](https://github.com/Nila4339/vending-sales-downloader/tree/main) | 最新已驗收的正式程式碼（目前 v1.3.0） |
| [`develop`](https://github.com/Nila4339/vending-sales-downloader/tree/develop) | 新功能開發、測試與歷史版本 |
| [Releases](https://github.com/Nila4339/vending-sales-downloader/releases) | 正式版本說明與 Windows ZIP 附件 |

v1.3.0 正式版的主要程式模組：

- `app_desktop_v130.py`：圖形介面。
- `desktop_entry_v130.py`：桌面版 EXE 啟動入口。
- `device_sync.py`：從 JUSTECH 讀取機台清單。
- `batch_download.py`、`download_core.py`：批次下載與報表處理。
- `notifications.py`、`date_helpers.py`、`open_login_desktop.py`：通知、日期及登入功能。

開發者若需自行打包，請使用 `build_windows_v130.bat`，需要 Windows、Python、網路連線以及安裝相依套件。一般使用者只要下載 Release ZIP 即可。

## ⚠️ 使用限制

- 執行時請避免多人或多個程序同時在同一 JUSTECH 帳號環境匯出相同報表，以免通知對應錯誤。
- 報表歸屬的自動判斷仍需人工核對；工具無法保證外部網站資料與通知百分之百正確。
- 本程式不提供 JUSTECH 帳號、網站權限或銷售資料。

---

**目前狀態：v1.3.0 已經 Windows 實測並正式發布。** 登入、同步機台、批次下載、續跑、日期區間、機台管理與結果總表已通過使用者驗收。
