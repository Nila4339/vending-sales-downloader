"""Read-only device discovery probe for JUSTECH orders page.

No exporting, downloading, or credentials stored. UI selectors must be tested
locally; the Choices.js menu may require adjustment for virtualized results.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="device_names.json")
    args = parser.parse_args()
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請在開啟的瀏覽器中登入 JUSTECH，確認已到訂單頁，再按 Enter：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            # Choices.js is used by the site's equipment dropdown.
            dropdown = page.locator(".choices__inner").first
            dropdown.click()
            page.locator(".choices__list--dropdown").first.wait_for(state="visible", timeout=15000)
            names = set()
            menu = page.locator(".choices__list--dropdown").first
            for _ in range(150):
                items = menu.locator(".choices__item--choice")
                for item in items.all():
                    if item.get_attribute("data-choice-selectable") is None and item.get_attribute("data-choice") is None:
                        continue
                    name = item.inner_text().strip()
                    if name and name not in ("全部", "選擇", "沒有結果", "No results found"):
                        names.add(" ".join(name.split()))
                # Scroll dropdown rather than page to load additional choices.
                menu.evaluate("(el) => {const list=el.querySelector('.choices__list'); (list || el).scrollTop=(list || el).scrollHeight;}")
                page.wait_for_timeout(400)
                # Break only when several attempts add no new items.
                if _ == 0:
                    stagnant = 0
                last_count = locals().get("last_count", -1)
                stagnant = stagnant + 1 if len(names) == last_count else 0
                last_count = len(names)
                if stagnant >= 5:
                    break
            result = sorted(names)
            out = ROOT / args.output
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"找到 {len(result)} 個候選設備名稱，輸出至：{out.name}")
            for name in result[:15]:
                print(" -", name)
            print("請核對數量及名稱；這是待驗證的 DOM 擷取結果，不代表已涵蓋全部設備。")
        finally:
            context.close()

if __name__ == "__main__":
    main()
