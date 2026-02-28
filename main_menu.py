import tkinter as tk
from face_detector.main import DoomscrollApp
from break_timer import BreakApp  # Import the new break module
from spinningWheel import ChallengeWheel
from combinedMsg import TypeWriterApp


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("App Name")
        self.root.geometry("500x400")
        self.root.configure(bg="#8ACE00")
        
        self.title_label = tk.Label(root, text="ANTI-DOOMSCROLL", font=("Arial", 36, "bold", "italic"), bg="#8ACE00", fg="black")
        self.title_label.pack(pady=50)
        
        self.start_button = tk.Button(
            root, text="START FOCUS", font=("Arial", 24, "bold"), 
            bg="black", fg="#8ACE00", bd=0, activebackground="#333333", activeforeground="#8ACE00",
            padx=30, pady=15, cursor="hand2", command=self.launch_tracker
        )
        self.start_button.pack(pady=10)

        self.break_button = tk.Button(
            root, text="START BREAK", font=("Arial", 24, "bold"), 
            bg="black", fg="#8ACE00", bd=0, activebackground="#333333", activeforeground="#8ACE00",
            padx=30, pady=15, cursor="hand2", command=self.launch_break
        )
        self.break_button.pack(pady=10)

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

    def on_close_tracker(self):
        if hasattr(self, 'app'):
            self.app.is_running = False
            if hasattr(self.app, 'cap') and self.app.cap and self.app.cap.isOpened():
                self.app.cap.release()
        if hasattr(self, 'tracker_window') and self.tracker_window.winfo_exists():
            self.tracker_window.destroy()
        self.root.deiconify()

    def on_close_break(self):
        if hasattr(self, 'break_app'):
            if hasattr(self.break_app, 'cap') and self.break_app.cap and self.break_app.cap.isOpened():
                self.break_app.cap.release()
            if hasattr(self.break_app, 'video_cap') and self.break_app.has_video and self.break_app.video_cap.isOpened():
                self.break_app.video_cap.release()
        if hasattr(self, 'break_window') and self.break_window.winfo_exists():
            self.break_window.destroy()
        self.root.deiconify()

    def on_close_wheel(self):
        if hasattr(self, 'wheel_window') and self.wheel_window.winfo_exists():
            self.wheel_window.destroy()
        self.root.deiconify()

    def on_close_telegram(self):
        if hasattr(self, 'telegram_window') and self.telegram_window.winfo_exists():
            self.telegram_window.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()