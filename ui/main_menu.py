"""
Main menu window — entry point UI for the Anti-Doomscroll app.
"""

import tkinter as tk

from detector.doomscroll_app import DoomscrollApp
from ui.break_timer import BreakApp
from ui.spinning_wheel import ChallengeWheel
from ui.telegram_app import TypeWriterApp


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Anti-Doomscroll")
        self.root.geometry("500x400")
        self.root.configure(bg="#8ACE00")

        self.title_label = tk.Label(
            root,
            text="ANTI-DOOMSCROLL",
            font=("Arial", 36, "bold", "italic"),
            bg="#8ACE00",
            fg="black",
        )
        self.title_label.pack(pady=50)

        self.start_button = tk.Button(
            root,
            text="START FOCUS",
            font=("Arial", 24, "bold"),
            bg="black",
            fg="#8ACE00",
            bd=0,
            activebackground="#333333",
            activeforeground="#8ACE00",
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.launch_tracker,
        )
        self.start_button.pack(pady=10)

        self.break_button = tk.Button(
            root,
            text="START BREAK",
            font=("Arial", 24, "bold"),
            bg="black",
            fg="#8ACE00",
            bd=0,
            activebackground="#333333",
            activeforeground="#8ACE00",
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.launch_break,
        )
        self.break_button.pack(pady=10)

    # ------------------------------------------------------------------
    # Launch helpers
    # ------------------------------------------------------------------

    def launch_tracker(self):
        self.root.withdraw()
        self.tracker_window = tk.Toplevel(self.root)
        self.tracker_window.main_menu_ref = self
        self.tracker_window.protocol("WM_DELETE_WINDOW", self.on_close_tracker)
        self.app = DoomscrollApp(self.tracker_window)

    def launch_break(self):
        self.root.withdraw()
        self.break_window = tk.Toplevel(self.root)
        self.break_window.protocol("WM_DELETE_WINDOW", self.on_close_break)
        self.break_app = BreakApp(self.break_window)

    def launch_wheel(self):
        self.root.withdraw()
        self.wheel_window = tk.Toplevel(self.root)
        self.wheel_window.protocol("WM_DELETE_WINDOW", self.on_close_wheel)
        self.wheel_app = ChallengeWheel(self.wheel_window)

    def launch_telegram(self):
        self.root.withdraw()
        self.telegram_window = tk.Toplevel(self.root)
        self.telegram_app = TypeWriterApp(self.telegram_window, main_menu_ref=self)

    # ------------------------------------------------------------------
    # Close handlers
    # ------------------------------------------------------------------

    def on_close_tracker(self):
        if hasattr(self, "app"):
            self.app.is_running = False
            if hasattr(self.app, "cap") and self.app.cap and self.app.cap.isOpened():
                self.app.cap.release()
        if hasattr(self, "tracker_window") and self.tracker_window.winfo_exists():
            self.tracker_window.destroy()
        self.root.deiconify()

    def on_close_break(self):
        if hasattr(self, "break_app"):
            self.break_app.cleanup()
        if hasattr(self, "break_window") and self.break_window.winfo_exists():
            self.break_window.destroy()
        self.root.deiconify()

    def on_close_wheel(self):
        if hasattr(self, "wheel_window") and self.wheel_window.winfo_exists():
            self.wheel_window.destroy()
        self.root.deiconify()

    def on_close_telegram(self):
        if hasattr(self, "telegram_window") and self.telegram_window.winfo_exists():
            self.telegram_window.destroy()
        self.root.deiconify()
