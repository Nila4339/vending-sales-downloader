"""Open JUSTECH login in the SAME persistent Playwright profile as downloads.

Close this browser after logging in, then start a batch; Chromium profiles
must not be opened by two concurrent processes.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def main():
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"),
            headless=False,
            viewport={"width": 1440, "height": 900},
            accept_downloads=True
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            page.bring_to_front()
            print("JUSTECH 登入瀏覽器已開啟。登入完成後，請直接關閉瀏覽器視窗，再回 GUI 按開始下載。", flush=True)
            # Do not close the context after a fixed delay: let user log in.
            while context.pages:
                page = context.pages[0]
                try:
                    page.wait_for_timeout(600)
                except Exception:
                    break
        finally:
            try:
                context.close()
            except Exception:
                pass
    print("登入視窗已關閉，現在可以開始下載。", flush=True)

if __name__ == "__main__":
    main()
