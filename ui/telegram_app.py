"""
Telegram typewriter app — sends a message to a configured Telegram chat and
displays incoming replies with a typewriter animation in a terminal-style UI.

Required environment variables (set in .env):
    TOKEN   — Telegram bot token
    CHAT_ID — Target chat ID
"""

import os
import threading
import tkinter as tk

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


class TypeWriterApp:
    POLL_INTERVAL_MS = 3000       # Normal polling cadence
    ERROR_RETRY_INTERVAL_MS = 5000
    TYPE_SPEED_MS = 50            # Delay between typed characters

    def __init__(self, root, main_menu_ref=None):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.is_running = True

        self.root.title("Terminal")
        self.root.geometry("600x400")
        self.root.configure(bg="black")

        if main_menu_ref:
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.text_area = tk.Text(
            root,
            bg="black",
            fg="#8ACE00",
            font=("Courier New", 14),
            relief="flat",
            padx=20,
            pady=20,
            borderwidth=0,
        )
        self.text_area.pack(expand=True, fill="both")

        # Typewriter state
        self.content = ""
        self.index = 0
        self.is_typing = False

        self.message_to_crush = "Hi crush :D I failed to focus again..."
        self._display_system_msg(f"SENT MESSAGE TO CRUSH: {self.message_to_crush}")
        self._send_telegram_msg(self.message_to_crush)
        self._check_for_updates()

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def on_close(self):
        self.is_running = False
        self.root.destroy()
        if self.main_menu_ref:
            self.main_menu_ref.root.deiconify()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _display_system_msg(self, msg: str):
        self.text_area.insert(tk.END, f"> {msg}\n")

    # ------------------------------------------------------------------
    # Telegram I/O
    # ------------------------------------------------------------------

    def _send_telegram_msg(self, text: str):
        url = (
            f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            f"?chat_id={CHAT_ID}&text={text}"
        )
        threading.Thread(
            target=lambda: requests.get(url, timeout=5), daemon=True
        ).start()

    def _check_for_updates(self):
        if not self.is_running or not self.root.winfo_exists():
            return
        threading.Thread(target=self._fetch_updates, daemon=True).start()

    def _fetch_updates(self):
        if not self.is_running:
            return
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        try:
            response = requests.get(url, timeout=5).json()
            if response.get("result"):
                last_msg = response["result"][-1]
                msg_data = last_msg.get("message", {})
                text = msg_data.get("text")
                sender = msg_data.get("from", {}).get("first_name", "Crush")

                if not text or "WAIT" in text:
                    self._schedule_next_poll(self.POLL_INTERVAL_MS)
                    return

                new_content = f"\n> Message from {sender}: {text}"
                if new_content != self.content and not self.is_typing:
                    self.content = new_content
                    self.index = 0
                    self.is_typing = True
                    self.root.after(0, self._type_character)
                else:
                    self._schedule_next_poll(self.POLL_INTERVAL_MS)
            else:
                self._schedule_next_poll(self.POLL_INTERVAL_MS)
        except Exception:
            self.root.after(
                0,
                lambda: self._display_system_msg("CONNECTION ERROR. RETRYING..."),
            )
            self._schedule_next_poll(self.ERROR_RETRY_INTERVAL_MS)

    def _schedule_next_poll(self, delay_ms: int):
        if self.is_running:
            self.root.after(delay_ms, self._check_for_updates)

    def _type_character(self):
        if not self.is_running:
            return
        if self.index < len(self.content):
            self.text_area.insert(tk.END, self.content[self.index])
            self.text_area.see(tk.END)
            self.index += 1
            self.root.after(self.TYPE_SPEED_MS, self._type_character)
        else:
            self.is_typing = False
            self._check_for_updates()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypeWriterApp(root)
    root.mainloop()
