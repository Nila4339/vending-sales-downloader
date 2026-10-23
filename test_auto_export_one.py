"""Single-machine automated export test. Requires manual confirmation before export.

Safety: only download a notification link newly added during this export. Stop
if there is no unambiguous new link. Confirm report type in export dialog.
"""
import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from test_date_range import desired_range, choose_day, set_clock

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def filename_safe(s):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", s).strip(" .") or "未命名"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default="2026-10", help="對帳年月 YYYY-MM")
    args = parser.parse_args()
    names_path = ROOT / "device_names.json"
    if not names_path.exists():
        raise SystemExit("缺少 device_names.json，請先執行 discover_devices.py")
    names = json.loads(names_path.read_text(encoding="utf-8"))
    for idx, name in enumerate(names, 1):
        print(f"{idx:>3}. {name}")
    choice = input("請輸入要測試的設備序號：").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        raise SystemExit("設備序號不正確")
    name = names[int(choice)-1]
    start, end = desired_range(args.month)
    expected = start.strftime("%d/%m/%Y 12:00:00 AM") + " - " + end.strftime("%d/%m/%Y 12:00:00 AM")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"), headless=False,
            viewport={"width":1440,"height":900}, accept_downloads=True)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請登入 JUSTECH、確認訂單頁已開啟，再按 Enter：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            # Notification baseline was unreliable (zero even with historical messages).
            # Do not inspect old notifications here; keep the orders page untouched.
            print("通知中心將在匯出後檢查最新一筆；不再以舊連結數量為依據。")
            page.locator(".choices__inner").first.click()
            dropdown = page.locator(".choices__list--dropdown").first
            dropdown.wait_for(state="visible")
            search = dropdown.locator("input.choices__input")
            if search.count():
                search.first.fill(name)
            options = dropdown.locator(".choices__item--choice")
            matches = [i for i in range(options.count()) if " ".join(options.nth(i).inner_text().split()) == name]
            if len(matches) != 1:
                raise RuntimeError(f"設備選項無法唯一匹配 {name}：{len(matches)} 筆")
            options.nth(matches[0]).click()
            field = page.get_by_role("textbox",name="建立時間")
            field.click()
            picker = page.locator(".daterangepicker:visible").first
            choose_day(picker,start)
            choose_day(picker,end)
            set_clock(picker,"left","12","0","0","AM")
            set_clock(picker,"right","12","0","0","AM")
            picker.get_by_role("button",name="套用").click()
            actual = field.input_value().strip()
            if actual != expected:
                raise RuntimeError(f"日期不符：預期 {expected}，實際 {actual}")
            print("已選取設備：", name)
            print("已套用日期：", actual)
            answer = input("請確認機台與日期正確；輸入 YES 讓程式匯出這一台，其他輸入取消：").strip()
            if answer != "YES":
                print("已取消，沒有匯出")
                return

            page.get_by_role("button", name="匯出報表").click()
            # The recorded steps did not include choosing the export report type.
            # Do not silently assume a default selection.
            # Wait for the export dialog to render. Previous '.fi-modal-window:visible'
            # matched zero when the modal's actual visible container differed.
            page.get_by_text("確定要進行嗎？").wait_for(state="visible", timeout=15000)
            modal = page.locator(".fi-modal-window").filter(
                has=page.get_by_text("確定要進行嗎？")
            ).first
            if modal.count() != 1:
                raise RuntimeError("無法唯一辨識匯出確認視窗，停止")
            selectors = modal.locator(".fi-modal-content .choices__inner")
            try:
                selectors.first.wait_for(state="visible", timeout=10000)
            except Exception:
                print("診斷：匯出視窗數：", page.locator(".fi-modal-window").count())
                print("診斷：整頁 Choices 數：", page.locator(".choices__inner").count())
                print("診斷：此視窗 Choices 數：", selectors.count())
                raise RuntimeError("匯出視窗找不到可見的報表選單；請提供診斷數字與視窗截圖")
            if selectors.count() != 1:
                raise RuntimeError(f"匯出視窗有 {selectors.count()} 個報表選單，無法唯一定位")
            selectors.click()
            menu = modal.locator(".choices__list--dropdown").filter(
                has=page.locator(".choices__item--choice")
            ).first
            menu.wait_for(state="visible", timeout=10000)
            entries = menu.locator(".choices__item--choice")
            options = [" ".join(item.inner_text().split()) for item in entries.all()]
            print("匯出視窗的報表類型選項：", options)
            desired = "商品月銷售數量統計表"
            matches = [i for i, label in enumerate(options) if label == desired]
            if len(matches) != 1:
                print("無法唯一找到指定報表，已停止。請提供上方選項。")
                return
            entries.nth(matches[0]).click()
            print("已自動選取報表類型：", desired)
            # Choices.js sometimes leaves the dropdown overlay visible. Close it
            # by clicking the modal heading rather than forcing the submit button.
            if menu.is_visible():
                modal.get_by_text("確定要進行嗎？").click()
            try:
                menu.wait_for(state="hidden", timeout=5000)
            except Exception as exc:
                raise RuntimeError("報表選單未收合，為避免誤操作，停止送出") from exc
            chosen = " ".join(selectors.first.inner_text().split())
            if desired not in chosen:
                raise RuntimeError(f"報表選擇結果不符：{chosen!r}，停止送出")
            print("已確認選單收合，且選定報表正確。")
            if input("目視確認選項正確後輸入 YES 提交（其他輸入取消）：").strip() != "YES":
                print("已取消提交")
                return
            modal.get_by_role("button", name="確定").click(timeout=10000)
            print("已提交單台匯出，等候通知中心的新下載連結（最長 3 分鐘）...")
            page.get_by_role("button", name="Open notifications").click()
            # User observed that new exports appear first in the notification list.
            # This is a single-machine supervised test, NOT proof of job ownership.
            import time
            deadline = time.monotonic() + 180
            top_link = page.get_by_role("link", name="下載報表").first
            while time.monotonic() < deadline:
                if top_link.count() and top_link.is_visible():
                    break
                page.wait_for_timeout(1500)
            else:
                raise RuntimeError("等候逾時：通知中心沒有出現可見的下載報表連結")
            parent = top_link.locator("xpath=..")
            notice_text = " ".join(parent.inner_text().split())
            print("最上方可下載通知附近內容：", notice_text[:300])
            print("請確認該項確為本次剛產生的『商品月銷售數量統計表』，")
            print("並留意有無其他人同時匯出；不確定時請取消。")
            if input("確認最上方下載連結屬於本次匯出，輸入 YES：").strip() != "YES":
                print("已取消，沒有下載可能錯配的報表。")
                return
            selected_link = top_link
            print("已確認本次下載通知，準備擷取下載事件...")
            # Recorder shows a popup and a download; popup is optional in runtime.
            pages_before_download = set(context.pages)
            with page.expect_download(timeout=60000) as download_info:
                selected_link.click()
            download = download_info.value
            # JUSTECH sometimes returns a UUID filename without any extension.
            # Inspect actual bytes before deciding the extension.
            import tempfile
            import zipfile
            import csv
            with tempfile.TemporaryDirectory() as tmpdir:
                temp = Path(tmpdir) / "downloaded_report"
                download.save_as(temp)
                if temp.stat().st_size == 0:
                    raise RuntimeError("下載內容為空")
                with temp.open("rb") as file_handle:
                    header = file_handle.read(8)
                if zipfile.is_zipfile(temp):
                    from openpyxl import load_workbook
                    try:
                        with temp.open("rb") as file_handle:
                            book = load_workbook(file_handle, read_only=True)
                            try:
                                if not book.sheetnames:
                                    raise ValueError("Excel 沒有工作表")
                            finally:
                                book.close()
                    except Exception as exc:
                        raise RuntimeError("下載檔是 ZIP，但無法辨識成 Excel xlsx") from exc
                    extension = ".xlsx"
                elif header.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
                    extension = ".xls"
                else:
                    try:
                        sample = temp.read_bytes()[:4096].decode("utf-8-sig")
                        if not sample.strip() or sample.lstrip().lower().startswith(("<html", "<!doctype")):
                            raise ValueError("不是 CSV 內容")
                        rows = list(csv.reader(sample.splitlines()))
                        if len(rows) == 0 or max(map(len, rows)) < 2:
                            raise ValueError("未辨識出 CSV 欄位")
                        extension = ".csv"
                    except Exception as exc:
                        raise RuntimeError(
                            f"檔案格式無法辨識（原始檔名 {download.suggested_filename}），"
                            "先保留人工檢查，不套用 Excel 副檔名"
                        ) from exc
                target_dir = ROOT / "downloads" / args.month
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f"{filename_safe(args.month)}_{filename_safe(name)}{extension}"
                if target.exists():
                    stem = target.stem
                    suffix = target.suffix
                    counter = 2
                    while (target_dir / f"{stem}_第{counter}次{suffix}").exists():
                        counter += 1
                    target = target_dir / f"{stem}_第{counter}次{suffix}"
                    print("原檔案已存在，為避免覆蓋，改存為：", target.name)
                target.write_bytes(temp.read_bytes())
            print("下載完成：",target)
            # JUSTECH may open a new browser tab when the download link is clicked.
            # Close only tabs created during this download, preserving the original orders tab.
            for extra_page in list(context.pages):
                if extra_page is not page and extra_page not in pages_before_download:
                    try:
                        extra_page.close()
                    except Exception as exc:
                        print("關閉下載分頁時出現提醒：", exc)
            if page.is_closed():
                raise RuntimeError("原訂單分頁已關閉，無法安全繼續")
            # Return to the known clean orders route. This avoids leftover notification
            # panels and stale machine/date filters when transitioning between machines.
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            if "/login" in page.url:
                raise RuntimeError("登入狀態已失效；請重新登入後再執行")
            page.get_by_role("textbox", name="建立時間").wait_for(timeout=15000)
            page.bring_to_front()
            print("已關閉額外下載分頁，返回原訂單頁。")
            print("注意：目前仍是單台測試；多台批次需逐台重新設定機台與日期，並核對新通知。")
        finally:
            context.close()

if __name__ == "__main__":
    main()
