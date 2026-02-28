"""
Challenge wheel — a spinning-wheel UI that assigns the user a challenge
(e.g., "touch grass"). Includes a camera-based grass detector powered by
the CLIP zero-shot image-classification model.
"""

import math
import random
import threading
import tkinter as tk

import cv2
from PIL import Image, ImageTk
from transformers import pipeline

from ui.telegram_app import TypeWriterApp


class ChallengeWheel:
    CHALLENGES = ["touch grass", "shower", "exercise"]
    SLICE_COLORS = ["#ffffff", "#000000"]

    def __init__(self, root):
        self.root = root
        self.root.title("Challenge Spinner")
        self.root.geometry("500x700")
        self.root.configure(bg="#8ACE00")
        self.root.overrideredirect(True)

        self._center_window(500, 700)

        # Load AI model in background to keep UI responsive
        self.classifier = None
        threading.Thread(target=self._load_model, daemon=True).start()

        self.root.bind("<Escape>", lambda e: self.close_app())

        # Close button
        self.close_btn = tk.Button(
            self.root, text="X", font=("Arial", 14, "bold"),
            bg="#8ACE00", fg="black", bd=0, command=self.close_app,
        )
        self.close_btn.place(x=460, y=10)

        # Wheel state
        self.angle = 0.0
        self.speed = 0.0
        self.is_spinning = False

        self.canvas = tk.Canvas(
            self.root, width=400, height=400, bg="#8ACE00", highlightthickness=0
        )
        self.canvas.pack(pady=40)
        self.canvas.create_polygon(380, 200, 400, 180, 400, 220, fill="red", tags="pointer")

        self.spin_btn = tk.Button(
            self.root, text="SPIN", font=("Arial", 20, "bold"),
            command=self.start_spin, bg="black", fg="#8ACE00",
        )
        self.spin_btn.pack(pady=10)

        self.result_label = tk.Label(
            self.root, text="Press Spin", font=("Arial", 18), bg="#8ACE00"
        )
        self.result_label.pack(pady=10)

        self._draw_wheel()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _center_window(self, width, height):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _load_model(self):
        self.classifier = pipeline(
            "zero-shot-image-classification", model="openai/clip-vit-base-patch32"
        )

    # ------------------------------------------------------------------
    # Wheel drawing & spinning
    # ------------------------------------------------------------------

    def _draw_wheel(self):
        self.canvas.delete("slice")
        num_slices = len(self.CHALLENGES)
        slice_angle = 360 / num_slices

        for i, challenge in enumerate(self.CHALLENGES):
            start_pos = (i * slice_angle + self.angle) % 360
            color = self.SLICE_COLORS[i % len(self.SLICE_COLORS)]
            self.canvas.create_arc(
                50, 50, 350, 350,
                start=start_pos, extent=slice_angle,
                fill=color, tags="slice", outline="gray",
            )
            text_angle = math.radians(start_pos + slice_angle / 2)
            tx = 200 + 100 * math.cos(text_angle)
            ty = 200 - 100 * math.sin(text_angle)
            t_color = "black" if color == "#ffffff" else "#8ACE00"
            self.canvas.create_text(
                tx, ty, text=challenge,
                angle=start_pos + slice_angle / 2,
                fill=t_color, font=("Arial", 10, "bold"), tags="slice",
            )

    def start_spin(self):
        if self.is_spinning:
            return
        num_slices = len(self.CHALLENGES)
        slice_angle = 360 / num_slices
        target_idx = 0
        random_offset = random.uniform(5, slice_angle - 5)
        target_final_angle = 360 - (target_idx * slice_angle) - random_offset
        current_angle_mod = self.angle % 360
        dist = target_final_angle - current_angle_mod
        if dist < 0:
            dist += 360
        total_rotation = dist + 360 * 5

        self.speed = total_rotation * (1 - 0.97)
        self.is_spinning = True
        self._animate_spin()

    def _animate_spin(self):
        if self.speed > 0.05:
            self.angle += self.speed
            self.speed *= 0.97
            self._draw_wheel()
            self.root.after(20, self._animate_spin)
        else:
            self.is_spinning = False
            self._determine_winner()

    def _determine_winner(self):
        num_slices = len(self.CHALLENGES)
        slice_angle = 360 / num_slices
        winning_index = int(((360 - (self.angle % 360)) / slice_angle) % num_slices)
        result = self.CHALLENGES[winning_index]
        self.result_label.config(text=f"CHALLENGE: {result}")

        if result == "touch grass":
            self.root.after(1500, self._load_grass_interface)

    # ------------------------------------------------------------------
    # Grass-detection interface
    # ------------------------------------------------------------------

    def _load_grass_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.close_btn = tk.Button(
            self.root, text="X", font=("Arial", 14, "bold"),
            bg="#8ACE00", fg="black", bd=0, command=self.close_app,
        )
        self.close_btn.place(x=460, y=10)

        tk.Label(
            self.root, text="TOUCH GRASS",
            font=("Arial", 32, "bold", "italic"), bg="#8ACE00", fg="black",
        ).pack(pady=10)

        self.timer_sec = 0
        self.timer_label = tk.Label(
            self.root, text="00:00",
            font=("Arial", 28, "bold"), bg="#8ACE00", fg="black",
        )
        self.timer_label.pack(pady=5)

        cam_frame = tk.Frame(self.root, width=400, height=280, bg="black")
        cam_frame.pack(pady=10)
        cam_frame.pack_propagate(False)
        self.video_label = tk.Label(cam_frame, bg="black")
        self.video_label.pack(expand=True, fill="both")

        self.capture_btn = tk.Button(
            self.root, text="TAKE PICTURE",
            font=("Arial", 18, "bold"), bg="black", fg="#8ACE00",
            command=self._take_picture,
        )
        self.capture_btn.pack(pady=10)

        self.status_label = tk.Label(
            self.root, text="Ready to capture...",
            font=("Arial", 16, "bold"), bg="#8ACE00", fg="black", wraplength=450,
        )
        self.status_label.pack(pady=10)

        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.camera_running = True
        self.current_img = None
        self._update_camera_frame()

        self.timer_running = True
        self._update_grass_timer()

    def _update_camera_frame(self):
        if not self.camera_running:
            return
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (400, 280))
            self.current_img = Image.fromarray(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
            imgtk = ImageTk.PhotoImage(image=self.current_img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(15, self._update_camera_frame)

    def _update_grass_timer(self):
        if not self.timer_running:
            return
        mins, secs = divmod(self.timer_sec, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.timer_sec += 1
        self.root.after(1000, self._update_grass_timer)

    def _take_picture(self):
        if not self.current_img:
            return
        self.timer_running = False
        self.camera_running = False
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="ANALYZING IMAGE...", fg="blue")
        self.status_label.update_idletasks()
        self.root.after(100, self._analyze_image)

    def _analyze_image(self):
        if self.classifier is None:
            self.status_label.config(text="LOADING AI MODEL... PLEASE WAIT", fg="orange")
            self.root.after(1000, self._analyze_image)
            return

        results = self.classifier(
            self.current_img, candidate_labels=["grass", "not grass"]
        )
        grass_score = next(
            (item["score"] for item in results if item["label"] == "grass"), 0
        )
        accuracy = grass_score * 100

        if accuracy > 50:
            self.status_label.config(text=f"GRASS DETECTED: {accuracy:.2f}%", fg="green")
        else:
            self.status_label.config(
                text=f"NO GRASS DETECTED. (Grass: {accuracy:.2f}%)", fg="red"
            )

        self.status_label.update_idletasks()
        self.root.after(2000, self._trigger_sike)

    def _trigger_sike(self):
        self.status_label.config(text="SIKE TOO LATE", fg="red")
        self.status_label.update_idletasks()
        self.root.after(1500, self._launch_send_message)

    def _launch_send_message(self):
        self.status_label.config(text="LAUNCHING MESSAGE PROTOCOL...", fg="black")
        self.status_label.update_idletasks()
        self.root.after(1500, self._load_terminal_interface)

    def _load_terminal_interface(self):
        self._release_camera()
        for widget in self.root.winfo_children():
            widget.destroy()

        TypeWriterApp(self.root)

        close_btn = tk.Button(
            self.root, text="X", font=("Arial", 14, "bold"),
            bg="black", fg="#8ACE00", bd=0, command=self.close_app,
        )
        close_btn.place(x=560, y=10)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _release_camera(self):
        self.camera_running = False
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()

    def close_app(self):
        self._release_camera()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChallengeWheel(root)
    root.mainloop()
