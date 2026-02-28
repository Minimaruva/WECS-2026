import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class DoomscrollApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Doomscroll Blocker")
        
        # Use OpenCV's Haar Cascade 
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Camera selection dropdown
        camera_frame = tk.Frame(window)
        camera_frame.pack(pady=5)
        tk.Label(camera_frame, text="Camera:").pack(side=tk.LEFT)
        self.camera_var = tk.StringVar(value="0")
        camera_dropdown = ttk.Combobox(camera_frame, textvariable=self.camera_var, 
                                       values=["0", "1", "2", "3"], width=5)
        camera_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(camera_frame, text="Switch", command=self.switch_camera).pack(side=tk.LEFT)
        
        # Setup UI and Camera
        self.cap = None
        self.switch_camera()
        
        self.video_label = tk.Label(window)
        self.video_label.pack(padx=10, pady=10)
        
        self.status_label = tk.Label(window, text="Status: Focused", font=("Arial", 24))
        self.status_label.pack(pady=5)

        self.counter_label = tk.Label(window, text="Distractions: 0", font=("Arial", 18))
        self.counter_label.pack(pady=5)
        
        # State tracking variables
        self.distraction_frames = 0
        self.threshold = 30 # Reduced for faster testing in a hackathon
        self.is_currently_distracted = False
        self.total_distractions = 0
        
        self.update_frame()
    
    def switch_camera(self):
        if self.cap is not None:
            self.cap.release()
        camera_index = int(self.camera_var.get())
        self.cap = cv2.VideoCapture(camera_index)
        
    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1) # Mirror for better UX
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw a bounding box around the face (Mesh is impossible with Haar)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Logic: No face = user looking away
            if len(faces) == 0:
                self.distraction_frames += 1
                
                if self.distraction_frames >= self.threshold:
                    self.is_currently_distracted = True
                    self.status_label.config(text="LOOKING AWAY!", fg="orange")
                else:
                    # Provide feedback that they are losing focus
                    self.status_label.config(text=f"Losing focus... {self.distraction_frames}/{self.threshold}", fg="gray")
                    
            else:
                # User returned to looking at screen
                if self.is_currently_distracted:
                    self.total_distractions += 1
                    self.counter_label.config(text=f"Distractions: {self.total_distractions}")
                    self.is_currently_distracted = False
                
                self.distraction_frames = 0
                
                # Check for absolute failure condition
                if self.total_distractions >= 5:
                    self.status_label.config(text="WARNING: YOU ARE DOOMSCROLLING!", fg="red", font=("Arial", 24, "bold"))
                else:
                    self.status_label.config(text="Focused", fg="green", font=("Arial", 24))
            
            # Display frame
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.window.after(15, self.update_frame)

    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = DoomscrollApp(root)
    root.mainloop()