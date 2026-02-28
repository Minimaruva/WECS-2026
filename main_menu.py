import tkinter as tk
from face_detector.main import DoomscrollApp
from break_timer import BreakApp  # Import the new break module

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("App Name")
        self.root.geometry("500x400")
        
        self.title_label = tk.Label(root, text="Anti-Doomscroll", font=("Arial", 32, "bold"))
        self.title_label.pack(pady=40)
        
        self.start_button = tk.Button(
            root, 
            text="START FOCUS", 
            font=("Arial", 20, "bold"), 
            bg="green", 
            fg="white",
            padx=20,
            pady=10,
            command=self.launch_tracker
        )
        self.start_button.pack(pady=10)

        # New Break Button
        self.break_button = tk.Button(
            root, 
            text="START BREAK", 
            font=("Arial", 20, "bold"), 
            bg="blue", 
            fg="white",
            padx=20,
            pady=10,
            command=self.launch_break
        )
        self.break_button.pack(pady=10)

    def launch_tracker(self):
        self.root.withdraw()
        self.tracker_window = tk.Toplevel(self.root)
        self.tracker_window.protocol("WM_DELETE_WINDOW", self.on_close_tracker)
        self.app = DoomscrollApp(self.tracker_window)

    def launch_break(self):
        self.root.withdraw()
        self.break_window = tk.Toplevel(self.root)
        self.break_window.protocol("WM_DELETE_WINDOW", self.on_close_break)
        self.break_app = BreakApp(self.break_window)

    def on_close_tracker(self):
        if hasattr(self.app, 'cap') and self.app.cap.isOpened():
            self.app.cap.release()
        self.tracker_window.destroy()
        self.root.deiconify()

    def on_close_break(self):
        if hasattr(self.break_app, 'cap') and self.break_app.cap.isOpened():
            self.break_app.cap.release()
        self.break_window.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()