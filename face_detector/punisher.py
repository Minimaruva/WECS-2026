import os
import random
import threading
import time
import platform
import subprocess
from tkinter import Toplevel, Label
from PIL import Image, ImageTk
import pygame

class Punisher:
    def __init__(self, media_folder, root_window):
        self.media_folder = media_folder
        self.is_punishing = False
        self.punish_thread = None
        self.windows = []
        self.root = root_window
        self.pending_images = []
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()

    def start_punishment(self):
        if self.is_punishing:
            return
        self.is_punishing = True
        self.punish_thread = threading.Thread(target=self._spam_loop, daemon=True)
        self.punish_thread.start()
        self._process_pending_images()

    def stop_punishment(self):
        self.is_punishing = False
        self.close_all_windows()
        pygame.mixer.stop()  # Instantly stop all playing audio

    def close_all_windows(self):
        """Close all punishment windows"""
        for window in self.windows[:]: 
            try:
                window.destroy()
            except:
                pass
        self.windows.clear()
        self.pending_images.clear()

    def _process_pending_images(self):
        """Process pending images on the main thread"""
        if not self.is_punishing:
            return
            
        while self.pending_images and len(self.windows) < 10: 
            image_path = self.pending_images.pop(0)
            self._open_image_window(image_path)
        
        if self.is_punishing:
            self.root.after(100, self._process_pending_images)

    def _open_image_window(self, image_path):
        """Open an image/gif in a Tkinter window at random position"""
        try:
            window = Toplevel(self.root)
            window.title("Focus!")
            
            img = Image.open(image_path)
            max_size = (400, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            x = random.randint(0, 1200)
            y = random.randint(0, 700)
            window.geometry(f"+{x}+{y}")
            
            window.overrideredirect(True)
            window.attributes('-topmost', True)
            
            label = Label(window, image=photo)
            label.image = photo 
            label.pack()
            
            self.windows.append(window)
            
            window.after(5000, lambda: self._close_window(window))
            
        except Exception as e:
            print(f"Error displaying {image_path}: {e}")

    def _close_window(self, window):
        """Safely close a window"""
        try:
            if window in self.windows:
                self.windows.remove(window)
            window.destroy()
        except:
            pass

    def _open_video_window(self, video_path):
        """Open video with default player"""
        abs_path = os.path.abspath(video_path)
        if platform.system() == 'Windows':
            subprocess.Popen(['powershell', '-command', f'Start-Process "{abs_path}"'])
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', abs_path])
        else:
            subprocess.Popen(['xdg-open', abs_path])

    def _play_audio(self, audio_path):
        """Play audio in the background using pygame"""
        try:
            # Using Sound allows overlapping audio for maximum annoyance
            sound = pygame.mixer.Sound(audio_path)
            sound.play()
        except Exception as e:
            print(f"Error playing audio {audio_path}: {e}")

    def _spam_loop(self):
        image_ext = ('.png', '.jpg', '.jpeg', '.gif')
        audio_ext = ('.mp3', '.wav', '.ogg')
        video_ext = ('.mp4', '.avi', '.mkv')
        valid_ext = image_ext + audio_ext + video_ext
        
        if not os.path.exists(self.media_folder):
            print(f"Error: Folder '{self.media_folder}' does not exist.")
            return
            
        files = [f for f in os.listdir(self.media_folder) if f.lower().endswith(valid_ext)]
        
        if not files:
            print("No valid media files found in folder.")
            return

        random.shuffle(files)
        file_index = 0

        while self.is_punishing:
            media_path = os.path.join(self.media_folder, files[file_index])
            ext = media_path.lower()
            
            # Determine file type and route to the correct handler
            if ext.endswith(image_ext):
                self.pending_images.append(media_path)
            elif ext.endswith(audio_ext):
                self._play_audio(media_path)
            elif ext.endswith(video_ext):
                self._open_video_window(media_path)
            
            file_index = (file_index + 1) % len(files)
            
            # Delay before opening the next file
            time.sleep(1.5)