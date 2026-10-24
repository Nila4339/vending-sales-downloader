"""Windows PyInstaller entrypoint: GUI, login and batch share one executable."""
import os
import sys
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
    main()
