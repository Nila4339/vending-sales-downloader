"""Read-only diagnosis of per-card notification X controls (v0.6).

Never clicks dismiss controls or downloads. Prints DOM structure without
hrefs, tokens, wire snapshots, cookies or session data.
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
URL="https://lvmm.justech.com.tw/admin/19/orders"
PATTERN=re.compile(r"商品月銷售數量統計表_\d{8}_\d{6}\.xlsx")

def main():
    with sync_playwright() as p:
        context=p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT/"browser_profile"),headless=False,
            viewport={"width":1440,"height":900},accept_downloads=True)
        try:
            page=context.pages[0] if context.pages else context.new_page()
            page.goto(URL,wait_until="domcontentloaded")
            input("確認已登入 JUSTECH 訂單頁，按 Enter：")
            if "/login" in page.url:
                page.goto(URL,wait_until="domcontentloaded")
            page.get_by_role("button",name="Open notifications").click()
            page.wait_for_timeout(1200)
            links=page.get_by_role("link",name="下載報表")
            print("下載通知筆數：",links.count())
            for i in range(min(links.count(),3)):
                link=links.nth(i)
                print(f"\n===== 通知 {i+1} =====")
                for depth in range(2,7):
                    node=link.locator("xpath=" + "/".join([".."]*depth))
                    details=node.evaluate("""el=>{
                        const txt=(el.innerText||'').replace(/\\s+/g,' ').trim();
                        const controls=[...el.querySelectorAll('button,[role="button"]')].map(c=>({
                            tag:c.tagName,
                            text:(c.innerText||'').trim().slice(0,40),
                            aria:c.getAttribute('aria-label')||'',
                            title:c.getAttribute('title')||'',
                            type:c.getAttribute('type')||'',
                            classes:typeof c.className==='string'?c.className.slice(0,160):'',
                            hasXIcon:!!c.querySelector('svg[class*="x-mark"],svg[data-icon*="xmark"],.fi-icon-btn-icon'),
                            svgCount:c.querySelectorAll('svg').length
                        }));
                        return {tag:el.tagName,classes:typeof el.className==='string'?el.className.slice(0,120):'', downloadLinks:[...el.querySelectorAll('a')].filter(a=>(a.innerText||'').includes('下載報表')).length,controls};
                    }""")
                    print(f"向上 {depth} 層：{details}")
                    if details["downloadLinks"]>1:
                        print("已到多張卡片共同容器，停止向上檢查。")
                        break
            print("\n只讀取控制項結構，沒有點擊 X 或清除任何通知。")
            input("請複製以上輸出（如有個人資訊請先隱藏），按 Enter 關閉：")
        finally:
            context.close()

if __name__=="__main__":
    main()
