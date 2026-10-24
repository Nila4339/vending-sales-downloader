"""Select exactly one known JUSTECH machine, without exporting any report.

Requires device_names.json from discover_devices.py; run locally only.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def main():
    path = ROOT / "device_names.json"
    if not path.exists():
        raise SystemExit("缺少 device_names.json；請先執行 discover_devices.py")
    names = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(names, list) or not names:
        raise SystemExit("設備清單格式錯誤或沒有資料")
    print("請選擇一台設備進行測試（不會匯出報表）：")
    for i, name in enumerate(names, 1):
        print(f"{i:>3}. {name}")
    value = input("設備序號：").strip()
    if not value.isdigit() or not (1 <= int(value) <= len(names)):
        raise SystemExit("無效序號")
    selected = names[int(value) - 1]

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請確認已登入訂單頁，然後按 Enter 繼續：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            page.locator(".choices__inner").first.click()
            dropdown = page.locator(".choices__list--dropdown").first
            dropdown.wait_for(state="visible", timeout=15000)
            search = dropdown.locator("input.choices__input")
            if search.count():
                search.first.fill(selected)
            option = dropdown.locator(".choices__item--choice").filter(has_text=selected)
            option.first.wait_for(state="visible", timeout=15000)
            candidates = option.all_text_contents()
            exact = [x.strip() for x in candidates if " ".join(x.split()) == selected]
            if len(exact) != 1:
                raise RuntimeError(f"找不到唯一完全相符的選項：{selected}；候選：{candidates[:5]}")
            option.filter(has_text=selected).first.click()
            print(f"已嘗試選取：{selected}")
            print("請目視核對訂單頁的設備欄位是否正確。此程式不匯出報表。")
            input("核對後按 Enter 關閉瀏覽器：")
        finally:
            context.close()

if __name__ == "__main__":
    main()
