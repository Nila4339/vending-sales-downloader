"""v0.6.1 three-machine no-YES batch test (requires an active login).

Each export performs automatic timestamp-based notification checks. Stops if
ambiguous or on any failure; progress is logged for reruns. Avoid concurrent
exports by other users: report timestamps alone do not prove device ownership.
"""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from test_auto_export_v061 import filename_safe

ROOT = Path(__file__).resolve().parent
FIELDS = ["timestamp", "month", "device_index", "device_name", "status", "file", "error"]

def load_successes(path, month):
    if not path.exists():
        return set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {
            (row["device_index"], row["device_name"])
            for row in csv.DictReader(stream)
            if row.get("month") == month and row.get("status") == "success"
        }

def append_log(path, row):
    present = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if not present:
            writer.writeheader()
        writer.writerow(row)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default="2026-10")
    parser.add_argument("--indices", help="Comma-separated 1-based device indices, maximum 3")
    parser.add_argument("--retry-success", action="store_true",
                        help="Also rerun devices logged successful")
    args = parser.parse_args()
    names_file = ROOT / "device_names.json"
    if not names_file.exists():
        raise SystemExit("缺少 device_names.json")
    names = json.loads(names_file.read_text(encoding="utf-8"))
    if not args.indices:
        print("請從以下列表選 2-3 台不同設備：")
        for i, name in enumerate(names, 1):
            print(f"{i:>3}. {name}")
        args.indices = input("輸入序號，例如 2,3,4：").strip()
    try:
        indices = [int(x.strip()) for x in args.indices.split(",")]
    except ValueError:
        raise SystemExit("輸入格式錯誤，應為 2,3,4")
    if not (1 <= len(indices) <= 3) or len(set(indices)) != len(indices):
        raise SystemExit("請選 1-3 台不同機台")
    if any(i < 1 or i > len(names) for i in indices):
        raise SystemExit("設備序號超出範圍")
    targets = [(i, names[i-1]) for i in indices]
    print("本次將依序執行：")
    for i, n in targets:
        print(f"  {i}. {n}")
    if input("確認執行上述機台，輸入 START：").strip() != "START":
        raise SystemExit("已取消")
    folder = ROOT / "downloads" / args.month
    folder.mkdir(parents=True, exist_ok=True)
    log_file = folder / "batch_log_v061.csv"
    successes = load_successes(log_file, args.month)
    for i, name in targets:
        if (str(i), name) in successes and not args.retry_success:
            print(f"略過已成功項目：{name}（如需重跑請使用 --retry-success）")
            continue
        print(f"\n===== 執行 {i}: {name} =====")
        before = {p.name for p in folder.iterdir()}
        run = subprocess.run([
            sys.executable, str(ROOT / "test_auto_export_v061.py"),
            "--month", args.month, "--device-index", str(i), "--skip-login-prompt"
        ], cwd=str(ROOT))
        after = {p.name for p in folder.iterdir()}
        # Only files created in this device run count; existing downloads
        # do not prove this iteration succeeded.
        new_files = [
            folder / entry for entry in after - before
            if (folder / entry).is_file()
            and (folder / entry).suffix.lower() in (".xlsx", ".xls", ".csv")
            and entry.startswith(filename_safe(args.month) + "_" + filename_safe(name))
        ]
        valid = (run.returncode == 0 and len(new_files) == 1 and new_files[0].stat().st_size > 0)
        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "month": args.month, "device_index": str(i), "device_name": name,
            "status": "success" if valid else "failed",
            "file": new_files[0].name if valid else "",
            "error": "" if valid else f"exit_code={run.returncode}, matching_new_files={len(new_files)}"
        }
        append_log(log_file, row)
        if not valid:
            raise SystemExit(f"第 {i} 台未確認成功，已停止後續下載。請檢查通知中心與 {log_file}")
        print(f"成功：{new_files[0].name}")
    print("\n本次小批次已結束。紀錄：", log_file)

if __name__ == "__main__":
    main()
