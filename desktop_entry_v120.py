"""Windows PyInstaller entrypoint: GUI, login and batch share one executable."""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

def main():
    import notifications
    import date_helpers
    import download_core
    import batch_download
    import open_login_desktop
    import app_desktop

    if getattr(sys, "frozen", False):
        home = Path(sys.executable).resolve().parent
        notifications.ROOT = home
        date_helpers.ROOT = home
        download_core.ROOT = home
        batch_download.ROOT = home
        open_login_desktop.ROOT = home

    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        sys.argv.pop(1)
        batch_download.main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--login":
        sys.argv.pop(1)
        open_login_desktop.main()
    else:
        import tkinter as tk
        root = tk.Tk()
        app_desktop.DownloaderApp(root)
        root.mainloop()

if __name__ == "__main__":
    try:
        if len(sys.argv)>1 and sys.argv[1] in ("--login","--batch"):
            # Windowed PyInstaller child processes lack real stdout/stderr.
            # Forward them to GUI-managed logs or inherited pipes.
            if sys.stdout is None:
                sys.stdout = open(os.devnull, "w", encoding="utf-8")
            if sys.stderr is None:
                sys.stderr = sys.stdout
        main()
    except BaseException:
        log = Path(sys.executable).resolve().parent / "desktop_error.log" if getattr(sys,"frozen",False) else Path(__file__).resolve().parent / "desktop_error.log"
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"\\n=== {datetime.now().isoformat()} ===\\n")
            traceback.print_exc(file=stream)
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        raise
