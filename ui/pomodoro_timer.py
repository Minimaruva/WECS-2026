"""
Pomodoro timer overlay bar — a slim, draggable HUD that stays on top of all
windows and updates in sync with the face-detector focus state.
"""

import os
import tkinter as tk
from PIL import Image, ImageTk

# Project root (two levels up: project/ui/pomodoro_timer.py → project/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RizeGlowBar:
    # ------------------------------------------------------------------
    # Colour palette
    # ------------------------------------------------------------------
    BRAT_GREEN = "#8ACE00"
    BG_BLACK = "#000000"
    ALERT_RED = "#FF0000"
    WARN_ORANGE = "#FF4500"

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def __init__(self, root):
        self.root = root

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.bar_height = 50

        self.y_limit = self.screen_height - self.bar_height - 40
        self.y_hidden = self.screen_height - 5

        self.seconds_left = 25 * 60
        self.distractions = 0
        self.focus_state = "focused"

        self._configure_root()
        self._load_companion_images()
        self._build_main_bar()
        self._bind_drag_events()

        self.update_sync()
        self.update_timer()

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _configure_root(self):
        self.root.geometry(
            f"{self.screen_width}x{self.bar_height}+0+{self.y_limit}"
        )
        self.root.overrideredirect(True)
        self.root.config(bg=self.BG_BLACK)
        self.root.attributes("-topmost", True)

    def _load_companion_images(self):
        images_dir = os.path.join(ROOT_DIR, "assets", "images")

        self.comp_w = 350

        self.cat_root = self._setup_companion_window()
        self.img_cat_closed, self.img_cat_open, self.comp_h = self._load_and_scale(
            os.path.join(images_dir, "cat_closed.png"),
            os.path.join(images_dir, "cat_open.png"),
        )
        self.cat_display = tk.Label(
            self.cat_root, image=self.img_cat_closed, bg="white", bd=0
        )
        self.cat_display.pack()

        self.gauge_root = self._setup_companion_window()
        self.img_low_cort, self.img_high_cort, _ = self._load_and_scale(
            os.path.join(images_dir, "cortisol_low.png"),
            os.path.join(images_dir, "cortisol_high.png"),
        )
        self.gauge_display = tk.Label(
            self.gauge_root, image=self.img_low_cort, bg="white", bd=0
        )
        self.gauge_display.pack()

    def _setup_companion_window(self):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-transparentcolor", "white")
        win.config(bg="white")
        return win

    def _load_and_scale(self, path1, path2):
        img1_data = Image.open(path1)
        img2_data = Image.open(path2)
        w_percent = self.comp_w / float(img1_data.size[0])
        h = int(float(img1_data.size[1]) * w_percent)
        res1 = img1_data.resize((self.comp_w, h), Image.Resampling.LANCZOS)
        res2 = img2_data.resize((self.comp_w, h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(res1), ImageTk.PhotoImage(res2), h

    def _build_main_bar(self):
        self.main_frame = tk.Frame(
            self.root, bg=self.BG_BLACK, bd=0, highlightthickness=0
        )
        self.main_frame.pack(expand=True, fill="both", padx=20)

        self.timer_label = tk.Label(
            self.main_frame,
            text="25:00",
            font=("Arial", 24, "bold"),
            bg=self.BG_BLACK,
            fg=self.BRAT_GREEN,
            bd=0,
        )
        self.timer_label.pack(side="left", padx=10)

        self.distract_label = tk.Label(
            self.main_frame,
            text="DISTRACTIONS: 0",
            font=("Arial", 18, "bold"),
            bg=self.BG_BLACK,
            fg=self.BRAT_GREEN,
            bd=0,
        )
        self.distract_label.pack(side="left", padx=30)

        self.status_label = tk.Label(
            self.main_frame,
            text="STAY FOCUSED",
            font=("Arial", 18, "bold"),
            bg=self.BG_BLACK,
            fg=self.BRAT_GREEN,
            bd=0,
        )
        self.status_label.pack(side="right", padx=20)

    def _bind_drag_events(self):
        self._y_offset = 0
        draggable_widgets = [
            self.root,
            self.main_frame,
            self.timer_label,
            self.distract_label,
            self.status_label,
        ]
        for widget in draggable_widgets:
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)
            widget.bind("<ButtonRelease-1>", self._snap_to_position)

        self.root.bind("<Button-3>", lambda e: self.root.destroy())

    # ------------------------------------------------------------------
    # Drag behaviour
    # ------------------------------------------------------------------

    def _start_drag(self, event):
        self._y_offset = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        new_y = event.y_root - self._y_offset
        if new_y < self.y_limit:
            new_y = self.y_limit
        self.root.geometry(f"+0+{int(new_y)}")

    def _snap_to_position(self, event):
        current_y = self.root.winfo_y()
        if current_y > self.y_limit + 25:
            self.root.geometry(f"+0+{self.y_hidden}")
            self.root.config(bg=self.BRAT_GREEN)
            self.main_frame.pack_forget()
        else:
            self.root.geometry(f"+0+{self.y_limit}")
            self.root.config(bg=self.BG_BLACK)
            self.main_frame.pack(expand=True, fill="both", padx=20)

    # ------------------------------------------------------------------
    # Update loops
    # ------------------------------------------------------------------

    def update_sync(self):
        bar_y = self.root.winfo_y()
        right_x = self.screen_width - self.comp_w
        left_x = 20

        cat_y = bar_y - self.comp_h + 5
        gauge_y = bar_y - self.comp_h - 5

        if bar_y >= self.y_hidden:
            self.cat_root.withdraw()
            self.gauge_root.withdraw()
        else:
            self.cat_root.deiconify()
            self.gauge_root.deiconify()
            self.cat_root.geometry(
                f"{self.comp_w}x{self.comp_h}+{int(right_x)}+{int(cat_y)}"
            )
            self.gauge_root.geometry(
                f"{self.comp_w}x{self.comp_h}+{int(left_x)}+{int(gauge_y)}"
            )

        self.root.after(10, self.update_sync)

    def update_timer(self):
        if self.focus_state != "distracted" and self.seconds_left > 0:
            self.seconds_left -= 1

        mins, secs = divmod(self.seconds_left, 60)
        time_string = f"{mins:02d}:{secs:02d}"

        if self.focus_state == "distracted":
            if self.root.winfo_y() > self.y_limit + 10:
                self._snap_to_position(None)
            self.cat_display.config(image=self.img_cat_open)
            self.gauge_display.config(image=self.img_high_cort)
            self.timer_label.config(text="TOUCH GRASS!!", fg=self.ALERT_RED)
            self.status_label.config(
                text="DOOMSCROLLING!!", fg=self.ALERT_RED,
                font=("Arial", 18, "bold italic"),
            )
            self.distract_label.config(
                text=f"DISTRACTIONS: {self.distractions}", fg=self.ALERT_RED
            )

        elif self.focus_state == "looking_away":
            self.cat_display.config(image=self.img_cat_open)
            self.gauge_display.config(image=self.img_low_cort)
            self.timer_label.config(text=time_string, fg=self.WARN_ORANGE)
            self.status_label.config(
                text="LOOKING AWAY...", fg=self.WARN_ORANGE,
                font=("Arial", 18, "bold"),
            )
            self.distract_label.config(
                text=f"DISTRACTIONS: {self.distractions}", fg=self.WARN_ORANGE
            )

        else:  # focused
            self.cat_display.config(image=self.img_cat_closed)
            self.gauge_display.config(image=self.img_low_cort)
            self.timer_label.config(text=time_string, fg=self.BRAT_GREEN)
            self.status_label.config(
                text="STAY FOCUSED", fg=self.BRAT_GREEN,
                font=("Arial", 18, "bold"),
            )
            self.distract_label.config(
                text=f"DISTRACTIONS: {self.distractions}", fg=self.BRAT_GREEN
            )

        self.root.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = RizeGlowBar(tk.Toplevel(root))
    root.mainloop()
