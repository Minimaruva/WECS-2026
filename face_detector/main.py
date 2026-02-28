import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from .punisher import Punisher
import os
import pygame
from pomodoro_timer import RizeGlowBar

class DoomscrollApp:
    def __init__(self, window):
        self.is_running = True
        self.window = window
        self.window.title("Doomscroll Blocker")
        # for sound play in bg
        pygame.mixer.init()
        # Use OpenCV's Haar Cascade 
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Camera selection dropdown
        camera_frame = tk.Frame(window)
        camera_frame.pack(pady=5)
        tk.Label(camera_frame, text="Camera:").pack(side=tk.LEFT)
        self.camera_var = tk.StringVar(value="1")
        camera_dropdown = ttk.Combobox(camera_frame, textvariable=self.camera_var, 
                                       values=["0", "1", "2", "3"], width=5)
        camera_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(camera_frame, text="Switch", command=self.switch_camera).pack(side=tk.LEFT)
        
        # 1. SETUP UI FIRST
        self.video_label = tk.Label(window)
        self.video_label.pack(padx=10, pady=10)
        
        self.status_label = tk.Label(window, text="Status: Focused", font=("Arial", 24))
        self.status_label.pack(pady=5)

        self.counter_label = tk.Label(window, text="Distractions: 0", font=("Arial", 18))
        self.counter_label.pack(pady=5)
        
        # 2. THEN INITIALIZE CAMERA
        self.cap = None
        self.switch_camera()
        
        # State tracking variables
        self.distraction_frames = 0
        self.threshold = 30 # Reduced for faster testing in a hackathon
        self.is_currently_distracted = False
        # number of distractions in one session
        self.total_distractions = 0
        
        self.punisher = Punisher("./media", window) # Folder with memes/videos for punishment
        self.pomodoro_window = tk.Toplevel(self.window)
        self.pomodoro_bar = RizeGlowBar(self.pomodoro_window)
        
        self.update_frame()
    
    def switch_camera(self):
        self.status_label.config(text="Loading camera...", fg="blue")
        self.window.update()  # Force UI update
        if self.cap is not None:
            self.cap.release()
        camera_index = int(self.camera_var.get())
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.status_label.config(text="Status: Focused", fg="green")
        
    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1) # Mirror for better UX
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw a bounding box around the face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Logic: No face = user looking away
            if len(faces) == 0:
                self.distraction_frames += 1
                if self.distraction_frames == 10:  # Just started getting distracted
                    sus_path = os.path.abspath("face_detector/sus.mp3")
                    if os.path.exists(sus_path):
                        pygame.mixer.music.load(sus_path)
                        pygame.mixer.music.play()
                    else:
                        print(f"Warning: sus.mp3 not found at {sus_path}")
                if self.distraction_frames >= self.threshold:
                    self.is_currently_distracted = True
                    self.status_label.config(text="LOOKING AWAY!", fg="orange")

                    # TRIGGER THE NEW MODULE
                    self.punisher.start_punishment()
                else:
                    self.status_label.config(text=f"Losing focus... {self.distraction_frames}/{self.threshold}", fg="gray")
                    
            else:
                # User returned to looking at screen
                if self.is_currently_distracted:
                    self.total_distractions += 1
                    self.counter_label.config(text=f"Distractions: {self.total_distractions}")
                    self.is_currently_distracted = False

                    # STOP THE MODULE
                    self.punisher.stop_punishment()
                
                self.distraction_frames = 0
                
                # Check for absolute failure condition
                if self.total_distractions >= 5:
                    self.status_label.config(text="WARNING: YOU ARE DOOMSCROLLING!", fg="red", font=("Arial", 24, "bold"))
                else:
                    self.status_label.config(text="Focused", fg="green", font=("Arial", 24))
            
            if self.pomodoro_window.winfo_exists():
                if self.is_currently_distracted:
                    self.pomodoro_bar.focus_state = "distracted"
                elif self.distraction_frames > 0:
                    self.pomodoro_bar.focus_state = "looking_away"
                else:
                    self.pomodoro_bar.focus_state = "focused"
                    
                self.pomodoro_bar.distractions = self.total_distractions
            
            # Display frame
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        # Un-indented to ensure the loop continues even if a frame drops
        if self.is_running:
            self.window.after(15, self.update_frame)    

    # Corrected indentation here
    def __del__(self):
        self.is_running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = DoomscrollApp(root)
    root.mainloop()