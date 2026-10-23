"""Read-only diagnosis of the JUSTECH notification panel.

Run in the same Python environment as the downloader.
Does not create exports, click download links, or save private URLs.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
URL="https://lvmm.justech.com.tw/admin/19/orders"

with sync_playwright() as p:
    context=p.chromium.launch_persistent_context(
        user_data_dir=str(ROOT/"browser_profile"), headless=False,
        viewport={"width":1440,"height":900}, accept_downloads=True)
    try:
        page=context.pages[0] if context.pages else context.new_page()
        page.goto(URL,wait_until="domcontentloaded")
        input("請登入並確認訂單頁已開啟，按 Enter：")
        if "/login" in page.url:
            page.goto(URL,wait_until="domcontentloaded")
        print("請在瀏覽器【手動打開通知中心】，確認過去的通知已顯示，再回 PowerShell 按 Enter。")
        input("通知中心已開啟且內容已載入：")
        for n, pg in enumerate(context.pages,1):
            if pg.is_closed():
                continue
            links=pg.get_by_role("link",name="下載報表")
            all_links=pg.locator("a")
            print(f"視窗 {n}：通知下載連結 {links.count()} 筆、全部 a 連結 {all_links.count()} 筆")
            print("通知相關字詞出現次數：",pg.get_by_text("下載報表",exact=False).count())
            for i in range(min(links.count(),12)):
                print(f"  下載連結 {i+1}：", " ".join(links.nth(i).inner_text().split())[:80])
        print("若目視有通知但結果是 0，代表目前的定位方式有問題。")
        input("按 Enter 關閉：")
    finally:
        context.close()
