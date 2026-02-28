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

# print(TOKEN)
# print(CHAT_ID)


class TypeWriterApp:
    def __init__(self, root, main_menu_ref=None):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.is_running = True # FIX: Kill switch flag
        self.root.title("Terminal")
        self.root.geometry("600x400")
        self.root.configure(bg="black")

        if main_menu_ref:
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.text_area = tk.Text(
            root, bg="black", fg="#8ACE00", font=("Courier New", 14),
            relief="flat", padx=20, pady=20, borderwidth=0
        )
        self.text_area.pack(expand=True, fill="both")

        self.content = ""
        self.index = 0
        self.is_typing = False

        self.message_to_crush = "Hi crush :D I failed to focus again..."

        self.display_system_msg(f"SENT MESSAGE TO CRUSH: {self.message_to_crush}")
        self.send_telegram_msg(self.message_to_crush)
        self.check_for_updates()

    def on_close(self):
        self.is_running = False # FIX: Stop the polling loop
        if self.main_menu_ref:
            self.root.destroy()
            self.main_menu_ref.root.deiconify()
        else:
            self.root.destroy()

    def display_system_msg(self, msg):
        self.text_area.insert(tk.END, f"> {msg}\n")

    def send_telegram_msg(self, text):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
        try:
            threading.Thread(target=lambda: requests.get(url, timeout=5), daemon=True).start()
        except Exception as e:
            print(f"Error sending: {e}")

    def check_for_updates(self):
        if not self.is_running or not self.root.winfo_exists():
            return
            
        # Run network request in background thread to avoid UI freeze
        threading.Thread(target=self._fetch_updates, daemon=True).start()

    def _fetch_updates(self):
        """Background thread method for fetching Telegram updates"""
        if not self.is_running:
            return
            
        print("[DEBUG] polling update")
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        try:
            response = requests.get(url, timeout=5).json()
            if response.get("result"):
                last_msg = response["result"][-1]
                
                # FIX: Safe extraction. Will not crash if message is a sticker/photo
                msg_data = last_msg.get("message", {})
                text = msg_data.get("text")
                sender_data = msg_data.get("from", {})
                sender = sender_data.get("first_name", "Crush")
                
                # Skip if there is no text (e.g., it's a photo)
                if not text:
                    if self.is_running:
                        self.root.after(3000, self.check_for_updates)
                    return

                new_content = f"\n> Message from {sender}: {text}"
                if self.content != new_content and not self.is_typing:
                    self.content = new_content
                    self.index = 0
                    self.is_typing = True
                    self.root.after(0, self.type_character)
                else:
                    if self.is_running:
                        self.root.after(3000, self.check_for_updates)
            else:
                if self.is_running:
                    self.root.after(3000, self.check_for_updates)
        except Exception as e:
            if self.is_running:
                self.root.after(0, lambda: self.display_system_msg("CONNECTION ERROR. RETRYING..."))
                self.root.after(5000, self.check_for_updates)

        print("[DEBUG] finished polling update")

    def type_character(self):
        if not self.is_running: # FIX: Stop typing if window closed
            return
            
        if self.index < len(self.content):
            char = self.content[self.index]
            self.text_area.insert(tk.END, char)
            self.text_area.see(tk.END)
            self.index += 1
            if self.is_running:
                self.root.after(50, self.type_character)
        else:
            print("[DEBUG] FINISHED TYPING")
            self.is_typing = False
            if self.is_running:
                self.check_for_updates()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypeWriterApp(root)
    root.mainloop()