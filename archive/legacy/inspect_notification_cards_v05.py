"""v0.5 read-only JUSTECH notification card inspector.

Prints report names and timestamps (not URLs or download tokens). Does not
export reports, click download links, or change notification read status.
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
URL="https://lvmm.justech.com.tw/admin/19/orders"
REPORT_RE=re.compile(r"商品月銷售數量統計表_(\d{8})_(\d{6})\.xlsx")

def main():
    with sync_playwright() as p:
        context=p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT/"browser_profile"),
            headless=False,viewport={"width":1440,"height":900},accept_downloads=True
        )
        try:
            page=context.pages[0] if context.pages else context.new_page()
            page.goto(URL,wait_until="domcontentloaded")
            input("請確認已登入訂單頁，按 Enter：")
            if "/login" in page.url:
                page.goto(URL,wait_until="domcontentloaded")
            page.get_by_role("button",name="Open notifications").click()
            print("通知中心已開啟。")
            input("請目視確認通知已載入，按 Enter 讀取通知卡片：")
            links=page.get_by_role("link",name="下載報表")
            print(f"目前可見的『下載報表』連結：{links.count()} 筆")
            if links.count()==0:
                print("定位不到下載連結，請檢查通知是否在同一個分頁，並提供畫面截圖。")
                return
            for i in range(min(links.count(),20)):
                link=links.nth(i)
                # Walk upwards to find the *nearest* ancestor containing an
                # actual timestamped report filename. The immediate parent
                # contains only the link caption in this site's layout.
                result=link.evaluate("""el => {
                  let node=el;
                  let levels=[];
                  const pattern=/商品月銷售數量統計表_\\d{8}_\\d{6}\\.xlsx/;
                  for(let depth=0;node && depth<=8;depth++,node=node.parentElement){
                    const text=(node.innerText||'').replace(/\\s+/g,' ').trim();
                    levels.push({depth,tag:node.tagName,classes:typeof node.className==='string' ? node.className.slice(0,140) : '',hasFilename:pattern.test(text),textLength:text.length});
                    if(pattern.test(text))return {found:true,depth,text:text.slice(0,400),levels};
                  }
                  return {found:false,levels};
                }""")
                match=REPORT_RE.search(result.get("text",""))
                print(f"通知 {i+1}: timestamp={match.group(1)+'_'+match.group(2) if match else '找不到'}; 層級={result.get('depth','?')}")
                print("  文字：",result.get("text","")[:250] if match else "尚未找到包含報表檔名的卡片")
                if not match:
                    print("  層級診斷（不包含網址）：",result["levels"])
            print("只做讀取；沒有匯出或下載任何報表。")
            input("按 Enter 關閉：")
        finally:
            context.close()

if __name__=="__main__":
    main()
