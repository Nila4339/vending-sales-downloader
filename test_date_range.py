"""Set and verify a JUSTECH date range without exporting reports.

Usage: python test_date_range.py --month 2026-10
Invoice month YYYY-MM maps to prior-month 26 00:00:00 through current-month
25 23:59:59 (local wall-clock time).
"""
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
URL = "https://lvmm.justech.com.tw/admin/19/orders"

def billing_window(month):
    dt = datetime.strptime(month, "%Y-%m")
    start = (dt - timedelta(days=1)).replace(day=26, hour=0, minute=0, second=0)
    end = dt.replace(day=25, hour=23, minute=59, second=59)
    return start.strftime("%d/%m/%Y %I:%M:%S %p"), end.strftime("%d/%m/%Y %I:%M:%S %p")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True, help="對帳年月 YYYY-MM，例如 2026-10")
    args = parser.parse_args()
    start, end = billing_window(args.month)
    print(f"預期區間：{start} - {end}")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / "browser_profile"), headless=False,
            viewport={"width":1440,"height":900}
        )
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            input("請確認已登入訂單頁，按 Enter 設定日期：")
            if "/login" in page.url:
                page.goto(URL, wait_until="domcontentloaded")
            field = page.get_by_role("textbox", name="建立時間")
            field.wait_for(timeout=15000)
            field.click()
            result = field.evaluate("""(el, values) => {
                const jq = window.jQuery;
                if (!jq) throw Error('未找到 jQuery，需採另一種 UI 操作方案');
                const picker = jq(el).data('daterangepicker');
                if (!picker) throw Error('欄位沒有綁定 daterangepicker 物件');
                const moment = window.moment;
                if (!moment) throw Error('未找到 moment 函式');
                const a = moment(values.start, 'DD/MM/YYYY hh:mm:ss A', true);
                const b = moment(values.end, 'DD/MM/YYYY hh:mm:ss A', true);
                if (!a.isValid() || !b.isValid()) throw Error('日期解析失敗');
                picker.setStartDate(a);
                picker.setEndDate(b);
                picker.clickApply();
                return {start:picker.startDate.format('DD/MM/YYYY hh:mm:ss A'),
                        end:picker.endDate.format('DD/MM/YYYY hh:mm:ss A')};
            }""", {"start": start, "end": end})
            actual = field.input_value()
            print("選擇器內容：", result)
            print("頁面日期欄位：", actual)
            if result["start"] != start or result["end"] != end or start not in actual or end not in actual:
                raise RuntimeError("日期核對失敗，請勿進行報表匯出")
            print("日期核對成功。未觸發報表匯出。")
            input("請目視確認頁面，再按 Enter 關閉：")
        finally:
            ctx.close()

if __name__ == "__main__":
    main()
