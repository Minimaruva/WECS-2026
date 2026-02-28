import tkinter as tk
import math
import random


class ChallengeWheel:
    def __init__(self, root):
        self.root = root
        self.root.title("Challenge Spinner")
        self.root.geometry("500x600")
        self.root.configure(bg="#8ACE00")  # Keeping the brat aesthetic

        self.root.overrideredirect(True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 500, 600
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Configuration
        self.challenges = ["touch grass", "shower", "exercise"]
        self.colors = ["#ffffff", "#000000"]  # High contrast black and white
        self.angle = 0
        self.speed = 0
        self.is_spinning = False

        # Canvas for the wheel
        self.canvas = tk.Canvas(
            root, width=400, height=400, bg="#8ACE00", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Draw static elements (Pointer)
        self.canvas.create_polygon(
            380, 200, 400, 180, 400, 220, fill="red", tags="pointer")

        # Spin Button
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

            # Draw the arc
            self.canvas.create_arc(50, 50, 350, 350, start=start_pos, extent=slice_angle,
                                   fill=color, tags="slice", outline="gray")

            # Calculate text position (midpoint of arc)
            text_angle = math.radians(start_pos + slice_angle / 2)
            tx = 200 + 100 * math.cos(text_angle)
            ty = 200 - 100 * math.sin(text_angle)

            # Contrast text color
            t_color = "black" if color == "#ffffff" else "#8ACE00"
            self.canvas.create_text(tx, ty, text=self.challenges[i], angle=start_pos + slice_angle/2,
                                    fill=t_color, font=("Arial", 10, "bold"), tags="slice")

    def start_spin(self):
        if not self.is_spinning:
            num_slices = len(self.challenges)
            slice_angle = 360 / num_slices

            target_idx = 0
            random_offset = random.uniform(5, slice_angle-5)
            target_final_angle = (
                360 - (target_idx * slice_angle) - random_offset)

            current_angle_mod = self.angle % 360
            dist_to_travel = (target_final_angle - current_angle_mod)
            if dist_to_travel < 0:
                dist_to_travel += 360
            total_rotation = dist_to_travel + (360 * 5)

            self.speed = total_rotation * (1 - 0.97)  # Random initial push
            self.is_spinning = True
            self.animate_spin()

    def animate_spin(self):
        if self.speed > 0.05:
            self.angle += self.speed
            self.speed *= 0.97  # Friction: reduces speed by 3% each frame
            self.draw_wheel()
            self.root.after(20, self.animate_spin)
        else:
            self.is_spinning = False
            self.determine_winner()

    def determine_winner(self):
        # The pointer is at 0 degrees (right side)
        # We calculate which slice landed at the pointer position
        num_slices = len(self.challenges)
        slice_angle = 360 / num_slices
        # Normalize angle and find index
        winning_index = int(
            ((360 - (self.angle % 360)) / slice_angle) % num_slices)
        result = self.challenges[winning_index]
        self.result_label.config(text=f"CHALLENGE: {result}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChallengeWheel(root)
    root.mainloop()
