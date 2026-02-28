import tkinter as tk
import math
import random
from combinedMsg import TypeWriterApp


class ChallengeWheel:
    def __init__(self, root):
        self.root = root
        self.root.title("Challenge Spinner")
        self.root.geometry("500x600")
        self.root.configure(bg="#8ACE00")

        self.root.overrideredirect(True)
        
        # Universal Escape key bind to close the app
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 500, 600
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Close button for the main wheel interface
        self.close_btn = tk.Button(root, text="X", font=("Arial", 14, "bold"), bg="#8ACE00", fg="black", bd=0, command=self.root.destroy)
        self.close_btn.place(x=460, y=10)

        self.challenges = ["touch grass", "shower", "exercise"]
        self.colors = ["#ffffff", "#000000"]
        self.angle = 0
        self.speed = 0
        self.is_spinning = False

        self.canvas = tk.Canvas(
            root, width=400, height=400, bg="#8ACE00", highlightthickness=0)
        self.canvas.pack(pady=40)

        self.canvas.create_polygon(
            380, 200, 400, 180, 400, 220, fill="red", tags="pointer")

        self.spin_btn = tk.Button(root, text="SPIN", font=("Arial", 20, "bold"),
                                  command=self.start_spin, bg="black", fg="#8ACE00")
        self.spin_btn.pack(pady=10)

        self.result_label = tk.Label(
            root, text="Press Spin", font=("Arial", 18), bg="#8ACE00")
        self.result_label.pack(pady=10)

        self.draw_wheel()

    def draw_wheel(self):
        self.canvas.delete("slice")
        num_slices = len(self.challenges)
        slice_angle = 360 / num_slices

        for i in range(num_slices):
            start_pos = (i * slice_angle + self.angle) % 360
            color = self.colors[i % len(self.colors)]

            self.canvas.create_arc(50, 50, 350, 350, start=start_pos, extent=slice_angle,
                                   fill=color, tags="slice", outline="gray")

            text_angle = math.radians(start_pos + slice_angle / 2)
            tx = 200 + 100 * math.cos(text_angle)
            ty = 200 - 100 * math.sin(text_angle)

            t_color = "black" if color == "#ffffff" else "#8ACE00"
            self.canvas.create_text(tx, ty, text=self.challenges[i], angle=start_pos + slice_angle/2,
                                    fill=t_color, font=("Arial", 10, "bold"), tags="slice")

    def start_spin(self):
        if not self.is_spinning:
            num_slices = len(self.challenges)
            slice_angle = 360 / num_slices

            # Hardcoded to 0 for the rigged "touch grass" outcome
            target_idx = 0
            random_offset = random.uniform(5, slice_angle-5)
            target_final_angle = (
                360 - (target_idx * slice_angle) - random_offset)

            current_angle_mod = self.angle % 360
            dist_to_travel = (target_final_angle - current_angle_mod)
            if dist_to_travel < 0:
                dist_to_travel += 360
            total_rotation = dist_to_travel + (360 * 5)

            self.speed = total_rotation * (1 - 0.97)
            self.is_spinning = True
            self.animate_spin()

    def animate_spin(self):
        if self.speed > 0.05:
            self.angle += self.speed
            self.speed *= 0.97
            self.draw_wheel()
            self.root.after(20, self.animate_spin)
        else:
            self.is_spinning = False
            self.determine_winner()

    def determine_winner(self):
        num_slices = len(self.challenges)
        slice_angle = 360 / num_slices
        winning_index = int(
            ((360 - (self.angle % 360)) / slice_angle) % num_slices)
        result = self.challenges[winning_index]
        self.result_label.config(text=f"CHALLENGE: {result}")
        
        if result == "touch grass":
            self.root.after(1500, self.load_grass_interface)

    def load_grass_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Re-add close button for this view
        self.close_btn = tk.Button(self.root, text="X", font=("Arial", 14, "bold"), bg="#8ACE00", fg="black", bd=0, command=self.root.destroy)
        self.close_btn.place(x=460, y=10)

        tk.Label(self.root, text="TOUCH GRASS", font=("Arial", 40, "bold", "italic"), bg="#8ACE00", fg="black").pack(pady=20)

        self.timer_sec = 0
        self.timer_label = tk.Label(self.root, text="00:00", font=("Arial", 36, "bold"), bg="#8ACE00", fg="black")
        self.timer_label.pack(pady=5)

        self.cam_frame = tk.Frame(self.root, width=400, height=250, bg="black")
        self.cam_frame.pack(pady=10)
        self.cam_frame.pack_propagate(False)
        tk.Label(self.cam_frame, text="[ CAMERA FEED DUMMY ]", font=("Arial", 16, "bold"), bg="black", fg="#8ACE00").place(relx=0.5, rely=0.5, anchor="center")

        self.capture_btn = tk.Button(self.root, text="TAKE PICTURE", font=("Arial", 20, "bold"), bg="black", fg="#8ACE00", command=self.take_picture)
        self.capture_btn.pack(pady=15)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 22, "bold"), bg="#8ACE00", fg="red")
        self.status_label.pack(pady=10)

        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        mins, secs = divmod(self.timer_sec, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.timer_sec += 1
        self.root.after(1000, self.update_timer)

    def take_picture(self):
        self.timer_running = False
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="GRASS DETECTED...", fg="black")
        self.root.after(1500, self.trigger_sike)

    def trigger_sike(self):
        self.status_label.config(text="SIKE TOO LATE", fg="red")
        self.root.after(1500, self.launch_send_message)

    def launch_send_message(self):
        self.status_label.config(text="LAUNCHING MESSAGE PROTOCOL...", fg="black")
        self.root.after(1500, self.load_terminal_interface)

    def load_terminal_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Instantiate the imported app
        app = TypeWriterApp(self.root)
        
        # Add a close button specifically for the terminal geometry
        term_close_btn = tk.Button(self.root, text="X", font=("Arial", 14, "bold"), bg="black", fg="#8ACE00", bd=0, command=self.root.destroy)
        term_close_btn.place(x=560, y=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChallengeWheel(root)
    root.mainloop()