import tkinter as tk

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
        
        # --- 3. Window Setup ---
        self.root.geometry(f"{self.screen_width}x{self.bar_height}+0+{self.y_limit}")
        self.root.overrideredirect(True)
        self.root.config(bg=self.bg_black) 
        self.root.attributes('-topmost', True)

        # --- 4. UI Elements ---
        self.main_frame = tk.Frame(self.root, bg=self.bg_black)
        self.main_frame.pack(expand=True, fill="both", padx=20)

        # LEFT: Timer
        self.timer_label = tk.Label(self.main_frame, text="25:00", font=("Arial", 14, "bold"), 
                                    bg=self.bg_black, fg=self.brat_green)
        self.timer_label.pack(side="left", padx=10)

        # MIDDLE: Distractions
        self.distract_label = tk.Label(self.main_frame, text=f"distractions: {self.distractions}", 
                                       font=("Arial", 12, "bold"), bg=self.bg_black, fg=self.brat_green)
        self.distract_label.pack(side="left", padx=20)

        # RIGHT: Status Text (Stay Focused / Losing Focus)
        self.status_label = tk.Label(self.main_frame, text="STAY FOCUSED", 
                                     font=("Arial", 11, "bold"), 
                                     bg=self.bg_black, fg=self.brat_green)
        self.status_label.pack(side="right", padx=20)

        # --- 5. INTERACTION LOGIC ---
        self._y_offset = 0
        
        widgets = [self.root, self.main_frame, self.timer_label, self.distract_label, self.status_label]
        for w in widgets:
            w.bind("<Button-1>", self.start_drag)
            w.bind("<B1-Motion>", self.do_drag)
            w.bind("<ButtonRelease-1>", self.snap_to_position)
            w.bind("<Enter>", lambda e: self.root.config(cursor="sb_v_double_arrow"))
            w.bind("<Leave>", lambda e: self.root.config(cursor="arrow"))
            
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

        self.update_timer()

    def start_drag(self, event):
        self._y_offset = event.y_root - self.root.winfo_y()
        self.root.config(bg=self.bg_black)
        self.main_frame.pack(expand=True, fill="both", padx=20)

    def do_drag(self, event):
        new_y = event.y_root - self._y_offset
        if new_y < self.y_limit:
            new_y = self.y_limit
        self.root.geometry(f"+0+{int(new_y)}")

    def snap_to_position(self, event):
        current_y = self.root.winfo_y()
        midpoint = self.y_limit + 15
        
        if current_y > midpoint:
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

        if self.focus_state == "distracted":
            if self.root.winfo_y() > self.y_limit + 10:
                self.snap_to_position(None) 
            
            self.timer_label.config(text="TOUCH GRASS!!", fg=self.alert_red)
            self.status_label.config(text="DOOMSCROLLING!!", fg=self.alert_red, font=("Arial", 11, "italic bold"))
            self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.alert_red)
            
        elif self.focus_state == "looking_away":
            self.timer_label.config(text=time_string, fg=self.warn_orange)
            self.status_label.config(text="LOOKING AWAY...", fg=self.warn_orange, font=("Arial", 11, "bold"))
            self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.warn_orange)
            
        else: # focused
            self.timer_label.config(text=time_string, fg=self.brat_green)
            self.status_label.config(text="STAY FOCUSED!1!", fg=self.brat_green, font=("Arial", 11, "bold"))
            self.distract_label.config(text=f"distractions: {self.distractions}", fg=self.brat_green)

        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = RizeGlowBar(root)
    root.mainloop()