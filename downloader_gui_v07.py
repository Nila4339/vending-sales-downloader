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
        self.backend = tk.StringVar(value="v063")
        self._build()
        self._load_names()
        root.after(120, self._drain)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="JUSTECH 銷售報表下載器", font=("Microsoft JhengHei UI", 17, "bold")).pack(anchor="w")
        ttk.Label(outer, text="使用 v0.6.3 已測試的下載流程；整批結束前會逐台開啟瀏覽器。", foreground="#555").pack(anchor="w", pady=(4, 14))
        form = ttk.Frame(outer)
        form.pack(fill="x")
        ttk.Label(form, text="對帳年月 (YYYY-MM)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.month, width=18).grid(row=1, column=0, sticky="w", padx=(0, 20))
        ttk.Radiobutton(form, text="全部機台", variable=self.all_devices, value=True, command=self._toggle_selection).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(form, text="指定機台（可複選）", variable=self.all_devices, value=False, command=self._toggle_selection).grid(row=1, column=2, sticky="w", padx=10)
        self.device_frame = ttk.LabelFrame(outer, text="機台清單", padding=7)
        self.device_frame.pack(fill="both", expand=False, pady=12)
        self.listbox = tk.Listbox(self.device_frame, selectmode=tk.EXTENDED, height=9, exportselection=False)
        y = ttk.Scrollbar(self.device_frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=y.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        y.pack(side="right", fill="y")
        mode_frame = ttk.Frame(outer)
        mode_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(mode_frame, text="執行模式：").pack(side="left")
        ttk.Radiobutton(mode_frame, text="穩定版 v0.6.3（每台重開瀏覽器）", variable=self.backend, value="v063").pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="測試版 v0.7（共用瀏覽器）", variable=self.backend, value="v07").pack(side="left", padx=5)
        ttk.Checkbutton(outer, text="重新下載已記錄成功的機台（預設不勾選）", variable=self.retry).pack(anchor="w")
        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=10)
        self.start_button = ttk.Button(controls, text="開始下載", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(controls, text="本台結束後停止", command=self.request_stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        ttk.Button(controls, text="開啟下載資料夾", command=self.open_folder).pack(side="left", padx=8)
        ttk.Label(outer, textvariable=self.status).pack(anchor="w")
        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill="x", pady=8)
        self.log = tk.Text(outer, wrap="word", height=12, state="disabled", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)
        self._toggle_selection()

    def _load_names(self):
        if not NAMES.exists() or not RUNNER.exists():
            messagebox.showwarning("缺少檔案", "請確認 device_names.json 和 batch_download_gui_runner.py 都在同一資料夾。")
            return
        try:
            self.names = json.loads(NAMES.read_text(encoding="utf-8"))
            self.listbox.delete(0, tk.END)
            for i, name in enumerate(self.names, 1):
                self.listbox.insert(tk.END, f"{i:02d}  {name}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("機台清單錯誤", str(exc))

    def _toggle_selection(self):
        self.listbox.configure(state="disabled" if self.all_devices.get() else "normal")

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
            indices = [i+1 for i in self.listbox.curselection()]
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
        self.progress.start(12)
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
                else:
                    self._append(f"===== 程式結束，退出碼 {value} =====")
                    self.progress.stop()
                    self.proc = None
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.status.set("已結束；請查看執行紀錄及 CSV")
                    self.stop_marker.unlink(missing_ok=True)
        except queue.Empty:
            pass
        self.root.after(120, self._drain)

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
