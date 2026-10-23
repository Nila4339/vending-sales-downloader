"""JUSTECH date picker UI test. No report export and no jQuery required.

Usage: python test_date_range.py --month 2026-10
Range: 2026-09-26 00:00:00 to 2026-10-26 00:00:00.
"""
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def desired_range(month):
    end = datetime.strptime(month, "%Y-%m").replace(day=26)
    start = (end.replace(day=1) - timedelta(days=1)).replace(day=26)
    return start, end

def month_header(value):
    match = re.search(r"([一二三四五六七八九十\d]+)月\s*(\d{4})", value)
    if not match:
        raise RuntimeError(f"無法辨識月份標題：{value!r}")
    chinese = {"一":1, "二":2, "三":3, "四":4, "五":5, "六":6,
               "七":7, "八":8, "九":9, "十":10, "十一":11, "十二":12}
    raw = match.group(1)
    return int(match.group(2)), int(raw) if raw.isdigit() else chinese[raw]

def set_visible_month(picker, target):
    """Navigate the left displayed calendar to the target month."""
    for _ in range(36):
        header = picker.locator(".drp-calendar.left .month").inner_text()
        year, mon = month_header(header)
        delta = (target.year - year) * 12 + target.month - mon
        if delta == 0:
            return
        arrow = ".drp-calendar.left .next" if delta > 0 else ".drp-calendar.left .prev"
        # Some implementations show only the right-side next button.
        if delta > 0 and picker.locator(arrow).count() == 0:
            arrow = ".drp-calendar.right .next"
        picker.locator(arrow).first.click(timeout=5000)
    raise RuntimeError("月曆換月超過限制，已停止")

def choose_day(picker, dt):
    set_visible_month(picker, dt)
    # .off are adjacent-month days (duplicates), skip them.
    cells = picker.locator(".drp-calendar.left td.available:not(.off)")
    candidates = cells.filter(has_text=re.compile(rf"^\s*{dt.day}\s*$"))
    if candidates.count() != 1:
        raise RuntimeError(f"{dt:%Y-%m-%d} 找到 {candidates.count()} 個日期格，已停止")
    candidates.first.click()

def set_clock(picker, side, hour, minute, second, ampm):
    root = picker.locator(f".drp-calendar.{side} .calendar-time")
    for selector, value in (
        (".hourselect", hour), (".minuteselect", minute),
        (".secondselect", second), (".ampmselect", ampm)
    ):
        ctl = root.locator(selector)
        if ctl.count() != 1:
            raise RuntimeError(f"{side} 時間選單 {selector} 不唯一或不存在")
        ctl.select_option(value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True, help="YYYY-MM，例如 2026-10")
    args = parser.parse_args()
    start, end = desired_range(args.month)
    expected = (start.strftime("%d/%m/%Y 12:00:00 AM") + " - " +
                end.strftime("%d/%m/%Y 12:00:00 AM"))
    print("預期區間：", expected)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"),
            headless=False, viewport={"width":1440, "height":900})
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請登入訂單頁，按 Enter 開始設定日期：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            field = page.get_by_role("textbox", name="建立時間")
            field.click()
            picker = page.locator(".daterangepicker:visible").first
            picker.wait_for(timeout=15000)
            choose_day(picker, start)
            # After picking start, the right calendar is normally next month.
            # Datepicker re-renders, so navigate to the end month and pick it.
            choose_day(picker, end)
            set_clock(picker, "left", "12", "0", "0", "AM")
            set_clock(picker, "right", "12", "0", "0", "AM")
            picker.get_by_role("button", name="套用").click()
            actual = field.input_value().strip()
            print("頁面日期欄位：", actual)
            if actual != expected:
                raise RuntimeError("日期核對失敗，預期："+expected+"；實際："+actual)
            print("日期核對成功（沒有匯出報表）。")
            input("請檢查頁面畫面後按 Enter 關閉：")
        finally:
            ctx.close()

if __name__ == "__main__":
    main()
