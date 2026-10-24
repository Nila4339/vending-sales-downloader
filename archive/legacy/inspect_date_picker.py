"""Read-only date picker inspection for JUSTECH (no export).

Select a test device first using test_select_device.py if needed.
This diagnostic saves only date field metadata, not customer/order records.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"), headless=False,
            viewport={"width": 1440, "height": 900}
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請登入並確認已進入訂單頁，按 Enter 進行日期欄位檢查：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            field = page.get_by_role("textbox", name="建立時間")
            field.wait_for(timeout=15000)
            print("建立時間欄位目前顯示：", repr(field.input_value()))
            field.click()
            page.locator(".daterangepicker").first.wait_for(state="visible", timeout=15000)
            info = page.locator(".daterangepicker").first.evaluate("""el => ({
                classes: el.className,
                ranges: [...el.querySelectorAll('.ranges li')].map(x=>x.innerText.trim()),
                inputs: [...el.querySelectorAll('input')].map(x=>({
                    className:x.className, type:x.type, value:x.value, readOnly:x.readOnly
                })),
                calendarTexts: [...el.querySelectorAll('.calendar-table .month')].map(x=>x.innerText.trim()),
                buttons: [...el.querySelectorAll('button')].map(x=>x.innerText.trim()).filter(Boolean)
            })""")
            print(json.dumps(info, ensure_ascii=False, indent=2))
            print("僅檢查日期選擇器，未修改日期、未匯出任何報表。")
            input("請確認畫面後按 Enter 關閉瀏覽器：")
        finally:
            context.close()

if __name__ == "__main__":
    main()
