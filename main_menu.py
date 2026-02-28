import tkinter as tk
# Import the class from your module
from face_detector.main import DoomscrollApp


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("App Name") # Change this to your hackathon app name
        self.root.geometry("500x400")
        
        # Title Label
        self.title_label = tk.Label(root, text="Anti-Doomscroll", font=("Arial", 32, "bold"))
        self.title_label.pack(pady=60)
        
        # Big Start Button
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
        self.start_button.pack(pady=20)

    def launch_tracker(self):
        # 1. Hide the main menu
        self.root.withdraw()
        
        # 2. Create a secondary window for the tracker
        self.tracker_window = tk.Toplevel(self.root)
        
        # 3. Define what happens when the user closes the tracker window
        self.tracker_window.protocol("WM_DELETE_WINDOW", self.on_close_tracker)
        
        # 4. Instantiate your existing tracker app inside this new window
        self.app = DoomscrollApp(self.tracker_window)

    def on_close_tracker(self):
        # Clean up the camera resources properly
        if hasattr(self.app, 'cap') and self.app.cap.isOpened():
            self.app.cap.release()
            
        # Destroy the tracker window and unhide the main menu
        self.tracker_window.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()