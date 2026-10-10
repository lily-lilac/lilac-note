#!/usr/bin/env python3
"""极简桌面便签 - 纯 tkinter 实现，零依赖"""

import atexit
import signal
import tkinter as tk
from tkinter import font
from pathlib import Path

# scripts/desktop_note.py -> 项目根目录
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
NOTE_FILE = DATA_DIR / "note.md"

FONT_SIZE = 20
SAVE_DELAY_MS = 200

# 莫兰迪丁香紫（Lilac）
BG_COLOR = "#E4D8E8"
BAR_COLOR = "#D0BCD8"
FG_COLOR = "#3A3340"
CLOSE_FG = "#877A8E"
SELECT_BG = "#C8A2C8"


class DesktopNote:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Note")

        self.root.overrideredirect(True)
        # 不置顶：可以被其他窗口盖住
        self.root.attributes("-topmost", False)

        self.root.geometry("400x320+80+120")

        self.note_font = font.Font(family="Helvetica", size=FONT_SIZE)

        # 顶部拖动条
        self.topbar = tk.Frame(self.root, bg=BAR_COLOR, height=22)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        close_btn = tk.Label(
            self.topbar, text="×", bg=BAR_COLOR, fg=CLOSE_FG,
            font=("Helvetica", 14, "bold"), cursor="hand2"
        )
        close_btn.pack(side="right", padx=(0, 6))
        close_btn.bind("<Button-1>", lambda e: self.on_close())

        self.topbar.bind("<Button-1>", self.start_move)
        self.topbar.bind("<B1-Motion>", self.do_move)

        # 文本区域
        self.text = tk.Text(
            self.root,
            font=self.note_font,
            wrap="word",
            undo=True,
            padx=14,
            pady=10,
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat",
            highlightthickness=0,
            borderwidth=0,
            selectbackground=SELECT_BG,
            selectforeground=FG_COLOR,
        )
        self.text.pack(fill="both", expand=True)

        if NOTE_FILE.exists():
            self.text.insert("1.0", NOTE_FILE.read_text(encoding="utf-8"))

        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<Double-Button-1>", self.toggle_checkbox)
        self.text.bind("<Command-s>", lambda e: self.save())
        self.text.bind("<Control-s>", lambda e: self.save())

        self.save_job = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.lift()
        self.root.focus_force()
        self.text.focus_set()

        atexit.register(self.save)
        signal.signal(signal.SIGTERM, lambda *_: (self.save(), self.root.destroy()))

        self.root.mainloop()

    def start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def schedule_save(self, event=None):
        if self.save_job:
            self.root.after_cancel(self.save_job)
        self.save_job = self.root.after(SAVE_DELAY_MS, self.save)

    def save(self):
        content = self.text.get("1.0", "end-1c")
        tmp = NOTE_FILE.with_suffix(".md.tmp")
        tmp.write_text(content, encoding="utf-8")
        if NOTE_FILE.exists():
            backup = NOTE_FILE.with_suffix(".md.bak")
            backup.write_text(NOTE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        tmp.replace(NOTE_FILE)
        self.save_job = None

    def on_modified(self, event=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.schedule_save()

    def toggle_checkbox(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        line_start = self.text.index(f"{index} linestart")
        line_end = self.text.index(f"{index} lineend")
        line = self.text.get(line_start, line_end)

        if "- [ ] " in line:
            new_line = line.replace("- [ ] ", "- [x] ", 1)
        elif "- [x] " in line:
            new_line = line.replace("- [x] ", "- [ ] ", 1)
        else:
            return

        self.text.delete(line_start, line_end)
        self.text.insert(line_start, new_line)
        self.schedule_save()
        return "break"

    def on_close(self):
        self.save()
        self.root.destroy()


if __name__ == "__main__":
    DesktopNote()
