"""Discover JUSTECH device names without changing the user's saved list.

The GUI reviews the proposed additions before appending them. Keeping existing
indices unchanged protects historical CSV records and the resume mechanism.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def discover():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"), headless=False,
            viewport={"width": 1440, "height": 900})
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            if "/login" in page.url:
                raise RuntimeError("尚未登入 JUSTECH，請先使用 GUI 登入按鈕。")
            page.get_by_role("textbox", name="建立時間").wait_for(timeout=15000)
            page.locator(".choices__inner").first.click()
            menu = page.locator(".choices__list--dropdown").first
            menu.wait_for(state="visible", timeout=15000)
            names = set()
            stagnant = 0
            for _ in range(150):
                items = menu.locator(".choices__item--choice")
                for item in items.all():
                    if item.get_attribute("data-choice-selectable") is None and item.get_attribute("data-choice") is None:
                        continue
                    name = " ".join(item.inner_text().split())
                    if name and name not in ("全部", "選擇", "沒有結果", "No results found"):
                        names.add(name)
                before = len(names)
                menu.evaluate("""el => { const box=el.querySelector('.choices__list') || el; box.scrollTop=box.scrollHeight; }""")
                page.wait_for_timeout(400)
                # Do not assume a full list if the component virtualizes options.
                current = len(names)
                stagnant = stagnant + 1 if current == before else 0
                if stagnant >= 5:
                    break
            if not names:
                raise RuntimeError("找不到任何機台，未更動本機清單。")
            return sorted(names)
        finally:
            context.close()

def main():
    found = discover()
    output = ROOT / ".device_sync_preview.json"
    temp = output.with_suffix(".tmp")
    temp.write_text(json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(output)
    print(f"本次讀取 {len(found)} 個機台名稱，待 GUI 確認。", flush=True)

if __name__ == "__main__":
    main()
