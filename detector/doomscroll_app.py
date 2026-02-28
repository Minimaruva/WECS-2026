"""
Doomscroll detector — webcam-based face-tracking app that monitors focus,
drives the Pomodoro overlay, and triggers the punishment/challenge system
when distractions exceed the configured threshold.
"""

import os
import tkinter as tk
from tkinter import ttk

import cv2
import pygame
from PIL import Image, ImageTk

from .punisher import Punisher
from ui.pomodoro_timer import RizeGlowBar
from ui.spinning_wheel import ChallengeWheel
from ui.break_timer import BreakApp

# Project root (two levels up: project/detector/doomscroll_app.py → project/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tuneable constants
DISTRACTION_THRESHOLD = 30   # Consecutive no-face frames before "distracted"
DISTRACTION_LIMIT = 5         # Total distractions before the challenge dialog
SUS_AUDIO_FRAME = 10          # Frame at which to play the "sus" audio cue


class DoomscrollApp:
    def __init__(self, window):
        self.is_running = True
        self.window = window
        self.window.title("Doomscroll Blocker")
        self.window.configure(bg="#8ACE00")

        pygame.mixer.init()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self._build_ui()

        self.wheel_launched = False
        self.cap = None
        self._switch_camera()

        self.distraction_frames = 0
        self.threshold = DISTRACTION_THRESHOLD
        self.is_currently_distracted = False
        self.total_distractions = 0

        media_dir = os.path.join(ROOT_DIR, "assets", "media")
        self.punisher = Punisher(media_dir, window)

        self.pomodoro_window = tk.Toplevel(self.window)
        self.pomodoro_bar = RizeGlowBar(self.pomodoro_window)

        self.update_frame()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        camera_frame = tk.Frame(self.window, bg="#8ACE00")
        camera_frame.pack(pady=10)

        tk.Label(
            camera_frame, text="CAMERA:",
            font=("Arial", 14, "bold"), bg="#8ACE00", fg="black",
        ).pack(side=tk.LEFT)

        self.camera_var = tk.StringVar(value="1")
        camera_dropdown = ttk.Combobox(
            camera_frame, textvariable=self.camera_var,
            values=["0", "1", "2", "3"], width=5,
        )
        camera_dropdown.pack(side=tk.LEFT, padx=10)

        tk.Button(
            camera_frame, text="SWITCH",
            font=("Arial", 10, "bold"), bg="black", fg="#8ACE00", bd=0,
            command=self._switch_camera,
        ).pack(side=tk.LEFT)

        self.video_label = tk.Label(self.window, bg="#8ACE00")
        self.video_label.pack(padx=10, pady=10)

        self.status_label = tk.Label(
            self.window, text="STATUS: FOCUSED",
            font=("Arial", 28, "bold"), bg="#8ACE00", fg="black",
        )
        self.status_label.pack(pady=5)

        self.counter_label = tk.Label(
            self.window, text="DISTRACTIONS: 0",
            font=("Arial", 20, "bold"), bg="#8ACE00", fg="black",
        )
        self.counter_label.pack(pady=5)

    # ------------------------------------------------------------------
    # Camera management
    # ------------------------------------------------------------------

    def _switch_camera(self):
        self.status_label.config(text="LOADING CAMERA...", fg="white")
        self.window.update()
        if self.cap is not None:
            self.cap.release()
        camera_index = int(self.camera_var.get())
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.status_label.config(text="STATUS: FOCUSED", fg="black")

    # ------------------------------------------------------------------
    # Distraction dialog
    # ------------------------------------------------------------------

    def _show_distraction_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Take a Break?")
        dialog.geometry("450x250")
        dialog.configure(bg="#8ACE00")
        dialog.transient(self.window)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        tk.Label(
            dialog,
            text="You are getting distracted!\n\nConsider taking a break or do the challenge!",
            font=("Arial", 16, "bold"), bg="#8ACE00", fg="black", justify="center",
        ).pack(pady=30)

        btn_frame = tk.Frame(dialog, bg="#8ACE00")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="TAKE BREAK",
            font=("Arial", 14, "bold"), bg="black", fg="#8ACE00",
            bd=0, padx=20, pady=10, cursor="hand2",
            command=lambda: self._take_break(dialog),
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="SPIN THE WHEEL",
            font=("Arial", 14, "bold"), bg="black", fg="#8ACE00",
            bd=0, padx=20, pady=10, cursor="hand2",
            command=lambda: self._accept_challenge(dialog),
        ).pack(side=tk.LEFT, padx=10)

        # Prevent closing by window manager
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def _take_break(self, dialog):
        dialog.destroy()
        self.is_running = False
        if hasattr(self, "cap") and self.cap and self.cap.isOpened():
            self.cap.release()
        self.punisher.stop_punishment()
        if self.pomodoro_window.winfo_exists():
            self.pomodoro_window.destroy()

        if hasattr(self.window, "main_menu_ref"):
            main_menu = self.window.main_menu_ref
            self.window.destroy()
            main_menu.launch_break()
        else:
            self.window.withdraw()
            break_window = tk.Toplevel(self.window)
            self.break_app = BreakApp(break_window)
            break_window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    def _accept_challenge(self, dialog):
        dialog.destroy()
        self._launch_wheel()

    # ------------------------------------------------------------------
    # Main frame-update loop
    # ------------------------------------------------------------------

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=6, minSize=(100, 100)
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if len(faces) == 0:
                self._handle_no_face()
            else:
                self._handle_face_detected()

            self._sync_pomodoro_state()

            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        if self.is_running:
            self.window.after(15, self.update_frame)

    def _handle_no_face(self):
        self.distraction_frames += 1

        if self.distraction_frames == SUS_AUDIO_FRAME:
            sus_path = os.path.join(ROOT_DIR, "assets", "audio", "sus.mp3")
            if os.path.exists(sus_path):
                pygame.mixer.music.load(sus_path)
                pygame.mixer.music.play()

        if self.distraction_frames >= self.threshold:
            self.is_currently_distracted = True
            self.status_label.config(text="LOOKING AWAY!", fg="red")
            self.punisher.start_punishment()
        else:
            self.status_label.config(
                text=f"LOSING FOCUS... {self.distraction_frames}/{self.threshold}",
                fg="white",
            )

    def _handle_face_detected(self):
        if self.is_currently_distracted:
            self.total_distractions += 1
            self.counter_label.config(text=f"DISTRACTIONS: {self.total_distractions}")
            self.is_currently_distracted = False
            self.punisher.stop_punishment()

        if self.distraction_frames > 0:
            self.distraction_frames = max(0, self.distraction_frames - 2)
            self.status_label.config(
                text=f"RECOVERING FOCUS... {self.distraction_frames}/{self.threshold}",
                fg="white",
            )

        if self.total_distractions >= DISTRACTION_LIMIT and not self.wheel_launched:
            self.status_label.config(
                text="WARNING: DOOMSCROLLING!", fg="red",
                font=("Arial", 28, "bold"),
            )
            self.wheel_launched = True
            self.is_running = False
            if hasattr(self, "cap") and self.cap and self.cap.isOpened():
                self.cap.release()
            self._show_distraction_dialog()

    def _sync_pomodoro_state(self):
        if not self.pomodoro_window.winfo_exists():
            return
        if self.is_currently_distracted:
            self.pomodoro_bar.focus_state = "distracted"
        elif self.distraction_frames > 0:
            self.pomodoro_bar.focus_state = "looking_away"
        else:
            self.pomodoro_bar.focus_state = "focused"
        self.pomodoro_bar.distractions = self.total_distractions

    # ------------------------------------------------------------------
    # Challenge wheel
    # ------------------------------------------------------------------

    def _launch_wheel(self):
        self.punisher.stop_punishment()
        self.is_running = False
        if hasattr(self, "cap") and self.cap and self.cap.isOpened():
            self.cap.release()
        if self.pomodoro_window.winfo_exists():
            self.pomodoro_window.destroy()
        self.window.withdraw()

        wheel_window = tk.Toplevel(self.window)
        self.wheel_app = ChallengeWheel(wheel_window)
        wheel_window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def __del__(self):
        self.is_running = False
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = DoomscrollApp(root)
    root.mainloop()
