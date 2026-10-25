"""Windows PyInstaller entrypoint: GUI, login and batch share one executable."""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

def _stream_from_handle(kind):
    """Recover redirected Windows STD_OUTPUT/STD_ERROR in --windowed EXE."""
    try:
        import ctypes
        import msvcrt
        handle = ctypes.windll.kernel32.GetStdHandle(kind)
        if handle in (0, -1) or handle is None:
            raise OSError("Missing redirected standard handle")
        flags = os.O_WRONLY | getattr(os, "O_BINARY", 0)
        fd = msvcrt.open_osfhandle(handle, flags)
        return os.fdopen(fd, "w", encoding="utf-8", errors="replace", buffering=1)
    except Exception:
        return open(os.devnull, "w", encoding="utf-8")

def main():
    import notifications
    import date_helpers
    import download_core
    import batch_download
    import open_login_desktop
    import app_desktop_v130
    import device_sync

    if getattr(sys, "frozen", False):
        home = Path(sys.executable).resolve().parent
        notifications.ROOT = home
        date_helpers.ROOT = home
        download_core.ROOT = home
        batch_download.ROOT = home
        open_login_desktop.ROOT = home
        device_sync.ROOT = home

    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        sys.argv.pop(1)
        batch_download.main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--login":
        sys.argv.pop(1)
        open_login_desktop.main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--sync-devices":
        sys.argv.pop(1)
        device_sync.main()
    else:
        import tkinter as tk
        root = tk.Tk()
        app_desktop_v130.DownloaderApp(root)
        root.mainloop()

if __name__ == "__main__":
    try:
        if len(sys.argv)>1 and sys.argv[1] in ("--login","--batch","--sync-devices"):
            # Windowed PyInstaller child processes lack real stdout/stderr.
            # Forward them to GUI-managed logs or inherited pipes.
            if sys.stdout is None:
                sys.stdout = _stream_from_handle(-11)
            if sys.stderr is None:
                sys.stderr = _stream_from_handle(-12)
        main()
    except BaseException:
        log = Path(sys.executable).resolve().parent / "desktop_error.log" if getattr(sys,"frozen",False) else Path(__file__).resolve().parent / "desktop_error.log"
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"\\n=== {datetime.now().isoformat()} ===\\n")
            traceback.print_exc(file=stream)
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        raise
