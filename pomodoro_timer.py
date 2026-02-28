import tkinter as tk
from PIL import Image, ImageTk
import os

class RizeGlowBar:
    def __init__(self, root):
        self.root = root
        
        # --- 1. Aesthetics ---
        self.brat_green = "#8ACE00"
        self.bg_black = "#000000" 
        self.alert_red = "#FF0000"
        self.warn_orange = "#FF4500"
        
        
        # --- 2. Screen & Logic Setup ---
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.bar_height = 35 
        
        self.y_limit = self.screen_height - self.bar_height - 40 
        self.y_hidden = self.screen_height - 3 
        
        self.seconds_left = 25 * 60
        self.distractions = 0
        # self.is_doomscrolling = False 
        self.focus_state = "focused"
        
        # --- 3. Main Bar Setup ---
        self.root.geometry(f"{self.screen_width}x{self.bar_height}+0+{self.y_limit}")
        self.root.overrideredirect(True)
        self.root.config(bg=self.bg_black) 
        self.root.attributes('-topmost', True)

        # --- 4. Companion Windows Setup ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # MASSIVE SIZE CONTROL
        self.comp_w = 350 

        # --- RIGHT COMPANION (Focus Cat) ---
        self.cat_root = self.setup_companion_window()
        self.img_cat_closed, self.img_cat_open, self.comp_h = self.load_and_scale(
            os.path.join(base_path, "cat_closed.png"), 
            os.path.join(base_path, "cat_open.png")
        )
        self.cat_display = tk.Label(self.cat_root, image=self.img_cat_closed, bg="white")
        self.cat_display.pack()

        # --- LEFT COMPANION (Cortisol Gauge) ---
        self.gauge_root = self.setup_companion_window()
        self.img_low_cort, self.img_high_cort, _ = self.load_and_scale(
            os.path.join(base_path, "Untitled_design__1_-removebg-preview.png"), 
            os.path.join(base_path, "Cortisol_level_spike_meme-removebg-preview.png")
        )
        self.gauge_display = tk.Label(self.gauge_root, image=self.img_low_cort, bg="white")
        self.gauge_display.pack()

        # --- 5. Main UI Elements ---
        self.main_frame = tk.Frame(self.root, bg=self.bg_black)
        self.main_frame.pack(expand=True, fill="both", padx=20)

        self.timer_label = tk.Label(self.main_frame, text="25:00", font=("Arial", 14, "bold"), 
                                    bg=self.bg_black, fg=self.brat_green)
        self.timer_label.pack(side="left", padx=10)

        self.distract_label = tk.Label(self.main_frame, text=f"distractions: {self.distractions}", 
                                       font=("Arial", 12, "bold"), bg=self.bg_black, fg=self.brat_green)
        self.distract_label.pack(side="left", padx=20)

        self.status_label = tk.Label(self.main_frame, text="STAY FOCUSED", 
                                     font=("Arial", 11, "bold"), 
                                     bg=self.bg_black, fg=self.brat_green)
        self.status_label.pack(side="right", padx=20)

        # --- 6. Interaction Logic ---
        self._y_offset = 0
        widgets = [self.root, self.main_frame, self.timer_label, self.distract_label, self.status_label]
        for w in widgets:
            w.bind("<Button-1>", self.start_drag)
            w.bind("<B1-Motion>", self.do_drag)
            w.bind("<ButtonRelease-1>", self.snap_to_position)
            
        self.root.bind("<Button-3>", lambda e: self.root.destroy())
        
        self.update_sync() 
        self.update_timer()

    def setup_companion_window(self):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.attributes("-transparentcolor", "white") 
        win.config(bg="white")
        return win

    def load_and_scale(self, path1, path2):
        img1_data = Image.open(path1)
        img2_data = Image.open(path2)
        w_percent = (self.comp_w / float(img1_data.size[0]))
        h = int((float(img1_data.size[1]) * float(w_percent)))
        res1 = img1_data.resize((self.comp_w, h), Image.Resampling.LANCZOS)
        res2 = img2_data.resize((self.comp_w, h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(res1), ImageTk.PhotoImage(res2), h

    def update_sync(self):
        """Fine-tuned positioning: Cat moved to the absolute right."""
        bar_y = self.root.winfo_y()
        
        # CAT POSITION: Margin set to 0 to push it to the far right edge
        right_x = self.screen_width - self.comp_w - 0
        
        # GAUGE POSITION: Standard left margin
        left_x = 20 
        
        # VERTICAL POSITIONING
        cat_y = bar_y - self.comp_h + 5
        gauge_y = bar_y - self.comp_h - 5
        
        if bar_y >= self.y_hidden:
            self.cat_root.withdraw()
            self.gauge_root.withdraw()
        else:
            self.cat_root.deiconify()
            self.gauge_root.deiconify()
            
            self.cat_root.geometry(f"{self.comp_w}x{self.comp_h}+{int(right_x)}+{int(cat_y)}")
            self.gauge_root.geometry(f"{self.comp_w}x{self.comp_h}+{int(left_x)}+{int(gauge_y)}")
        
        self.root.after(10, self.update_sync)

    def start_drag(self, event):
        self._y_offset = event.y_root - self.root.winfo_y()

    def do_drag(self, event):
        new_y = event.y_root - self._y_offset
        if new_y < self.y_limit: new_y = self.y_limit
        self.root.geometry(f"+0+{int(new_y)}")

    def snap_to_position(self, event):
        current_y = self.root.winfo_y()
        if current_y > self.y_limit + 15:
            self.root.geometry(f"+0+{self.y_hidden}")
            self.root.config(bg=self.brat_green) 
            self.main_frame.pack_forget() 
        else:
            self.root.geometry(f"+0+{self.y_limit}")
            self.root.config(bg=self.bg_black)
            self.main_frame.pack(expand=True, fill="both", padx=20)

    # def update_timer(self):
    #     if not self.is_doomscrolling and self.seconds_left > 0:
    #         self.seconds_left -= 1
        
    #     mins, secs = divmod(self.seconds_left, 60)
    #     time_string = f"{mins:02d}:{secs:02d}"

    #     if self.is_doomscrolling:
    #         # If hidden, snap up immediately
    #         if self.root.winfo_y() > self.y_limit + 10:
    #             self.snap_to_position(None) 
            
    #         self.timer_label.config(text="TOUCH GRASS!!", fg=self.alert_red)
    #         self.status_label.config(text="LOSING FOCUS!!", fg=self.alert_red, font=("Arial", 11, "italic bold"))
    #         self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.alert_red)
    #     else:
    #         self.timer_label.config(text=time_string, fg=self.brat_green)
    #         self.status_label.config(text="STAY FOCUSED!1!", fg=self.brat_green, font=("Arial", 11, "bold"))
    #         self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.brat_green)

    #     self.root.after(1000, self.update_timer)

    def update_timer(self):
        if self.focus_state != "distracted" and self.seconds_left > 0:
            self.seconds_left -= 1
        
        mins, secs = divmod(self.seconds_left, 60)
        time_string = f"{mins:02d}:{secs:02d}"

        if self.is_doomscrolling:
            if self.root.winfo_y() > self.y_limit + 10:
                self.snap_to_position(None) 
            
            self.cat_display.config(image=self.img_cat_open)
            self.gauge_display.config(image=self.img_high_cort)
            
            self.timer_label.config(text="TOUCH GRASS", fg=self.alert_red)
            self.status_label.config(text="LOSING FOCUS", fg=self.alert_red)
            self.distract_label.config(fg=self.alert_red)
        else:
            self.cat_display.config(image=self.img_cat_closed)
            self.gauge_display.config(image=self.img_low_cort)
            
            self.timer_label.config(text=time_string, fg=self.brat_green)
            self.status_label.config(text="STAY FOCUSED", fg=self.brat_green)
            self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.brat_green)

        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    app = RizeGlowBar(tk.Toplevel(root))
    root.mainloop()


