import os
import random
import threading
import time
import webbrowser
import platform
import subprocess

# this is punishment for getting distracted

class Punisher:
    def __init__(self, media_folder):
        self.media_folder = media_folder
        self.is_punishing = False
        self.punish_thread = None

    def start_punishment(self):
        if self.is_punishing:
            return
        self.is_punishing = True
        self.punish_thread = threading.Thread(target=self._spam_loop, daemon=True)
        self.punish_thread.start()

    def stop_punishment(self):
        self.is_punishing = False

    def _spam_loop(self):
        valid_ext = ('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mp3', '.wav')
        
        if not os.path.exists(self.media_folder):
            print(f"Error: Folder '{self.media_folder}' does not exist.")
            return
            
        files = [f for f in os.listdir(self.media_folder) if f.lower().endswith(valid_ext)]
        
        if not files:
            print("No valid media files found in folder.")
            return

        while self.is_punishing:
            media_path = os.path.join(self.media_folder, random.choice(files))
            abs_path = os.path.abspath(media_path)

            # Random position on screen
            x = random.randint(0, 1200)
            y = random.randint(0, 700)

            # Let the OS handle the video/gif/audio playback to save resources
            if platform.system() == 'Windows':
                # Use PowerShell to open with position (limitation: default app doesn't always respect position)
                subprocess.Popen(['powershell', '-command', f'Start-Process "{abs_path}"'])
            elif platform.system() == 'Darwin': # macOS
                subprocess.Popen(['open', abs_path])
            else: # Linux
                subprocess.Popen(['xdg-open', abs_path])

            # Wait before opening the next window so you don't instantly crash the PC
            time.sleep(2.0)