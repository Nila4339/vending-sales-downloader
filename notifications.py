"""JUSTECH notification matching, cleanup and filename helpers."""
import re
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def filename_safe(s):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", s).strip(" .") or "未命名"

def scan_notification_cards(page, report_pattern, submitted_at):
    """One browser roundtrip for all notification cards; no download URLs returned."""
    records = page.get_by_role("link", name="下載報表").evaluate_all("""links => links.slice(0,30).map((a, index) => {
        const text=(a.parentElement?.parentElement?.innerText||'').replace(/\\s+/g,' ').trim();
        return {index,text};
    })""")
    matching = []
    newest = None
    for record in records:
        match = report_pattern.search(record["text"])
        if not match:
            continue
        stamp = datetime.strptime(match.group(1)+match.group(2), "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo("Asia/Taipei"))
        newest = max(newest, stamp) if newest else stamp
        if (submitted_at - timedelta(seconds=2) <= stamp <=
                datetime.now(ZoneInfo("Asia/Taipei")) + timedelta(seconds=3)
                and "匯出成功" in record["text"]):
            matching.append((record["index"], match.group(0), stamp))
    return len(records), matching, newest


def diagnose_notification_cards(page, report_pattern, submitted_at):
    """Explain the first available card; do not expose download URLs."""
    rows = page.get_by_role("link", name="下載報表").evaluate_all("""links => links.slice(0, 3).map(a =>
      (a.parentElement?.parentElement?.innerText||'').replace(/\\s+/g, ' ').trim()
    )""")
    lower = submitted_at - timedelta(seconds=2)
    upper = datetime.now(ZoneInfo("Asia/Taipei")) + timedelta(seconds=3)
    print(f"  時間範圍：{lower:%H:%M:%S} 至 {upper:%H:%M:%S}")
    if not rows:
        print("  通知面板尚無可讀取的下載連結")
        return
    for i, row in enumerate(rows, 1):
        match = report_pattern.search(row)
        if not match:
            print(f"  通知 {i}：報表名稱格式未符合預期；內容摘要：{row[:120]}")
            continue
        stamp = datetime.strptime(match.group(1)+match.group(2), "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo("Asia/Taipei"))
        problems = []
        if not lower <= stamp <= upper:
            problems.append("時間不在範圍內")
        if "匯出成功" not in row:
            problems.append("沒有匯出成功標記")
        print(f"  通知 {i}：{match.group(0)}；原因：{', '.join(problems) if problems else '符合條件'}")


def reopen_notifications(page):
    """Reload orders page and reopen notifications, avoiding the covered toggle.

    The Filament notification overlay can intercept all clicks, even after Escape.
    Navigation clears it; the next notification open is a fresh UI request.
    """
    page.goto(URL, wait_until="domcontentloaded", timeout=30000)
    if "/login" in page.url:
        raise RuntimeError("登入狀態已失效，停止通知檢查")
    toggle = page.get_by_role("button", name="Open notifications")
    toggle.click(timeout=12000)
    page.wait_for_timeout(1800)



def clear_downloaded_notification(page, report_filename):
    """After verified download, dismiss only the matching card via its X.

    Filament cards use an icon-only close action. Match the exact report filename
    within the same card containing the download link, and never click global
    '清除' or other cards' controls.
    """
    links = page.get_by_role("link", name="下載報表")
    print(f"通知清理：重新開啟後可見 {links.count()} 筆下載通知，尋找 {report_filename}")
    matched = []
    for i in range(links.count()):
        card = links.nth(i).locator("xpath=../..")
        text = " ".join(card.inner_text().split())
        found = re.search(r"商品月銷售數量統計表_\d{8}_\d{6}\.xlsx", text)
        if found and found.group(0) == report_filename:
            matched.append(card)
    if len(matched) != 1:
        print(f"通知清除略過：對應卡片數 {len(matched)}，無法唯一定位。")
        return False
    card = matched[0]
    # Confirmed by read-only DOM inspection (2026-10-23):
    # download link -> parent^3: a single notification row with one icon-only
    # BUTTON containing an SVG. parent^6 contains multiple notifications.
    # Never use the global list "清除" control.
    single_row = card.locator("xpath=..")
    # 'card' is parent^2, so this row is parent^3.
    if single_row.get_by_role("link", name="下載報表").count() != 1:
        print("通知清除略過：單筆卡片含有非唯一下載連結。")
        return False
    row_text = " ".join(single_row.inner_text().split())
    match = re.search(r"商品月銷售數量統計表_\d{8}_\d{6}\.xlsx", row_text)
    if not match or match.group(0) != report_filename:
        print("通知清除略過：單筆卡片的報表名稱不符。")
        return False
    buttons = single_row.locator("button")
    if buttons.count() != 1:
        print(f"通知清除略過：單筆卡片有 {buttons.count()} 個按鈕，不符合實測結構。")
        return False
    close_button = buttons.first
    if close_button.locator("svg").count() != 1:
        print("通知清除略過：找不到預期的單個 SVG 關閉圖示。")
        return False
    print("通知清理：已找到本次報表卡片中的唯一 X，準備清除。")
    close_button.click(timeout=8000)
    page.wait_for_timeout(600)
    remaining = 0
    for i in range(page.get_by_role("link", name="下載報表").count()):
        text = " ".join(page.get_by_role("link", name="下載報表").nth(i).locator("xpath=../..").inner_text().split())
        found = re.search(r"商品月銷售數量統計表_\d{8}_\d{6}\.xlsx", text)
        if found and found.group(0) == report_filename:
            remaining += 1
    if remaining:
        print("已點擊單筆 X，但通知仍存在，請人工確認；不重複點擊。")
        return False
    print("已清除本次下載通知：", report_filename)
    return True

