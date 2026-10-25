# JUSTECH 銷售報表下載器｜PROJECT MEMORY（交接文件）

**狀態：v1.3.0 已完成 Windows 使用者驗收、正式發布；目前暫停新功能開發。**
最後整理：2026-10-25。

## 1. 專案定位
- GitHub：`Nila4339/vending-sales-downloader`
- 用途：Windows 圖形化工具，協助 JUSTECH 販賣機營運人員逐台批次匯出銷售報表，將重複操作自動化，供後續對帳、結算使用。
- 技術：Python、Playwright、Tkinter、PyInstaller、GitHub Actions（Windows 自動打包）。
- **正式版：v1.3.0**：`release/v1.3.0` 分支，GitHub Release `https://github.com/Nila4339/vending-sales-downloader/releases/tag/v1.3.0`。
- v1.2.0 亦已正式發布，可作備援：`release/v1.2.0`。
- **開發分支：`develop`**，保留歷史實驗、回退與原始開發紀錄。**未經使用者明確同意，不修改 `main`、正式 GAS 或已發布穩定版本。**

## 2. 已實測完成的功能（截至 v1.3.0）
- 開啟 GUI，透過 JUSTECH 登入按鈕開啟瀏覽器，登入後返回主程式。
- 共用瀏覽器逐台批次匯出、以機台名稱命名報表，選擇全部或指定機台。
- 月結預設區間為上月 26 日 00:00 至本月 26 日 00:00（結束日不含），可儲存不同月份的自訂期間。
- 臨時指定日期區間獨立匯出，不列入月結下載紀錄與續跑。
- 下載中停止、重新執行略過已成功下載者，必要時選擇重新下載。
- 搜尋機台、啟用／停用機台、每月下載狀態顯示、匯出結果總表 CSV。
- **v1.3.0 新增「從 JUSTECH 同步機台」**：登入後擷取設備清單，可在沒有 `device_names.json` 時建立；有舊清單時顯示差異並確認新增。既有機台順序與停用設定保留，未擷取到的舊機台不自動刪除。
- **Windows EXE 的登入、下載、續跑、臨時匯出、機台管理、結果總表，以及 v1.3.0 同步清單數量／名稱與同步後下載，均經使用者確認成功。**
- PyInstaller `--onedir --windowed`，正式使用者可下載 GitHub Release 的 ZIP，解壓縮後直接啟動 EXE，無需 Python。

## 3. 重要原始碼（v1.3.0）
- `app_desktop_v130.py` — GUI、機台同步確認及下載管理。
- `desktop_entry_v130.py` — EXE 模式入口（GUI / --login / --batch / --sync-devices）。
- `device_sync.py` — JUSTECH 機台清單讀取，輸出暫存預覽。
- `batch_download.py` — 批次流程、續跑和結果記錄。
- `download_core.py` — 網頁操作、匯出與檔案檢核。
- `notifications.py` — 通知處理。
- `date_helpers.py` — 日期區間。
- `open_login_desktop.py` — 開啟登入瀏覽器。
- `build_windows_v130.bat` — 本機 Windows 打包。
- `.github/workflows/release-v1.3.0.yml` 在正式 release 分支 — GitHub Actions 打包發布 ZIP。

## 4. 使用者本機檔案：絕不可公開
- `device_names.json` 機台名稱及其索引排序。v1.3.0 可同步建立。
- `enabled_devices.json` 啟用／停用設定。
- `billing_periods.json` 對帳期間。
- `browser_profile/` 登入工作階段。
- `downloads/YYYY-MM/` 正式月結結果及 CSV 續跑紀錄；`downloads/custom/` 臨時匯出。
- `login_diagnostic.log`、`desktop_error.log` 可能包含敏感錯誤資訊；分享前檢查。
- **升級搬移 EXE 時，若要保留原先續跑、停用設定、日期設定，應複製相應 JSON 與 `downloads/`；登入工作階段可在關閉瀏覽器後搬移或直接重新登入。**
- 設備清單索引可能影響歷史 CSV；同步功能不得重新排列既有機台。
- 通知中心時間戳比對不代表百分之百可證明匯出檔歸屬，不要多人同時競爭匯出。

## 5. 正式發布與分享
- v1.3.0 Windows ZIP：`JUSTECH-Downloader-v1.3.0-Windows.zip`（Release assets）。ZIP 須含 EXE 與 `_internal/`，不能只取出 EXE。
- 正式 Release 說明已改為新使用者可理解的軟體介紹。
- GitHub Actions 官方 action 升級至 `actions/checkout@v6`、`actions/setup-python@v6`。
- 討論過限制下載的分享方案：使用者考慮**私人發布儲存庫／GitHub Organization Read 權限**，但此私人儲存庫**尚未證實已建立**。不要誤認它已完成；需使用者在 GitHub 建立組織／儲存庫並授權後才能配置。
- 現有公開 GitHub Release 若繼續公開，建立私人發布儲存庫也不會讓舊版自動隱藏。

## 6. 後續繼續開發原則
1. 在新 ChatGPT 對話請先讀 `PROJECT_MEMORY.md`、`README.md`、`CHANGELOG.md`，再檢查 GitHub `develop` 與最新 release 的實際檔案。
2. 先詢問或確認新需求範圍；不主動重構已驗收的下載核心。新功能從 `develop` 或獨立 feature 分支開始。
3. 遵守版本規範：新增功能可規劃 v1.4.0，修復小問題可用 v1.3.1；以使用者確認為準。
4. 建立測試 EXE、由使用者在 Windows 實測後，再建立乾淨的獨立 `release/vX.Y.Z` 分支與 GitHub Release。
5. 不能破壞原本的 v1.3.0 ZIP，不能將憑證、機台名單、銷售報表上傳 GitHub。

## 7. 新對話可直接貼上的啟動提示
請接續開發 GitHub 專案 `Nila4339/vending-sales-downloader`（JUSTECH 銷售報表下載器）。穩定正式版為 v1.3.0，已完成 Windows EXE 驗收；開發分支是 `develop`，已發布分支 `release/v1.3.0`。請先讀取 GitHub 的 `PROJECT_MEMORY.md`、`README.md`、`CHANGELOG.md` 和最新發布版本的程式，列出目前架構及你理解的狀態，再依我提供的新需求規劃。未經同意不要修改 `main`、正式 GAS 或覆蓋已驗收的 v1.3.0。
