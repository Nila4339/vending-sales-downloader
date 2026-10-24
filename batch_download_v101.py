"""v0.7 sequential downloader: one Chromium process, one authenticated page."""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from download_core_v101 import ROOT, URL, filename_safe, run_one, LOG_FIELDS

def load_successes(log_file, month):
    if not log_file.exists():
        return set()
    with log_file.open(encoding="utf-8-sig", newline="") as f:
        return {(r["device_index"], r["device_name"]) for r in csv.DictReader(f)
                if r.get("month")==month and r.get("status")=="success"}

def record(log_file, item):
    fresh = not log_file.exists()
    with log_file.open("a", newline="", encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if fresh:
            writer.writeheader()
        writer.writerow(item)

def main():
    ap=argparse.ArgumentParser(description="JUSTECH v0.7 shared-browser downloader")
    ap.add_argument("--month", default=datetime.now().strftime("%Y-%m"))
    ap.add_argument("--indices", help="Comma separated 1-based device indices")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--retry-success", action="store_true")
    ap.add_argument("--auto-start", action="store_true")
    ap.add_argument("--stop-file")
    ap.add_argument("--adhoc", action="store_true", help="Temporary date range: never write or read monthly download logs")
    ap.add_argument("--start-date", help="Custom start YYYY-MM-DD (midnight)")
    ap.add_argument("--end-date", help="Custom end YYYY-MM-DD (midnight, exclusive)")
    args=ap.parse_args()
    if bool(args.start_date) != bool(args.end_date):
        ap.error("自訂日期必須同時提供起訖日")
    custom_start = custom_end = None
    if args.start_date:
        try:
            custom_start = datetime.strptime(args.start_date, "%Y-%m-%d")
            custom_end = datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            ap.error("自訂日期格式須為 YYYY-MM-DD")
        if custom_end <= custom_start:
            ap.error("結束日期必須晚於開始日期")
    if args.adhoc and not custom_start:
        ap.error("臨時匯出必須指定自訂日期區間")
    names=json.loads((ROOT/"device_names.json").read_text(encoding="utf-8"))
    if args.all and args.indices:
        ap.error("--all and --indices cannot be combined")
    if args.all:
        indices=list(range(1,len(names)+1))
    else:
        if not args.indices:
            for i,name in enumerate(names,1):
                print(f"{i:>3}. {name}")
            args.indices=input("輸入機台序號，例如 1,2,3：")
        try:
            indices=[int(x.strip()) for x in args.indices.split(",")]
        except ValueError:
            ap.error("機台序號格式錯誤")
    if not indices or len(indices)!=len(set(indices)) or any(i<1 or i>len(names) for i in indices):
        ap.error("無效或重複的機台序號")
    if not args.auto_start and input(f"將執行 {len(indices)} 台，輸入 START：").strip()!="START":
        raise SystemExit("已取消")
    output=(ROOT/"downloads"/"custom"/f"{custom_start:%Y%m%d}-{custom_end:%Y%m%d}") if args.adhoc else (ROOT/"downloads"/args.month)
    output.mkdir(parents=True,exist_ok=True)
    log_name = f"batch_log_period_{custom_start:%Y%m%d}-{custom_end:%Y%m%d}.csv" if custom_start else "batch_log_v063.csv"
    log=output/log_name
    successes=set() if args.adhoc else load_successes(log,args.month)
    completed=0
    with sync_playwright() as p:
        context=p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT/"browser_profile"),headless=False,
            viewport={"width":1440,"height":900},accept_downloads=True
        )
        try:
            page=context.pages[0] if context.pages else context.new_page()
            page.goto(URL,wait_until="domcontentloaded")
            if "/login" in page.url:
                raise RuntimeError("請先登入 JUSTECH；v0.7 不會自動填入帳密")
            page.get_by_role("textbox",name="建立時間").wait_for(timeout=15000)
            print("v0.7 已啟動單一瀏覽器工作階段。",flush=True)
            for pos,index in enumerate(indices,1):
                if args.stop_file and Path(args.stop_file).exists():
                    print("收到停止要求，在機台邊界安全停止。",flush=True)
                    break
                name=names[index-1]
                print(f"\n進度 {pos}/{len(indices)}：{name}",flush=True)
                if (str(index),name) in successes and not args.retry_success:
                    print("略過已成功機台",flush=True)
                    completed+=1
                    continue
                try:
                    target=run_one(page,context,args.month,index,names,custom_start,custom_end,output)
                    target=Path(target).resolve()
                    expected=filename_safe(args.month)+"_"+filename_safe(name)
                    if (target.parent!=output.resolve() or
                        not target.name.startswith(expected) or
                        target.suffix.lower() not in (".xlsx",".xls",".csv") or
                        not target.exists() or target.stat().st_size==0):
                        raise RuntimeError("下載檔案路徑或格式驗證失敗")
                    if not args.adhoc:
                        record(log,{"timestamp":datetime.now().isoformat(timespec="seconds"),
                                "month":args.month,"device_index":str(index),"device_name":name,
                                "status":"success","file":target.name,"error":""})
                    completed+=1
                    print(f"成功：{target.name}",flush=True)
                except Exception as exc:
                    if not args.adhoc:
                        record(log,{"timestamp":datetime.now().isoformat(timespec="seconds"),
                                "month":args.month,"device_index":str(index),"device_name":name,
                                "status":"failed","file":"","error":str(exc)[:400]})
                    print(f"第 {index} 台失敗：{exc}。已停止後續機台。",flush=True)
                    raise
            print(f"本次結束：本輪成功或略過 {completed}/{len(indices)} 台；" + ("臨時匯出不建立紀錄" if args.adhoc else f"紀錄：{log}"),flush=True)
        finally:
            context.close()

if __name__=="__main__":
    main()
