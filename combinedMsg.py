import tkinter as tk
import requests
import threading
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
# CHANGE
load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print(TOKEN)
print(CHAT_ID)


class TypeWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal")
        self.root.geometry("600x400")
        self.root.configure(bg="black")

        self.text_area = tk.Text(
            root, bg="black", fg="#8ACE00", font=("Courier New", 14),
            relief="flat", padx=20, pady=20, borderwidth=0
        )
        self.text_area.pack(expand=True, fill="both")

        self.content = ""
        self.index = 0
        self.is_typing = False

        self.message_to_crush = "hello :D"

        # Initial Status
        self.display_system_msg(
            f"SENT MESSAGE TO CRUSH: {self.message_to_crush}")

        # Send the initial message
        self.send_telegram_msg(self.message_to_crush)

        # Start checking for a response every 3 seconds
        self.check_for_updates()

    def display_system_msg(self, msg):
        """Helper to show status text before the real typing begins"""
        self.text_area.insert(tk.END, f"> {msg}\n")

    def send_telegram_msg(self, text):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
        try:
            # We use a thread so the UI doesn't stutter when sending
            threading.Thread(target=lambda: requests.get(url)).start()
        except Exception as e:
            print(f"Error sending: {e}")

    def check_for_updates(self):
        print("[DEBUG] polling update")
        """Polls Telegram for a new message"""
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        try:
            response = requests.get(url).json()
            if response.get("result"):
                last_msg = response["result"][-1]
                text = last_msg["message"]["text"]
                sender = last_msg["message"]["from"]["first_name"]
                sender = "Crush"

                # Logic: If we haven't started typing this specific message yet
                new_content = f"\n> Message from {sender}: {text}"
                if self.content != new_content and not self.is_typing:
                    self.content = new_content
                    self.index = 0
                    self.is_typing = True
                    self.type_character()
                else:
                    self.root.after(3000, self.check_for_updates)
            else:
                # No message yet, check again in 3 seconds
                self.root.after(300, self.check_for_updates)
        except Exception as e:
            self.display_system_msg("CONNECTION ERROR. RETRYING...")
            self.root.after(5000, self.check_for_updates)

        print("[DEBUG] finished polling update")

    def type_character(self):
        """The typewriter effect animation"""
        if self.index < len(self.content):
            char = self.content[self.index]
            self.text_area.insert(tk.END, char)
            self.text_area.see(tk.END)
            self.index += 1
            self.root.after(50, self.type_character)
        else:
            print("[DEBUG] FINISHED TYPING")
            self.is_typing = False
            self.check_for_updates()
            # After finishing typing, you could potentially
            # start checking for the NEXT message here.


if __name__ == "__main__":
    root = tk.Tk()
    app = TypeWriterApp(root)
    root.mainloop()
