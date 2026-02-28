"""
Break timer window — shows a countdown, webcam feed, dance video, and a GIF
to encourage the user to move during their break.
"""

import os

import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Project root (two levels up from this file: project/ui/break_timer.py → project/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BreakApp:
    BREAK_DURATION_SECONDS = 300  # 5 minutes

    def __init__(self, window):
        self.window = window
        self.window.title("Break Time")
        self.window.geometry("1000x550")
        self.window.configure(bg="#8ACE00")

        self.time_left = self.BREAK_DURATION_SECONDS
        self.is_running = True

        self._build_ui()
        self._init_camera()
        self._load_video()
        self._load_gif()

        self.update_timer()
        self.update_media()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.timer_label = tk.Label(
            self.window,
            text="05:00",
            font=("Arial", 48, "bold"),
            fg="black",
            bg="#8ACE00",
        )
        self.timer_label.pack(pady=10)

        self.warning_label = tk.Label(
            self.window,
            text="NO ONE DETECTED",
            font=("Arial", 32, "bold"),
            fg="white",
            bg="#8ACE00",
        )
        self.warning_label.pack(pady=10)

        self.media_frame = tk.Frame(self.window, bg="#8ACE00")
        self.media_frame.pack(expand=True, fill="both")

        self.cam_label = tk.Label(
            self.media_frame, bg="#8ACE00",
            text="CAMERA MISSING", font=("Arial", 16, "bold"), fg="black",
        )
        self.cam_label.pack(side="left", padx=10)

        self.video_label = tk.Label(
            self.media_frame, bg="#8ACE00",
            text="VIDEO MISSING", font=("Arial", 16, "bold"), fg="black",
        )
        self.video_label.pack(side="left", padx=10)

        self.gif_label = tk.Label(
            self.media_frame, bg="#8ACE00",
            text="GIF MISSING", font=("Arial", 16, "bold"), fg="black",
        )
        self.gif_label.pack(side="right", padx=10)

    # ------------------------------------------------------------------
    # Resource initialisation
    # ------------------------------------------------------------------

    def _init_camera(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    def _load_video(self):
        vid_path = os.path.join(ROOT_DIR, "assets", "videos", "dance_break.mp4")
        self.has_video = os.path.exists(vid_path)
        if self.has_video:
            self.video_cap = cv2.VideoCapture(vid_path)
        else:
            print(f"Warning: Dance-break video not found at {vid_path}")

    def _load_gif(self):
        self.gif_frames = []
        gif_path = os.path.join(ROOT_DIR, "assets", "media", "dancing-cat.gif")
        try:
            gif = Image.open(gif_path)
            for i in range(gif.n_frames):
                gif.seek(i)
                frame = gif.copy().convert("RGBA")
                frame = frame.resize((300, 250), Image.Resampling.LANCZOS)
                self.gif_frames.append(ImageTk.PhotoImage(frame))
        except Exception as e:
            print(f"Failed to load GIF: {e}")
        self.current_gif_frame = 0

    # ------------------------------------------------------------------
    # Update loops
    # ------------------------------------------------------------------

    def update_timer(self):
        if not self.window.winfo_exists():
            return

        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.window.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="BREAK OVER!", fg="red")

    def update_media(self):
        if not self.window.winfo_exists() or not self.is_running:
            return

        self._update_camera_feed()
        self._update_video_feed()
        self._update_gif()

        self.window.after(33, self.update_media)

    def _update_camera_feed(self):
        if not (hasattr(self, "cap") and self.cap.isOpened()):
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        warning_text = "NO ONE DETECTED"
        tk_color = "white"

        for (x, y, w, h) in faces:
            if w > 120:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                warning_text = "STAND UP & STEP BACK!"
                tk_color = "red"
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                warning_text = "GOOD JOB! KEEP MOVING"
                tk_color = "black"

        self.warning_label.config(text=warning_text, fg=tk_color)

        frame = cv2.resize(frame, (300, 250))
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.cam_label.imgtk = imgtk
        self.cam_label.configure(image=imgtk)

    def _update_video_feed(self):
        if not (self.has_video and self.video_cap.isOpened()):
            return

        ret, frame = self.video_cap.read()
        if not ret:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_cap.read()

        if ret:
            frame = cv2.resize(frame, (300, 250))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

    def _update_gif(self):
        if not self.gif_frames:
            return
        self.gif_label.configure(image=self.gif_frames[self.current_gif_frame])
        self.current_gif_frame = (self.current_gif_frame + 1) % len(self.gif_frames)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self):
        self.is_running = False
        if hasattr(self, "cap") and self.cap and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, "video_cap") and self.has_video and self.video_cap.isOpened():
            self.video_cap.release()

    def __del__(self):
        self.cleanup()
