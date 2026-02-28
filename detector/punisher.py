"""
Punisher — floods the screen with random images, GIFs, videos, and audio
from the assets/media folder while the user is distracted.
"""

import os
import random
import threading
import time
from tkinter import Label, Toplevel

import cv2
import pygame
from PIL import Image, ImageTk


class Punisher:
    IMAGE_EXT = (".png", ".jpg", ".jpeg")
    AUDIO_EXT = (".mp3", ".wav", ".ogg")
    VIDEO_EXT = (".mp4", ".avi", ".mkv", ".gif")

    MAX_WINDOWS = 10            # Cap on concurrent popup windows
    POPUP_LIFETIME_MS = 5000    # How long each popup stays on screen
    SPAWN_INTERVAL_S = 0.7      # Seconds between new media spawns

    def __init__(self, media_folder: str, root_window):
        self.media_folder = media_folder
        self.root = root_window
        self.is_punishing = False
        self.punish_thread = None
        self.windows: list = []
        self.pending_images: list = []

        pygame.mixer.init()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_punishment(self):
        if self.is_punishing:
            return
        self.is_punishing = True
        self.punish_thread = threading.Thread(
            target=self._spam_loop, daemon=True
        )
        self.punish_thread.start()
        self._process_pending_images()

    def stop_punishment(self):
        self.is_punishing = False
        self._close_all_windows()
        pygame.mixer.stop()

    # ------------------------------------------------------------------
    # Window / image management
    # ------------------------------------------------------------------

    def _close_all_windows(self):
        for window in self.windows[:]:
            try:
                window.destroy()
            except Exception:
                pass
        self.windows.clear()
        self.pending_images.clear()

    def _close_window(self, window):
        try:
            if window in self.windows:
                self.windows.remove(window)
            window.destroy()
        except Exception:
            pass

    def _process_pending_images(self):
        """Dequeue pending image paths and open them on the main thread."""
        if not self.is_punishing:
            return
        while self.pending_images and len(self.windows) < self.MAX_WINDOWS:
            image_path = self.pending_images.pop(0)
            self._open_image_window(image_path)
        if self.is_punishing:
            self.root.after(100, self._process_pending_images)

    def _open_image_window(self, image_path: str):
        try:
            window = Toplevel(self.root)
            window.title("Focus!")
            window.overrideredirect(True)
            window.attributes("-topmost", True)

            x = random.randint(0, 1200)
            y = random.randint(0, 700)
            window.geometry(f"+{x}+{y}")

            img = Image.open(image_path)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label = Label(window, image=photo)
            label.image = photo  # Keep reference
            label.pack()

            self.windows.append(window)
            window.after(self.POPUP_LIFETIME_MS, lambda: self._close_window(window))
        except Exception as e:
            print(f"Error displaying {image_path}: {e}")

    def _open_video_window(self, video_path: str):
        try:
            window = Toplevel(self.root)
            window.title("Focus!")
            window.overrideredirect(True)
            window.attributes("-topmost", True)

            x = random.randint(0, 1200)
            y = random.randint(0, 700)
            window.geometry(f"+{x}+{y}")

            label = Label(window)
            label.pack()
            self.windows.append(window)

            cap = cv2.VideoCapture(video_path)

            def update_frame():
                if not window.winfo_exists() or not self.is_punishing:
                    cap.release()
                    return
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    self._close_window(window)
                    return
                frame = cv2.resize(frame, (400, 300))
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                photo = ImageTk.PhotoImage(image=img)
                label.photo = photo
                label.config(image=photo)
                window.after(33, update_frame)  # ~30 FPS

            update_frame()
            # Safety timeout to avoid runaway memory usage
            window.after(self.POPUP_LIFETIME_MS, lambda: self._close_window(window))
        except Exception as e:
            print(f"Error displaying video {video_path}: {e}")

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------

    def _play_audio(self, audio_path: str):
        try:
            pygame.mixer.Sound(audio_path).play()
        except Exception as e:
            print(f"Error playing audio {audio_path}: {e}")

    # ------------------------------------------------------------------
    # Spam loop (background thread)
    # ------------------------------------------------------------------

    def _spam_loop(self):
        valid_ext = self.IMAGE_EXT + self.AUDIO_EXT + self.VIDEO_EXT

        if not os.path.exists(self.media_folder):
            print(f"Error: Media folder '{self.media_folder}' does not exist.")
            return

        files = [
            f for f in os.listdir(self.media_folder)
            if f.lower().endswith(valid_ext)
        ]
        if not files:
            print("No valid media files found in assets/media.")
            return

        random.shuffle(files)
        file_index = 0

        while self.is_punishing:
            media_path = os.path.join(self.media_folder, files[file_index])
            ext = media_path.lower()

            if ext.endswith(self.IMAGE_EXT):
                self.pending_images.append(media_path)
            elif ext.endswith(self.AUDIO_EXT):
                self._play_audio(media_path)
            elif ext.endswith(self.VIDEO_EXT):
                self.root.after(0, lambda p=media_path: self._open_video_window(p))

            file_index = (file_index + 1) % len(files)
            time.sleep(self.SPAWN_INTERVAL_S)
