# vending-sales-downloader

JUSTECH 銷售平台「商品月銷售數量統計表」逐台下載器（B 方案）。

- 訂單查詢入口：https://lvmm.justech.com.tw/admin/19/orders
- Python + Playwright，Windows 本機執行
- 每台單獨匯出；預定檔名：`對帳年月_機台名稱_機台編號.xlsx`
- 開發中：**目前僅支援設定與 dry-run 預覽，不支援正式批次下載。** 網站定位與通知中心下載關聯尚需登入後實測。

## Windows 安裝與預覽

1. 在 GitHub 切到 `develop`，選 **Code → Download ZIP** 並解壓縮。
2. 在資料夾開啟 PowerShell，執行：
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m playwright install chromium
   Copy-Item config.example.json config.json
   ```
3. 編輯 `machines.csv`：填入**真實機台編號及名稱**，測試機台設 `enabled=1`，其他設 `0`。
4. 編輯 `config.json`：檢查 `billing_month`、`start_datetime`、`end_datetime` 是否符合對帳期間。
5. 預覽檔名：
   ```powershell
   .\.venv\Scripts\python.exe downloader.py --dry-run
   ```

**請勿直接執行未加 `--dry-run` 的正式下載測試。** 目前網站的選擇器尚未驗證，程式會在安全檢查停止。

## 取得網站元素資訊（下一階段）

網站需要登入，無法只靠網址得知訂單頁內各按鈕和選單的 DOM。請在本機登入後，以 Playwright Inspector／瀏覽器開發者工具辨識：機台下拉、建立時間的起訖輸入、匯出報表、報表種類、通知中心與新任務下載連結。需先驗證「通知中心的檔案確實屬於當次機台與日期」，再開啟真正下載動作。

**安全**：不要上傳帳密、cookie、登入後 HTML 中的個資／訂單資訊、HAR、原始 Excel、`config.json` 或 `browser_profile/`；提供截圖時遮蔽敏感資訊。公開頁面網址可以分享。

## 狀態

- [x] GitHub `develop` 分支與文件
- [x] 訂單頁網址、CSV 機台清單、檔名預覽
- [ ] DOM 定位與日期選擇器
- [ ] 匯出後通知中心新任務比對
- [ ] Excel 下載、驗證與改名
- [ ] 單台實測、批次失敗續跑

正式 GAS 專案 `vending-report-system` 與本儲存庫的 `main` 不會因本階段修改。
