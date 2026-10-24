"""JUSTECH Windows GUI for proven v0.6.3 backend. No external GUI packages."""
import csv
import json
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "batch_download_gui_runner.py"
RUNNER_V07 = ROOT / "batch_download_v070.py"
NAMES = ROOT / "device_names.json"

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("JUSTECH 銷售報表下載器")
        root.geometry("870x670")
        root.minsize(720, 570)
        self.proc = None
        self.messages = queue.Queue()
        self.stop_marker = ROOT / ".gui_stop_requested"
        self.names = []
        self.month = tk.StringVar(value=date.today().strftime("%Y-%m"))
        self.all_devices = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="尚未開始")
        self.retry = tk.BooleanVar(value=False)
        self.backend = tk.StringVar(value="v07")
        self.search_text = tk.StringVar()
        self.search_text.trace_add("write", lambda *_: self._refresh_list())
        self.visible_indices = []
        self.selected_indices = set()
        self._refreshing = False
        self.processed = 0
        self.total = 0
        self.tally = {"success":0, "skip":0, "failed":0}
        self._build()
        self._load_names()
        root.after(120, self._drain)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="JUSTECH 銷售報表下載器", font=("Microsoft JhengHei UI", 17, "bold")).pack(anchor="w")
        ttk.Label(outer, text="v0.7 共用瀏覽器／v0.6.3 備援；從本月紀錄顯示每台狀態。", foreground="#555").pack(anchor="w", pady=(4, 14))
        form = ttk.Frame(outer)
        form.pack(fill="x")
        ttk.Label(form, text="對帳年月 (YYYY-MM)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.month, width=18).grid(row=1, column=0, sticky="w", padx=(0, 20))
        ttk.Radiobutton(form, text="全部機台", variable=self.all_devices, value=True, command=self._toggle_selection).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(form, text="指定機台（可複選）", variable=self.all_devices, value=False, command=self._toggle_selection).grid(row=1, column=2, sticky="w", padx=10)
        search_row = ttk.Frame(outer)
        search_row.pack(fill="x", pady=(8, 0))
        ttk.Label(search_row, text="搜尋機台：").pack(side="left")
        ttk.Entry(search_row, textvariable=self.search_text).pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="清除搜尋", command=lambda: self.search_text.set("")).pack(side="left", padx=5)
        self.device_frame = ttk.LabelFrame(outer, text="機台清單（顯示每月下載狀態）", padding=7)
        self.device_frame.pack(fill="both", expand=False, pady=12)
        self.listbox = tk.Listbox(self.device_frame, selectmode=tk.EXTENDED, height=9, exportselection=False)
        y = ttk.Scrollbar(self.device_frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=y.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._remember_selection)
        self.month.trace_add("write", lambda *_: self._refresh_list())
        y.pack(side="right", fill="y")
        mode_frame = ttk.Frame(outer)
        mode_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(mode_frame, text="執行模式：").pack(side="left")
        ttk.Radiobutton(mode_frame, text="穩定版 v0.6.3（每台重開瀏覽器）", variable=self.backend, value="v063").pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="測試版 v0.7（共用瀏覽器）", variable=self.backend, value="v07").pack(side="left", padx=5)
        ttk.Button(outer, text="重新讀取機台清單", command=self._load_names).pack(anchor="w", pady=(0, 5))
        ttk.Checkbutton(outer, text="重新下載已記錄成功的機台（預設不勾選）", variable=self.retry).pack(anchor="w")
        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=10)
        self.start_button = ttk.Button(controls, text="開始下載", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(controls, text="本台結束後停止", command=self.request_stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        ttk.Button(controls, text="開啟下載資料夾", command=self.open_folder).pack(side="left", padx=8)
        ttk.Label(outer, textvariable=self.status).pack(anchor="w")
        self.counts = tk.StringVar(value="成功 0｜略過 0｜失敗 0｜已處理 0/0")
        ttk.Label(outer, textvariable=self.counts).pack(anchor="w", pady=(3,0))
        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=8)
        self.log = tk.Text(outer, wrap="word", height=12, state="disabled", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)
        self._toggle_selection()

    def _read_month_status(self):
        folder = ROOT / "downloads" / self.month.get().strip()
        log = folder / "batch_log_v063.csv"
        result = {}
        if not log.exists():
            return result
        try:
            with log.open(encoding="utf-8-sig", newline="") as stream:
                for row in csv.DictReader(stream):
                    if row.get("month") != self.month.get().strip():
                        continue
                    try:
                        idx = int(row.get("device_index", ""))
                    except ValueError:
                        continue
                    if not (1 <= idx <= len(self.names)) or row.get("device_name") != self.names[idx-1]:
                        continue
                    if row.get("status") == "success":
                        filename = row.get("file", "")
                        path = folder / filename
                        result[idx] = "已下載" if (filename and path.is_file() and path.stat().st_size > 0) else "檔案遺失"
                    elif row.get("status") == "failed":
                        result[idx] = "失敗"
        except (OSError, csv.Error) as exc:
            self.status.set(f"紀錄讀取失敗：{exc}")
        return result

    def _remember_selection(self, event=None):
        if self._refreshing or self.all_devices.get():
            return
        visible = set(self.visible_indices)
        self.selected_indices.difference_update(visible)
        self.selected_indices.update(self.visible_indices[j] for j in self.listbox.curselection())

    def _refresh_list(self):
        if not hasattr(self, "listbox"):
            return
        self._refreshing = True
        self.listbox.configure(state="normal")
        self.listbox.delete(0, tk.END)
        query = self.search_text.get().strip().casefold()
        statuses = self._read_month_status()
        self.visible_indices = []
        for idx, name in enumerate(self.names, 1):
            if query and query not in name.casefold() and query not in str(idx):
                continue
            self.visible_indices.append(idx)
            self.listbox.insert(tk.END, f"{idx:02d}  [{statuses.get(idx, '尚未下載')}] {name}")
            if idx in self.selected_indices:
                self.listbox.selection_set(tk.END)
        self._refreshing = False
        self._toggle_selection()

    def _load_names(self):
        self.names = []
        if not NAMES.exists():
            self.status.set(f"找不到機台清單：{NAMES}")
            messagebox.showwarning("缺少機台清單", f"找不到 {NAMES}；請複製先前的 device_names.json。")
        else:
            try:
                data = json.loads(NAMES.read_text(encoding="utf-8-sig"))
                if not isinstance(data, list) or not data or not all(isinstance(x, str) and x.strip() for x in data):
                    raise ValueError("機台清單必須是非空的名稱陣列")
                self.names = data
                self.status.set(f"已載入 {len(data)} 台機器")
            except (OSError, ValueError) as exc:
                self.status.set(f"機台清單錯誤：{exc}")
                messagebox.showerror("機台清單錯誤", str(exc))
        self.selected_indices.clear()
        self._refresh_list()

    def _toggle_selection(self):
        # Always show machine names; only disable selection in all-device mode.
        self.listbox.configure(state="disabled" if self.all_devices.get() and self.names else "normal")

    def _append(self, msg):
        self.log.configure(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def start(self):
        if self.proc is not None:
            return
        month = self.month.get().strip()
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
            messagebox.showerror("日期錯誤", "請輸入 YYYY-MM，例如 2026-10。")
            return
        if not self.names:
            messagebox.showerror("無機台", "尚未載入 device_names.json。")
            return
        if self.all_devices.get():
            indices = list(range(1, len(self.names)+1))
        else:
            indices = sorted(self.selected_indices)
            if not indices:
                messagebox.showerror("未選機台", "請先勾選至少一台機器。")
                return
        if not messagebox.askyesno("開始下載", f"對帳年月：{month}\n選取機台：{len(indices)} 台\n請先確認 JUSTECH 已登入，且沒有其他使用者同時匯出相同報表。\n確定開始嗎？"):
            return
        try:
            self.stop_marker.unlink(missing_ok=True)
            active_runner = RUNNER_V07 if self.backend.get() == "v07" else RUNNER
            if not active_runner.exists():
                messagebox.showerror("缺少程式", f"找不到 {active_runner.name}")
                return
            command = [sys.executable, "-u", str(active_runner), "--month", month,
                       "--indices", ",".join(map(str, indices)), "--auto-start",
                       "--stop-file", str(self.stop_marker)]
            if self.retry.get():
                command.append("--retry-success")
            self.proc = subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.DEVNULL,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, encoding="utf-8", errors="replace",
                                         bufsize=1)
        except OSError as exc:
            messagebox.showerror("無法啟動", str(exc))
            self.proc = None
            return
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.total = len(indices)
        self.processed = 0
        self.tally = {"success":0, "skip":0, "failed":0}
        self.progress.configure(value=0)
        self._update_counts()
        self.status.set(f"執行中：{month}，共 {len(indices)} 台")
        self._append(f"===== 開始 {month} / {len(indices)} 台 / {self.backend.get()} =====")
        threading.Thread(target=self._stream, daemon=True).start()

    def _stream(self):
        proc = self.proc
        try:
            for line in proc.stdout:
                self.messages.put(("line", line.rstrip()))
        finally:
            code = proc.wait()
            self.messages.put(("done", code))

    def _drain(self):
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "line":
                    self._append(value)
                    self._consume_progress(value)
                else:
                    self._append(f"===== 程式結束，退出碼 {value} =====")
                    self._refresh_list()
                    self.proc = None
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.status.set("已結束；請查看執行紀錄及 CSV")
                    self.stop_marker.unlink(missing_ok=True)
        except queue.Empty:
            pass
        self.root.after(120, self._drain)

    def _update_counts(self):
        self.counts.set(f"成功 {self.tally['success']}｜略過 {self.tally['skip']}｜失敗 {self.tally['failed']}｜已處理 {self.processed}/{self.total}")
        self.progress.configure(value=(100*self.processed/self.total) if self.total else 0)

    def _consume_progress(self, line):
        # Both v0.6.3 and v0.7 emit these messages. Count only completed devices.
        if line.startswith("成功："):
            self.tally["success"] += 1
            self.processed += 1
        elif "略過已成功" in line:
            self.tally["skip"] += 1
            self.processed += 1
        elif re.search(r"第 \d+ 台失敗|第 \d+ 台未確認成功", line):
            self.tally["failed"] += 1
            self.processed += 1
        self._update_counts()
        if self.proc is not None:
            self.status.set(f"下載執行中：{self.processed}/{self.total} 台")

    def request_stop(self):
        if self.proc is None:
            return
        self.stop_marker.touch()
        self.stop_button.configure(state="disabled")
        self.status.set("已要求停止：目前這台執行完後才會停止")
        self._append("使用者要求停止；為保護下載完整性，將於下一台開始前停止。")

    def open_folder(self):
        folder = ROOT / "downloads" / self.month.get().strip()
        folder.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(folder))
        else:
            messagebox.showinfo("下載資料夾", str(folder))

    def _on_close(self):
        if self.proc is not None:
            messagebox.showwarning("仍在下載", "下載仍在執行。請按「本台結束後停止」，待程式結束再關閉視窗。")
            return
        self.root.destroy()

if __name__ == "__main__":
    tk_root = tk.Tk()
    DownloaderApp(tk_root)
    tk_root.mainloop()
